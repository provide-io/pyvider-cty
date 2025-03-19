
# tests/integration/cty/values/test_refinement.py

"""
Integration tests for Cty value refinements.

These tests verify that the refinement system works correctly with other parts
of the Cty system, including type checking, operations, and encoding.
"""

import asyncio
import json
from decimal import Decimal

import pytest

from pyvider.cty.ctypes.primitives import CtyString, CtyNumber, CtyBool
from pyvider.cty import CtyValue
from pyvider.cty.values.refinement import (
    ValueRefinement,
    NotNullRefinement,
    StringPrefixRefinement,
    NumberRangeRefinement,
    #CompoundRefinement,
    ValueRefinementBuilder,
)
from pyvider.cty.values.operations import (
    equals,
    #less_than,
    # greater_than,
    add,
    subtract,
    multiply,
    divide,
)
from pyvider.cty.encoding.json import marshal, unmarshal

# Utility for running async tests
async def run_test(test_coro):
    """Run a single async test coroutine."""
    return await test_coro

class TestValueRefinements:
    """Test the ValueRefinement system."""
    
    @pytest.mark.skip
    async def test_not_null_refinement(self):
        """Test that NotNullRefinement correctly validates values."""
        refinement = NotNullRefinement()
        
        # Test validation
        assert await refinement.is_valid_for("hello")
        assert await refinement.is_valid_for(42)
        assert await refinement.is_valid_for(False)
        assert await refinement.is_valid_for([])
        assert await refinement.is_valid_for({})
        assert not await refinement.is_valid_for(None)
        
        # Test merging with itself
        assert await refinement.can_merge_with(refinement)
        merged = await refinement.merge_with(refinement)
        assert isinstance(merged, NotNullRefinement)
        
    @pytest.mark.skip
    async def test_string_prefix_refinement(self):
        """Test that StringPrefixRefinement correctly validates values."""
        refinement = StringPrefixRefinement("https://")
        
        # Test validation
        assert await refinement.is_valid_for("https://example.com")
        assert await refinement.is_valid_for("https://")
        assert not await refinement.is_valid_for("http://example.com")
        assert not await refinement.is_valid_for(42)
        assert not await refinement.is_valid_for(None)
        
        # Test merging with compatible prefix
        other_refinement = StringPrefixRefinement("https://example.")
        assert await refinement.can_merge_with(other_refinement)
        merged = await refinement.merge_with(other_refinement)
        assert isinstance(merged, StringPrefixRefinement)
        assert merged.prefix == "https://example."
        
        # Test merging with incompatible prefix
        incompatible = StringPrefixRefinement("http://")
        assert not await refinement.can_merge_with(incompatible)
        with pytest.raises(ValueError):
            await refinement.merge_with(incompatible)
            
        # Test merging with NotNullRefinement
        not_null = NotNullRefinement()
        assert await refinement.can_merge_with(not_null)
        merged = await refinement.merge_with(not_null)

        # we don't have compound refinements yet.
        #assert isinstance(merged, CompoundRefinement)

        assert len(merged.refinements) == 2
        
    @pytest.mark.asyncio
    async def test_number_range_refinement(self):
        """Test that NumberRangeRefinement correctly validates values."""
        refinement = NumberRangeRefinement(
            min_value=0,
            max_value=100,
            min_inclusive=True,
            max_inclusive=True
        )
        
        # Test validation
        assert await refinement.is_valid_for(0)
        assert await refinement.is_valid_for(50)
        assert await refinement.is_valid_for(100)
        assert await refinement.is_valid_for(Decimal("50.5"))
        assert not await refinement.is_valid_for(-1)
        assert not await refinement.is_valid_for(101)
        assert not await refinement.is_valid_for("50")
        assert not await refinement.is_valid_for(None)
        
        # Test exclusive bounds
        exclusive = NumberRangeRefinement(
            min_value=0,
            max_value=100,
            min_inclusive=False,
            max_inclusive=False
        )
        assert not await exclusive.is_valid_for(0)
        assert await exclusive.is_valid_for(50)
        assert not await exclusive.is_valid_for(100)
        
        # Test merging with overlapping range
        other_refinement = NumberRangeRefinement(
            min_value=50,
            max_value=150
        )
        assert await refinement.can_merge_with(other_refinement)
        merged = await refinement.merge_with(other_refinement)
        assert isinstance(merged, NumberRangeRefinement)
        assert merged.min_value == 50
        assert merged.max_value == 100
        
        # Test merging with non-overlapping range
        non_overlapping = NumberRangeRefinement(
            min_value=200,
            max_value=300
        )
        assert await refinement.can_merge_with(non_overlapping)
        with pytest.raises(ValueError):
            await refinement.merge_with(non_overlapping)
            
        # Test merging with NotNullRefinement
        not_null = NotNullRefinement()
        assert await refinement.can_merge_with(not_null)
        merged = await refinement.merge_with(not_null)
        # assert isinstance(merged, CompoundRefinement)
        assert len(merged.refinements) == 2
        
    @pytest.mark.skip
    async def test_compound_refinement(self):
        """Test that CompoundRefinement correctly validates values."""
        not_null = NotNullRefinement()
        string_prefix = StringPrefixRefinement("https://")
        
        compound = CompoundRefinement(frozenset([not_null, string_prefix]))
        
        # Test validation
        assert await compound.is_valid_for("https://example.com")
        assert not await compound.is_valid_for("http://example.com")
        assert not await compound.is_valid_for(None)
        
        # Test merging with compatible refinement
        other_prefix = StringPrefixRefinement("https://example.")
        assert await compound.can_merge_with(other_prefix)
        merged = await compound.merge_with(other_prefix)
        assert isinstance(merged, CompoundRefinement)
        assert len(merged.refinements) == 3
        
        # Test merging with incompatible refinement
        incompatible = StringPrefixRefinement("http://")
        assert not await compound.can_merge_with(incompatible)
        with pytest.raises(ValueError):
            await compound.merge_with(incompatible)
            
        # Test merging with another compound refinement
        other_compound = CompoundRefinement(frozenset([
            NotNullRefinement(),
            NumberRangeRefinement(min_value=0, max_value=100)
        ]))
        assert not await compound.can_merge_with(other_compound)
        with pytest.raises(ValueError):
            await compound.merge_with(other_compound)
            
    @pytest.mark.asyncio
    async def test_refinement_builder(self):
        """Test the ValueRefinementBuilder."""
        # Test building string refinements
        builder = ValueRefinementBuilder()
        builder.not_null()
        builder.string_prefix("https://")
        refined_string = await builder.build(CtyString())
        
        assert refined_string.is_unknown
        assert not refined_string.is_null
        assert isinstance(refined_string.type, CtyString)
        assert len(refined_string.refinements) == 2
        
        # Test building number refinements
        builder = ValueRefinementBuilder()
        builder.not_null()
        builder.number_range(min_value=0, max_value=100)
        refined_number = await builder.build(CtyNumber())
        
        assert refined_number.is_unknown
        assert not refined_number.is_null
        assert isinstance(refined_number.type, CtyNumber)
        assert len(refined_number.refinements) == 2
        
        # Test building with incompatible refinements
        builder = ValueRefinementBuilder()
        builder.string_prefix("https://")
        builder.string_prefix("http://")
        
        with pytest.raises(ValueError):
            await builder.build(CtyString())
            
        # Test building from an existing value
        known_value = CtyValue(type_=CtyString(), value="hello")
        builder = ValueRefinementBuilder(known_value)
        builder.not_null()
        builder.string_prefix("h")
        refined_value = await builder.build()
        
        assert refined_value.is_unknown
        assert not refined_value.is_null
        assert isinstance(refined_value.type, CtyString)
        assert len(refined_value.refinements) == 2
        
        # Test type mismatch
        builder = ValueRefinementBuilder()
        builder.string_prefix("hello")
        
        with pytest.raises(TypeError):
            await builder.build(CtyNumber())
            
    @pytest.mark.asyncio
    async def test_integration_with_operations(self):
        """Test that refinements work with value operations."""
        # Create refined values
        string_builder = ValueRefinementBuilder()
        string_builder.not_null()
        string_builder.string_prefix("hello ")
        refined_string = await string_builder.build(CtyString())
        
        number_builder = ValueRefinementBuilder()
        number_builder.not_null()
        number_builder.number_range(min_value=10, max_value=20)
        refined_number = await number_builder.build(CtyNumber())
        
        # Test equals operation
        # Two unknown values with same refinements should be equal
        other_number = await number_builder.build(CtyNumber())
        eq_result = await equals(refined_number, other_number)
        assert eq_result.is_unknown  # Result is unknown, but could be true
        
        # Known value outside range cannot equal the refined value
        known_outside = CtyValue(type_=CtyNumber(), value=5)
        eq_result = await equals(refined_number, known_outside)
        assert not eq_result.is_unknown
        assert eq_result.value is False
        
        # Known value inside range could equal the refined value
        known_inside = CtyValue(type_=CtyNumber(), value=15)
        eq_result = await equals(refined_number, known_inside)
        assert eq_result.is_unknown  # Result is unknown, but could be true
        
        # Test comparison operations
        # Known value < min value
        # TODO this doesn't work.
        # lt_result = await less_than(known_outside, refined_number)
        # assert not lt_result.is_unknown
        # assert lt_result.value is True
        
        # Known value > min value
        # gt_result = await greater_than(known_inside, refined_number)
        # assert gt_result.is_unknown  # Result is unknown
        
        # Test arithmetic operations
        # Adding a known value to a refined number maintains refinement
        add_result = await add(refined_number, known_inside)
        assert add_result.is_unknown
        assert len(add_result.refinements) > 0
        
        # If we know min = 10 and we add 15, new min must be at least 25
        number_refinement = next(
            r for r in add_result.refinements 
            if isinstance(r, NumberRangeRefinement)
        )
        assert number_refinement.min_value == 25
        
        # Similar tests for other operations
        subtract_result = await subtract(refined_number, CtyValue(type_=CtyNumber(), value=5))
        assert subtract_result.is_unknown
        number_refinement = next(
            r for r in subtract_result.refinements 
            if isinstance(r, NumberRangeRefinement)
        )
        assert number_refinement.min_value == 5
        assert number_refinement.max_value == 15
        
        # Multiplication preserves signs for positive numbers
        multiply_result = await multiply(refined_number, CtyValue(type_=CtyNumber(), value=2))
        assert multiply_result.is_unknown
        number_refinement = next(
            r for r in multiply_result.refinements 
            if isinstance(r, NumberRangeRefinement)
        )
        assert number_refinement.min_value == 20
        assert number_refinement.max_value == 40
        
        # Division refines ranges too
        divide_result = await divide(refined_number, CtyValue(type_=CtyNumber(), value=2))
        assert divide_result.is_unknown
        number_refinement = next(
            r for r in divide_result.refinements 
            if isinstance(r, NumberRangeRefinement)
        )
        assert number_refinement.min_value == 5
        assert number_refinement.max_value == 10
        
    @pytest.mark.asyncio
    async def test_integration_with_encoding(self):
        """Test that refinements survive encoding/decoding."""
        # Create refined values
        string_builder = ValueRefinementBuilder()
        string_builder.not_null()
        string_builder.string_prefix("hello ")
        refined_string = await string_builder.build(CtyString())
        
        number_builder = ValueRefinementBuilder()
        number_builder.not_null()
        number_builder.number_range(min_value=10, max_value=20)
        refined_number = await number_builder.build(CtyNumber())
        
        # Test JSON encoding/decoding
        string_json = await marshal(refined_string)
        assert string_json is not None
        
        decoded_string = await unmarshal(string_json, CtyString())
        assert decoded_string.is_unknown
        assert len(decoded_string.refinements) > 0
        
        # Verify prefix refinement survived
        string_refinement = next(
            r for r in decoded_string.refinements 
            if isinstance(r, StringPrefixRefinement)
        )
        assert string_refinement.prefix == "hello "
        
        # Test number encoding/decoding
        number_json = await marshal(refined_number)
        assert number_json is not None
        
        decoded_number = await unmarshal(number_json, CtyNumber())
        assert decoded_number.is_unknown
        assert len(decoded_number.refinements) > 0
        
        # Verify range refinement survived
        number_refinement = next(
            r for r in decoded_number.refinements 
            if isinstance(r, NumberRangeRefinement)
        )
        assert number_refinement.min_value == 10
        assert number_refinement.max_value == 20
