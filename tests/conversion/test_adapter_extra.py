import pytest
from decimal import Decimal

from pyvider.cty import (
    CtySet,
    CtyString,
    CtyTuple,
    CtyValue,
    CtyDynamic,
    CtyNumber,
    CtyList,
)
from pyvider.cty.conversion.adapter import cty_to_native


def test_cty_to_native_with_set():
    set_type = CtySet(element_type=CtyString())
    cty_val = set_type.validate({"a", "b", "c"})
    native = cty_to_native(cty_val)
    assert isinstance(native, list)
    assert sorted(native) == ["a", "b", "c"]


def test_cty_to_native_with_tuple():
    tuple_type = CtyTuple(element_types=(CtyString(), CtyString()))
    cty_val = tuple_type.validate(("a", "b"))
    native = cty_to_native(cty_val)
    assert isinstance(native, tuple)
    assert native == ("a", "b")


def test_cty_to_native_with_non_cty_value():
    assert cty_to_native("hello") == "hello"
    assert cty_to_native(123) == 123
    assert cty_to_native(None) is None


def test_cty_to_native_with_dynamic_value():
    # Test with a CtyValue wrapping a primitive
    dynamic_type = CtyDynamic()
    cty_val = dynamic_type.validate("hello")
    native = cty_to_native(cty_val)
    assert native == "hello"

    # Test with a CtyValue wrapping a collection
    list_val = CtyList(element_type=CtyString()).validate(["a", "b"])
    cty_val_dynamic_list = dynamic_type.validate(list_val)
    native_list = cty_to_native(cty_val_dynamic_list)
    assert native_list == ["a", "b"]


def test_cty_to_native_with_decimal():
    # Test integer conversion
    cty_val_int = CtyNumber().validate(Decimal("123"))
    native_int = cty_to_native(cty_val_int)
    assert isinstance(native_int, int)
    assert native_int == 123

    # Test float conversion
    cty_val_float = CtyNumber().validate(Decimal("123.45"))
    native_float = cty_to_native(cty_val_float)
    assert isinstance(native_float, float)
    assert native_float == 123.45
