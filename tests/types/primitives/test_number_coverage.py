import pytest
from pyvider.cty.types.primitives.number import CtyNumber
from pyvider.cty.values import CtyValue, UnknownValue
from pyvider.cty.exceptions import CtyNumberValidationError

def test_validate_unknown_value():
    number_type = CtyNumber()
    unknown_value = UnknownValue()
    result = number_type.validate(unknown_value)
    assert result.is_unknown
    assert result.type.equal(number_type)
