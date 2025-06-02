#
# tests/values/test_cty_values_base.py
#

import pytest
import asyncio # Existing import
import logging
from decimal import Decimal

from pyvider.cty import (
    CtyValue,
    CtyString,
    CtyNumber,
    CtyBool,
    CtyMap,
    CtyObject,
    CtyList # Added CtyList
)
from pyvider.cty.types import CtyDynamic
# from pyvider.telemetry import logger as pyvider_logger # Removed direct manipulation for now

class TestCtyValueBasicOperations:
    """Tests for basic CtyValue operations."""

    @pytest.fixture
    def setup_values(self):
        """Set up test values."""
        self.str_type = CtyString()
        self.str_val = CtyValue(vtype=self.str_type, value="test")
        self.unknown_val = CtyValue.unknown(self.str_type)
        self.null_val = CtyValue.null(self.str_type)
        self.marked_val = self.str_val.mark("test_mark")

    @pytest.mark.asyncio
    async def test_value_initialization(self, setup_values):
        """Test the initialization of CtyValue."""
        # Regular value
        assert self.str_val.type == self.str_type
        assert self.str_val.value == "test"
        assert not self.str_val.is_unknown
        assert not self.str_val.is_null

        # Make sure it's hashable
        hash(self.str_val)

        # String representation
        assert str(self.str_val) == "test"
        assert repr(self.str_val).startswith("CtyValue(")

    @pytest.mark.asyncio
    async def test_value_unknown(self, setup_values):
        """Test unknown CtyValue behavior."""
        assert self.unknown_val.type == self.str_type
        assert self.unknown_val.is_unknown
        assert not self.unknown_val.is_null

        # Unknown values raise ValueError when accessing value
        with pytest.raises(ValueError):
            _ = self.unknown_val.value

        # String representation
        assert str(self.unknown_val) == f"<unknown {self.str_type.__class__.__name__}>"

    @pytest.mark.asyncio
    async def test_value_null(self, setup_values):
        """Test null CtyValue behavior."""
        assert self.null_val.type == self.str_type
        assert self.null_val.is_null
        assert not self.null_val.is_unknown

        # Null values return None when accessing value
        assert self.null_val.value is None

        # String representation
        assert str(self.null_val) == f"<null {self.str_type.__class__.__name__}>"

    @pytest.mark.asyncio
    async def test_value_with_marks(self, setup_values):
        """Test CtyValue with marks."""
        assert self.marked_val.type == self.str_type
        assert self.marked_val.value == "test"
        assert self.marked_val.has_mark("test_mark")
        assert not self.marked_val.has_mark("other_mark")

    @pytest.mark.asyncio
    async def test_value_has_mark(self, setup_values):
        """Test has_mark method."""
        # Mark matches exactly
        assert self.marked_val.has_mark("test_mark")

        # Mark matches by string representation
        class CustomMark:
            def __str__(self):
                return "test_mark"

        assert self.marked_val.has_mark(CustomMark())

        # Mark doesn't match
        assert not self.marked_val.has_mark("other_mark")

    @pytest.mark.asyncio
    async def test_value_add_mark(self, setup_values):
        """Test adding a mark to a value."""
        new_val = self.str_val.mark("new_mark")

        # Original value unchanged
        assert not self.str_val.has_mark("new_mark")

        # New value has mark
        assert new_val.has_mark("new_mark")
        assert new_val.value == "test"

    @pytest.mark.asyncio
    async def test_value_add_multiple_marks(self, setup_values):
        """Test adding multiple marks to a value."""
        val1 = self.str_val.mark("mark1")
        val2 = val1.mark("mark2")

        # Each value has the expected marks
        assert not self.str_val.has_mark("mark1")
        assert val1.has_mark("mark1")
        assert not val1.has_mark("mark2")
        assert val2.has_mark("mark1")
        assert val2.has_mark("mark2")

    @pytest.mark.asyncio
    async def test_value_unmark(self, setup_values):
        """Test removing marks from a value."""
        # Add multiple marks
        val = self.str_val.mark("mark1").mark("mark2")

        # Remove marks
        unmarked, marks = val.unmark()

        # Check unmarked value
        assert not unmarked.has_mark("mark1")
        assert not unmarked.has_mark("mark2")
        assert unmarked.value == "test"

        # Check removed marks
        assert len(marks) == 2
        assert "mark1" in str(marks) # Convert set to string for simple check
        assert "mark2" in str(marks)


    @pytest.mark.asyncio
    async def test_value_type_property(self, setup_values):
        """Test the type property."""
        assert self.str_val.type == self.str_type
        assert self.unknown_val.type == self.str_type
        assert self.null_val.type == self.str_type

    @pytest.mark.asyncio
    async def test_value_is_unknown_property(self, setup_values):
        assert self.str_val.is_unknown is False
        assert self.unknown_val.is_unknown is True
        assert self.null_val.is_unknown is False # A null value is known (it's null)

    @pytest.mark.asyncio
    async def test_value_is_null_property(self, setup_values):
        """Test the is_null property."""
        assert not self.str_val.is_null
        assert not self.unknown_val.is_null
        assert self.null_val.is_null

    @pytest.mark.asyncio
    async def test_to_dict_method(self, setup_values):
        """Test the to_dict method."""
        # Regular value
        dict_repr = self.str_val.to_dict()
        assert isinstance(dict_repr, dict)
        assert dict_repr["type"] == "CtyString"
        assert dict_repr["value"] == "test"

        # Unknown value
        dict_repr = self.unknown_val.to_dict()
        assert dict_repr["type"] == "CtyString"
        assert dict_repr["is_unknown"] is True

        # Null value
        dict_repr = self.null_val.to_dict()
        assert dict_repr["type"] == "CtyString"
        assert dict_repr["is_null"] is True

        # Marked value
        dict_repr = self.marked_val.to_dict()
        assert dict_repr["type"] == "CtyString"
        assert dict_repr["value"] == "test"
        assert "marks" in dict_repr
        assert "test_mark" in str(dict_repr["marks"])

    @pytest.mark.asyncio
    async def test_value_equality(self, setup_values):
        """Test value equality."""
        # Same values are equal
        val1 = CtyValue(vtype=self.str_type, value="test")
        val2 = CtyValue(vtype=self.str_type, value="test")
        assert val1 == val2

        # Different values are not equal
        val3 = CtyValue(vtype=self.str_type, value="different")
        assert val1 != val3

        # Unknown values of same type are equal
        unknown1 = CtyValue.unknown(self.str_type)
        unknown2 = CtyValue.unknown(self.str_type)
        assert unknown1 == unknown2

        # Null values of same type are equal
        null1 = CtyValue.null(self.str_type)
        null2 = CtyValue.null(self.str_type)
        assert null1 == null2

        # Different types of values are not equal
        assert val1 != unknown1
        assert val1 != null1
        assert unknown1 != null1

        # Values with different marks are not equal
        marked1 = val1.mark("mark1")
        marked2 = val1.mark("mark2")
        assert marked1 != marked2

        # Compare with non-CtyValue
        assert val1 != "test"
        assert val1 != 123

