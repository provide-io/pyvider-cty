# tests/path/test_path.py

"""
Integration tests for the Cty path system.

These tests verify that paths can navigate through nested Cty values,
including objects, lists, tuples, and maps.
"""

from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from pyvider.cty import CtyValue
from pyvider.cty.exceptions import AttributePathError, CtyValidationError
from pyvider.cty.path import (
    CtyPath,
)
from pyvider.cty.path.base import GetAttrStep, IndexStep, KeyStep
from pyvider.cty.types.collections import CtyList, CtyMap
from pyvider.cty.types.primitives import CtyBool, CtyNumber, CtyString
from pyvider.cty.types.structural import CtyObject, CtyTuple


class TestPathSystem:
    """Test the Cty path system."""

    @pytest.mark.asyncio
    async def test_attribute_paths(self) -> None:
        """Test paths with attribute access."""
        # Create an object type
        person_type = CtyObject(
            attribute_types={
                "name": CtyString(),
                "age": CtyNumber(),
                "address": CtyObject(
                    attribute_types={
                        "street": CtyString(),
                        "city": CtyString(),
                        "zip": CtyString(),
                    }
                ),
            }
        )

        # Create a properly wrapped object value
        person = CtyValue(
            vtype=person_type,
            value={
                "name": CtyValue(vtype=CtyString(), value="Alice"),
                "age": CtyValue(vtype=CtyNumber(), value=30),
                "address": CtyValue(
                    vtype=CtyObject(
                        attribute_types={
                            "street": CtyString(),
                            "city": CtyString(),
                            "zip": CtyString(),
                        }
                    ),
                    value={
                        "street": CtyValue(vtype=CtyString(), value="123 Main St"),
                        "city": CtyValue(vtype=CtyString(), value="Anytown"),
                        "zip": CtyValue(vtype=CtyString(), value="12345"),
                    },
                ),
            },
        )

        # Test direct attribute access
        name_path = CtyPath.get_attr("name")
        name_result = name_path.apply_path(person)
        assert isinstance(name_result, CtyValue)
        assert isinstance(name_result.type, CtyString)
        assert name_result.value == "Alice"

        # Test nested attribute access
        street_path = CtyPath.get_attr("address").child("street")
        street_result = street_path.apply_path(person)
        assert isinstance(street_result, CtyValue)
        assert isinstance(street_result.type, CtyString)
        assert street_result.value == "123 Main St"

        # Test invalid attribute
        invalid_path = CtyPath.get_attr("invalid")
        with pytest.raises(
            AttributePathError
        ):  # Message can vary depending on where it's caught
            invalid_path.apply_path(person)

        # Test type checking
        name_type = name_path.apply_path_type(person_type)
        assert isinstance(name_type, CtyString)

        street_type = street_path.apply_path_type(person_type)
        assert isinstance(street_type, CtyString)

        # Create an unknown value
        unknown_person = CtyValue.unknown(person_type)

        # Test path to attribute should return unknown value of correct type
        unknown_name_result = name_path.apply_path(unknown_person)
        assert unknown_name_result.is_unknown
        assert isinstance(unknown_name_result.type, CtyString)

    @pytest.mark.asyncio
    async def test_index_paths(self) -> None:
        """Test paths with index access."""
        numbers_type = CtyList(element_type=CtyNumber())
        numbers = numbers_type.validate([10, 20, 30, 40, 50])

        second_path = CtyPath.index(1)
        second_result = second_path.apply_path(numbers)
        assert isinstance(second_result, CtyValue)
        assert second_result.value == 20

        last_path = CtyPath.index(-1)
        last_result = last_path.apply_path(numbers)
        assert isinstance(last_result, CtyValue)
        assert last_result.value == 50

        out_of_bounds_path = CtyPath.index(10)
        with pytest.raises(AttributePathError, match="Index out of bounds"):
            out_of_bounds_path.apply_path(numbers)

        element_type = second_path.apply_path_type(numbers_type)
        assert isinstance(element_type, CtyNumber)

        tuple_type = CtyTuple(element_types=(CtyString(), CtyNumber(), CtyBool()))
        tuple_value = tuple_type.validate(("hello", 42, True))

        middle_path = CtyPath.index(1)
        middle_result = middle_path.apply_path(tuple_value)
        assert isinstance(middle_result, CtyValue)
        assert middle_result.value == 42

        middle_type = middle_path.apply_path_type(tuple_type)
        assert isinstance(middle_type, CtyNumber)

    @pytest.mark.asyncio
    async def test_key_paths(self) -> None:
        """Test paths with key access."""
        scores_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        raw_scores_data = {"Alice": 95, "Bob": 87}
        scores = scores_type.validate(raw_scores_data)

        bob_path = CtyPath.key("Bob")
        bob_result = bob_path.apply_path(scores)
        assert isinstance(bob_result, CtyValue)
        assert bob_result.value == 87

        invalid_path = CtyPath.key("Eve")
        with pytest.raises(AttributePathError, match="Map has no key 'Eve'"):
            invalid_path.apply_path(scores)

        value_type = bob_path.apply_path_type(scores_type)
        assert isinstance(value_type, CtyNumber)

    @pytest.mark.asyncio
    async def test_complex_paths(self) -> None:
        """Test complex paths with multiple step types."""
        user_type = CtyObject(
            attribute_types={
                "name": CtyString(),
                "scores": CtyMap(key_type=CtyString(), value_type=CtyNumber()),
            }
        )
        users_type = CtyList(element_type=user_type)
        raw_users_data = [
            {"name": "Alice", "scores": {"math": 95}},
            {"name": "Bob", "scores": {"math": 87}},
        ]
        users = users_type.validate(raw_users_data)

        path = CtyPath.index(1).child("scores").key_step("math")
        result = path.apply_path(users)
        assert isinstance(result, CtyValue)
        assert result.value == 87

        path_name = CtyPath.index(0).child("name")
        result_name = path_name.apply_path(users)
        assert isinstance(result_name, CtyValue)
        assert result_name.value == "Alice"

        name_type = path_name.apply_path_type(users_type)
        assert isinstance(name_type, CtyString)

    @pytest.mark.asyncio
    async def test_null_and_unknown_handling(self) -> None:
        """Test paths with null and unknown values."""
        person_type = CtyObject(
            attribute_types={"name": CtyString(), "age": CtyNumber()}
        )
        name_path = CtyPath.get_attr("name")

        null_person = CtyValue.null(person_type)
        with pytest.raises(
            AttributePathError, match="Cannot get attribute from null value"
        ):
            name_path.apply_path(null_person)

        unknown_person = CtyValue.unknown(person_type)
        name_result = name_path.apply_path(unknown_person)
        assert name_result.is_unknown
        assert isinstance(name_result.type, CtyString)

        address_type = CtyObject(attribute_types={"street": CtyString()})
        person_with_address_type = CtyObject(attribute_types={"address": address_type})

        person_with_null_address = person_with_address_type.validate(
            {"address": CtyValue.null(address_type)}
        )
        street_path = CtyPath.get_attr("address").child("street")
        with pytest.raises(
            AttributePathError,
            match=r"Error at step 2 \(\.street\): Cannot get attribute 'street' from object: Object validation error: Cannot get attribute from null value",
        ):
            street_path.apply_path(person_with_null_address)

        person_with_unknown_address = person_with_address_type.validate(
            {"address": CtyValue.unknown(address_type)}
        )
        street_result = street_path.apply_path(person_with_unknown_address)
        assert street_result.is_unknown
        assert isinstance(street_result.type, CtyString)

    @pytest.mark.asyncio
    async def test_path_string_representation(self) -> None:
        """Test string representation of paths."""
        empty_path = CtyPath.empty()
        assert str(empty_path) == "(empty path)"
        attr_path = CtyPath.get_attr("name")
        assert str(attr_path) == ".name"
        index_path = CtyPath.index(1)
        assert str(index_path) == "[1]"
        key_path = CtyPath.key("foo")
        assert str(key_path) == "['foo']"
        complex_path = CtyPath.index(0).child("scores").key_step("math")
        assert str(complex_path) == "[0].scores['math']"

    @pytest.mark.asyncio
    async def test_getattr_on_map_value(self) -> None:
        """Test GetAttrStep.apply on a CtyMap value."""
        map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        map_value_data = {"existing_key": 123}
        cty_map_value = map_type.validate(map_value_data)

        path_existing = CtyPath.get_attr("existing_key")
        result = path_existing.apply_path(cty_map_value)
        assert isinstance(result, CtyValue)
        assert isinstance(result.type, CtyNumber)
        assert result.value == 123

        path_non_existent = CtyPath.get_attr("non_existent_key")
        with pytest.raises(
            AttributePathError, match="Key 'non_existent_key' not found in map"
        ):
            path_non_existent.apply_path(cty_map_value)

        with pytest.raises(
            AttributePathError, match="Cannot get attribute from non-object type CtyMap"
        ):
            path_existing.apply_path_type(map_type)

    @pytest.mark.asyncio
    async def test_getattr_apply_type_errors(self) -> None:
        """Test error conditions for GetAttrStep.apply_type."""
        list_type = CtyList(element_type=CtyString())  # Corrected constructor
        path = CtyPath.get_attr("any_attr")
        with pytest.raises(
            AttributePathError,
            match="Cannot get attribute from non-object type CtyList",
        ):
            path.apply_path_type(list_type)

        obj_type = CtyObject(attribute_types={"name": CtyString()})
        path_missing_attr = CtyPath.get_attr("age")
        with pytest.raises(
            AttributePathError, match="Object type has no attribute age"
        ):
            path_missing_attr.apply_path_type(obj_type)

    @pytest.mark.asyncio
    async def test_index_step_apply_errors_and_unknown(self) -> None:
        """Test IndexStep.apply error conditions and unknown value handling."""
        null_list_value = CtyValue.null(CtyList(element_type=CtyString()))
        path_index = CtyPath.index(0)
        with pytest.raises(AttributePathError, match="Cannot index into null value"):
            path_index.apply_path(null_list_value)

        unknown_list_value = CtyValue.unknown(CtyList(element_type=CtyString()))
        result_unknown = path_index.apply_path(unknown_list_value)
        assert isinstance(result_unknown, CtyValue)
        assert result_unknown.is_unknown
        assert isinstance(result_unknown.type, CtyString)

        string_value = CtyString().validate("not a list")
        with pytest.raises(
            AttributePathError, match="Cannot index into value of type CtyString"
        ):
            path_index.apply_path(string_value)

    @pytest.mark.asyncio
    async def test_index_step_apply_type_errors(self) -> None:
        """Test error conditions for IndexStep.apply_type."""
        string_type = CtyString()
        path_index = CtyPath.index(0)
        with pytest.raises(
            AttributePathError, match="Cannot index into non-collection type CtyString"
        ):
            path_index.apply_path_type(string_type)

        tuple_type = CtyTuple(element_types=(CtyString(), CtyNumber()))
        path_oob_pos = CtyPath.index(2)
        with pytest.raises(AttributePathError, match="Tuple index 2 out of bounds"):
            path_oob_pos.apply_path_type(tuple_type)

        path_oob_neg = CtyPath.index(-3)
        with pytest.raises(AttributePathError, match="Tuple index -3 out of bounds"):
            path_oob_neg.apply_path_type(tuple_type)

        path_valid_neg = CtyPath.index(-1)
        result_type = path_valid_neg.apply_path_type(tuple_type)
        assert isinstance(result_type, CtyNumber)

    @pytest.mark.asyncio
    async def test_key_step_apply_errors_and_unknown(self) -> None:
        """Test KeyStep.apply error conditions and unknown value handling."""
        map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        unknown_map_value = CtyValue.unknown(map_type)
        path_key = CtyPath.key("some_key")
        result_unknown = path_key.apply_path(unknown_map_value)
        assert isinstance(result_unknown, CtyValue)
        assert result_unknown.is_unknown
        assert isinstance(result_unknown.type, CtyNumber)

        string_value = CtyString().validate("not a map")
        with pytest.raises(
            AttributePathError,
            match="Cannot get key from non-map value of type CtyString",
        ):
            path_key.apply_path(string_value)

        cty_map_value = map_type.validate({"a": 1})
        null_key_path = CtyPath.key(CtyValue.null(CtyString()))
        # Updated regex to match the actual error output which includes path step context
        with pytest.raises(
            AttributePathError,
            match=r"Error at step 1 \(\[CtyValue\(vtype=CtyString\(value=''\), is_null=True\)\]\): Invalid CtyValue key in path step: CtyValue\(vtype=CtyString\(value=''\), is_null=True\)",
        ):
            null_key_path.apply_path(cty_map_value)

        unknown_key_path = CtyPath.key(CtyValue.unknown(CtyString()))
        with pytest.raises(
            AttributePathError,
            match=r"Error at step 1 \(\[CtyValue\(vtype=CtyString\(value=''\), is_unknown=True\)\]\): Invalid CtyValue key in path step: CtyValue\(vtype=CtyString\(value=''\), is_unknown=True\)",
        ):
            unknown_key_path.apply_path(cty_map_value)

        number_key_path = CtyPath.key(CtyNumber().validate(123))
        with pytest.raises(
            AttributePathError,
            match=r"Error at step 1 \(\[CtyValue\(vtype=CtyNumber\(value=0\), value=Decimal\('123'\)\)\]\): Map has no key CtyValue\(vtype=CtyNumber\(value=0\), value=Decimal\('123'\)\)",
        ):
            number_key_path.apply_path(cty_map_value)

        list_key_path = CtyPath.key([])
        # str(KeyStep(key=[])) is "['[]']". The error message is f"Error at step 1 ({step}): {e}"
        with pytest.raises(
            AttributePathError,
            match=r"Error at step 1 \(\['\[\]'\]\): Unsupported key type in path step: .*",
        ):
            list_key_path.apply_path(cty_map_value)

    @pytest.mark.asyncio
    async def test_key_step_apply_type_errors(self) -> None:
        """Test error conditions for KeyStep.apply_type."""
        list_type = CtyList(element_type=CtyString())
        path_key = CtyPath.key("any_key")
        with pytest.raises(
            AttributePathError, match="Cannot get key from non-map type CtyList"
        ):
            path_key.apply_path_type(list_type)

        map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        invalid_cty_value_key_path = CtyPath.key(CtyNumber().validate(123))
        # Applying a CtyNumber key to a CtyString-keyed map should now succeed for apply_path_type
        # due to changes in KeyStep.apply_type and CtyNumber.usable_as
        resolved_type = invalid_cty_value_key_path.apply_path_type(map_type)
        assert isinstance(resolved_type, CtyNumber)

    @pytest.mark.asyncio
    async def test_cty_path_apply_errors(self) -> None:
        """Test error conditions for CtyPath.apply_path and CtyPath.apply_path_type."""
        path = CtyPath.get_attr("some_attr")
        raw_python_dict = {"some_attr": "some_value"}
        with pytest.raises(
            AttributePathError, match="Cannot apply path to non-CtyValue: dict"
        ):
            path.apply_path(raw_python_dict)

        obj_type = CtyObject(attribute_types={"name": CtyString()})
        failing_path = CtyPath.get_attr("non_existent_attr").child("another_attr")
        with pytest.raises(
            AttributePathError,
            match=r"Error at type step 1 \(.non_existent_attr\): Object type has no attribute non_existent_attr",
        ):
            failing_path.apply_path_type(obj_type)

        cty_obj_value = CtyObject(attribute_types={"name": CtyString()}).validate(
            {"name": "test"}
        )
        # Regex made more general for the wrapped error message
        with pytest.raises(
            AttributePathError,
            match=r"Error at step 1 \(.non_existent_attr\): Cannot get attribute 'non_existent_attr' from object.*",
        ):
            failing_path.apply_path(cty_obj_value)

    # Note: The duplicated tests previously present here were removed by S14T3.
    # The file now contains only one of each of the test_key_step and test_cty_path_apply_errors methods.
    # The version of test_key_step_apply_type_errors kept is the one with the more precise regex.
    # The version of test_cty_path_apply_errors kept is the one with the more general regex.

    @pytest.mark.asyncio
    async def test_getattrstep_apply_generic_exception(self) -> None:
        """Test GetAttrStep.apply raises AttributePathError on generic exception."""
        obj_type = CtyObject(attribute_types={"attr_name": CtyString()})
        cty_obj_value = obj_type.validate({"attr_name": "test_value"})

        step = GetAttrStep("attr_name")

        # Mock the 'type' attribute of the CtyValue instance to return a mock object
        # This mock object will have a 'get_attribute' method that we can control
        mock_type_for_value = MagicMock(spec=CtyObject)
        mock_type_for_value.get_attribute.side_effect = RuntimeError(
            "mocked runtime error"
        )
        # Set a descriptive name for the mock_type, in case error messages from the path system itself refer to it.
        # str(obj_type) gives a string like "object({attr_name: CtyString})"
        mock_type_for_value.name = str(obj_type)

        # Patch the 'type' property of the cty_obj_value instance.
        # CtyValue.type is a property, so we use PropertyMock.
        with patch.object(
            CtyValue,
            "type",
            PropertyMock(return_value=mock_type_for_value),
            create=True,
        ):
            # We need to ensure our specific instance cty_obj_value uses this mocked type property.
            # This can be tricky if the property is on the class and not easily overridden per instance by patch.object directly on instance.
            # A robust way is to ensure GetAttrStep.apply calls `cty_obj_value.type` and that call is what we intercept.
            # The current patch on CtyValue.type should affect all instances.
            # Let's ensure the instance cty_obj_value.type actually returns our mock.
            # This might require a different approach if this doesn't work,
            # perhaps by creating a CtyValue wrapper that allows easier mocking,
            # or by ensuring the instance `cty_obj_value` itself is a mock that returns mock_type_for_value for its `type`.

            # For this test, the simplest is to ensure that when step.apply(cty_obj_value) is called,
            # and it internally access cty_obj_value.type, it gets our mock_type_for_value.
            # The patch on CtyValue.type should achieve this for the duration of the context.

            # Re-create/re-validate the value *after* the class-level property mock is in place,
            # if CtyValue caches its .type at instantiation (it doesn't seem to).
            # Or, ensure the instance `cty_obj_value` is what `step.apply` works with.
            # The current `step.apply(cty_obj_value)` should pick up the mocked property.

            with pytest.raises(AttributePathError, match="mocked runtime error"):
                step.apply(cty_obj_value)

    @pytest.mark.asyncio
    async def test_keystep_apply_type_key_validation_failure(self) -> None:
        """Test KeyStep.apply_type raises AttributePathError on key validation failure."""
        mock_key_type = MagicMock(spec=CtyString)
        mock_key_type.validate.side_effect = CtyValidationError(
            "mocked key validation error"
        )
        # Provide a name attribute for the mock type, as it's used in error messages
        mock_key_type.name = "MockCtyString"
        # Provide a __repr__ for the mock_key_type for better error messages
        mock_key_type.__repr__ = lambda self: "<MockCtyString spec='CtyString'>"

        map_type = CtyMap(key_type=mock_key_type, value_type=CtyNumber())
        step = KeyStep("some_key")

        # Update the regex to match the actual error message format
        expected_error_regex = (
            r"Invalid key for map: 'some_key' is not a valid <MockCtyString spec='CtyString'> "
            r"\(validation error: mocked key validation error\)"
        )
        with pytest.raises(AttributePathError, match=expected_error_regex):
            step.apply_type(map_type)

    @pytest.mark.asyncio
    async def test_indexstep_apply_generic_exception(self) -> None:
        """Test IndexStep.apply raises AttributePathError on generic exception from element_at."""
        list_type = CtyList(element_type=CtyString())
        cty_list_value = list_type.validate(["a", "b"])

        step = IndexStep(0)

        mock_type_for_value = MagicMock(spec=CtyList)
        mock_type_for_value.element_at.side_effect = RuntimeError(
            "mocked runtime error for list index"
        )
        # Set a descriptive name for the mock_type
        mock_type_for_value.name = str(list_type)  # e.g., "list(string)"

        # Patch the 'type' property of the CtyValue instance.
        with patch.object(
            CtyValue,
            "type",
            PropertyMock(return_value=mock_type_for_value),
            create=True,
        ):
            with pytest.raises(
                AttributePathError, match="mocked runtime error for list index"
            ):
                step.apply(cty_list_value)

    @pytest.mark.asyncio
    async def test_keystep_apply_generic_exception_key_processing(self) -> None:
        """Test KeyStep.apply raises AttributePathError on generic exception during key processing."""
        map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        cty_map_value = map_type.validate({"a": 1, "b": 2})

        # Create a CtyValue whose inner 'value' is a mock.
        # This mock's __str__ method will first return a safe string (for logging)
        # and then raise a RuntimeError (for the actual key processing).
        mock_inner_key_value = MagicMock()
        mock_inner_key_value.__str__.side_effect = [
            "safe_key_for_logging",  # First call to str() (likely by logger)
            RuntimeError(
                "mocked runtime error for key processing"
            ),  # Second call (by str(self.key.value))
        ]
        # If repr is also called by the logger or error reporting, ensure it's safe too.
        mock_inner_key_value.__repr__ = lambda self: "<MockInnerKeyValue>"

        # Construct a CtyValue directly. vtype is CtyString as map keys are strings.
        problem_cty_key = CtyValue(vtype=CtyString(), value=mock_inner_key_value)

        step = KeyStep(problem_cty_key)

        # When step.apply is called:
        # 1. logger.debug(f"... {self.key} ...") might call str(problem_cty_key), which calls mock_inner_key_value.__str__() (returns "safe_key_for_logging").
        # 2. Inside the try-block, str(self.key.value) calls mock_inner_key_value.__str__() again (raises RuntimeError).
        # 3. This RuntimeError should be caught and wrapped in AttributePathError.
        with pytest.raises(
            AttributePathError, match="mocked runtime error for key processing"
        ):
            step.apply(cty_map_value)
