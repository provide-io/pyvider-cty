
# tests/integration/cty/convert/test_convert.py

"""
Integration tests for the CTY conversion system.

These tests verify that the conversion system correctly converts between
different CTY types, handling both safe and unsafe conversions, as well
as integration with other parts of the CTY system.
"""

import asyncio
from decimal import Decimal

import pytest

from pyvider.cty.types.primitives import CtyString, CtyNumber, CtyBool
from pyvider.cty.types.collections import CtyList, CtyMap, CtySet
from pyvider.cty.types.structural import CtyObject, CtyDynamic, CtyTuple
from pyvider.cty.values.base import Value
from pyvider.cty.convert.convert import (
    registry,
    convert,
    convert_unsafe,
    can_convert,
    can_convert_unsafe,
    unify,
    unify_unsafe,
    ConversionError,
)

class TestConversionSystem:
    """Test the CTY conversion system."""
    
    @pytest.mark.asyncio
    async def test_primitive_conversions(self):
        """Test conversions between primitive types."""
        # String to Number
        string_val = Value(type_=CtyString(), value="42")
        number_result = await convert_unsafe(string_val, CtyNumber)
        assert isinstance(number_result.type, CtyNumber)
        assert number_result.value == 42
        
        # String to Bool
        string_val = Value(type_=CtyString(), value="true")
        bool_result = await convert_unsafe(string_val, CtyBool)
        assert isinstance(bool_result.type, CtyBool)
        assert bool_result.value is True
        
        # Number to String
        number_val = Value(type_=CtyNumber(), value=42)
        string_result = await convert(number_val, CtyString)
        assert isinstance(string_result.type, CtyString)
        assert string_result.value == "42"
        
        # Number to Bool
        number_val = Value(type_=CtyNumber(), value=1)
        bool_result = await convert_unsafe(number_val, CtyBool)
        assert isinstance(bool_result.type, CtyBool)
        assert bool_result.value is True
        
        # Bool to String
        bool_val = Value(type_=CtyBool(), value=True)
        string_result = await convert(bool_val, CtyString)
        assert isinstance(string_result.type, CtyString)
        assert string_result.value == "true"
        
        # Bool to Number
        bool_val = Value(type_=CtyBool(), value=True)
        number_result = await convert(bool_val, CtyNumber)
        assert isinstance(number_result.type, CtyNumber)
        assert number_result.value == 1
        
    @pytest.mark.asyncio
    async def test_invalid_conversions(self):
        """Test conversions that should fail."""
        # Invalid string to number
        string_val = Value(type_=CtyString(), value="not a number")
        with pytest.raises(ConversionError):
            await convert_unsafe(string_val, CtyNumber)
            
        # Invalid string to bool
        string_val = Value(type_=CtyString(), value="not a bool")
        with pytest.raises(ConversionError):
            await convert_unsafe(string_val, CtyBool)
            
        # Conversion that doesn't exist
        # For example, direct conversion from string to list
        string_val = Value(type_=CtyString(), value="hello")
        with pytest.raises(ConversionError):
            await convert_unsafe(string_val, CtyList)
            
    @pytest.mark.asyncio
    async def test_null_and_unknown_handling(self):
        """Test that null and unknown values are handled correctly."""
        # Null string to number
        null_string = Value(type_=CtyString(), is_null=True)
        null_number = await convert_unsafe(null_string, CtyNumber)
        assert null_number.is_null
        assert isinstance(null_number.type, CtyNumber)
        
        # Unknown string to number
        unknown_string = Value(type_=CtyString(), is_unknown=True)
        unknown_number = await convert_unsafe(unknown_string, CtyNumber)
        assert unknown_number.is_unknown
        assert isinstance(unknown_number.type, CtyNumber)
        
        # Null bool to string
        null_bool = Value(type_=CtyBool(), is_null=True)
        null_string = await convert(null_bool, CtyString)
        assert null_string.is_null
        assert isinstance(null_string.type, CtyString)
        
        # Unknown bool to string
        unknown_bool = Value(type_=CtyBool(), is_unknown=True)
        unknown_string = await convert(unknown_bool, CtyString)
        assert unknown_string.is_unknown
        assert isinstance(unknown_string.type, CtyString)
        
    @pytest.mark.asyncio
    async def test_can_convert(self):
        """Test the can_convert function."""
        # Safe conversions
        assert await can_convert(CtyBool(), CtyString())
        assert await can_convert(CtyBool(), CtyNumber())
        assert await can_convert(CtyNumber(), CtyString())
        
        # Unsafe conversions
        assert not await can_convert(CtyString(), CtyNumber())
        assert not await can_convert(CtyString(), CtyBool())
        assert not await can_convert(CtyNumber(), CtyBool())
        
        # Unsafe conversions with can_convert_unsafe
        assert await can_convert_unsafe(CtyString(), CtyNumber())
        assert await can_convert_unsafe(CtyString(), CtyBool())
        assert await can_convert_unsafe(CtyNumber(), CtyBool())
        
        # Impossible conversions
        assert not await can_convert_unsafe(CtyString(), CtyList(element_type=CtyString()))
        assert not await can_convert_unsafe(CtyNumber(), CtyMap(key_type=CtyString(), value_type=CtyNumber()))
        
    @pytest.mark.asyncio
    async def test_unification(self):
        """Test type unification."""
        # Unify identical types
        types = [CtyString(), CtyString(), CtyString()]
        result = await unify(types)
        assert result is not None
        unified_type, conversions = result
        assert unified_type == CtyString
        assert len(conversions) == 3
        
        # Unify compatible types (all convert safely to string)
        types = [CtyBool(), CtyBool(), CtyNumber()]
        result = await unify(types)
        assert result is not None
        unified_type, conversions = result
        assert unified_type == CtyString
        assert len(conversions) == 3
        
        # Unify with unsafe conversions
        types = [CtyString(), CtyNumber(), CtyBool()]
        result = await unify(types)
        assert result is None  # Can't safely unify
        
        result = await unify_unsafe(types)
        assert result is not None  # Can unsafely unify
        unified_type, conversions = result
        # Either String or Number would work, but one will be chosen
        assert unified_type in (CtyString, CtyNumber)
        assert len(conversions) == 3
        
        # Can't unify incompatible types even with unsafe
        types = [CtyString(), CtyList(element_type=CtyNumber())]
        result = await unify_unsafe(types)
        assert result is None
        
    @pytest.mark.asyncio
    async def test_custom_conversion(self):
        """Test registering and using a custom conversion."""
        # Define a custom conversion from string to list of strings
        async def string_to_string_list(value: Value) -> Value:
            """Convert string to list by splitting on commas."""
            if value.is_null or value.is_unknown:
                return Value(
                    type_=CtyList(element_type=CtyString()),
                    is_null=value.is_null,
                    is_unknown=value.is_unknown
                )
                
            # Split on commas
            items = [s.strip() for s in value.value.split(",")]
            return Value(
                type_=CtyList(element_type=CtyString()),
                value=items
            )
            
        # Register the conversion
        registry.register(
            CtyString,
            CtyList,
            string_to_string_list,
            is_safe=False
        )
        
        # Test the conversion
        string_val = Value(type_=CtyString(), value="a, b, c")
        list_result = await convert_unsafe(string_val, CtyList)
        assert isinstance(list_result.type, CtyList)
        assert list_result.value == ["a", "b", "c"]
        
    @pytest.mark.asyncio
    async def test_conversion_path_finding(self):
        """Test finding conversion paths through multiple steps."""
        # Define a custom multi-step conversion path
        # String -> Number -> Bool
        
        # First, ensure the direct String -> Bool conversion doesn't exist
        # (we'll remove it temporarily for this test)
        old_string_to_bool = registry._unsafe_conversions.pop((CtyString, CtyBool), None)
        
        try:
            # Now, find a path String -> Number -> Bool
            path = registry.find_conversion_path(CtyString, CtyBool, allow_unsafe=True)
            assert path is not None
            assert len(path) == 2
            assert path[0].source_type == CtyString
            assert path[0].target_type == CtyNumber
            assert path[1].source_type == CtyNumber
            assert path[1].target_type == CtyBool
            
            # Test the actual conversion
            string_val = Value(type_=CtyString(), value="1")
            bool_result = await convert_unsafe(string_val, CtyBool)
            assert isinstance(bool_result.type, CtyBool)
            assert bool_result.value is True
            
        finally:
            # Restore the original conversion
            if old_string_to_bool:
                registry._unsafe_conversions[(CtyString, CtyBool)] = old_string_to_bool
                
    @pytest.mark.asyncio
    async def test_collection_type_handling(self):
        """Test conversion with collection types."""
        # Create a list of strings
        string_list = Value(
            type_=CtyList(element_type=CtyString()),
            value=["1", "2", "3"]
        )
        
        # Custom conversion from list of strings to list of numbers
        async def string_list_to_number_list(value: Value) -> Value:
            """Convert list of strings to list of numbers."""
            if value.is_null or value.is_unknown:
                return Value(
                    type_=CtyList(element_type=CtyNumber()),
                    is_null=value.is_null,
                    is_unknown=value.is_unknown
                )
                
            # Convert each string to number
            try:
                numbers = [Decimal(item) for item in value.value]
                return Value(
                    type_=CtyList(element_type=CtyNumber()),
                    value=numbers
                )
            except Exception as e:
                raise ConversionError(f"Failed to convert string list to number list: {e}")
                
        # Register the conversion
        registry.register(
            CtyList,
            CtyList,
            string_list_to_number_list,
            is_safe=False
        )
        
        # Test the conversion
        number_list_result = await convert_unsafe(string_list, CtyList)
        assert isinstance(number_list_result.type, CtyList)
        assert isinstance(number_list_result.type.element_type, CtyNumber)
        assert number_list_result.value == [Decimal("1"), Decimal("2"), Decimal("3")]
        
    @pytest.mark.asyncio
    async def test_integration_with_operations(self):
        """Test that conversions work with value operations."""
        from pyvider.cty.values.operations import add, subtract, multiply, divide
        
        # Add a string representing a number to a number
        string_val = Value(type_=CtyString(), value="10")
        number_val = Value(type_=CtyNumber(), value=5)
        
        # This should convert the string to a number first
        result = await add(string_val, number_val)
        assert result.value == 15
        
        # Subtract
        result = await subtract(string_val, number_val)
        assert result.value == 5
        
        # Multiply
        result = await multiply(string_val, number_val)
        assert result.value == 50
        
        # Divide
        result = await divide(string_val, number_val)
        assert result.value == 2
        
    @pytest.mark.asyncio
    async def test_integration_with_functions(self):
        """Test that conversions work with functions."""
        from pyvider.cty.function.base import (
            Parameter,
            FunctionSpec,
            Function,
        )
        
        # Create a function that takes a number and returns a string
        def return_string(args):
            return CtyString()
            
        def format_number(args, return_type):
            # Format the number with two decimal places
            num = args[0].value
            if isinstance(num, Decimal):
                result = f"{num:.2f}"
            else:
                result = f"{Decimal(str(num)):.2f}"
                
            return Value(type_=return_type, value=result)
            
        spec = FunctionSpec(
            name="format_number",
            params=[
                Parameter(name="num", type=CtyNumber(), allow_null=False, allow_unknown=True)
            ],
            return_type_fn=return_string,
            implementation=format_number,
            description="Format a number with two decimal places"
        )
        
        format_fn = Function(spec)
        
        # Test with a normal number
        result = await format_fn(Value(type_=CtyNumber(), value=42.5))
        assert result.value == "42.50"
        
        # Test with a string that can be converted to a number
        # This should fail without conversion
        string_val = Value(type_=CtyString(), value="42.5")
        with pytest.raises(Exception):
            await format_fn(string_val)
            
        # Now, use a wrapper that applies conversion
        async def convert_and_call(fn, *args):
            # Convert all arguments to the expected types
            converted_args = []
            for i, arg in enumerate(args):
                if i < len(fn.spec.params):
                    param = fn.spec.params[i]
                    if not isinstance(arg.type, type(param.type)):
                        # Need to convert
                        arg = await convert_unsafe(arg, type(param.type))
                converted_args.append(arg)
                
            # Call the function with converted arguments
            return await fn(*converted_args)
            
        # Test with conversion
        result = await convert_and_call(format_fn, string_val)
        assert result.value == "42.50"