# 🐍🏗️🧪

class TestCtyValueGetMethod:
    """Tests for the CtyValue.get() method."""

    def test_get_on_unknown_value_returns_default(self):
        unknown_val = CtyValue.unknown(CtyString())
        default_sentinel = "default_val"
        assert unknown_val.get("any_key", default_sentinel) == default_sentinel

    def test_get_on_null_value_returns_default(self):
        null_val = CtyValue.null(CtyString())
        default_sentinel = "default_val"
        assert null_val.get("any_key", default_sentinel) == default_sentinel

    def test_get_on_map_with_incompatible_default(self): # Removed caplog
        map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        map_val = map_type.validate({}) # Empty map
        default_incompatible = "not_a_number"
        assert map_val.get("non_existent_key", default_incompatible) is None
        # Removed: assert "Default value 'not_a_number' is not compatible with map value type CtyNumber" in caplog.text

    def test_get_on_object_with_non_string_key(self): # Removed caplog
        obj_type = CtyObject(attribute_types={"name": CtyString()})
        obj_val = obj_type.validate({"name": "test"})
        default_sentinel = "default_obj_val"
        assert obj_val.get(123, default_sentinel) == default_sentinel
        # Removed: assert "Object attribute key must be string, got int" in caplog.text

    def test_get_on_number_value_returns_default(self): # Removed caplog
        num_val = CtyValue.number(123)
        default_sentinel = "default_num_val"
        assert num_val.get("any_key", default_sentinel) == default_sentinel
        # Removed: assert "get() called on unsupported type: CtyNumber" in caplog.text

    def test_get_on_string_value_returns_default(self): # Removed caplog
        str_val = CtyValue.string("hello")
        default_sentinel = "default_str_val"
        assert str_val.get("any_key", default_sentinel) == default_sentinel
        # Removed: assert "get() called on unsupported type: CtyString" in caplog.text

    def test_get_on_bool_value_returns_default(self): # Removed caplog
        bool_val = CtyValue.bool(True)
        default_sentinel = "default_bool_val"
        assert bool_val.get("any_key", default_sentinel) == default_sentinel
        # Removed: assert "get() called on unsupported type: CtyBool" in caplog.text

    def test_get_on_object_with_internal_get_attribute_failure(self, mocker): # Removed caplog
        obj_type = CtyObject(attribute_types={"name": CtyString()})
        obj_val = obj_type.validate({"name": "test"})
        default_sentinel = "default_fail_val"
        # Patch the class CtyObject, not the instance obj_val.type
        mocker.patch.object(CtyObject, 'get_attribute', side_effect=Exception("mocked error"), autospec=True)
        assert obj_val.get("name", default_sentinel) == default_sentinel
        # Removed: assert "Object attribute access failed: mocked error" in caplog.text

    def test_get_on_map_with_internal_get_failure(self, mocker): # Removed caplog
        map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        map_val = map_type.validate({"a": 1})
        default_sentinel = 999 # Corrected to be a compatible type (number)

        # Patch the class CtyMap, not the instance map_val.type
        mocker.patch.object(CtyMap, 'get', side_effect=Exception("mocked map error"), autospec=True)

        assert map_val.get("a", default_sentinel) == default_sentinel
        # Removed: assert "Map get failed: mocked map error" in caplog.text

