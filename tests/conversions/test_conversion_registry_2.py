
# tests/conversions/test_conversion_registry.py

import pytest
from decimal import Decimal
import asyncio

from pyvider.cty.convert.convert import registry, ConversionRegistry, convert, convert_unsafe
from pyvider.cty.convert.base import Conversion
from pyvider.cty.ctypes import (
    CtyString, CtyNumber, CtyBool, CtyList, CtyMap, CtyDynamic
)
from pyvider.cty.values import CtyValue
from pyvider.cty.exceptions import ConversionError

class TestConversionRegistry:
    """Test the ConversionRegistry class."""
    
    def setup_method(self):
        """Set up a fresh registry for each test."""
        self.registry = ConversionRegistry()
        
        # Register some test conversions
        async def string_to_number(value: CtyValue) -> CtyValue:
            if value.is_null or value.is_unknown:
                return CtyValue(type_=CtyNumber(), is_null=value.is_null, is_unknown=value.is_unknown)
            return CtyValue(type_=CtyNumber(), value=Decimal(value.value))
            
        async def number_to_string(value: CtyValue) -> CtyValue:
            if value.is_null or value.is_unknown:
                return CtyValue(type_=CtyString(), is_null=value.is_null, is_unknown=value.is_unknown)
            return CtyValue(type_=CtyString(), value=str(value.value))
            
        self.registry.register(CtyString, CtyNumber, string_to_number, is_safe=False)
        self.registry.register(CtyNumber, CtyString, number_to_string, is_safe=True)

    def test_register_conversion(self):
        """Test registering a conversion."""
        async def bool_to_string(value: CtyValue) -> CtyValue:
            if value.is_null or value.is_unknown:
                return CtyValue(type_=CtyString(), is_null=value.is_null, is_unknown=value.is_unknown)
            return CtyValue(type_=CtyString(), value="true" if value.value else "false")
            
        self.registry.register(CtyBool, CtyString, bool_to_string, is_safe=True)
        
        # Verify it's in the registry
        conversion = self.registry.get_safe_conversion(CtyBool, CtyString)
        assert conversion is not None
        assert conversion.source_type == CtyBool
        assert conversion.target_type == CtyString
        assert conversion.is_safe

    def test_get_safe_conversion(self):
        """Test getting a safe conversion."""
        # String to Number is unsafe, should not be found
        conversion = self.registry.get_safe_conversion(CtyString, CtyNumber)
        assert conversion is None
        
        # Number to String is safe, should be found
        conversion = self.registry.get_safe_conversion(CtyNumber, CtyString)
        assert conversion is not None
        assert conversion.source_type == CtyNumber
        assert conversion.target_type == CtyString
        assert conversion.is_safe
        
    def test_get_unsafe_conversion(self):
        """Test getting an unsafe conversion."""
        # String to Number is unsafe, should be found
        conversion = self.registry.get_unsafe_conversion(CtyString, CtyNumber)
        assert conversion is not None
        assert conversion.source_type == CtyString
        assert conversion.target_type == CtyNumber
        assert not conversion.is_safe
        
        # Number to String is also in unsafe registry
        conversion = self.registry.get_unsafe_conversion(CtyNumber, CtyString)
        assert conversion is not None

    def test_identity_conversion(self):
        """Test identity conversion."""
        # Same type conversion is always available
        conversion = self.registry.get_safe_conversion(CtyString, CtyString)
        assert conversion is not None
        assert conversion.source_type == CtyString
        assert conversion.target_type == CtyString
        assert conversion.is_safe
        
        # Test conversion works
        val = CtyValue(type_=CtyString(), value="test")
        result = asyncio.run(conversion.convert(val))
        assert result.type == CtyString()
        assert result.value == "test"

    @pytest.mark.asyncio
    async def test_conversion_path_direct(self):
        """Test finding a direct conversion path."""
        # Number to String (direct)
        path = self.registry.find_conversion_path(CtyNumber, CtyString, allow_unsafe=False)
        assert path is not None
        assert len(path) == 1
        assert path[0].source_type == CtyNumber
        assert path[0].target_type == CtyString

    @pytest.mark.asyncio
    async def test_conversion_path_multi_step(self):
        """Test finding a multi-step conversion path."""
        # Add Boolean to Number conversion
        async def bool_to_number(value: CtyValue) -> CtyValue:
            if value.is_null or value.is_unknown:
                return CtyValue(type_=CtyNumber(), is_null=value.is_null, is_unknown=value.is_unknown)
            return CtyValue(type_=CtyNumber(), value=Decimal(1 if value.value else 0))
            
        self.registry.register(CtyBool, CtyNumber, bool_to_number, is_safe=True)
        
        # Boolean to String (via Number)
        path = self.registry.find_conversion_path(CtyBool, CtyString, allow_unsafe=False)
        assert path is not None
        assert len(path) == 2
        assert path[0].source_type == CtyBool
        assert path[0].target_type == CtyNumber
        assert path[1].source_type == CtyNumber
        assert path[1].target_type == CtyString

    @pytest.mark.asyncio
    async def test_conversion_path_not_found(self):
        """Test finding a non-existent conversion path."""
        # No path from List to Map
        path = self.registry.find_conversion_path(CtyList, CtyMap, allow_unsafe=True)
        assert path is None

    @pytest.mark.asyncio
    async def test_convert_value(self):
        """Test converting a value."""
        val = CtyValue(type_=CtyNumber(), value=42)
        result = await self.registry.convert(val, CtyString, allow_unsafe=False)
        assert result.type == CtyString()
        assert result.value == "42"
        
        # Converting String to Number requires allow_unsafe=True
        val = CtyValue(type_=CtyString(), value="42")
        with pytest.raises(ConversionError):
            await self.registry.convert(val, CtyNumber, allow_unsafe=False)
            
        result = await self.registry.convert(val, CtyNumber, allow_unsafe=True)
        assert result.type == CtyNumber()
        assert result.value == Decimal("42")

    @pytest.mark.asyncio
    async def test_convert_null_unknown(self):
        """Test converting null and unknown values."""
        # Null value
        val = CtyValue(type_=CtyNumber(), is_null=True)
        result = await self.registry.convert(val, CtyString, allow_unsafe=False)
        assert result.type == CtyString()
        assert result.is_null
        
        # Unknown value
        val = CtyValue(type_=CtyNumber(), is_unknown=True)
        result = await self.registry.convert(val, CtyString, allow_unsafe=False)
        assert result.type == CtyString()
        assert result.is_unknown

    @pytest.mark.asyncio
    async def test_convert_impossible(self):
        """Test converting when no path exists."""
        val = CtyValue(type_=CtyList(element_type=CtyString()), ["a", "b"])
        with pytest.raises(ConversionError):
            await self.registry.convert(val, CtyMap, allow_unsafe=True)
            
    @pytest.mark.asyncio
    async def test_unify_empty(self):
        """Test unifying an empty list of types."""
        result = self.registry.unify([], allow_unsafe=False)
        assert result is not None
        unified_type, conversions = result
        assert unified_type == CtyDynamic
        assert conversions == []

    @pytest.mark.asyncio
    async def test_unify_single(self):
        """Test unifying a single type."""
        result = self.registry.unify([CtyString], allow_unsafe=False)
        assert result is not None
        unified_type, conversions = result
        assert unified_type == CtyString
        assert len(conversions) == 1
        assert conversions[0].source_type == CtyString
        assert conversions[0].target_type == CtyString

    @pytest.mark.asyncio
    async def test_unify_same_types(self):
        """Test unifying multiple instances of the same type."""
        result = self.registry.unify([CtyNumber, CtyNumber, CtyNumber], allow_unsafe=False)
        assert result is not None
        unified_type, conversions = result
        assert unified_type == CtyNumber
        assert len(conversions) == 3
        for conv in conversions:
            assert conv.source_type == CtyNumber
            assert conv.target_type == CtyNumber

    @pytest.mark.asyncio
    async def test_unify_convertible_types(self):
        """Test unifying types that can be converted to a common type."""
        # Add Boolean to Number conversion if not registered
        if self.registry.get_safe_conversion(CtyBool, CtyNumber) is None:
            async def bool_to_number(value: CtyValue) -> CtyValue:
                if value.is_null or value.is_unknown:
                    return CtyValue(type_=CtyNumber(), is_null=value.is_null, is_unknown=value.is_unknown)
                return CtyValue(type_=CtyNumber(), value=Decimal(1 if value.value else 0))
                
            self.registry.register(CtyBool, CtyNumber, bool_to_number, is_safe=True)
        
        # Bool and Number should unify to Number
        result = self.registry.unify([CtyBool, CtyNumber], allow_unsafe=False)
        assert result is not None
        unified_type, conversions = result
        assert unified_type == CtyNumber
        assert len(conversions) == 2
        
        # Check that first conversion is from Bool to Number
        assert conversions[0].source_type == CtyBool
        assert conversions[0].target_type == CtyNumber
        
        # Check that second conversion is identity for Number
        assert conversions[1].source_type == CtyNumber
        assert conversions[1].target_type == CtyNumber

    @pytest.mark.asyncio
    async def test_unify_impossible(self):
        """Test unifying types that cannot be converted to a common type."""
        # No conversions between List and Map
        result = self.registry.unify([CtyList, CtyMap], allow_unsafe=True)
        assert result is None
        
    @pytest.mark.asyncio
    async def test_unify_using_unsafe(self):
        """Test unifying types using unsafe conversions."""
        # String and Number can unify to Number using unsafe conversion
        result = self.registry.unify([CtyString, CtyNumber], allow_unsafe=True)
        assert result is not None
        
        # With allow_unsafe=False, they cannot unify
        # unless there's a safe path in both directions
        if self.registry.find_conversion_path(CtyString, CtyNumber, allow_unsafe=False) is None:
            result = self.registry.unify([CtyString, CtyNumber], allow_unsafe=False)
            assert result is None

# Test the global registry and helpers
class TestGlobalRegistry:
    """Test the global registry and convenience functions."""
    
    @pytest.mark.asyncio
    async def test_convert_global(self):
        """Test the global convert function."""
        # This depends on what conversions are registered in the global registry
        # Let's test with Number to String, which should be safe
        val = CtyValue(type_=CtyNumber(), value=42)
        
        # Check if the conversion exists in global registry
        if registry.get_safe_conversion(CtyNumber, CtyString) is not None:
            result = await convert(val, CtyString)
            assert result.type == CtyString()
            assert result.value == "42"
        else:
            pytest.skip("Number to String conversion not registered in global registry")
            
    @pytest.mark.asyncio
    async def test_convert_unsafe_global(self):
        """Test the global convert_unsafe function."""
        # This depends on what conversions are registered in the global registry
        # Let's test with String to Number, which should be unsafe
        val = CtyValue(type_=CtyString(), value="42")
        
        # Check if the conversion exists in global registry
        if registry.get_unsafe_conversion(CtyString, CtyNumber) is not None:
            result = await convert_unsafe(val, CtyNumber)
            assert result.type == CtyNumber()
            assert result.value == Decimal("42")
        else:
            pytest.skip("String to Number conversion not registered in global registry")
