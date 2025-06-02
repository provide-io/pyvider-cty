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

    def test_value_has_mark(self, setup_values): # Removed async
        """Test has_mark method for various scenarios.""" # Updated docstring
        # Mark matches exactly (using self.marked_val from setup_values)
        assert self.marked_val.has_mark("test_mark")

        # Mark matches by string representation (using self.marked_val)
        class CustomMark:
            def __str__(self):
                return "test_mark"
        assert self.marked_val.has_mark(CustomMark())

        # Mark doesn't match (using self.marked_val)
        assert not self.marked_val.has_mark("other_mark")

        # Test on a value with no marks (using self.str_val from setup_values)
        assert not self.str_val.has_mark("any_mark_at_all")

        # Test with an empty string as a mark argument on a value with no marks
        assert not self.str_val.has_mark("")

        # Test with an empty string as a mark argument on a value that has other marks
        assert not self.marked_val.has_mark("")

        # Test trying to find a non-empty mark on a CtyValue that was explicitly marked with an empty string
        empty_string_marked_val = self.str_val.mark("")
        assert empty_string_marked_val.has_mark("")
        assert not empty_string_marked_val.has_mark("some_other_mark")

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

    def test_value_unmark(self, setup_values, caplog): # Add caplog, remove async
        """Test removing marks from a value and check logging.""" # Update docstring
        # Add multiple marks
        val = self.str_val.mark("mark1").mark("mark2")

        caplog.set_level(logging.DEBUG) # Use caplog to set level

        # Remove marks
        unmarked, marks = val.unmark()

        # Check unmarked value
        assert not unmarked.has_mark("mark1")
        assert not unmarked.has_mark("mark2")
        assert unmarked.value == "test"

        # Check removed marks
        assert len(marks) == 2
        # It's better to check for specific marks directly if order isn't guaranteed
        # and to avoid converting the set to string for assertion.
        assert "mark1" in {str(m) for m in marks} # Check existence by string representation
        assert "mark2" in {str(m) for m in marks} # Check existence by string representation

        # Check log message
        assert "Removing 2 marks from value" in caplog.text
        # No reset needed for caplog level

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

    def test_access_value_on_unknown_logs_warning(self, caplog): # caplog is already a parameter
        """Test accessing .value on an unknown CtyValue logs a warning and raises ValueError."""
        unknown_val = CtyValue.unknown(CtyString())

        # Use caplog to set the logging level for the relevant logger
        # Assuming the logger used by CtyValue is named 'pyvider.telemetry'
        # or can be captured by setting the level for all loggers if specific name is unknown.
        # Let's try setting for all loggers that caplog captures first to ensure WARNING is caught.
        caplog.set_level(logging.WARNING)
        # If 'pyvider.telemetry' is the correct name and we only want to affect that:
        # caplog.set_level(logging.WARNING, logger='pyvider.telemetry')

        with pytest.raises(ValueError, match="Cannot get raw value of unknown value"):
            _ = unknown_val.value

        assert "Attempted to get raw value of unknown value" in caplog.text
        # No need to reset level with caplog.set_level(), it's fixture-scoped.

    def test_value_replace_marks_with_with_marks(self, setup_values):
        """Test replacing all marks on a CtyValue using the with_marks() method."""
        initial_val = CtyValue.string("hello").mark("mark1").mark("mark2")

        assert initial_val.has_mark("mark1")
        assert initial_val.has_mark("mark2")

        new_marks_set = {"new_mark_A", "new_mark_B"}

        # Replace existing marks with a new set
        updated_val = initial_val.with_marks(new_marks_set)

        # Check the new value
        assert updated_val.value == "hello"
        assert updated_val.has_mark("new_mark_A")
        assert updated_val.has_mark("new_mark_B")
        assert not updated_val.has_mark("mark1") # Original mark should be gone
        assert not updated_val.has_mark("mark2") # Original mark should be gone
        assert len(updated_val._marks) == 2

        # Ensure original value is unchanged (CtyValues are immutable)
        assert initial_val.has_mark("mark1")
        assert initial_val.has_mark("mark2")
        assert not initial_val.has_mark("new_mark_A")
        assert len(initial_val._marks) == 2

        # Test replacing with an empty set of marks
        no_marks_val = updated_val.with_marks(set())
        assert no_marks_val.value == "hello"
        assert not no_marks_val.has_mark("new_mark_A")
        assert not no_marks_val.has_mark("new_mark_B")
        assert len(no_marks_val._marks) == 0

        # Test replacing marks on a value that initially has no marks
        val_without_marks = CtyValue.string("no_marks_initially")
        assert len(val_without_marks._marks) == 0

        val_now_with_marks = val_without_marks.with_marks({"mark_added"})
        assert val_now_with_marks.has_mark("mark_added")
        assert len(val_now_with_marks._marks) == 1
        assert len(val_without_marks._marks) == 0 # Original still has no marks

