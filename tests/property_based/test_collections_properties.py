#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


import unicodedata

from hypothesis import given, settings, strategies as st
import pytest

from pyvider.cty import CtyBool, CtyList, CtyNumber, CtyString, CtyValidationError


@given(st.lists(st.text()))
def test_list_of_strings_validation(value: list[str]) -> None:
    """
    Tests that a CtyList(element_type=CtyString) correctly validates lists of strings.
    """
    list_type = CtyList(element_type=CtyString())
    validated_value = list_type.validate(value)
    normalized_value = tuple(unicodedata.normalize("NFC", v) for v in value)
    assert tuple(v.value for v in validated_value.value) == normalized_value


@given(st.lists(st.integers() | st.floats(allow_nan=False, allow_infinity=False)))
def test_list_of_numbers_validation(value: list[int | float]) -> None:
    """
    Tests that a CtyList(element_type=CtyNumber) correctly validates lists of numbers.
    """
    list_type = CtyList(element_type=CtyNumber())
    validated_value = list_type.validate(value)
    # Compare using float to avoid floating point precision issues
    assert [float(v.value) for v in validated_value.value] == pytest.approx([float(v) for v in value])


@given(st.lists(st.booleans()))
def test_list_of_booleans_validation(value: list[bool]) -> None:
    """
    Tests that a CtyList(element_type=CtyBool) correctly validates lists of booleans.
    """
    list_type = CtyList(element_type=CtyBool())
    validated_value = list_type.validate(value)
    assert [v.value for v in validated_value.value] == value


@given(st.lists(st.none() | st.integers(), max_size=20))
@settings(deadline=500)  # Increase deadline to 500ms for validation-heavy test
def test_list_of_strings_with_invalid_types(value: list[None | int]) -> None:
    """
    Tests that a CtyList(element_type=CtyString) raises a validation error for lists containing non-strings.
    """
    list_type = CtyList(element_type=CtyString())
    if any(not isinstance(v, str) for v in value):
        with pytest.raises(CtyValidationError):
            list_type.validate(value)
    else:
        # This branch is for hypothesis to have valid cases as well
        list_type.validate(value)


# 🌊🪢🔚
