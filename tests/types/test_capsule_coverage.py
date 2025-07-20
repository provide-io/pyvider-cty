import pytest
from pyvider.cty.types.capsule import CtyCapsule
from pyvider.cty.values import CtyValue, UnknownValue
from pyvider.cty.exceptions import CtyValidationError

class MyObject:
    pass

class MyOtherObject:
    pass

def test_validate_with_cty_value_different_capsule_type():
    capsule_type = CtyCapsule("MyObject", MyObject)
    other_capsule_type = CtyCapsule("MyOtherObject", MyOtherObject)
    value = other_capsule_type.validate(MyOtherObject())
    with pytest.raises(CtyValidationError):
        capsule_type.validate(value)

def test_to_wire_json():
    capsule_type = CtyCapsule("MyObject", MyObject)
    assert capsule_type._to_wire_json() is None
