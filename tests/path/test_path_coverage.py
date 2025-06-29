import pytest
from decimal import Decimal
from unittest.mock import patch

from pyvider.cty import (
    CtyBool, CtyDynamic, CtyList, CtyMap, CtyNumber, CtyObject, CtyString, CtyTuple, CtyValue
)
from pyvider.cty.types import CtyType
from pyvider.cty.path import CtyPath, GetAttrStep, IndexStep, KeyStep
from pyvider.cty.path.base import PathStep
from pyvider.cty.exceptions import AttributePathError, CtyTypeMismatchError, CtyValidationError

class TestPathCoverage:
    """Targeted tests to improve coverage for pyvider.cty.path."""

    def test_getattrstep_apply_on_invalid_type(self):
        step = GetAttrStep("name")
        value = CtyString().validate("not an object")
        with pytest.raises(AttributePathError, match="Cannot get attribute from non-object value"):
            step.apply(value)

    def test_indexstep_apply_on_invalid_type(self):
        step = IndexStep(0)
        value = CtyString().validate("not a list")
        with pytest.raises(AttributePathError, match="Cannot index into value of type CtyString"):
            step.apply(value)

    def test_keystep_apply_on_invalid_type(self):
        step = KeyStep("key")
        value = CtyList(element_type=CtyString()).validate([])
        with pytest.raises(AttributePathError, match="Cannot get key from non-map/non-dynamic value"):
            step.apply(value)

    def test_keystep_apply_on_dynamic_non_dict(self):
        step = KeyStep("key")
        value = CtyDynamic().validate("i am a string")
        with pytest.raises(AttributePathError, match="Cannot get key from CtyDynamic whose internal value is not a dictionary"):
            step.apply(value)
            
    def test_keystep_apply_type_with_invalid_key(self):
        map_type = CtyMap(key_type=CtyNumber(), value_type=CtyString())
        step = KeyStep("not-a-number")
        with pytest.raises(AttributePathError, match="Invalid key for map: 'not-a-number' is not a valid number"):
            step.apply_type(map_type)

    def test_path_apply_path_on_non_ctyvalue(self):
        path = CtyPath.get_attr("name")
        with pytest.raises(AttributePathError, match="Cannot apply path to non-CtyValue"):
            path.apply_path({"name": "test"})

    def test_getattrstep_apply_map_key_not_found(self):
        step = GetAttrStep("missing_key")
        map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
        map_value = map_type.validate({"existing_key": "value"})
        with pytest.raises(AttributePathError, match="Key 'missing_key' not found in map"):
            step.apply(map_value)

    def test_getattrstep_apply_type_non_object(self):
        step = GetAttrStep("name")
        non_obj_type = CtyString()
        with pytest.raises(AttributePathError, match="Cannot get attribute from non-object type CtyString"):
            step.apply_type(non_obj_type)

    def test_indexstep_apply_on_null_collection(self):
        step = IndexStep(0)
        null_list_val = CtyValue.null(CtyList(element_type=CtyString()))
        null_tuple_val = CtyValue.null(CtyTuple(element_types=(CtyString(),)))
        with pytest.raises(AttributePathError, match="Cannot index into null value"):
            step.apply(null_list_val)
        with pytest.raises(AttributePathError, match="Cannot index into null value"):
            step.apply(null_tuple_val)

    def test_indexstep_apply_on_unknown_collection(self):
        step = IndexStep(0)
        list_type = CtyList(element_type=CtyString())
        unknown_list_val = CtyValue.unknown(list_type)
        result = step.apply(unknown_list_val)
        assert result.is_unknown
        assert result.type.equal(CtyString())

        tuple_type = CtyTuple(element_types=(CtyNumber(), CtyBool()))
        unknown_tuple_val = CtyValue.unknown(tuple_type)
        result_tuple = step.apply(unknown_tuple_val)
        assert result_tuple.is_unknown
        assert result_tuple.type.equal(CtyNumber())

    def test_indexstep_apply_type_non_collection(self):
        step = IndexStep(0)
        non_coll_type = CtyString()
        with pytest.raises(AttributePathError, match="Cannot index into non-collection type CtyString"):
            step.apply_type(non_coll_type)

    def test_keystep_apply_on_null_map(self):
        step = KeyStep("some_key")
        null_map_val = CtyValue.null(CtyMap(key_type=CtyString(), value_type=CtyString()))
        with pytest.raises(AttributePathError, match="Cannot get key from null value"):
            step.apply(null_map_val)

    def test_keystep_apply_on_unknown_map(self):
        step = KeyStep("any_key")
        map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        unknown_map_val = CtyValue.unknown(map_type)
        result = step.apply(unknown_map_val)
        assert result.is_unknown
        assert result.type.equal(CtyNumber())

    def test_keystep_apply_type_non_map_or_dynamic(self):
        step = KeyStep("key")
        non_map_type = CtyString()
        with pytest.raises(AttributePathError, match="Cannot get key from non-map type CtyString"):
            step.apply_type(non_map_type)

    def test_keystep_apply_on_dynamic_null_map(self):
        step = KeyStep("key")
        inner_null_map = CtyValue.null(CtyMap(key_type=CtyString(), value_type=CtyString()))
        dynamic_null_map = CtyDynamic().validate(inner_null_map)
        with pytest.raises(AttributePathError, match=r"Cannot get key from CtyDynamic whose internal value is not a dictionary \(got NoneType\)\."):
            step.apply(dynamic_null_map)

    def test_getattrstep_apply_on_dynamic_object(self):
        step = GetAttrStep("name")
        obj_data = {"name": "tester", "age": 30}
        dynamic_obj_val = CtyDynamic().validate(obj_data)
        result = step.apply(dynamic_obj_val)
        assert not result.is_unknown and not result.is_null
        assert result.type.equal(CtyDynamic())
        assert result.value.type.equal(CtyString())
        assert result.value.value == "tester"

    def test_indexstep_apply_on_dynamic_list(self):
        step = IndexStep(0)
        list_data = ["first", "second"]
        dynamic_list_val = CtyDynamic().validate(list_data)
        result = step.apply(dynamic_list_val)
        assert not result.is_unknown and not result.is_null
        assert result.type.equal(CtyDynamic())
        assert result.value.type.equal(CtyString())
        assert result.value.value == "first"

    def test_getattrstep_name_validation(self):
        with pytest.raises(ValueError, match="Attribute name cannot be empty"):
            GetAttrStep("")

    def test_keystep_apply_dynamic_key_ctyvalue_non_str_num(self):
        step = KeyStep(CtyBool().validate(True))
        dynamic_dict_val = CtyDynamic().validate({"True": "found"})
        with pytest.raises(AttributePathError, match="Unsupported CtyValue key type for raw dictionary lookup: bool"): # Corrected CtyBool to bool
            step.apply(dynamic_dict_val)

    def test_keystep_apply_map_key_validation_failure(self):
        map_type = CtyMap(key_type=CtyNumber(), value_type=CtyString())
        map_value = map_type.validate({1: "one"})
        step_invalid_key = KeyStep("not-a-number")
        with pytest.raises(AttributePathError, match="Failed to get value for key 'not-a-number' from map: Number validation error: Cannot convert string 'not-a-number' to number"):
            step_invalid_key.apply(map_value)
        step_invalid_cty_key = KeyStep(CtyString().validate("alsonotanumber"))
        with pytest.raises(AttributePathError, match="Failed to get value for key .* Number validation error: Cannot convert string 'alsonotanumber' to number"):
            step_invalid_cty_key.apply(map_value)

    def test_apply_type_keystep_unexpected_key_validation_error(self):
        map_type = CtyMap(key_type=CtyNumber(), value_type=CtyString())
        class MockFailingValidatorType(CtyType):
            def validate(self, value): raise ValueError("Mock internal validation error")
            def is_empty_type(self): return False
            def equal(self, other): return isinstance(other, MockFailingValidatorType)
            def usable_as(self, other): return False
        map_type_bad_key = CtyMap(key_type=MockFailingValidatorType(), value_type=CtyString())
        step = KeyStep("somekey")
        with pytest.raises(AttributePathError, match="Unexpected error validating key"):
            step.apply_type(map_type_bad_key)

    @patch.object(CtyMap, 'get', side_effect=RuntimeError("Unexpected map access failure mock"))
    def test_getattrstep_apply_map_unexpected_error(self, mock_map_get):
        # Note: GetAttrStep delegates to CtyObject.get_attribute or CtyMap.get
        # This test specifically mocks CtyMap.get to simulate an unexpected error there.
        step = GetAttrStep("key")
        map_value = CtyMap(key_type=CtyString(), value_type=CtyString()).validate({"key": "value"})
        with pytest.raises(AttributePathError, match="Unexpected error getting key 'key' from map: Unexpected map access failure mock"):
            step.apply(map_value)


    @patch.object(CtyList, 'element_at', side_effect=RuntimeError("Unexpected list access failure mock"))
    def test_indexstep_apply_unexpected_error(self, mock_list_element_at):
        step = IndexStep(0)
        list_value = CtyList(element_type=CtyString()).validate(["a"])
        with pytest.raises(AttributePathError, match="Failed to get element at index 0: Unexpected list access failure mock"):
            step.apply(list_value)

    def test_path_apply_path_type_unexpected_error(self):
        class MockFailingStep(PathStep):
            def apply(self, value): raise NotImplementedError
            def apply_type(self, vtype): raise RuntimeError("Mock type application failure")
            def __str__(self): return "MockFailingStep"
        path = CtyPath([MockFailingStep()])
        with pytest.raises(AttributePathError, match="Error at type step 1 .*Mock type application failure"):
            path.apply_path_type(CtyString())

    def test_path_apply_path_unexpected_error(self):
        class MockFailingStep(PathStep):
            def apply(self, value): raise RuntimeError("Mock value application failure")
            def apply_type(self, vtype): raise NotImplementedError
            def __str__(self): return "MockFailingStep"
        path = CtyPath([MockFailingStep()])
        with pytest.raises(AttributePathError, match="Error at step 1 .*Mock value application failure"):
            path.apply_path(CtyString().validate("test"))

    def test_get_attr_step_apply_map_key_is_cty_value_valid(self):
        step = GetAttrStep("123")
        map_type = CtyMap(key_type=CtyNumber(), value_type=CtyString())
        map_value = map_type.validate({Decimal('123'): "found"})
        result = step.apply(map_value)
        assert result.value == "found"

    def test_get_attr_step_apply_map_key_is_cty_value_not_found(self):
        step = GetAttrStep("456")
        map_type = CtyMap(key_type=CtyNumber(), value_type=CtyString())
        map_value = map_type.validate({Decimal('123'): "found"})
        with pytest.raises(AttributePathError, match="Key '456' not found in map"):
            step.apply(map_value)

    def test_getattr_missing_attribute_on_object(self):
        path = CtyPath([GetAttrStep("nonexistent")])
        cty_obj_simple = CtyObject({"name": CtyString(), "age": CtyNumber()}).validate({"name": "Alice", "age": 30})
        with pytest.raises(AttributePathError, match="Object has no attribute named \"nonexistent\""):
            path.apply_path(cty_obj_simple)

    def test_keystep_apply_type_dynamic(self):
        step = KeyStep("anyKey")
        assert step.apply_type(CtyDynamic()).equal(CtyDynamic())

    # --- SplatStep Error Coverage ---
    def test_splatstep_then_getattr_on_list_of_non_objects(self):
        list_of_strings = CtyList(CtyString()).validate(["foo", "bar"])
        path = CtyPath([SplatStep(), GetAttrStep("length")]) # "length" is not an attr of string
        with pytest.raises(AttributePathError, match="Cannot access attribute \"length\" on value of type string"):
            path.apply_path(list_of_strings)

    def test_splatstep_then_index_on_list_of_non_collections(self):
        list_of_numbers = CtyList(CtyNumber()).validate([1,2,3])
        path = CtyPath([SplatStep(), IndexStep(0)])
        with pytest.raises(AttributePathError, match="Cannot index into value of type CtyNumber"):
            path.apply_path(list_of_numbers)

    def test_splatstep_on_non_iterable_type(self):
        path = CtyPath([SplatStep(), GetAttrStep("foo")])
        cty_obj_simple = CtyObject({"name": CtyString()}).validate({"name":"test"})
        cty_map_str_to_num = CtyMap(CtyString(), CtyNumber()).validate({"a": 1})

        with pytest.raises(AttributePathError, match="Splat operator \\[\r?\n?\*\r?\n?\\] requires list, tuple, or set; got object"):
            path.apply_path(cty_obj_simple)

        # For map, SplatStep.apply_type returns list(DynamicPseudoType)
        # The error will occur when GetAttrStep tries to operate on the elements if they don't have "foo"
        # If map values are strings, for example:
        map_of_strings = CtyMap(CtyString(), CtyString()).validate({"a": "apple", "b": "banana"})
        with pytest.raises(AttributePathError, match="Cannot access attribute \"foo\" on value of type string"):
             path.apply_path(map_of_strings)


    def test_splatstep_apply_type_on_non_iterable(self):
        step = SplatStep()
        with pytest.raises(AttributePathError, match="Splat operator \\[\r?\n?\*\r?\n?\\] can only be applied to list, tuple, or set types, not object"):
            step.apply_type(CtyObject({"a": CtyString()}))
        with pytest.raises(AttributePathError, match="Splat operator \\[\r?\n?\*\r?\n?\\] can only be applied to list, tuple, or set types, not map"):
            step.apply_type(CtyMap(CtyString(),CtyString()))
        with pytest.raises(AttributePathError, match="Splat operator \\[\r?\n?\*\r?\n?\\] can only be applied to list, tuple, or set types, not string"):
            step.apply_type(CtyString())
