import pytest
from pyvider.cty import CtyNumber, CtyString, CtyValue
from pyvider.cty.functions.numeric_functions import add
from pyvider.cty.exceptions import CtyFunctionError

def test_add_numbers():
    assert add(CtyNumber().validate(1), CtyNumber().validate(2)).value == 3
    assert add(CtyNumber().validate(-1), CtyNumber().validate(2)).value == 1
    assert add(CtyNumber().validate(1.5), CtyNumber().validate(2.5)).value == 4.0

def test_add_null():
    assert add(CtyValue.null(CtyNumber()), CtyNumber().validate(1)).is_unknown
    assert add(CtyNumber().validate(1), CtyValue.null(CtyNumber())).is_unknown

def test_add_unknown():
    assert add(CtyValue.unknown(CtyNumber()), CtyNumber().validate(1)).is_unknown
    assert add(CtyNumber().validate(1), CtyValue.unknown(CtyNumber())).is_unknown

def test_add_type_error():
    with pytest.raises(CtyFunctionError):
        add(CtyString().validate("a"), CtyNumber().validate(1))
