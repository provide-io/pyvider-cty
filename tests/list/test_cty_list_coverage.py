#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


import pytest

from pyvider.cty.exceptions import CtyListValidationError
from pyvider.cty.types import CtyNumber, CtyString
from pyvider.cty.types.collections.list import CtyList
from pyvider.cty.values import CtyValue


def test_attrs_post_init_invalid_element_type() -> None:
    with pytest.raises(CtyListValidationError):
        CtyList(element_type="not_a_type")


def test_validate_none() -> None:
    list_type = CtyList(element_type=CtyString())
    assert list_type.validate(None).is_null


def test_validate_with_set() -> None:
    list_type = CtyList(element_type=CtyNumber())
    value = {1, 2, 3}
    result = list_type.validate(value)
    assert isinstance(result.value, tuple)
    assert sorted([v.value for v in result.value]) == [1, 2, 3]


def test_validate_null_element_in_list() -> None:
    """A null element is a value, not an error.

    This used to assert the opposite, which recorded what the code did rather
    than what cty says: a null is a value of any type there, so go-cty writes
    one inside a list and Terraform sends it for `["a", null]`. The refusal
    happened on read too, so decoding that state raised.
    """
    list_type = CtyList(element_type=CtyString())

    validated = list_type.validate(["a", None, "c"])

    assert validated.raw_value == ["a", None, "c"]
    assert validated.value[1].is_null
    assert validated.value[1].type == CtyString()


def test_element_at_on_non_cty_list_value() -> None:
    list_type = CtyList(element_type=CtyString())
    with pytest.raises(CtyListValidationError, match="Expected CtyValue with CtyList type"):
        list_type.element_at(CtyValue(CtyNumber(), 1), 0)


def test_element_at_on_non_list_internal_value() -> None:
    list_type = CtyList(element_type=CtyString())
    # Manually create a CtyValue with an inconsistent internal value
    inconsistent_value = CtyValue(list_type, value="not a list")
    with pytest.raises(
        CtyListValidationError,
        match="Internal error: CtyValue of CtyList type does not wrap a list/tuple",
    ):
        list_type.element_at(inconsistent_value, 0)


def test_element_at_with_a_non_index_answers_inside_the_taxonomy() -> None:
    """A bad index is a CtyListValidationError, as of 2026-08-17.

    This used to catch `TypeError` around *both* the subscript and the element
    validation that follows it, and re-raise a brand-new **bare** `TypeError`
    saying "list indices must be integers" -- so a TypeError from anywhere
    inside validation was relabelled as an index problem, the original was
    discarded, and the answer was not a `CtyError` a caller could catch beside
    every other validation failure.
    """
    list_type = CtyList(element_type=CtyString())
    value = list_type.validate(["a"])

    with pytest.raises(CtyListValidationError, match="List index must be an integer or slice, not str"):
        list_type.element_at(value, "nope")  # type: ignore[arg-type]


def test_element_at_out_of_range_is_still_an_index_error() -> None:
    """`IndexError` is Python's answer for a valid index that is out of range.

    Pinned alongside the case above so that narrowing the `except TypeError` did
    not quietly convert this one too.
    """
    list_type = CtyList(element_type=CtyString())

    with pytest.raises(IndexError):
        list_type.element_at(list_type.validate(["a"]), 5)


# 🌊🪢🔚
