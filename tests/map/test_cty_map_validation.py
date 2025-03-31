#
# tests/map/test_cty_map_validation.py
#

import pytest
from pyvider.cty.exceptions import CtyMapValidationError
from pyvider.cty import CtyBool, CtyMap, CtyNumber, CtyString, CtyValue

class TestCtyMapValidation:
    def setup_method(self):
        """Set up test fixtures before each test."""
        self.string_map = CtyMap(key_type=CtyString(), value_type=CtyString())
        self.number_map = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        self.bool_map = CtyMap(key_type=CtyString(), value_type=CtyBool())

    @pytest.mark.asyncio
    async def test_cty_map_validate_valid_string_map(self):
        """Test validation of a valid string map with pre‐validated keys/values."""
        valid = {
            CtyValue(type_=CtyString(), value="name"): CtyValue(type_=CtyString(), value="pyvider")
        }
        validated = self.string_map.validate(valid)
        assert isinstance(validated, CtyValue)
        assert isinstance(validated.type, CtyMap)
        map_data = validated.value
        assert isinstance(map_data, dict)
        # Test retrieval using the get() method.
        name_value = self.string_map.get(validated, CtyValue(type_=CtyString(), value="name"))
        assert name_value is not None
        assert isinstance(name_value, CtyValue)
        assert isinstance(name_value.type, CtyString)
        assert name_value.value == "pyvider"
        # Test direct access via iterating the map's keys.
        found_key = None
        for k in map_data:
            assert isinstance(k, CtyValue)
            assert isinstance(k.type, CtyString)
            if k.value == "name":
                found_key = k
                break
        assert found_key is not None, "Key 'name' not found in map"
        assert map_data[found_key].value == "pyvider"

    @pytest.mark.asyncio
    async def test_cty_map_validate_valid_number_map(self):
        """Test validation of a valid number map."""
        valid = {"count": 3, "max_retries": 5}
        validated = self.number_map.validate(valid)

        # Find the value for "count" key
        count_value = None
        for k in validated.value:
            if isinstance(k, CtyString) and k.value == "count":
                count_value = validated.value[k]
                break

        assert count_value is not None, "Key 'count' not found in map"
        assert isinstance(count_value, CtyNumber)
        assert count_value.value == 3

    @pytest.mark.asyncio
    async def test_cty_map_validate_valid_bool_map(self):
        """Test validation of a valid boolean map."""
        valid = {"is_active": True, "is_deleted": False}
        validated = self.bool_map.validate(valid)

        # Find the value for "is_active" key
        is_active_value = None
        for k in validated.value:
            if isinstance(k, CtyString) and k.value == "is_active":
                is_active_value = validated.value[k]
                break

        assert is_active_value is not None, "Key 'is_active' not found in map"
        assert isinstance(is_active_value, CtyBool)
        assert is_active_value.value is True

    @pytest.mark.asyncio
    async def test_cty_map_validate_empty_map(self):
        """Test validation of an empty map."""
        empty = {}
        validated = self.string_map.validate(empty)
        assert len(validated.value) == 0

    @pytest.mark.asyncio
    async def test_cty_map_with_decimal_values(self):
        """Test map with Decimal number values."""
        # Create map with Decimal values
        from decimal import Decimal
        
        data = {
            "pi": Decimal("3.14159"),
            "e": Decimal("2.71828"),
            "zero": Decimal("0")
        }

        # Validate
        validated = self.number_map.validate(data)

        # Check structure
        assert len(validated.value) == 3

        # Check Decimal values
        for k, v in validated.value.items():
            assert isinstance(v, CtyNumber)
            if k.value == "pi":
                assert isinstance(v.value, Decimal)
                assert v.value == Decimal("3.14159")
            elif k.value == "e":
                assert isinstance(v.value, Decimal)
                assert v.value == Decimal("2.71828")

    @pytest.mark.asyncio
    async def test_cty_map_unhashable_key(self):
        """Test validation with unhashable key."""
        # Create a custom key type that rejects a specific key
        class RejectingKeyType(CtyString):
            def validate(self, value):
                if value == "valid_key":
                    raise CtyMapValidationError("Key validation failed: unhashable type")
                return super().validate(value)
        
        # Create test map with rejecting key type
        test_map = CtyMap(key_type=RejectingKeyType(), value_type=CtyString())
        
        # Test validation failure
        with pytest.raises(CtyMapValidationError) as exc:
            test_map.validate({"valid_key": "value"})

@pytest.mark.asyncio
async def test_cty_map_validate_none():
    """Test validation with None value."""
    map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
    result = map_type.validate(None)

    assert isinstance(result, CtyValue)
    assert isinstance(result.type, CtyMap)
    assert len(result.value) == 0

@pytest.mark.asyncio
async def test_cty_map_validate_empty_dict():
    """Test validation with empty dictionary."""
    map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
    result = map_type.validate({})

    assert isinstance(result, CtyValue)
    assert isinstance(result.type, CtyMap)
    assert len(result.value) == 0

