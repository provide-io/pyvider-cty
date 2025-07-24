import attrs
import pytest

from pyvider.cty.conversion.raw_to_cty import _attrs_to_dict_safe
from pyvider.cty.types import CtyString
from pyvider.cty.values import CtyValue


@attrs.define
class MyAttrsClass:
    a: int
    b: str


def test_attrs_to_dict_safe_with_attrs() -> None:
    inst = MyAttrsClass(a=1, b="test")
    assert _attrs_to_dict_safe(inst) == {"a": 1, "b": "test"}


def test_attrs_to_dict_safe_with_cty_type() -> None:
    with pytest.raises(
        TypeError, match="Cannot infer data type from a CtyType instance"
    ):
        _attrs_to_dict_safe(CtyString())


def test_attrs_to_dict_safe_with_cty_value() -> None:
    cty_val = CtyValue(CtyString(), "hello")
    with pytest.raises(
        TypeError, match="Cannot infer data type from a CtyValue instance"
    ):
        _attrs_to_dict_safe(cty_val)