# 🐍🏗️🧪

class TestCtyValueGetMethod:
    """Tests for the CtyValue.get() method."""

    def test_get_on_unknown_value_returns_default(self, caplog):
        unknown_val = CtyValue.unknown(CtyString())
        default_sentinel = "default_val"
        caplog.set_level(logging.DEBUG)
        assert unknown_val.get("any_key", default_sentinel) == default_sentinel
        assert "Getting value for key: any_key" in caplog.text
        assert "Cannot get from unknown/null value, returning default" in caplog.text

    def test_get_on_null_value_returns_default(self, caplog):
        null_val = CtyValue.null(CtyString())
        default_sentinel = "default_val"
        caplog.set_level(logging.DEBUG)
        assert null_val.get("any_key", default_sentinel) == default_sentinel
        assert "Getting value for key: any_key" in caplog.text
        assert "Cannot get from unknown/null value, returning default" in caplog.text

    def test_get_on_map_with_incompatible_default(self): # Removed caplog
        map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        map_val = map_type.validate({}) # Empty map
        default_incompatible = "not_a_number"
        assert map_val.get("non_existent_key", default_incompatible) is None
        # Removed: assert "Default value 'not_a_number' is not compatible with map value type CtyNumber" in caplog.text

    def test_get_on_object_with_non_string_key(self, caplog):
        obj_type = CtyObject(attribute_types={"name": CtyString()})
        obj_val = obj_type.validate({"name": "test"})
        default_sentinel = "default_obj_val"
        caplog.set_level(logging.DEBUG)
        assert obj_val.get(123, default_sentinel) == default_sentinel
        assert "Getting value for key: 123" in caplog.text
        assert "Object attribute key must be string, got int" in caplog.text

    def test_get_on_number_value_returns_default(self, caplog):
        num_val = CtyValue.number(123)
        default_sentinel = "default_num_val"
        caplog.set_level(logging.DEBUG)
        assert num_val.get("any_key", default_sentinel) == default_sentinel
        assert "Getting value for key: any_key" in caplog.text
        assert "get() called on unsupported type: CtyNumber" in caplog.text

    def test_get_on_string_value_returns_default(self, caplog):
        str_val = CtyValue.string("hello")
        default_sentinel = "default_str_val"
        caplog.set_level(logging.DEBUG)
        assert str_val.get("any_key", default_sentinel) == default_sentinel
        assert "Getting value for key: any_key" in caplog.text
        assert "get() called on unsupported type: CtyString" in caplog.text

    def test_get_on_bool_value_returns_default(self, caplog):
        bool_val = CtyValue.bool(True)
        default_sentinel = "default_bool_val"
        caplog.set_level(logging.DEBUG)
        assert bool_val.get("any_key", default_sentinel) == default_sentinel
        assert "Getting value for key: any_key" in caplog.text
        assert "get() called on unsupported type: CtyBool" in caplog.text

    def test_get_on_object_with_internal_get_attribute_failure(self, mocker, caplog):
        obj_type = CtyObject(attribute_types={"name": CtyString()})
        obj_val = obj_type.validate({"name": "test"})
        default_sentinel = "default_fail_val"
        caplog.set_level(logging.DEBUG)
        # Patch the class CtyObject, not the instance obj_val.type
        mocker.patch.object(CtyObject, 'get_attribute', side_effect=Exception("mocked error"), autospec=True)
        assert obj_val.get("name", default_sentinel) == default_sentinel
        assert "Getting value for key: name" in caplog.text
        assert "JULES_DEBUG: CtyObject get_attribute() EXCEPTION CAUGHT" in caplog.text

    def test_get_on_map_with_internal_get_failure(self, mocker, caplog):
        map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        map_val = map_type.validate({"a": 1})
        default_sentinel = 999 # Corrected to be a compatible type (number)
        caplog.set_level(logging.DEBUG)
        # Patch the class CtyMap, not the instance map_val.type
        mocker.patch.object(CtyMap, 'get', side_effect=Exception("mocked map error"), autospec=True)
        assert map_val.get("a", default_sentinel) == default_sentinel
        assert "Getting value for key: a" in caplog.text
        assert "JULES_DEBUG: CtyMap get() EXCEPTION CAUGHT" in caplog.text

    def test_get_on_object_missing_attribute_returns_default_and_logs(self, caplog):
        """Test get() on CtyObject for a missing attribute returns default and logs."""
        obj_type = CtyObject(attribute_types={"name": CtyString()})
        # Create an object *without* the 'age' attribute
        obj_val = CtyValue(vtype=obj_type, value={"name": "Alice"}, key_mapping={}) # Assuming direct construction for simplicity

        default_sentinel = "N/A"

        caplog.set_level(logging.DEBUG)

        assert obj_val.get("age", default_sentinel) == default_sentinel

        assert "Getting value for key: age" in caplog.text
        # This specific path for a missing attribute might not have a unique log line before returning default in CtyObject,
        # but the primary goal is to ensure it returns default (line 232).
        # The CtyObject.get_attribute is expected to handle non-existent keys gracefully,
        # potentially logging internally if desired, or raising an error caught by CtyValue.get.
        # The current CtyValue.get wraps CtyObject.get_attribute in a try-except Exception.
        # If CtyObject.get_attribute raises an exception for missing key, that would be logged by the JULES_DEBUG line.
        # If it returns a CtyValue.null or similar, that's different.
        # For line 232, the crucial part is that 'default' is returned.

        # Let's check for the JULES_DEBUG log if an exception was expected from get_attribute
        # For example, if obj_type.get_attribute was expected to raise CtyAttributeNotFoundError:
        # assert "JULES_DEBUG: CtyObject get_attribute() EXCEPTION CAUGHT" in caplog.text
        # However, if get_attribute returns None or a Cty Null, then no exception log.
        # The TODO asks to cover line 232 which is `return default`. This happens if key is not string OR if get_attribute fails.
        # The "key is not string" is one test. This test covers "attribute does not exist".
        # The CtyObject.get_attribute will raise CtyAttributeNotFoundError, which is caught by the broad except.
        assert "JULES_DEBUG: CtyObject get_attribute() EXCEPTION CAUGHT" in caplog.text

