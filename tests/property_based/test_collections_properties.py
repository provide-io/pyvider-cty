import unicodedata

from hypothesis import given, strategies as st
import pytest

from pyvider.cty import CtyBool, CtyList, CtyNumber, CtyString, CtyValidationError


from typing import Any


@given(st.lists(st.text()))
def test_list_of_strings_validation(value: list[str]) -> None:
    """
    Tests that a CtyList(CtyString) correctly validates lists of strings.
    """
    list_type = CtyList(element_type=CtyString())
    validated_value = list_type.validate(value)
    normalized_value = [unicodedata.normalize("NFC", v) for v in value]
    assert validated_value.raw_value == normalized_value


@given(st.lists(st.integers() | st.floats(allow_nan=False, allow_infinity=False)))
def test_list_of_numbers_validation(value: list[int | float]) -> None:
    """
    Tests that a CtyList(CtyNumber) correctly validates lists of numbers.
    """
    list_type = CtyList(element_type=CtyNumber())
    validated_value = list_type.validate(value)
    # Compare using float to avoid floating point precision issues
    assert [float(v) for v in validated_value.raw_value] == [float(v) for v in value]


@given(st.lists(st.booleans()))
def test_list_of_booleans_validation(value: list[bool]) -> None:
    """
    Tests that a CtyList(CtyBool) correctly validates lists of booleans.
    """
    list_type = CtyList(element_type=CtyBool())
    validated_value = list_type.validate(value)
    assert validated_value.raw_value == value


@given(st.lists(st.none() | st.integers()))
def test_list_of_strings_with_invalid_types(value: list[None | int]) -> None:
    """
    Tests that a CtyList(CtyString) raises a validation error for lists containing non-strings.
    """
    list_type = CtyList(element_type=CtyString())
    if any(not isinstance(v, str) for v in value):
        with pytest.raises(CtyValidationError):
            list_type.validate(value)
    else:
        # This branch is for hypothesis to have valid cases as well
        list_type.validate(value)
