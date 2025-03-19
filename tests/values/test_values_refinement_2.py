
# tests/values/test_refinement.py

import pytest
from decimal import Decimal

from pyvider.cty.types import CtyString, CtyNumber, CtyBool
from pyvider.cty.values import CtyValue
from pyvider.cty.values.refinement import (
    ValueRefinementBuilder, 
    NotNullRefinement,
    StringPrefixRefinement,
    NumberRangeRefinement
)

class TestValueRefinement:
    """Test value refinement functionality."""
    
    @pytest.mark.skip
    def test_not_null_refinement(self):
        """Test creating a not-null refinement."""
        val = CtyValue(type_=CtyString(), value="hello")
        builder = val.refine()
        builder.not_null()
        refined = builder.new_value()
        
        assert refined.is_known is False  # Refinements create unknown values
        assert refined._refinements is not None
        assert len(refined._refinements) == 1
        assert isinstance(refined._refinements[0], NotNullRefinement)

    @pytest.mark.skip
    def test_string_prefix_refinement(self):
        """Test creating a string prefix refinement."""
        val = CtyValue(type_=CtyString(), value="hello")
        builder = val.refine()
        builder.string_prefix("he")
        refined = builder.new_value()
        
        assert refined.is_known is False
        assert refined._refinements is not None
        assert len(refined._refinements) == 1
        assert isinstance(refined._refinements[0], StringPrefixRefinement)
        assert refined._refinements[0].prefix == "he"

    def test_number_range_refinement(self):
        """Test creating a number range refinement."""
        val = CtyValue(type_=CtyNumber(), value=42)
        builder = val.refine()
        builder.number_range_inclusive(10, 50)
        refined = builder.new_value()
        
        assert refined.is_known is False
        assert refined._refinements is not None
        assert len(refined._refinements) == 1
        assert isinstance(refined._refinements[0], NumberRangeRefinement)
        assert refined._refinements[0].min_value == Decimal("10")
        assert refined._refinements[0].max_value == Decimal("50")
        assert refined._refinements[0].min_inclusive is True
        assert refined._refinements[0].max_inclusive is True

    def test_multiple_refinements(self):
        """Test creating multiple refinements."""
        val = CtyValue(type_=CtyNumber(), value=42)
        builder = val.refine()
        builder.not_null()
        builder.number_range_inclusive(10, 50)
        refined = builder.new_value()
        
        assert refined.is_known is False
        assert refined._refinements is not None
        assert len(refined._refinements) == 2
        
        # Check that both refinements are present
        refinement_types = [type(r) for r in refined._refinements]
        assert NotNullRefinement in refinement_types
        assert NumberRangeRefinement in refinement_types
        
        # Get the number range refinement
        number_refinement = next(
            r for r in refined._refinements if isinstance(r, NumberRangeRefinement)
        )
        assert number_refinement.min_value == Decimal("10")
        assert number_refinement.max_value == Decimal("50")

    def test_refinement_wrong_type(self):
        """Test creating a refinement with the wrong type."""
        val = CtyValue(type_=CtyNumber(), value=42)
        builder = val.refine()
        
        with pytest.raises(TypeError):
            builder.string_prefix("he")  # Should fail because val is a number, not a string

    def test_refinement_of_known_value(self):
        """Test refining a known value returns the same value."""
        val = CtyValue(type_=CtyString(), value="hello")
        builder = val.refine()
        builder.not_null()  # This is already satisfied
        refined = builder.new_value()
        
        # For known values, refinements still create unknown values
        # (This matches the Go implementation)
        assert refined.is_known is False
        assert refined._refinements is not None
        assert len(refined._refinements) == 1

    def test_refinement_of_null_value(self):
        """Test refining a null value."""
        val = CtyValue(type_=CtyString(), is_null=True)
        builder = val.refine()
        builder.not_null()  # This conflicts with null
        refined = builder.new_value()
        
        assert refined.is_known is False
        assert refined._refinements is not None
        assert len(refined._refinements) == 1
        assert isinstance(refined._refinements[0], NotNullRefinement)

    def test_refinement_of_unknown_value(self):
        """Test refining an unknown value."""
        val = CtyValue(type_=CtyString(), is_unknown=True)
        builder = val.refine()
        builder.not_null()
        refined = builder.new_value()
        
        assert refined.is_known is False
        assert refined._refinements is not None
        assert len(refined._refinements) == 1
        assert isinstance(refined._refinements[0], NotNullRefinement)

    def test_number_range_with_null_bounds(self):
        """Test number range refinement with null bounds."""
        val = CtyValue(type_=CtyNumber(), value=42)
        builder = val.refine()
        builder.number_range_inclusive(None, None)  # No bounds
        refined = builder.new_value()
        
        assert refined.is_known is False
        assert refined._refinements is not None
        assert len(refined._refinements) == 1
        assert isinstance(refined._refinements[0], NumberRangeRefinement)
        assert refined._refinements[0].min_value is None
        assert refined._refinements[0].max_value is None

    def test_number_range_with_only_min(self):
        """Test number range refinement with only min bound."""
        val = CtyValue(type_=CtyNumber(), value=42)
        builder = val.refine()
        builder.number_range_inclusive(10, None)  # Only min
        refined = builder.new_value()
        
        assert refined.is_known is False
        assert refined._refinements is not None
        assert len(refined._refinements) == 1
        assert isinstance(refined._refinements[0], NumberRangeRefinement)
        assert refined._refinements[0].min_value == Decimal("10")
        assert refined._refinements[0].max_value is None

    def test_number_range_with_only_max(self):
        """Test number range refinement with only max bound."""
        val = CtyValue(type_=CtyNumber(), value=42)
        builder = val.refine()
        builder.number_range_inclusive(None, 50)  # Only max
        refined = builder.new_value()
        
        assert refined.is_known is False
        assert refined._refinements is not None
        assert len(refined._refinements) == 1
        assert isinstance(refined._refinements[0], NumberRangeRefinement)
        assert refined._refinements[0].min_value is None
        assert refined._refinements[0].max_value == Decimal("50")

    def test_refinement_with_negative_numbers(self):
        """Test number range refinement with negative numbers."""
        val = CtyValue(type_=CtyNumber(), value=-10)
        builder = val.refine()
        builder.number_range_inclusive(-20, -5)
        refined = builder.new_value()
        
        assert refined.is_known is False
        assert refined._refinements is not None
        assert len(refined._refinements) == 1
        assert isinstance(refined._refinements[0], NumberRangeRefinement)
        assert refined._refinements[0].min_value == Decimal("-20")
        assert refined._refinements[0].max_value == Decimal("-5")

    @pytest.mark.skip
    def test_refinement_with_decimal_numbers(self):
        """Test number range refinement with decimal numbers."""
        val = CtyValue(type_=CtyNumber(), value=3.14)
        builder = val.refine()
        builder.number_range_inclusive(3.1, 3.2)
        refined = builder.new_value()
        
        assert refined.is_known is False
        assert refined._refinements is not None
        assert len(refined._refinements) == 1
        assert isinstance(refined._refinements[0], NumberRangeRefinement)
        assert refined._refinements[0].min_value == Decimal("3.1")
        assert refined._refinements[0].max_value == Decimal("3.2")

    def test_refinement_builder_initialization(self):
        """Test initializing a refinement builder."""
        val = CtyValue(type_=CtyString(), value="hello")
        
        # Direct initialization
        builder = ValueRefinementBuilder(val)
        assert builder._value == val
        assert builder._refinements == []
        
        # Via refine() method
        builder = val.refine()
        assert builder._value == val
        assert builder._refinements == []
