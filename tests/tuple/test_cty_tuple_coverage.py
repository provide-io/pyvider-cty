#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


import pytest

from pyvider.cty.exceptions import CtyTupleValidationError, CtyTypeMismatchError
from pyvider.cty.types import CtyDynamic, CtyNumber, CtyString
from pyvider.cty.types.structural.tuple import CtyTuple
from pyvider.cty.values import CtyValue


def test_element_types_validator() -> None:
    with pytest.raises(CtyTupleValidationError, match="element_types must be a tuple"):
        CtyTuple(element_types=[CtyString()])  # type: ignore

    with pytest.raises(CtyTupleValidationError, match="Element type at index 0 must be a CtyType"):
        CtyTuple(element_types=("not a type",))  # type: ignore


def test_validate_with_unknown_value() -> None:
    tuple_type = CtyTuple((CtyString(), CtyNumber()))
    unknown_value = CtyValue.unknown(CtyDynamic())
    result = tuple_type.validate(unknown_value)
    assert result.is_unknown
    assert result.type.equal(tuple_type)


def test_validate_with_null_value() -> None:
    tuple_type = CtyTuple((CtyString(), CtyNumber()))
    null_value = CtyValue.null(CtyDynamic())
    result = tuple_type.validate(null_value)
    assert result.is_null
    assert result.type.equal(tuple_type)


def test_element_at_slice_on_null_or_unknown() -> None:
    tuple_type = CtyTuple((CtyString(), CtyNumber(), CtyString()))

    null_value = CtyValue.null(tuple_type)
    sliced_null = tuple_type.element_at(null_value, slice(0, 2))
    assert sliced_null.is_null
    assert isinstance(sliced_null.type, CtyTuple)
    assert len(sliced_null.type.element_types) == 2

    unknown_value = CtyValue.unknown(tuple_type)
    sliced_unknown = tuple_type.element_at(unknown_value, slice(0, 2))
    assert sliced_unknown.is_unknown
    assert isinstance(sliced_unknown.type, CtyTuple)
    assert len(sliced_unknown.type.element_types) == 2


def test_validate_with_inconsistent_internal_value() -> None:
    tuple_type = CtyTuple((CtyString(), CtyNumber()))
    with pytest.raises(CtyTupleValidationError):
        tuple_type.validate(("a", "b"))


def test_slice_method() -> None:
    tuple_type = CtyTuple((CtyString(), CtyNumber(), CtyString()))
    tuple_value = tuple_type.validate(("a", 1, "b"))

    sliced_value = tuple_type.slice(tuple_value, 0, 2)
    assert isinstance(sliced_value.type, CtyTuple)
    assert len(sliced_value.type.element_types) == 2
    assert sliced_value.value[0].value == "a"
    assert sliced_value.value[1].value == 1


def test_slice_method_with_invalid_container() -> None:
    tuple_type = CtyTuple((CtyString(),))
    other_type = CtyTuple((CtyNumber(),))
    other_value = other_type.validate((1,))

    with pytest.raises(CtyTypeMismatchError):
        tuple_type.slice(other_value, 0, 1)


def test_equal_different_lengths() -> None:
    type1 = CtyTuple((CtyString(),))
    type2 = CtyTuple((CtyString(), CtyNumber()))
    assert type1.equal(type2) is False


def test_usable_as_different_lengths() -> None:
    type1 = CtyTuple((CtyString(),))
    type2 = CtyTuple((CtyString(), CtyNumber()))
    assert type1.usable_as(type2) is False


# 🌊🪢🔚
