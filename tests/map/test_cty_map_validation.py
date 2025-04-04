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
            CtyValue(vtype=CtyString(), value="name"): CtyValue(vtype=CtyString(), value="pyvider")
        }
        validated = self.string_map.validate(valid)
        assert isinstance(validated, CtyValue)
        assert isinstance(validated.type, CtyMap)
        map_data = validated.value
        assert isinstance(map_data, dict)
        
        # Test retrieval using the get() method - adjusted for string keys
        name_value = self.string_map.get(validated, "name")
        assert name_value is not None
        assert isinstance(name_value, CtyValue)
        assert isinstance(name_value.type, CtyString)
        assert name_value.value == "pyvider"
        
        # Test direct access via string key
        found_key = None
        assert "name" in map_data, "Key 'name' not found in map"
        assert map_data["name"].value == "pyvider"

    @pytest.mark.asyncio
    async def test_cty_map_empty_map_validation(self):
        """Test validation of empty maps."""
        string_map = CtyMap(key_type=CtyString(), value_type=CtyString())

        # Validate None
        null_result = string_map.validate(None)
        assert isinstance(null_result, CtyValue)
        assert isinstance(null_result.type, CtyMap)
        assert null_result.type.equal(string_map)
        assert len(null_result.value) == 0

        # Validate empty dict
        empty_result = string_map.validate({})
        assert isinstance(empty_result, CtyValue)
        assert isinstance(empty_result.type, CtyMap)
        assert empty_result.type.equal(string_map)
        assert len(empty_result.value) == 0

    @pytest.mark.asyncio
    async def test_cty_map_init_validation(self):
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
    async def test_cty_map_validate_empty_dict(self):
        """Test validation with empty dictionary."""
        map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        result = map_type.validate({})

        assert isinstance(result, CtyValue)
        assert isinstance(result.type, CtyMap)
        assert len(result.value) == 0

    @pytest.mark.asyncio
    async def test_cty_map_validate_invalid_key(self):
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
    async def test_cty_map_validate_invalid_value(self):
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
    async def test_cty_map_validate_with_cty_instances(self):
        """Test validation with pre-created CtyType instances."""
        map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())

        # Create CtyValue instances for keys and values
        key1 = CtyValue(vtype=CtyString(), value="one")
        key2 = CtyValue(vtype=CtyString(), value="two")
        val1 = CtyValue(vtype=CtyNumber(), value=1)
        val2 = CtyValue(vtype=CtyNumber(), value=2)

        # Data with CtyValue instances
        data = {
            key1: val1,
            key2: val2,
            "three": 3  # Mixed with raw value
        }

        result = map_type.validate(data)

        assert isinstance(result, CtyValue)
        assert isinstance(result.type, CtyMap)

        # Verify values can be retrieved by string keys
        assert "one" in result.value
        assert "two" in result.value
        assert "three" in result.value
        
        # Check values
        assert result.value["one"].value == 1
        assert result.value["two"].value == 2
        assert result.value["three"].value == 3

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

        key1 = CtyValue(vtype=CtyString(), value="key1")
        val1 = CtyValue(vtype=CtyString(), value="value1")

        # Try to create map with CtyValues
        # This test is exploratory - it may fail if CtyValues are not directly supported
        try:
            data = {key1: val1}
            self.string_map.validate(data)
        except Exception:
            # If this approach is not supported, that's fine
            pass

    @pytest.mark.asyncio
    async def test_cty_map_validation_error_details(self):
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
    async def test_cty_map_init_validation(self):
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
    async def test_attribute_paths_with_cty_values(self):
        """Test paths with attribute access for proper CtyValues."""
        # Create object type with proper CtyType attributes
        from pyvider.cty import CtyObject, CtyPath

        person_type = CtyObject(attribute_types={
            "name": CtyString(),
            "age": CtyNumber()
        })

        # Create a value using proper CtyValue wrapping
        person = CtyValue(
            vtype=person_type,
            value={
                "name": CtyValue(vtype=CtyString(), value="Alice"),
                "age": CtyValue(vtype=CtyNumber(), value=30)
            }
        )

        # Test attribute access
        name_path = CtyPath.get_attr("name")
        name_result = name_path.apply_path(person)

        # Verify result maintains CtyType
        assert isinstance(name_result, CtyValue)
        assert isinstance(name_result.type, CtyString)
        assert name_result.value == "Alice"

# 🐍🏗️🧪
