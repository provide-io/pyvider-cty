import pytest
from unittest.mock import MagicMock, patch
from decimal import Decimal

from pyvider.cty.convert.convert import (
    registry, convert, convert_unsafe, can_convert, can_convert_unsafe,
    unify, unify_unsafe, Conversion
)
from pyvider.cty.exceptions import ConversionError
from pyvider.cty import CtyString, CtyNumber, CtyBool, CtyList, CtyDynamic
from pyvider.cty.values.base import CtyValue


class TestConversion:
    """Tests for the Conversion class."""
    
    @pytest.mark.asyncio
    async def test_conversion_init(self):
        """Test Conversion initialization."""
        # Create test types
        source_type = CtyString
        target_type = CtyNumber
        converter = MagicMock()
        
        # Create conversion
        conversion = Conversion(
            source_type=source_type,
            target_type=target_type,
            converter=converter,
            is_safe=True
        )
        
        # Verify attributes
        assert conversion.source_type == source_type
        assert conversion.target_type == target_type
        assert conversion.converter == converter
        assert conversion.is_safe is True
    
    @pytest.mark.asyncio
    async def test_conversion_convert_success(self):
        """Test successful conversion."""
        # Create mock converter
        mock_result = CtyValue(CtyNumber(), 123)
        mock_converter = MagicMock(return_value=mock_result)
        
        # Create conversion
        conversion = Conversion(
            source_type=CtyString,
            target_type=CtyNumber,
            converter=mock_converter,
            is_safe=True
        )
        
        # Create value to convert
        value = CtyValue(CtyString(), "123")
        
        # Convert value
        result = await conversion.convert(value)
        
        # Verify converter was called
        mock_converter.assert_called_once_with(value)
        
        # Verify result
        assert result == mock_result
    
    @pytest.mark.asyncio
    async def test_conversion_convert_failure(self):
        """Test conversion failure."""
        # Create mock converter that raises an exception
        mock_converter = MagicMock(side_effect=ValueError("Invalid value"))
        
        # Create conversion
        conversion = Conversion(
            source_type=CtyString,
            target_type=CtyNumber,
            converter=mock_converter,
            is_safe=False
        )
        
        # Create value to convert
        value = CtyValue(CtyString(), "not_a_number")
        
        # Convert value should raise ConversionError
        with pytest.raises(ConversionError):
            await conversion.convert(value)


