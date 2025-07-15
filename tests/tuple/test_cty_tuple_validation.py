import pytest
from decimal import Decimal
from pyvider.cty import (
    CtyBool, CtyNumber, CtyString, CtyList, CtyTuple, CtyValue, CtyDynamic
)
from pyvider.cty.exceptions import CtyValidationError, CtyTupleValidationError

class TestCtyTupleValidation:
    @pytest.fixture
    def tuple_type_sn(self):
        return CtyTuple(element_types=(CtyString(), CtyNumber()))

    @pytest.fixture
    def cty_tuple_val(self, tuple_type_sn):
        return tuple_type_sn.validate(("text", 123))
        
    @pytest.fixture
    def nested_tuple_type(self):
        inner_tuple = CtyTuple(element_types=(CtyNumber(), CtyBool()))
        return CtyTuple(element_types=(CtyString(), inner_tuple))

    def test_validate_with_ctyvalues_mismatched_type(self, tuple_type_sn) -> None:
        val1 = CtyString().validate("cty")
        val2_convertible = CtyBool().validate(True)
        data = (val1, val2_convertible)
        validated_tuple = tuple_type_sn.validate(data)
        assert isinstance(validated_tuple, CtyValue)
        assert isinstance(validated_tuple.type, CtyTuple)
        element1, element2 = validated_tuple.value
        assert element1.type.equal(CtyString()) and element1.value == "cty"
        assert element2.type.equal(CtyNumber()) and element2.value == Decimal("1")

    def test_validate_correct_input(self, tuple_type_sn):
        data = ("hello", 123)
        validated_tuple = tuple_type_sn.validate(data)
        assert validated_tuple.value[0].value == "hello"
        assert validated_tuple.value[1].value == Decimal("123")

    def test_validate_incorrect_length_too_few(self, tuple_type_sn):
        with pytest.raises(CtyTupleValidationError, match="Expected 2 elements, got 1"):
            tuple_type_sn.validate(("hello",))

    def test_validate_element_type_mismatch_raw(self, tuple_type_sn):
        with pytest.raises(CtyTupleValidationError, match="Cannot represent str value 'not-a-number'"):
            tuple_type_sn.validate(("hello", "not-a-number"))

    def test_validate_element_type_mismatch_ctyvalue(self, tuple_type_sn):
        data = (CtyString().validate("hello"), CtyString().validate("not-a-number"))
        with pytest.raises(CtyTupleValidationError, match="Cannot represent str value 'not-a-number'"):
            tuple_type_sn.validate(data)

    def test_nested_validate_inner_type_mismatch(self, nested_tuple_type):
        data = ("outer", (123, "not-a-bool"))
        with pytest.raises(CtyTupleValidationError, match="Cannot convert string 'not-a-bool' to boolean"):
            nested_tuple_type.validate(data)

    def test_element_at_invalid_index_type(self, tuple_type_sn, cty_tuple_val):
        with pytest.raises(TypeError, match="Tuple indices must be integers or slices, not str"):
            tuple_type_sn.element_at(cty_tuple_val, "zero")
