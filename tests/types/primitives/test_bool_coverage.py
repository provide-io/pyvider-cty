import pytest
from pyvider.cty.types.primitives.bool import CtyBool
from pyvider.cty.values import CtyValue, UnknownValue
from pyvider.cty.exceptions import CtyBoolValidationError

def test_validate_unknown_value():
    bool_type = CtyBool()
    unknown_value = UnknownValue()
    result = bool_type.validate(unknown_value)
    assert result.is_unknown
    assert result.type.equal(bool_type)
