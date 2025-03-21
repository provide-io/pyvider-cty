
# tests/collections/test_collections_map.py

import pytest
from pyvider.cty.exceptions import ValidationError
from pyvider.cty import CtyBool, CtyMap, CtyNumber, CtyString, CtyValue


class TestCtyMapType:
    def setup_method(self):
        """Set up test fixtures before each test."""
        self.string_map = CtyMap(key_type=CtyString(), value_type=CtyString())
        self.number_map = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        self.bool_map = CtyMap(key_type=CtyString(), value_type=CtyBool())

    # -------------------- VALIDATION TESTS --------------------
    def test_validate_valid_string_map(self):
        """Test validation of a valid string map."""
        valid = {"name": "pyvider"}
        validated = self.string_map.validate(valid)
        # Compare directly with the original input
        assert validated.value == {"name": "pyvider"}

    def test_validate_valid_number_map(self):
        """Test validation of a valid number map."""
        valid = {"count": 3, "max_retries": 5}
        validated = self.number_map.validate(valid)
        # Extract validated value by indexing
        assert validated.value["count"] == 3

    def test_validate_valid_bool_map(self):
        """Test validation of a valid boolean map."""
        valid = {"is_active": True, "is_deleted": False}
        validated = self.bool_map.validate(valid)
        assert validated.value["is_active"] is True

    def test_validate_invalid_key_type(self):
        """Test validation with invalid key type."""
        invalid = {123: "invalid_key"}
        with pytest.raises(ValidationError):
            self.string_map.validate(invalid)

    def test_validate_invalid_value_type(self):
        """Test validation with invalid value type."""
        invalid = {"key": 42}
        with pytest.raises(ValidationError):
            self.string_map.validate(invalid)

    def test_validate_empty_map(self):
        """Test validation of an empty map."""
        empty = {}
        validated = self.string_map.validate(empty)
        assert len(validated.value) == 0

    def test_validate_nested_map(self):
        """Test validation with a nested map."""
        nested_map = CtyMap(key_type=CtyString(), value_type=self.string_map)
        valid = {"config": {"filename": "test.txt"}}
        validated = nested_map.validate(valid)
        # Access nested value correctly
        nested_map_value = validated.value["config"]
        assert nested_map_value.value["filename"] == "test.txt"

    def test_validate_nested_map_invalid(self):
        """Test validation with an invalid nested map."""
        nested_map = CtyMap(key_type=CtyString(), value_type=self.string_map)
        invalid = {"config": {"filename": 123}}
        with pytest.raises(ValidationError):
            nested_map.validate(invalid)

    # -------------------- EQUALITY AND COMPARISON TESTS --------------------
    def test_map_equality(self):
        """Test equality of maps with same element type."""
        map1 = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        map2 = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        assert map1.equal(map2) is True

    def test_map_inequality(self):
        """Test inequality of maps with different element types."""
        map1 = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        map2 = CtyMap(key_type=CtyString(), value_type=CtyString())
        assert map1.equal(map2) is False

    # -------------------- EDGE CASES --------------------
    def test_large_map(self):
        """Test validation of a large map."""
        large_map = {str(i): i for i in range(1000)}
        validated = self.number_map.validate(large_map)
        assert len(validated.value) == 1000

    def test_map_with_none(self):
        """Test validation with None value."""
        invalid = {"key": None}
        with pytest.raises(ValidationError):
            self.string_map.validate(invalid)

    #@pytest.mark.
    def test_unhashable_key(self):
        """Test validation with unhashable key."""
        invalid = {{"nested": "key"}: "vale"}  # dict key is unhashable
        with pytest.raises(ValidationError):
            self.string_map.validate(invalid)

    def test_map_with_nested_lists(self):
        """Test validation with nested lists."""
        # Here we need to initialize the map correctly with both key_type and value_type
        tf_map = CtyMap(key_type=CtyString(), value_type=CtyString())
        nested_data = {"key1": ["item1", "item2"], "key2": ["item3"]}
        
        # This may be failing because strings can't validate lists
        # Let's modify the test to use a more compatible type
        with pytest.raises(ValidationError):
            tf_map.validate(nested_data)

    def test_map_with_incompatible_nested(self):
        """Test validation with incompatible nested values."""
        nested_map = CtyMap(key_type=CtyString(), value_type=self.string_map)
        invalid = {"nested": {"key": 42}}  # Key type valid, value type invalid
        with pytest.raises(ValidationError):
            nested_map.validate(invalid)

    #@pytest.mark.skip
    def test_validate_invalid_bool_map(self):
        """Test validation with invalid bool map."""
        invalid = {"is_active": CtyNumber(1)}  # Incorrect type for boolean field
        with pytest.raises(ValidationError) as excinfo:
            self.bool_map.validate(invalid)
        assert "Expected CtyBool" in str(excinfo.exception)
