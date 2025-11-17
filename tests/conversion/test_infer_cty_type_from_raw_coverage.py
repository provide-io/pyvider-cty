#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

from typing import Never

import attrs
import pytest

from pyvider.cty.conversion.raw_to_cty import infer_cty_type_from_raw
from pyvider.cty.types import (
    CtyBool,
    CtyDynamic,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyTuple,
)


def test_infer_tuple_with_mixed_types() -> None:
    raw_val = ("hello", 123, True)
    inferred_type = infer_cty_type_from_raw(raw_val)
    expected_type = CtyTuple(element_types=(CtyString(), CtyNumber(), CtyBool()))
    assert inferred_type.equal(expected_type)


def test_infer_from_set() -> None:
    raw_val = {"hello", "world"}
    inferred_type = infer_cty_type_from_raw(raw_val)
    from pyvider.cty.types import CtySet

    expected_type = CtySet(element_type=CtyString())
    assert inferred_type.equal(expected_type)


def test_infer_object_with_non_identifier_keys() -> None:
    raw_val = {"hello-world": 123}
    inferred_type = infer_cty_type_from_raw(raw_val)
    # All string-keyed dicts should be inferred as objects.
    expected_type = CtyObject(attribute_types={"hello-world": CtyNumber()})
    assert inferred_type.equal(expected_type)


@attrs.define
class UnsafeAttrs:
    x: int

    def __attrs_post_init__(self):
        if self.x > 0:
            raise TypeError("This is an unsafe attrs class")


def test_infer_from_unsafe_attrs() -> None:
    with pytest.raises(TypeError, match="This is an unsafe attrs class"):
        UnsafeAttrs(x=1)

    class FakeAttrs:
        def __init__(self) -> None:
            self.__attrs_attrs__ = [
                attrs.Attribute(
                    name="a",
                    default=None,
                    validator=None,
                    repr=True,
                    eq=True,
                    order=True,
                    hash=None,
                    init=True,
                    on_setattr=None,
                    converter=None,
                    kw_only=False,
                    inherited=False,
                    metadata=None,
                    cmp=None,
                )
            ]

        @property
        def a(self) -> Never:
            raise TypeError("permission denied")

    inferred_type = infer_cty_type_from_raw(FakeAttrs())
    assert inferred_type == CtyDynamic()


def test_infer_from_other_types() -> None:
    class Other:
        pass

    inferred_type = infer_cty_type_from_raw(Other())
    assert inferred_type == CtyDynamic()


# 🌊🪢🔚