class TestConversionRegistry:
    """Tests for the ConversionRegistry class."""
    
    def setup_method(self):
        """Reset the registry for each test."""
        # Create a backup of the original registry
        self._original_safe_conversions = registry._safe_conversions
        self._original_unsafe_conversions = registry._unsafe_conversions
        
        # Clear the registry
        registry._safe_conversions = {}
        registry._unsafe_conversions = {}
    
    def teardown_method(self):
        """Restore the original registry after each test."""
        registry._safe_conversions = self._original_safe_conversions
        registry._unsafe_conversions = self._original_unsafe_conversions
    
    def test_registry_register(self):
        """Test registering a conversion."""
        # Create test converter
        converter = MagicMock()
        
        # Register the conversion
        registry.register(
            source_type=CtyString,
            target_type=CtyNumber,
            converter=converter,
            is_safe=True
        )
        
        # Verify conversion was registered
        key = (CtyString, CtyNumber)
        assert key in registry._safe_conversions
        assert key in registry._unsafe_conversions
        
        # Verify conversion
        conversion = registry._safe_conversions[key]
        assert isinstance(conversion, Conversion)
        assert conversion.source_type == CtyString
        assert conversion.target_type == CtyNumber
        assert conversion.converter == converter
        assert conversion.is_safe is True
    
    def test_registry_register_unsafe_only(self):
        """Test registering an unsafe conversion."""
        # Create test converter
        converter = MagicMock()
        
        # Register the conversion
        registry.register(
            source_type=CtyString,
            target_type=CtyNumber,
            converter=converter,
            is_safe=False
        )
        
        # Verify conversion was registered
        key = (CtyString, CtyNumber)
        assert key not in registry._safe_conversions
        assert key in registry._unsafe_conversions
    
    def test_registry_get_safe_conversion(self):
        """Test getting a safe conversion."""
        # Register a safe conversion
        converter = MagicMock()
        registry.register(
            source_type=CtyString,
            target_type=CtyNumber,
            converter=converter,
            is_safe=True
        )
        
        # Get the conversion
        conversion = registry.get_safe_conversion(CtyString, CtyNumber)
        
        # Verify conversion
        assert isinstance(conversion, Conversion)
        assert conversion.source_type == CtyString
        assert conversion.target_type == CtyNumber
    
    def test_registry_get_unsafe_conversion(self):
        """Test getting an unsafe conversion."""
        # Register an unsafe conversion
        converter = MagicMock()
        registry.register(
            source_type=CtyString,
            target_type=CtyNumber,
            converter=converter,
            is_safe=False
        )
        
        # Get the conversion
        conversion = registry.get_unsafe_conversion(CtyString, CtyNumber)
        
        # Verify conversion
        assert isinstance(conversion, Conversion)
        assert conversion.source_type == CtyString
        assert conversion.target_type == CtyNumber
    
    def test_registry_get_identity_conversion(self):
        """Test getting an identity conversion."""
        # Get identity conversion
        conversion = registry.get_safe_conversion(CtyString, CtyString)
        
        # Verify conversion
        assert isinstance(conversion, Conversion)
        assert conversion.source_type == CtyString
        assert conversion.target_type == CtyString
        assert conversion.is_safe is True
    
    def test_registry_find_direct_path(self):
        """Test finding a direct conversion path."""
        # Register a conversion
        converter = MagicMock()
        registry.register(
            source_type=CtyString,
            target_type=CtyNumber,
            converter=converter,
            is_safe=True
        )
        
        # Find the path
        path = registry.find_conversion_path(CtyString, CtyNumber, allow_unsafe=False)
        
        # Verify path
        assert path is not None
        assert len(path) == 1
        assert path[0].source_type == CtyString
        assert path[0].target_type == CtyNumber
    
    def test_registry_find_multistep_path(self):
        """Test finding a multi-step conversion path."""
        # Register conversions
        converter = MagicMock()
        registry.register(
            source_type=CtyString,
            target_type=CtyNumber,
            converter=converter,
            is_safe=True
        )
        registry.register(
            source_type=CtyNumber,
            target_type=CtyBool,
            converter=converter,
            is_safe=True
        )
        
        # Find the path
        path = registry.find_conversion_path(CtyString, CtyBool, allow_unsafe=False)
        
        # Verify path
        assert path is not None
        assert len(path) == 2
        assert path[0].source_type == CtyString
        assert path[0].target_type == CtyNumber
        assert path[1].source_type == CtyNumber
        assert path[1].target_type == CtyBool
    
    def test_registry_find_no_path(self):
        """Test finding no conversion path."""
        # Find a path for types with no conversion
        path = registry.find_conversion_path(CtyString, CtyList, allow_unsafe=False)
        
        # Verify no path found
        assert path is None
    
    @pytest.mark.asyncio
    async def test_registry_convert(self):
        """Test converting a value."""
        # Mock the find_conversion_path method
        mock_path = [
            MagicMock(spec=Conversion)
        ]
        mock_path[0].convert = MagicMock()
        mock_path[0].convert.return_value = CtyValue(CtyNumber(), 123)
        
        with patch.object(registry, 'find_conversion_path', return_value=mock_path):
            # Create value to convert
            value = CtyValue(CtyString(), "123")
            
            # Convert value
            result = await registry.convert(value, CtyNumber, allow_unsafe=False)
            
            # Verify mock was called
            mock_path[0].convert.assert_called_once_with(value)
            
            # Verify result
            assert result.type == CtyNumber()
            assert result.value == 123
    
    @pytest.mark.asyncio
    async def test_registry_convert_no_path(self):
        """Test converting a value with no path."""
        # Mock the find_conversion_path method to return None
        with patch.object(registry, 'find_conversion_path', return_value=None):
            # Create value to convert
            value = CtyValue(CtyString(), "123")
            
            # Convert value should raise ConversionError
            with pytest.raises(ConversionError):
                await registry.convert(value, CtyNumber, allow_unsafe=False)
    
    @pytest.mark.asyncio
    async def test_registry_unify(self):
        """Test unifying types."""
        # Register conversions
        converter = MagicMock()
        registry.register(
            source_type=CtyString,
            target_type=CtyBool,
            converter=converter,
            is_safe=True
        )
        registry.register(
            source_type=CtyNumber,
            target_type=CtyBool,
            converter=converter,
            is_safe=True
        )
        
        # Unify types
        result = registry.unify([CtyString, CtyNumber], allow_unsafe=False)
        
        # Verify result
        assert result is not None
        target_type, conversions = result
        assert target_type == CtyBool
        assert len(conversions) == 2
        
        # Verify conversions
        assert conversions[0].source_type == CtyString
        assert conversions[0].target_type == CtyBool
        assert conversions[1].source_type == CtyNumber
        assert conversions[1].target_type == CtyBool