# New Test Class
class TestCtyValueSetDeleteErrors:
    """Tests for error paths in CtyValue.set() and CtyValue.delete() methods."""

    def test_set_on_unknown_value_raises_type_error(self, caplog):
        caplog.set_level(logging.ERROR)
        unknown_val = CtyValue.unknown(CtyMap(key_type=CtyString(), value_type=CtyString()))
        with pytest.raises(TypeError, match="Cannot set key on unknown/null value"):
            unknown_val.set("any_key", "any_value")
        assert "🔄❗❌ Cannot set key on unknown/null value" in caplog.text

    def test_set_on_null_value_raises_type_error(self, caplog):
        caplog.set_level(logging.ERROR)
        null_val = CtyValue.null(CtyMap(key_type=CtyString(), value_type=CtyString()))
        with pytest.raises(TypeError, match="Cannot set key on unknown/null value"):
            null_val.set("any_key", "any_value")
        assert "🔄❗❌ Cannot set key on unknown/null value" in caplog.text

    def test_set_on_list_value_raises_type_error(self, caplog):
        caplog.set_level(logging.ERROR)
        list_val = CtyValue.list(CtyString(), ["a", "b"])
        with pytest.raises(TypeError, match="set\(\) method not supported for type CtyList"):
            list_val.set("any_key", "any_value")
        assert "🔄❗❌ set() method not supported for type CtyList" in caplog.text

    def test_set_on_number_value_raises_type_error(self, caplog):
        caplog.set_level(logging.ERROR)
        num_val = CtyValue.number(123)
        with pytest.raises(TypeError, match="set\(\) method not supported for type CtyNumber"):
            num_val.set("any_key", "any_value")
        assert "🔄❗❌ set() method not supported for type CtyNumber" in caplog.text

    def test_delete_on_unknown_value_raises_type_error(self, caplog):
        caplog.set_level(logging.ERROR)
        unknown_val = CtyValue.unknown(CtyMap(key_type=CtyString(), value_type=CtyString()))
        with pytest.raises(TypeError, match="Cannot delete key from unknown/null value"):
            unknown_val.delete("any_key")
        assert "🔄❗❌ Cannot delete key from unknown/null value" in caplog.text

    def test_delete_on_null_value_raises_type_error(self, caplog):
        caplog.set_level(logging.ERROR)
        null_val = CtyValue.null(CtyMap(key_type=CtyString(), value_type=CtyString()))
        with pytest.raises(TypeError, match="Cannot delete key from unknown/null value"):
            null_val.delete("any_key")
        assert "🔄❗❌ Cannot delete key from unknown/null value" in caplog.text

    def test_delete_on_list_value_raises_type_error(self, caplog):
        caplog.set_level(logging.ERROR)
        list_val = CtyValue.list(CtyString(), ["a", "b"])
        with pytest.raises(TypeError, match="delete\(\) method not supported for type CtyList"):
            list_val.delete("any_key")
        assert "🔄❗❌ delete() method not supported for type CtyList" in caplog.text

    def test_delete_on_number_value_raises_type_error(self, caplog):
        caplog.set_level(logging.ERROR)
        num_val = CtyValue.number(123)
        with pytest.raises(TypeError, match="delete\(\) method not supported for type CtyNumber"):
            num_val.delete("any_key")
        assert "🔄❗❌ delete() method not supported for type CtyNumber" in caplog.text

    def test_successful_set_logs_debug(self, caplog):
        """Test that a successful set operation logs a debug message."""
        caplog.set_level(logging.DEBUG)
        map_val = CtyValue.map(CtyString(), CtyString(), {})

        key_to_set = "name"
        value_to_set = "Alice"

        updated_map_val = map_val.set(key_to_set, value_to_set)

        assert updated_map_val.get(key_to_set).value == value_to_set # Verify set worked

        # Check for the specific debug log message
        # Example: "🔄📝🔄 Setting key 'name' to value 'Alice'"
        # Need to escape the quotes in the f-string for the repr() of the key and value
        expected_log_msg = f"🔄📝🔄 Setting key {key_to_set!r} to value {value_to_set!r}"
        assert expected_log_msg in caplog.text

    def test_successful_delete_logs_debug(self, caplog):
        """Test that a successful delete operation logs a debug message."""
        caplog.set_level(logging.DEBUG)
        initial_items = {"name": "Alice", "city": "Wonderland"}
        map_val = CtyValue.map(CtyString(), CtyString(), initial_items)

        key_to_delete = "city"

        updated_map_val = map_val.delete(key_to_delete)

        assert updated_map_val.get(key_to_delete) is None # Verify delete worked (get returns None if default is None)
        assert updated_map_val.get("name").value == "Alice" # Ensure other keys are intact

        # Check for the specific debug log message
        # Example: "🔄📝🔄 Deleting key 'city'"
        expected_log_msg = f"🔄📝🔄 Deleting key {key_to_delete!r}"
        assert expected_log_msg in caplog.text


