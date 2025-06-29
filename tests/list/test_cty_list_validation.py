import pytest
from pyvider.cty import CtyBool, CtyList, CtyNumber, CtyString, CtyValue, CtyDynamic
from pyvider.cty.exceptions import CtyListValidationError, CtyValidationError

class TestCtyListValidation:
    def test_string_representation(self):
        list_type = CtyList(element_type=CtyString())
        assert str(list_type) == "list(string)"
        nested_type = CtyList(element_type=CtyList(element_type=CtyNumber()))
        assert str(nested_type) == "list(list(number))"

    def test_post_init_validates_element_type(self):
        with pytest.raises(CtyListValidationError, match="Expected CtyType for element_type"):
            CtyList(element_type="not_a_cty_type")

    def test_validate_valid_inputs(self):
        string_list_type = CtyList(element_type=CtyString())
        list_val = string_list_type.validate(["a", "b"])
        assert [v.value for v in list_val.value] == ["a", "b"]
        tuple_val = string_list_type.validate(("c", "d"))
        assert [v.value for v in tuple_val.value] == ["c", "d"]
        cty_val = string_list_type.validate(list_val)
        assert cty_val == list_val

    def test_validate_invalid_inputs(self):
        string_list_type = CtyList(element_type=CtyString())
        with pytest.raises(CtyListValidationError, match="Input to CtyList.validate cannot be None"):
            string_list_type.validate(None)
        with pytest.raises(CtyListValidationError, match="Expected list, tuple, or CtyValue list, got dict"):
            string_list_type.validate({"a": 1})
        with pytest.raises(CtyListValidationError, match="Input CtyValue is not of a list type"):
            string_list_type.validate(CtyNumber().validate(123))

    def test_validate_with_element_errors(self):
        number_list_type = CtyList(element_type=CtyNumber())
        with pytest.raises(CtyListValidationError) as exc_info:
            number_list_type.validate([1, "two", 3])
        assert "Item 1" in str(exc_info.value)
        assert "Cannot convert string 'two' to number" in str(exc_info.value)

    def test_validate_incompatible_cty_list(self):
        string_list_type = CtyList(element_type=CtyString())
        number_list_value = CtyList(element_type=CtyNumber()).validate([1, 2])
        with pytest.raises(CtyListValidationError, match="incompatible list element type"):
            string_list_type.validate(number_list_value)

    def test_element_at_on_non_cty_value_list(self):
        list_type = CtyList(element_type=CtyString())
        with pytest.raises(CtyListValidationError, match="Expected CtyValue\\[CtyList\\]"):
            list_type.element_at(["a", "b"], 0)

    def test_element_at_on_null_value(self):
        list_type = CtyList(element_type=CtyString())
        null_val = CtyValue.null(list_type)
        with pytest.raises(IndexError, match="Cannot access element at index 0 in a null list"):
            list_type.element_at(null_val, 0)
