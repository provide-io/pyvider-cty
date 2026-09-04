#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Which values become a bool, matched to go-cty.

go-cty converts a string to a bool only as an *unsafe* conversion, and only for
four spellings (`cty/convert/conversion_primitive.go:38-54`):

    case "true", "1":  return cty.True
    case "false", "0": return cty.False
    default:
        switch strings.ToLower(val.AsString()) {
        case "true":  ... "a bool is required; to convert from string, use lowercase \\"true\\""

There is no number-to-bool conversion at all: neither the safe nor the unsafe
primitive table has one. And on the wire a bool is `dec.DecodeBool()`
(`cty/msgpack/unmarshal.go:67-72`), with no coercion of any kind.

Accepting `1` as true means a provider that returns a count where it meant a
flag gets a plausible answer instead of an error, and the mistake reaches a
plan.
"""

import pytest

from pyvider.cty import CtyBool
from pyvider.cty.exceptions import CtyValidationError


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("true", True), ("1", True), ("false", False), ("0", False)],
)
def test_the_four_spellings_go_cty_accepts(raw: str, expected: bool) -> None:
    assert CtyBool().validate(raw).value is expected


@pytest.mark.parametrize("raw", ["True", "TRUE", "False", "FALSE"])
def test_other_casings_are_refused_with_the_hint_go_cty_gives(raw: str) -> None:
    with pytest.raises(CtyValidationError, match=r"(?i)lowercase"):
        CtyBool().validate(raw)


@pytest.mark.parametrize("raw", [1, 0, 1.0, 0.0, 2, -1])
def test_a_number_is_not_a_bool(raw: object) -> None:
    """go-cty has no number-to-bool conversion, safe or unsafe."""
    with pytest.raises(CtyValidationError):
        CtyBool().validate(raw)


@pytest.mark.parametrize("raw", [True, False])
def test_a_real_bool_still_passes(raw: bool) -> None:
    assert CtyBool().validate(raw).value is raw


def test_an_unrelated_string_is_refused() -> None:
    with pytest.raises(CtyValidationError, match=r"(?i)bool is required"):
        CtyBool().validate("yes")


# 🐍🔚
