#!/usr/bin/env python3
# tests/integration/cty/function/test_function_base.py

"""
Integration tests for the Cty function system.

These tests verify that the function system works correctly with other parts
of the Cty system, including type checking, validation, and execution.
"""

from decimal import Decimal
from typing import List

import pytest

from pyvider.cty import (
    CtyString,
    CtyNumber,
    CtyBool,
    CtyValue,
)
from pyvider.cty.function.base import (
    Parameter,
    VariadicParameter,
    FunctionSpec,
    Function,
    FunctionRegistry,
)
from pyvider.cty.exceptions import ValidationError

class TestFunctionSystem:
    """Test the Cty function system."""
    
    @pytest.mark.asyncio
    async def test_parameter_validation(self):
        """Test parameter validation rules."""
        # Create parameter
        param = Parameter(
            name="test",
            type=CtyString(),
            allow_null=False,
            allow_unknown=False
        )
        
        # Test valid value
        valid_value = CtyValue(type_=CtyString(), value="test")
        assert await param.validate(valid_value)
        
        # Test null value
        null_value = CtyValue(type_=CtyString(), is_null=True)
        with pytest.raises(ValidationError):
            await param.validate(null_value)
            
        # Test unknown value
        unknown_value = CtyValue(type_=CtyString(), is_unknown=True)
        with pytest.raises(ValidationError):
            await param.validate(unknown_value)
            
        # Test wrong type
        wrong_type = CtyValue(type_=CtyNumber(), value=42)
        with pytest.raises(ValidationError):
            await param.validate(wrong_type)
            
        # Test with more permissive parameter
        permissive = Parameter(
            name="permissive",
            type=CtyString(),
            allow_null=True,
            allow_unknown=True,
            allow_dynamic_type=True
        )
        
        assert await permissive.validate(valid_value)
        assert await permissive.validate(null_value)
        assert await permissive.validate(unknown_value)
        assert await permissive.validate(wrong_type)  # allow_dynamic_type allows this
        
    @pytest.mark.asyncio
    async def test_variadic_parameter(self):
        """Test variadic parameter validation."""
        # Create variadic parameter
        variadic = VariadicParameter(
            name="args",
            type=CtyNumber(),
            min_elements=1,
            max_elements=3,
            allow_null=False,
            allow_unknown=True,
        )
        
        # Create test values
        values = [
            CtyValue(type_=CtyNumber(), value=1),
            CtyValue(type_=CtyNumber(), value=2),
            CtyValue(type_=CtyNumber(), is_unknown=True)
        ]
        
        # Test valid values
        assert await variadic.validate_all(values)
        
        # Test too few values
        with pytest.raises(ValidationError):
            await variadic.validate_all([])
            
        # Test too many values
        too_many = values + [CtyValue(type_=CtyNumber(), value=4)]
        with pytest.raises(ValidationError):
            await variadic.validate_all(too_many)
            
        # Test invalid value type
        invalid_type = values.copy()
        invalid_type[1] = CtyValue(type_=CtyString(), value="not a number")
        with pytest.raises(ValidationError):
            await variadic.validate_all(invalid_type)
            
        # Test null value
        null_value = values.copy()
        null_value[1] = CtyValue(type_=CtyNumber(), is_null=True)
        with pytest.raises(ValidationError):
            await variadic.validate_all(null_value)
            
    @pytest.mark.asyncio
    async def test_function_spec(self):
        """Test function specification and validation."""
        # Create a simple function to add two numbers
        def return_number(args: List[CtyValue]) -> CtyType:
            return CtyNumber()
            
        def add_numbers(args: List[CtyValue], return_type: CtyType) -> Value:
            # Simple implementation that adds two numbers
            num1 = args[0].value
            num2 = args[1].value
            
            # Handle null or unknown
            if args[0].is_null or args[1].is_null:
                return CtyValue(type_=return_type, is_null=True)
                
            if args[0].is_unknown or args[1].is_unknown:
                return CtyValue(type_=return_type, is_unknown=True)
                
            # Add as Decimal for consistency
            if not isinstance(num1, Decimal):
                numt_ = Decimal(str(num1))
            if not isinstance(num2, Decimal):
                num2 = Decimal(str(num2))
                
            return CtyValue(type_=return_type, value=num1 + num2)
            
        # Create function spec
        spec = FunctionSpec(
            name="add",
            params=[
                Parameter(name="a", type=CtyNumber()),
                Parameter(name="b", type=CtyNumber())
            ],
            return_type_fn=return_number,
            implementation=add_numbers,
            description="Add two numbers"
        )
        
        # Create valid arguments
        valid_args = [
            CtyValue(type_=CtyNumber(), value=5),
            CtyValue(type_=CtyNumber(), value=3)
        ]
        
        # Test argument validation
        assert await spec.validate_args(valid_args)
        
        # Test with too few arguments
        with pytest.raises(ValidationError):
            await spec.validate_args([valid_args[0]])
            
        # Test with too many arguments
        with pytest.raises(ValidationError):
            await spec.validate_args(valid_args + [CtyValue(type_=CtyNumber(), value=1)])
            
        # Test with wrong type
        invalid_args = [
            CtyValue(type_=CtyNumber(), value=5),
            CtyValue(type_=CtyString(), value="3")
        ]
        with pytest.raises(ValidationError):
            await spec.validate_args(invalid_args)
            
        # Test function call
        result = await spec.call(valid_args)
        assert not result.is_unknown
        assert not result.is_null
        assert result.value == 8
        
        # Test call with unknown value
        unknown_args = [
            CtyValue(type_=CtyNumber(), value=5),
            CtyValue(type_=CtyNumber(), is_unknown=True)
        ]
        result = await spec.call(unknown_args)
        assert result.is_unknown
        assert not result.is_null
        
        # Test call with null value
        null_args = [
            CtyValue(type_=CtyNumber(), value=5),
            CtyValue(type_=CtyNumber(), is_null=True)
        ]
        result = await spec.call(null_args)
        assert not result.is_unknown
        assert result.is_null
        
    @pytest.mark.asyncio
    async def test_function_callable(self):
        """Test Function object as a callable."""
        # Create a simple function to concatenate strings
        def return_string(args: List[CtyValue]) -> CtyType:
            return CtyString()
            
        def concat_strings(args: List[CtyValue], return_type: CtyType) -> Value:
            # Simple implementation that concatenates strings
            if any(arg.is_null for arg in args):
                return CtyValue(type_=return_type, is_null=True)
                
            if any(arg.is_unknown for arg in args):
                return CtyValue(type_=return_type, is_unknown=True)
                
            result = "".join(str(arg.value) for arg in args)
            return CtyValue(type_=return_type, value=result)
            
        # Create function spec with variadic parameter
        spec = FunctionSpec(
            name="concat",
            params=[
                Parameter(name="first", type=CtyString())
            ],
            variadic_param=VariadicParameter(
                name="rest",
                type=CtyString(),
                min_elements=0
            ),
            return_type_fn=return_string,
            implementation=concat_strings,
            description="Concatenate strings"
        )
        
        # Create Function object
        concat_fn = Function(spec)
        
        # Test with single argument
        result = await concat_fn(Value(type_=CtyString(), value="hello"))
        assert result.value == "hello"
        
        # Test with multiple arguments
        result = await concat_fn(
            CtyValue(type_=CtyString(), value="hello"),
            CtyValue(type_=CtyString(), value=" "),
            CtyValue(type_=CtyString(), value="world")
        )
        assert result.value == "hello world"
        
        # Test with unknown value
        result = await concat_fn(
            CtyValue(type_=CtyString(), value="hello"),
            CtyValue(type_=CtyString(), is_unknown=True)
        )
        assert result.is_unknown
        
        # Test with null value
        result = await concat_fn(
            CtyValue(type_=CtyString(), value="hello"),
            CtyValue(type_=CtyString(), is_null=True)
        )
        assert result.is_null
        
        # Test function metadata
        assert concat_fn.name == "concat"
        assert concat_fn.description == "Concatenate strings"
        assert str(concat_fn) == "concat(first: CtyString, *args: CtyString)"
        
    @pytest.mark.asyncio
    async def test_function_registry(self):
        """Test function registry operations."""
        # Create a registry
        registry = FunctionRegistry()
        
        # Create a simple function
        def return_string(args: List[CtyValue]) -> CtyType:
            return CtyString()
            
        def upper_string(args: List[CtyValue], return_type: CtyType) -> Value:
            # Convert string to uppercase
            if args[0].is_null:
                return CtyValue(type_=return_type, is_null=True)
                
            if args[0].is_unknown:
                return CtyValue(type_=return_type, is_unknown=True)
                
            result = str(args[0].value).upper()
            return CtyValue(type_=return_type, value=result)
            
        # Create function spec
        spec = FunctionSpec(
            name="upper",
            params=[
                Parameter(name="str", type=CtyString())
            ],
            return_type_fn=return_string,
            implementation=upper_string,
            description="Convert string to uppercase"
        )
        
        # Create Function object
        upper_fn = Function(spec)
        
        # Register the function
        registry.register(upper_fn)
        
        # Test registry operations
        assert registry.has("upper")
        assert not registry.has("lower")
        
        # Get function
        fn = registry.get("upper")
        assert fn is not None
        assert fn.name == "upper"
        
        # Call the function
        result = await fn(Value(type_=CtyString(), value="hello"))
        assert result.value == "HELLO"
        
        # Test list of functions
        assert registry.list() == ["upper"]
        assert len(registry) == 1
        
        # Test iteration
        functions = list(registry)
        assert len(functions) == 1
        assert functions[0].name == "upper"
        
        # Test registering duplicate
        with pytest.raises(ValueError):
            registry.register(upper_fn)
            
    @pytest.mark.asyncio
    async def test_integration_with_values(self):
        """Test function integration with the value system."""
        # Create a function to test a string
        def return_bool(args: List[CtyValue]) -> CtyType:
            return CtyBool()
            
        def starts_with(args: List[CtyValue], return_type: CtyType) -> Value:
            # Check if string starts with prefix
            str_val = args[0]
            prefix = args[1]
            
            if str_val.is_null or prefix.is_null:
                return CtyValue(type_=return_type, is_null=True)
                
            # Special handling for unknown with refinements
            if str_val.is_unknown and str_val.refinements:
                from pyvider.cty.values.refinement import StringPrefixRefinement
                
                # Check if we have a string prefix refinement
                for refinement in str_val.refinements:
                    if isinstance(refinement, StringPrefixRefinement):
                        if refinement.prefix.startswith(prefix.value):
                            # We know the result must be true
                            return CtyValue(type_=return_type, value=True)
                        elif not prefix.value.startswith(refinement.prefix):
                            # We know the result must be false
                            return CtyValue(type_=return_type, value=False)
                
            if str_val.is_unknown or prefix.is_unknown:
                return CtyValue(type_=return_type, is_unknown=True)
                
            result = str(str_val.value).startswith(str(prefix.value))
            return CtyValue(type_=return_type, value=result)
            
        # Create function spec
        spec = FunctionSpec(
            name="startswith",
            params=[
                Parameter(name="str", type=CtyString()),
                Parameter(name="prefix", type=CtyString())
            ],
            return_type_fn=return_bool,
            implementation=starts_with,
            description="Check if string starts with prefix"
        )
        
        # Create Function object
        startswith_fn = Function(spec)
        
        # Test with known values
        result = await startswith_fn(
            CtyValue(type_=CtyString(), value="hello world"),
            CtyValue(type_=CtyString(), value="hello")
        )
        assert result.value is True
        
        result = await startswith_fn(
            CtyValue(type_=CtyString(), value="hello world"),
            CtyValue(type_=CtyString(), value="world")
        )
        assert result.value is False
        
        # Test with refined unknown value
        from pyvider.cty.values.refinement import ValueRefinementBuilder
        
        builder = ValueRefinementBuilder()
        builder.not_null()
        builder.string_prefix("hello")
        refined_string = await builder.build(CtyString())
        
        result = await startswith_fn(
            refined_string,
            CtyValue(type_=CtyString(), value="hello")
        )
        assert not result.is_unknown
        assert result.value is True
        
        result = await startswith_fn(
            refined_string,
            CtyValue(type_=CtyString(), value="world")
        )
        assert not result.is_unknown
        assert result.value is False
        
        # Test with indeterminate case
        result = await startswith_fn(
            refined_string,
            CtyValue(type_=CtyString(), value="h")
        )
        assert not result.is_unknown
        assert result.value is True
        
        # Test with complex case
        result = await startswith_fn(
            refined_string,
            CtyValue(type_=CtyString(), value="hello world")
        )
        assert result.is_unknown  # We can't determine this
