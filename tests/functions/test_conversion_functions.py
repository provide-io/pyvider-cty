#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from collections.abc import Callable
from typing import Any

import pytest

from pyvider.cty import CtyBool, CtyList, CtyNumber, CtyString, CtyType, CtyValue
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import to_bool, to_number, to_string


def test_to_string() -> None:
    assert to_string(CtyNumber().validate(123)).value == "123"
    assert to_string(CtyBool().validate(True)).value == "true"
    assert to_string(CtyString().validate("a")).value == "a"


def test_to_number() -> None:
    assert to_number(CtyString().validate("123")).value == 123
    with pytest.raises(CtyFunctionError):
        to_number(CtyString().validate("abc"))


def test_to_bool() -> None:
    assert to_bool(CtyString().validate("true")).value is True
    assert to_bool(CtyString().validate("false")).value is False
    with pytest.raises(CtyFunctionError):
        to_bool(CtyString().validate("abc"))


def test_an_unconvertible_value_is_refused_rather_than_stringified() -> None:
    """`tostring` used to end in `str(value.value)`.

    The payload of a collection is its internal tuple of CtyValues, so this
    returned the literal text of a repr: a well-formed string, of the right
    type, headed for Terraform state. go-cty refuses the conversion.
    """
    collection = CtyList(element_type=CtyString()).validate(["a"])

    with pytest.raises(CtyFunctionError):
        to_string(collection)


def test_a_bool_is_not_a_number() -> None:
    """A Python bool is an int, so `CtyNumber().validate(True)` gives 1.

    go-cty has no bool-to-number conversion at all.
    """
    with pytest.raises(CtyFunctionError):
        to_number(CtyBool().validate(True))


@pytest.mark.parametrize(
    ("function", "source_type", "target_type"),
    [
        (to_string, CtyNumber(), CtyString()),
        (to_string, CtyString(), CtyString()),
        (to_number, CtyString(), CtyNumber()),
        (to_bool, CtyString(), CtyBool()),
    ],
)
def test_a_null_converts_to_a_null_of_the_target_type(
    function: Callable[[CtyValue[Any]], CtyValue[Any]],
    source_type: CtyType[Any],
    target_type: CtyType[Any],
) -> None:
    """Not unknown. go-cty's parameter sets `AllowNull: true` for exactly this.

    These returned unknown, which claims the value might yet turn out to be
    something. A null converted to a string is still nothing -- now typed as a
    string.
    """
    result = function(CtyValue.null(source_type))

    assert result.is_null
    assert not result.is_unknown
    assert result.type.equal(target_type)


@pytest.mark.parametrize("function", [to_string, to_number, to_bool])
def test_an_unknown_stays_unknown(function: Callable[[CtyValue[Any]], CtyValue[Any]]) -> None:
    assert function(CtyValue.unknown(CtyString())).is_unknown


# 🌊🪢🔚
