import pytest
from pyvider.cty.types.collections.set import CtySet
from pyvider.cty.types import CtyString, CtyNumber, CtyDynamic
from pyvider.cty.values import CtyValue
from pyvider.cty.exceptions import CtySetValidationError

def test_attrs_post_init_invalid_element_type():
    with pytest.raises(CtySetValidationError):
        CtySet(element_type="not_a_type")

def test_validate_with_unhashable_elements_in_list():
    set_type = CtySet(element_type=CtyDynamic())
    with pytest.raises(CtySetValidationError, match="Input collection contains unhashable elements"):
        set_type.validate([[]])

def test_validate_with_unhashable_elements_in_set():
    set_type = CtySet(element_type=CtyDynamic())
    class Unhashable:
        __hash__ = None
    with pytest.raises(TypeError, match="unhashable type: 'Unhashable'"):
        set_type.validate({Unhashable()})

def test_validate_with_cty_value_different_set_type():
    set_type = CtySet(element_type=CtyString())
    other_set_type = CtySet(element_type=CtyNumber())
    value = other_set_type.validate({1, 2, 3})
    with pytest.raises(CtySetValidationError):
        set_type.validate(value)