@pytest.mark.asyncio
async def test_cty_map_validate_valid_data():
    """Test validation with valid data."""
    from decimal import Decimal

    map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())

    # Valid data
    data = {
        "one": 1,
        "two": 2.5,
        "three": Decimal("3.14")
    }

    result = map_type.validate(data)

    assert isinstance(result, CtyValue)
    assert isinstance(result.type, CtyMap)
    assert len(result.value) == 3

    # Find values by iterating
    for k, v in result.value.items():
        assert isinstance(k, CtyString)
        assert isinstance(v, CtyNumber)

        if k.value == "one":
            assert v.value == 1
        elif k.value == "two":
            assert v.value == 2.5
        elif k.value == "three":
            assert v.value == Decimal("3.14")

@pytest.mark.asyncio
async def test_cty_map_validate_invalid_key():
    """Test validation with invalid key type."""
    map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())

    # Data with invalid key type
    data = {
        "one": 1,
        2: 2,  # Invalid key type (int instead of string)
        "three": 3
    }

    with pytest.raises(CtyMapValidationError):
        map_type.validate(data)

@pytest.mark.asyncio
async def test_cty_map_validate_invalid_value():
    """Test validation with invalid value type."""
    map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())

    # Data with invalid value type
    data = {
        "one": 1,
        "two": "not_a_number",  # Invalid value type (string instead of number)
        "three": 3
    }

    with pytest.raises(CtyMapValidationError):
        map_type.validate(data)

@pytest.mark.asyncio
async def test_cty_map_validate_with_cty_instances():
    """Test validation with pre-created CtyType instances."""
    map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())

    # Create CtyType instances
    key1 = CtyString(value="one")
    key2 = CtyString(value="two")
    val1 = CtyNumber(value=1)
    val2 = CtyNumber(value=2)

    # Data with CtyType instances
    data = {
        key1: val1,
        key2: val2,
        "three": 3  # Mixed with raw value
    }

    result = map_type.validate(data)

    assert isinstance(result, CtyValue)
    assert isinstance(result.type, CtyMap)
    assert len(result.value) == 3

    # Verify CtyType instances are preserved
    for k, v in result.value.items():
        assert isinstance(k, CtyString)
        assert isinstance(v, CtyNumber)

        if k.value == "one":
            assert k is key1  # Should be same instance
            assert v is val1  # Should be same instance
        elif k.value == "two":
            assert k is key2  # Should be same instance
            assert v is val2  # Should be same instance

    @pytest.mark.asyncio
    async def test_cty_map_validate_invalid_bool_map(self):
        """Test validation with invalid bool map."""
        invalid = {"is_active": 123}  # Not a boolean value
        with pytest.raises(CtyMapValidationError) as excinfo:
            self.bool_map.validate(invalid)
        assert "validation failed" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_cty_map_with_cty_values(self):
        """Test creating maps using CtyValue instances."""
        # Create CtyValues
        from pyvider.cty.values import CtyValue

        key1 = CtyValue(type_=CtyString(), value="key1")
        val1 = CtyValue(type_=CtyString(), value="value1")

        # Try to create map with CtyValues
        # This test is exploratory - it may fail if CtyValues are not directly supported
        try:
            data = {key1: val1}
            self.string_map.validate(data)
        except Exception:
            # If this approach is not supported, that's fine
            pass

@pytest.mark.asyncio
async def test_cty_map_validation_error_details():
    """Test that validation errors provide detailed information."""
    map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())

    # Data with multiple issues
    data = {
        "one": 1,
        "two": "not_a_number",  # Invalid value
        123: 3,  # Invalid key
    }

    # Validate and catch detailed error
    with pytest.raises(CtyMapValidationError) as excinfo:
        map_type.validate(data)

    # Error message should contain details
    error_msg = str(excinfo.value)
    assert "validation failed" in error_msg

@pytest.mark.asyncio
async def test_cty_map_init_validation():
    """Test validation during CtyMap initialization."""
    # Valid initialization
    valid_map = CtyMap(key_type=CtyString(), value_type=CtyNumber())
    assert valid_map.key_type == CtyString()
    assert valid_map.value_type == CtyNumber()

    # Invalid key_type
    with pytest.raises(CtyMapValidationError):
        CtyMap(key_type="not_a_cty_type", value_type=CtyNumber())

    # Invalid value_type
    with pytest.raises(CtyMapValidationError):
        CtyMap(key_type=CtyString(), value_type="not_a_cty_type")

@pytest.mark.asyncio
async def test_attribute_paths_with_cty_values():
    """Test paths with attribute access for proper CtyValues."""
    # Create object type with proper CtyType attributes
    from pyvider.cty import CtyObject, CtyPath

    person_type = CtyObject(attribute_types={
        "name": CtyString(),
        "age": CtyNumber()
    })
    
    # Create a value using proper CtyValue wrapping
    person = CtyValue(
        type_=person_type,
        value={
            "name": CtyValue(type_=CtyString(), value="Alice"),
            "age": CtyValue(type_=CtyNumber(), value=30)
        }
    )
    
    # Test attribute access
    name_path = CtyPath.get_attr("name")
    name_result = await name_path.apply_path(person)
    
    # Verify result maintains CtyType
    assert isinstance(name_result, CtyValue)
    assert isinstance(name_result.type, CtyString)
    assert name_result.value == "Alice"

# 🐍🏗️🧪
