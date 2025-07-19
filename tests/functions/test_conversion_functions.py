import pytest
from pyvider.cty import CtyString, CtyNumber, CtyBool, CtyValue
from pyvider.cty.functions import to_string, to_number, to_bool
from pyvider.cty.exceptions import CtyFunctionError

def test_to_string():
    assert to_string(CtyNumber().validate(123)).value == "123"
    assert to_string(CtyBool().validate(True)).value == "true"

def test_to_number():
    assert to_number(CtyString().validate("123")).value == 123
    with pytest.raises(CtyFunctionError):
        to_number(CtyString().validate("abc"))

def test_to_bool():
    assert to_bool(CtyString().validate("true")).value is True
    assert to_bool(CtyString().validate("false")).value is False
    with pytest.raises(CtyFunctionError):
        to_bool(CtyString().validate("abc"))
