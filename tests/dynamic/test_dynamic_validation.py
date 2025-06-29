# pyvider-cty/tests/dynamic/test_dynamic_validation.py
import pytest
from decimal import Decimal

from pyvider.cty.types.primitives import CtyString, CtyNumber, CtyBool
from pyvider.cty.types.collections import CtyList, CtyMap, CtySet
from pyvider.cty.types.structural import CtyTuple, CtyDynamic
from pyvider.cty.values import CtyValue
from pyvider.cty.exceptions import CtyValidationError

# Helper to get the dynamic type instance
dynamic_type = CtyDynamic()

class TestCtyDynamicValidation:
    def test_validate_none(self):
        val = dynamic_type.validate(None)
        assert val.is_null  # Changed from val.is_null()
        assert val.type == dynamic_type

    def test_validate_simple_primitives(self):
        # String
        py_val_str = "hello"
        cty_val_str = dynamic_type.validate(py_val_str)
        assert cty_val_str.type == dynamic_type
        assert isinstance(cty_val_str.value, CtyValue), "Inner value should be a CtyValue"
        assert cty_val_str.value.type == CtyString()
        assert cty_val_str.value.value == py_val_str

        # Number
        py_val_num = Decimal("123.45")
        cty_val_num = dynamic_type.validate(py_val_num)
        assert cty_val_num.type == dynamic_type
        assert isinstance(cty_val_num.value, CtyValue)
        assert cty_val_num.value.type == CtyNumber()
        assert cty_val_num.value.value == py_val_num

        # Bool
        py_val_bool = True
        cty_val_bool = dynamic_type.validate(py_val_bool)
        assert cty_val_bool.type == dynamic_type
        assert isinstance(cty_val_bool.value, CtyValue)
        assert cty_val_bool.value.type == CtyBool()
        assert cty_val_bool.value.value == py_val_bool

    def test_validate_already_cty_value_concrete(self):
        concrete_val = CtyString().validate("test")
        cty_val = dynamic_type.validate(concrete_val)
        assert cty_val.type == dynamic_type
        assert cty_val.value is concrete_val, "Should wrap the exact same CtyValue instance"

    def test_validate_already_cty_value_dynamic_wrapping_concrete(self):
        inner_concrete = CtyString().validate("inner")
        existing_dynamic = CtyValue(dynamic_type, inner_concrete)

        cty_val = dynamic_type.validate(existing_dynamic)
        assert cty_val is existing_dynamic, "Should return the same dynamic CtyValue if correctly structured"
        assert cty_val.type == dynamic_type
        assert cty_val.value is inner_concrete

    def test_validate_already_cty_value_dynamic_wrapping_raw(self):
        # This tests the backward compatibility case where a CtyDynamic might wrap a raw Python value
        # This case should now re-process the inner raw value.
        raw_inner_py = {"key": "old_raw_value"}
        old_style_dynamic_val = CtyValue(dynamic_type, raw_inner_py) # Manually create old style

        cty_val = dynamic_type.validate(old_style_dynamic_val)
        assert cty_val.type == dynamic_type
        assert isinstance(cty_val.value, CtyValue), "Inner value of reprocessed dynamic should be CtyValue"

        inner_wrapped_val = cty_val.value
        assert inner_wrapped_val.type == CtyMap(CtyString(), CtyString()) # Inferred type
        assert inner_wrapped_val.value["key"].value == "old_raw_value"


    def test_validate_list_homogeneous(self):
        py_list = [1, 2, 3]
        cty_val = dynamic_type.validate(py_list)
        assert cty_val.type == dynamic_type
        assert isinstance(cty_val.value, CtyValue)

        inner_list_val = cty_val.value
        assert inner_list_val.type == CtyList(CtyNumber())
        assert len(inner_list_val.value) == 3
        assert inner_list_val.value[0].value == Decimal("1")

    def test_validate_list_mixed_becomes_list_dynamic(self):
        # Current behavior without full unification: mixed lists become list(dynamic)
        py_list = [1, "hello", True]
        cty_val = dynamic_type.validate(py_list)
        assert cty_val.type == dynamic_type
        assert isinstance(cty_val.value, CtyValue)

        inner_list_val = cty_val.value
        assert inner_list_val.type == CtyList(element_type=CtyDynamic()) # Corrected
        assert len(inner_list_val.value) == 3
        assert inner_list_val.value[0].type == CtyDynamic()
        assert inner_list_val.value[0].value.type == CtyNumber() # Inner value of the dynamic element
        assert inner_list_val.value[0].value.value == Decimal("1")
        assert inner_list_val.value[1].value.type == CtyString()
        assert inner_list_val.value[1].value.value == "hello"

    def test_validate_list_empty(self):
        py_list = []
        cty_val = dynamic_type.validate(py_list)
        assert cty_val.type == dynamic_type
        assert isinstance(cty_val.value, CtyValue)
        assert cty_val.value.type == CtyList(element_type=CtyDynamic()) # Already correct
        assert len(cty_val.value.value) == 0

    def test_validate_map_homogeneous_values(self):
        py_map = {"a": 10, "b": 20}
        cty_val = dynamic_type.validate(py_map)
        assert cty_val.type == dynamic_type
        assert isinstance(cty_val.value, CtyValue)

        inner_map_val = cty_val.value
        assert inner_map_val.type == CtyMap(key_type=CtyString(), value_type=CtyNumber()) # Already correct
        assert inner_map_val.value["a"].value == Decimal("10")

    def test_validate_map_mixed_values_becomes_map_dynamic_values(self):
        py_map = {"name": "Jules", "age": 30, "verified": True}
        cty_val = dynamic_type.validate(py_map)
        assert cty_val.type == dynamic_type
        assert isinstance(cty_val.value, CtyValue)

        inner_map_val = cty_val.value
        assert inner_map_val.type == CtyMap(key_type=CtyString(), value_type=CtyDynamic()) # Already correct
        assert inner_map_val.value["name"].value.type == CtyString()
        assert inner_map_val.value["name"].value.value == "Jules"
        assert inner_map_val.value["age"].value.type == CtyNumber()

    def test_validate_map_empty(self):
        py_map = {}
        cty_val = dynamic_type.validate(py_map)
        assert cty_val.type == dynamic_type
        assert isinstance(cty_val.value, CtyValue)
        assert cty_val.value.type == CtyMap(key_type=CtyString(), value_type=CtyDynamic()) # Already correct
        assert len(cty_val.value.value) == 0

    def test_validate_map_non_string_keys_fail(self):
        py_map = {123: "value"}
        with pytest.raises(CtyValidationError, match="Map keys must be strings"):
            dynamic_type.validate(py_map)

    def test_validate_set_homogeneous(self):
        py_set = {"a", "b", "c"}
        cty_val = dynamic_type.validate(py_set)
        assert cty_val.type == dynamic_type
        assert isinstance(cty_val.value, CtyValue)

        inner_set_val = cty_val.value
        assert inner_set_val.type.equal(CtySet(element_type=CtyString())) # Use .equal and ensure kwarg
        # Order is not guaranteed, so check existence and types
        assert len(inner_set_val.value) == 3
        str_vals = {v.value for v in inner_set_val.value}
        assert str_vals == {"a", "b", "c"}

    def test_validate_set_mixed_becomes_set_dynamic(self):
        py_set = {1, "hello"}
        cty_val = dynamic_type.validate(py_set)
        assert cty_val.type == dynamic_type
        assert isinstance(cty_val.value, CtyValue)

        inner_set_val = cty_val.value
        assert inner_set_val.type.equal(CtySet(element_type=CtyDynamic())) # Corrected
        assert len(inner_set_val.value) == 2
        # Check that elements are dynamic and wrap correct concrete types
        dynamic_elements = list(inner_set_val.value)
        types_of_wrapped_values = {elem.value.type for elem in dynamic_elements}
        assert CtyNumber() in types_of_wrapped_values
        assert CtyString() in types_of_wrapped_values


    def test_validate_set_empty(self):
        py_set = set()
        cty_val = dynamic_type.validate(py_set)
        assert cty_val.type == dynamic_type
        assert isinstance(cty_val.value, CtyValue)
        assert cty_val.value.type.equal(CtySet(element_type=CtyDynamic())) # Corrected
        assert len(cty_val.value.value) == 0

    def test_validate_tuple_homogeneous(self):
        py_tuple = (True, False, True)
        cty_val = dynamic_type.validate(py_tuple)
        assert cty_val.type == dynamic_type
        assert isinstance(cty_val.value, CtyValue)

        inner_tuple_val = cty_val.value
        assert inner_tuple_val.type.equal(CtyTuple(element_types=(CtyBool(), CtyBool(), CtyBool()))) # Corrected
        assert inner_tuple_val.value[0].value is True

    def test_validate_tuple_heterogeneous(self):
        py_tuple = ("name", 42)
        cty_val = dynamic_type.validate(py_tuple)
        assert cty_val.type == dynamic_type
        assert isinstance(cty_val.value, CtyValue)

        inner_tuple_val = cty_val.value
        assert inner_tuple_val.type.equal(CtyTuple(element_types=(CtyString(), CtyNumber()))) # Corrected
        assert inner_tuple_val.value[0].value == "name"
        assert inner_tuple_val.value[1].value == Decimal("42")

    def test_validate_tuple_empty(self):
        py_tuple = tuple()
        cty_val = dynamic_type.validate(py_tuple)
        assert cty_val.type == dynamic_type
        assert isinstance(cty_val.value, CtyValue)
        assert cty_val.value.type.equal(CtyTuple(element_types=tuple())) # Corrected
        assert len(cty_val.value.value) == 0

    def test_validate_nested_structure(self):
        py_nested = {
            "id": "item1",
            "data": [
                {"point": 1, "tags": ("a", "b")},
                {"point": 2, "tags": ("c", "d", "e")},
            ],
            "active": True
        }
        cty_val = dynamic_type.validate(py_nested)
        assert cty_val.type == dynamic_type
        assert isinstance(cty_val.value, CtyValue) # Outer dynamic wraps a concrete CtyValue

        # Check inferred type of the wrapped CtyValue
        # map(string, dynamic) because 'id' is string, 'data' is list, 'active' is bool
        inferred_map = cty_val.value
        assert inferred_map.type.equal(CtyMap(key_type=CtyString(), value_type=CtyDynamic())) # Corrected

        # Check 'id'
        id_val_dyn = inferred_map.value["id"]
        assert id_val_dyn.type == CtyDynamic()
        assert id_val_dyn.value.type.equal(CtyString()) # Corrected
        assert id_val_dyn.value.value == "item1"

        # Check 'active'
        active_val_dyn = inferred_map.value["active"]
        assert active_val_dyn.type == CtyDynamic()
        assert active_val_dyn.value.type.equal(CtyBool()) # Corrected
        assert active_val_dyn.value.value is True

        # Check 'data' list
        data_list_dyn = inferred_map.value["data"]
        assert data_list_dyn.type == CtyDynamic()
        assert data_list_dyn.value.type.equal(CtyList(element_type=CtyDynamic())) # Corrected (List of dynamic maps)

        list_elements = data_list_dyn.value.value
        assert len(list_elements) == 2

        # Check first element of 'data' list
        first_elem_dyn = list_elements[0]
        assert first_elem_dyn.type == CtyDynamic()
        first_elem_map = first_elem_dyn.value # This is map(string, dynamic)
        assert first_elem_map.type.equal(CtyMap(key_type=CtyString(), value_type=CtyDynamic())) # Corrected

        point1_dyn = first_elem_map.value["point"]
        assert point1_dyn.type == CtyDynamic()
        assert point1_dyn.value.type.equal(CtyNumber()) # Corrected
        assert point1_dyn.value.value == Decimal("1")

        tags1_dyn = first_elem_map.value["tags"]
        assert tags1_dyn.type == CtyDynamic()
        assert tags1_dyn.value.type.equal(CtyTuple(element_types=(CtyString(), CtyString()))) # Corrected
        assert tags1_dyn.value.value[0].value == "a"

    def test_unsupported_type_raises_error(self):
        class SomeCustomClass:
            pass

        with pytest.raises(CtyValidationError, match="Cannot infer a concrete CtyType for raw Python type: SomeCustomClass"):
            dynamic_type.validate(SomeCustomClass())

    def test_dynamic_value_wrapping_cty_dynamic_value(self):
        # CtyValue(Dynamic, CtyValue(Dynamic, CtyString("hello")))
        # This should just return the outer one if it's correctly structured
        inner_str = CtyString().validate("hello")
        inner_dyn = CtyValue(dynamic_type, inner_str) # CtyValue(Dynamic, CtyString("hello"))
        outer_dyn = CtyValue(dynamic_type, inner_dyn)  # CtyValue(Dynamic, CtyValue(Dynamic, CtyString("hello")))

        validated_outer = dynamic_type.validate(outer_dyn)
        assert validated_outer is outer_dyn
        assert validated_outer.value is inner_dyn
        assert validated_outer.value.value is inner_str

    def test_is_dynamic_type_method(self):
        assert dynamic_type.is_dynamic_type()
        assert not CtyString().is_dynamic_type()
        assert not CtyList(element_type=CtyNumber()).is_dynamic_type() # Corrected

    def test_validate_list_of_lists(self):
        py_list = [[1,2], [3,4]]
        cty_val = dynamic_type.validate(py_list)
        assert cty_val.type == dynamic_type
        inner_list_val = cty_val.value
        assert isinstance(inner_list_val, CtyValue)
        assert inner_list_val.type.equal(CtyList(element_type=CtyList(element_type=CtyNumber()))) # Corrected
        assert inner_list_val.value[0].value[0].value == Decimal("1")

    def test_validate_list_of_mixed_lists_becomes_list_of_list_dynamic(self):
        py_list = [[1,2], ["a", "b"]] # list(list(number)) and list(list(string))
        cty_val = dynamic_type.validate(py_list)
        assert cty_val.type == dynamic_type
        inner_list_val = cty_val.value # This is a CtyValue(CtyList(CtyDynamic()), ...)
        assert isinstance(inner_list_val, CtyValue)
        assert inner_list_val.type.equal(CtyList(element_type=CtyDynamic())) # Corrected (Because inner lists are of different concrete types)

        # Check first inner list (dynamic wrapping list(number))
        first_inner_dyn = inner_list_val.value[0]
        assert first_inner_dyn.type == CtyDynamic()
        assert first_inner_dyn.value.type.equal(CtyList(element_type=CtyNumber())) # Corrected
        assert first_inner_dyn.value.value[0].value == Decimal("1")

        # Check second inner list (dynamic wrapping list(string))
        second_inner_dyn = inner_list_val.value[1]
        assert second_inner_dyn.type == CtyDynamic()
        assert second_inner_dyn.value.type.equal(CtyList(element_type=CtyString())) # Corrected
        assert second_inner_dyn.value.value[0].value == "a"

    def test_validate_marks_are_preserved_on_reprocessing(self):
        raw_inner_py = {"key": "old_raw_value"}
        marks_to_apply = {"source": "test"}
        # Manually create an old-style CtyDynamic value with marks
        old_style_dynamic_val = CtyValue(dynamic_type, raw_inner_py, _marks=frozenset(marks_to_apply.items())) # Use _marks and frozenset

        cty_val = dynamic_type.validate(old_style_dynamic_val)
        assert cty_val.type == dynamic_type
        # Access internal _marks for assertion, or use has_mark if appropriate
        assert cty_val._marks == frozenset(marks_to_apply.items())
        assert isinstance(cty_val.value, CtyValue) # Inner value should be CtyValue

        inner_wrapped_val = cty_val.value
        assert inner_wrapped_val.type == CtyMap(CtyString(), CtyString())
        # The marks should be on the outer dynamic value, not propagated to the newly inferred inner one by default.
        assert not inner_wrapped_val._marks # Check internal _marks
