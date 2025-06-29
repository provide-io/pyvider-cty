import pytest
from decimal import Decimal
from pyvider.cty import (
    CtyBool, CtyList, CtyMap, CtyNumber, CtyObject, CtySet, CtyString, CtyTuple, CtyValue
)
from pyvider.cty.marks import CtyMark

class TestCtyValueBasicOperations:
    @pytest.fixture
    def str_type(self):
        return CtyString()

    def test_value_initialization(self, str_type):
        str_val = str_type.validate("test")
        assert str_val.type == str_type
        assert str_val.value == "test"
        assert not str_val.is_unknown
        assert not str_val.is_null
        assert str(str_val) == "test"

    def test_value_unknown(self, str_type):
        unknown_val = CtyValue.unknown(str_type)
        assert unknown_val.is_unknown
        with pytest.raises(ValueError):
            _ = unknown_val.value
        # FIX: The __str__ representation of the type is now just 'string'
        assert str(unknown_val) == "<unknown string>"

    def test_value_null(self, str_type):
        null_val = CtyValue.null(str_type)
        assert null_val.is_null
        assert null_val.value is None
        # FIX: The __str__ representation of the type is now just 'string'
        assert str(null_val) == "<null string>"

    def test_value_marks(self, str_type):
        str_val = str_type.validate("test")
        marked_val = str_val.mark(CtyMark(name="sensitive"))
        assert marked_val.has_mark("sensitive")
        unmarked, marks = marked_val.unmark()
        assert not unmarked.has_mark("sensitive")
        assert len(marks) == 1

    def test_value_equality(self, str_type):
        val1 = str_type.validate("test")
        val2 = str_type.validate("test")
        val3 = str_type.validate("different")
        assert val1 == val2
        assert val1 != val3
        assert CtyValue.unknown(str_type) == CtyValue.unknown(str_type)
        assert CtyValue.null(str_type) == CtyValue.null(str_type)
        assert val1 != "test"
