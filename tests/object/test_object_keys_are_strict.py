#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Object and map keys are strings, and two that spell the same NFC string are a collision.

`CtyMap` already refused a non-string key; `CtyObject` coerced one with `str()`,
so `{1: ...}` satisfied an attribute named `"1"`. And both normalized keys to NFC
through a dict comprehension, where the later spelling silently won. go-cty does
the same last-wins thing, but a configuration that spells one attribute two ways
is never what anyone meant, so refusing it is strictly more useful than matching.
"""

import pytest

from pyvider.cty import CtyMap, CtyObject, CtyString
from pyvider.cty.exceptions import CtyAttributeValidationError, CtyMapValidationError

COMPOSED = "é"  # é as one code point
DECOMPOSED = "é"  # e + combining acute


def test_object_refuses_a_non_string_key() -> None:
    obj = CtyObject(attribute_types={"1": CtyString()})
    with pytest.raises(CtyAttributeValidationError, match="must be strings"):
        obj.validate({1: "value"})


def test_object_refuses_two_spellings_of_one_attribute() -> None:
    obj = CtyObject(attribute_types={COMPOSED: CtyString()})
    with pytest.raises(CtyAttributeValidationError, match="normalize to the same"):
        obj.validate({COMPOSED: "a", DECOMPOSED: "b"})


def test_object_still_accepts_a_decomposed_spelling_alone() -> None:
    obj = CtyObject(attribute_types={COMPOSED: CtyString()})
    assert obj.validate({DECOMPOSED: "a"})[COMPOSED].value == "a"


def test_map_refuses_two_spellings_of_one_key() -> None:
    m = CtyMap(element_type=CtyString())
    with pytest.raises(CtyMapValidationError, match="normalize to the same"):
        m.validate({COMPOSED: "a", DECOMPOSED: "b"})


def test_map_still_normalizes_a_decomposed_key_alone() -> None:
    m = CtyMap(element_type=CtyString())
    assert {k: v.value for k, v in m.validate({DECOMPOSED: "a"}).value.items()} == {COMPOSED: "a"}
