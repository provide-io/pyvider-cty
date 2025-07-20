import pytest

from pyvider.cty import (
    CtyTuple,
    CtyNumber,
    CtyString,
    CtyValue,
    CtyDynamic,
)
from pyvider.cty.exceptions import CtyTupleValidationError


@pytest.fixture
def simple_tuple_type():
    return CtyTuple(element_types=(CtyString(), CtyNumber()))


def test_validate_with_cty_value_different_tuple_type(simple_tuple_type):
    another_tuple_type = CtyTuple(element_types=(CtyString(), CtyString()))
    another_tuple_value = another_tuple_type.validate(("hello", "world"))
    with pytest.raises(CtyTupleValidationError):
        simple_tuple_type.validate(another_tuple_value)


def test_getitem(simple_tuple_type):
    assert simple_tuple_type[0] == CtyString()
    assert simple_tuple_type[1] == CtyNumber()

    sliced = simple_tuple_type[0:1]
    assert isinstance(sliced, tuple)
    assert sliced[0] == CtyString()

def test_validate_with_unknown_value(simple_tuple_type):
    unknown_value = CtyValue.unknown(simple_tuple_type)
    validated = simple_tuple_type.validate(unknown_value)
    assert validated.is_unknown

def test_validate_with_null_value(simple_tuple_type):
    null_value = CtyValue.null(simple_tuple_type)
    validated = simple_tuple_type.validate(null_value)
    assert validated.is_null