class TestConvertFunctions:
    """Tests for the global convert functions."""
    
    @pytest.mark.asyncio
    async def test_convert_function(self):
        """Test the convert function."""
        # Mock registry.convert
        mock_result = CtyValue(CtyNumber(), 123)
        mock_convert = MagicMock(return_value=mock_result)
        
        with patch('pyvider.cty.convert.convert.registry.convert', mock_convert):
            # Create value to convert
            value = CtyValue(CtyString(), "123")
            
            # Call convert
            result = await convert(value, CtyNumber)
            
            # Verify mock was called
            mock_convert.assert_called_once_with(value, CtyNumber, allow_unsafe=False)
            
            # Verify result
            assert result == mock_result
    
    @pytest.mark.asyncio
    async def test_convert_unsafe_function(self):
        """Test the convert_unsafe function."""
        # Mock registry.convert
        mock_result = CtyValue(CtyNumber(), 123)
        mock_convert = MagicMock(return_value=mock_result)
        
        with patch('pyvider.cty.convert.convert.registry.convert', mock_convert):
            # Create value to convert
            value = CtyValue(CtyString(), "123")
            
            # Call convert_unsafe
            result = await convert_unsafe(value, CtyNumber)
            
            # Verify mock was called
            mock_convert.assert_called_once_with(value, CtyNumber, allow_unsafe=True)
            
            # Verify result
            assert result == mock_result
    
    @pytest.mark.asyncio
    async def test_can_convert_function(self):
        """Test the can_convert function."""
        # Mock registry.find_conversion_path
        mock_path = [MagicMock()]
        mock_find = MagicMock(return_value=mock_path)
        
        with patch('pyvider.cty.convert.convert.registry.find_conversion_path', mock_find):
            # Create types to check
            source_type = CtyString()
            target_type = CtyNumber()
            
            # Call can_convert
            result = await can_convert(source_type, target_type)
            
            # Verify mock was called
            mock_find.assert_called_once_with(
                type(source_type), 
                type(target_type), 
                allow_unsafe=False
            )
            
            # Verify result
            assert result is True
    
    @pytest.mark.asyncio
    async def test_can_convert_false(self):
        """Test the can_convert function returning False."""
        # Mock registry.find_conversion_path to return None
        mock_find = MagicMock(return_value=None)
        
        with patch('pyvider.cty.convert.convert.registry.find_conversion_path', mock_find):
            # Create types to check
            source_type = CtyString()
            target_type = CtyNumber()
            
            # Call can_convert
            result = await can_convert(source_type, target_type)
            
            # Verify result
            assert result is False
    
    @pytest.mark.asyncio
    async def test_can_convert_unsafe_function(self):
        """Test the can_convert_unsafe function."""
        # Mock registry.find_conversion_path
        mock_path = [MagicMock()]
        mock_find = MagicMock(return_value=mock_path)
        
        with patch('pyvider.cty.convert.convert.registry.find_conversion_path', mock_find):
            # Create types to check
            source_type = CtyString()
            target_type = CtyNumber()
            
            # Call can_convert_unsafe
            result = await can_convert_unsafe(source_type, target_type)
            
            # Verify mock was called
            mock_find.assert_called_once_with(
                type(source_type), 
                type(target_type), 
                allow_unsafe=True
            )
            
            # Verify result
            assert result is True
    
    @pytest.mark.asyncio
    async def test_unify_function(self):
        """Test the unify function."""
        # Mock registry.unify
        mock_result = (CtyBool, [MagicMock(), MagicMock()])
        mock_unify = MagicMock(return_value=mock_result)
        
        with patch('pyvider.cty.convert.convert.registry.unify', mock_unify):
            # Create types to unify
            types = [CtyString(), CtyNumber()]
            
            # Call unify
            result = await unify(types)
            
            # Verify mock was called
            mock_unify.assert_called_once_with([type(t) for t in types], allow_unsafe=False)
            
            # Verify result
            assert result == mock_result
    
    @pytest.mark.asyncio
    async def test_unify_unsafe_function(self):
        """Test the unify_unsafe function."""
        # Mock registry.unify
        mock_result = (CtyBool, [MagicMock(), MagicMock()])
        mock_unify = MagicMock(return_value=mock_result)
        
        with patch('pyvider.cty.convert.convert.registry.unify', mock_unify):
            # Create types to unify
            types = [CtyString(), CtyNumber()]
            
            # Call unify_unsafe
            result = await unify_unsafe(types)
            
            # Verify mock was called
            mock_unify.assert_called_once_with([type(t) for t in types], allow_unsafe=True)
            
            # Verify result
            assert result == mock_result


class TestBuiltinConversions:
    """Tests for the built-in conversions."""
    
    @pytest.mark.asyncio
    async def test_string_to_number_conversion(self):
        """Test the string to number conversion."""
        # Create string value
        string_value = CtyValue(CtyString(), "123.45")
        
        # Mock the registry and conversion
        mock_result = CtyValue(CtyNumber(), Decimal("123.45"))
        mock_converter = MagicMock()
        
        # Register a test conversion
        with patch('pyvider.cty.convert.convert.string_to_number', return_value=mock_result):
            registry.register(
                source_type=CtyString,
                target_type=CtyNumber,
                converter=mock_converter,
                is_safe=False
            )
            
            # Perform conversion
            result = await convert_unsafe(string_value, CtyNumber)
            
            # Verify result
            assert result == mock_result
    
    @pytest.mark.asyncio
    async def test_identity_conversion(self):
        """Test converting a value to its own type."""
        # Create a value
        value = CtyValue(CtyString(), "test")
        
        # Convert to same type
        result = await convert(value, CtyString)
        
        # Verify result is same as input
        assert result == value