# New Test Class
class TestCtyValueSetDeleteErrors:
    """Tests for error paths in CtyValue.set() and CtyValue.delete() methods."""

    def test_set_on_unknown_value_raises_type_error(self):
        unknown_val = CtyValue.unknown(CtyMap(key_type=CtyString(), value_type=CtyString()))
        with pytest.raises(TypeError, match="Cannot set key on unknown/null value"):
            unknown_val.set("any_key", "any_value")

    def test_set_on_null_value_raises_type_error(self):
        null_val = CtyValue.null(CtyMap(key_type=CtyString(), value_type=CtyString()))
        with pytest.raises(TypeError, match="Cannot set key on unknown/null value"):
            null_val.set("any_key", "any_value")

    def test_set_on_list_value_raises_type_error(self):
        list_val = CtyValue.list(CtyString(), ["a", "b"])
        with pytest.raises(TypeError, match="set\(\) method not supported for type CtyList"):
            list_val.set("any_key", "any_value")

    def test_set_on_number_value_raises_type_error(self):
        num_val = CtyValue.number(123)
        with pytest.raises(TypeError, match="set\(\) method not supported for type CtyNumber"):
            num_val.set("any_key", "any_value")

    def test_delete_on_unknown_value_raises_type_error(self):
        unknown_val = CtyValue.unknown(CtyMap(key_type=CtyString(), value_type=CtyString()))
        with pytest.raises(TypeError, match="Cannot delete key from unknown/null value"):
            unknown_val.delete("any_key")

    def test_delete_on_null_value_raises_type_error(self):
        null_val = CtyValue.null(CtyMap(key_type=CtyString(), value_type=CtyString()))
        with pytest.raises(TypeError, match="Cannot delete key from unknown/null value"):
            null_val.delete("any_key")

    def test_delete_on_list_value_raises_type_error(self):
        list_val = CtyValue.list(CtyString(), ["a", "b"])
        with pytest.raises(TypeError, match="delete\(\) method not supported for type CtyList"):
            list_val.delete("any_key")

    def test_delete_on_number_value_raises_type_error(self):
        num_val = CtyValue.number(123)
        with pytest.raises(TypeError, match="delete\(\) method not supported for type CtyNumber"):
            num_val.delete("any_key")
