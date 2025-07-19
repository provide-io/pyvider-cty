import pytest
from pyvider.cty import CtyTuple, CtyString, CtyNumber, CtyBool, CtyList, CtyValue
from pyvider.cty.exceptions import CtyTupleValidationError, CtyValidationError

class TestCtyTupleValidation:
    def test_validate_with_ctyvalues_mismatched_type(self):
        schema = CtyTuple((CtyNumber(),))
        value = CtyString().validate("not a number")
        with pytest.raises(CtyValidationError):
            schema.validate(value)

    def test_validate_correct_input(self):
        schema = CtyTuple((CtyString(), CtyNumber()))
        value = ("hello", 123)
        result = schema.validate(value)
        assert result.raw_value == value

    def test_validate_incorrect_length_too_few(self):
        schema = CtyTuple((CtyString(), CtyNumber()))
        value = ("hello",)
        with pytest.raises(CtyTupleValidationError, match="Expected 2 elements, got 1"):
            schema.validate(value)

    def test_validate_element_type_mismatch_raw(self):
        schema = CtyTuple((CtyString(), CtyNumber()))
        value = ("hello", "world")
        with pytest.raises(CtyTupleValidationError, match="At \\[1\\]: Number validation error: Cannot represent str value 'world' as Decimal"):
            schema.validate(value)

    def test_validate_element_type_mismatch_ctyvalue(self):
        schema = CtyTuple((CtyString(), CtyNumber()))
        value = (CtyString().validate("hello"), CtyString().validate("world"))
        with pytest.raises(CtyTupleValidationError):
            schema.validate(value)

    def test_nested_validate_inner_type_mismatch(self):
        nested_tuple_type = CtyTuple((CtyString(), CtyTuple((CtyNumber(), CtyBool()))))
        data = ("outer", (123, "not-a-bool"))
        with pytest.raises(CtyTupleValidationError, match="At \\[1\\]\\[1\\]: Boolean validation error: Cannot convert str to bool."):
            nested_tuple_type.validate(data)

    def test_element_at_invalid_index_type(self):
        schema = CtyTuple((CtyString(),))
        with pytest.raises(TypeError):
            schema.element_at(schema.validate(("hello",)), "a")
