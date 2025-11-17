#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

import attrs
import pytest

from pyvider.cty.conversion._utils import _attrs_to_dict_safe
from pyvider.cty.types import CtyString


@attrs.define
class MyAttrsClass:
    a: int
    b: str


def test_attrs_to_dict_safe_with_attrs_instance() -> None:
    """Tests that a standard attrs instance is converted correctly."""
    instance = MyAttrsClass(a=1, b="test")
    assert _attrs_to_dict_safe(instance) == {"a": 1, "b": "test"}


def test_attrs_to_dict_safe_with_non_attrs_class() -> None:
    """Tests that a non-attrs class results in an empty dict."""

    class NotAttrs:
        def __init__(self) -> None:
            self.a = 1

    instance = NotAttrs()
    assert _attrs_to_dict_safe(instance) == {}


def test_attrs_to_dict_safe_with_cty_type_raises_error() -> None:
    """Tests that passing a CtyType instance raises a TypeError."""
    with pytest.raises(TypeError, match="Cannot infer data type from a CtyType instance"):
        _attrs_to_dict_safe(CtyString())


def test_attrs_to_dict_safe_with_cty_value_raises_error() -> None:
    """Tests that passing a CtyValue instance raises a TypeError."""
    cty_val = CtyString().validate("hello")
    with pytest.raises(TypeError, match="Cannot infer data type from a CtyValue instance"):
        _attrs_to_dict_safe(cty_val)


# 🌊🪢🔚