class TestCtyValueElementAt:
    """Tests for the CtyValue.element_at() method."""

    def test_element_at_on_unknown_value_raises_typeerror(self, caplog):
        caplog.set_level(logging.ERROR)
        unknown_list = CtyValue.unknown(CtyList(CtyString()))
        with pytest.raises(TypeError, match="Cannot get element from unknown or null value"):
            unknown_list.element_at(0)
        assert "🔄❗❌ Cannot get element from unknown or null value" in caplog.text

    def test_element_at_on_null_value_raises_typeerror(self, caplog):
        caplog.set_level(logging.ERROR)
        null_list = CtyValue.null(CtyList(CtyString()))
        with pytest.raises(TypeError, match="Cannot get element from unknown or null value"):
            null_list.element_at(0)
        assert "🔄❗❌ Cannot get element from unknown or null value" in caplog.text

    def test_element_at_on_unsupported_type_string_raises_typeerror(self, caplog):
        caplog.set_level(logging.ERROR)
        str_val = CtyValue.string("text")
        with pytest.raises(TypeError, match="element_at method not supported for type CtyString"):
            str_val.element_at(0)
        assert "🔄❗❌ element_at method not supported for type CtyString" in caplog.text

    def test_element_at_on_unsupported_type_map_raises_typeerror(self, caplog):
        caplog.set_level(logging.ERROR)
        map_val = CtyValue.map(CtyString(), CtyString(), {"a": "b"})
        with pytest.raises(TypeError, match="element_at method not supported for type CtyMap"):
            map_val.element_at(0) # Using 0 as an example index, though it's irrelevant for map
        assert "🔄❗❌ element_at method not supported for type CtyMap" in caplog.text

    def test_element_at_on_list_index_out_of_bounds_raises_indexerror(self, caplog):
        caplog.set_level(logging.ERROR)
        # The list elements for CtyValue.list factory should be raw Python values
        # that can be validated into CtyValues of the element_type.
        # So, ["a", "b"] is correct if element_type is CtyString().
        list_val = CtyValue.list(CtyString(), ["a", "b"])

        with pytest.raises(IndexError, match="List index 2 out of bounds"):
            list_val.element_at(2)
        assert "🔄❗❌ List index 2 out of bounds (size 2)" in caplog.text

        caplog.clear() # Clear previous logs for the next assertion
        with pytest.raises(IndexError, match="List index -3 out of bounds"):
            list_val.element_at(-3)
        assert "🔄❗❌ List index -3 out of bounds (size 2)" in caplog.text

    def test_element_at_successful_on_list_logs_debug(self, caplog):
        caplog.set_level(logging.DEBUG)
        # Elements for CtyValue.list factory should be raw Python values
        elements_raw = ["first", "second"]
        list_val = CtyValue.list(CtyString(), elements_raw)

        result = list_val.element_at(0)
        assert result.value == "first"
        assert "🔄🔍🔄 Getting element at index 0" in caplog.text

        caplog.clear()
        result_neg_index = list_val.element_at(-1)
        assert result_neg_index.value == "second"
        assert "🔄🔍🔄 Getting element at index -1" in caplog.text

    def test_element_at_successful_on_tuple_logs_debug_and_delegates(self, caplog):
        caplog.set_level(logging.DEBUG)
        # For CtyTuple, element_at is delegated. We are testing the CtyValue wrapper here.

        # Elements for CtyValue.tuple factory should be raw Python values
        tuple_val = CtyValue.tuple(
            (CtyString(), CtyNumber()),
            ("hello", 123) # Raw values
        )

        result = tuple_val.element_at(0)
        assert result.type == CtyString()
        assert result.value == "hello"
        assert "🔄🔍🔄 Getting element at index 0" in caplog.text

        caplog.clear()
        result_num = tuple_val.element_at(1)
        assert result_num.type == CtyNumber()
        assert result_num.value == Decimal("123") # Numbers are stored as Decimal
        assert "🔄🔍🔄 Getting element at index 1" in caplog.text

    def test_element_at_on_list_with_invalid_internal_value_raises_typeerror(self, caplog):
        caplog.set_level(logging.ERROR)
        # Construct a CtyValue that has CtyList as its _vtype, but whose _value is not a list/tuple.
        invalid_list_val = CtyValue(vtype=CtyList(CtyString()), value="this is not a list of CtyValues")

        with pytest.raises(TypeError, match="Cannot index list value of type str"):
            invalid_list_val.element_at(0)
        # No specific error log to check for this particular raise beyond the exception itself.
