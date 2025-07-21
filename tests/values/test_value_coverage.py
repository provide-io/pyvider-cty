"""
This test suite specifically targets edge cases and error paths in the
CtyValue class to ensure 100% test coverage.
"""

import pytest

from pyvider.cty import (
    CtyList,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyValue,
)


def test_constructor_with_unknown_and_null() -> None:
    """Covers the case where both is_unknown and is_null are True."""
    val = CtyValue(CtyString(), is_unknown=True, is_null=True)
    assert val.is_unknown
    assert not val.is_null


def test_raw_value_on_unknown_raises_error() -> None:
    """Covers the error path for accessing .raw_value on an unknown value."""
    unknown_val = CtyValue.unknown(CtyString())
    with pytest.raises(ValueError, match="Cannot get raw value of unknown value"):
        _ = unknown_val.raw_value


def test_len_on_primitive_type_raises_error() -> None:
    """Covers the error path for calling len() on a non-collection value."""
    string_val = CtyString().validate("hello")
    with pytest.raises(TypeError, match="Value of type CtyString has no len()"):
        len(string_val)


def test_iter_on_non_iterable_type_raises_error() -> None:
    """Covers the error path for iterating a non-collection value."""
    obj_val = CtyObject({"a": CtyString()}).validate({"a": "hello"})
    with pytest.raises(TypeError, match="Value of type CtyObject is not iterable"):
        list(obj_val)


def test_getitem_on_object_with_non_string_key() -> None:
    """Covers the error path for using a non-string key on an object."""
    obj_val = CtyObject({"a": CtyString()}).validate({"a": "hello"})
    with pytest.raises(TypeError, match="Object attribute name must be a string"):
        _ = obj_val[123]


def test_getitem_on_list_with_bad_internal_value() -> None:
    """Covers an internal error path for __getitem__ on a malformed list value."""
    list_val = CtyList(element_type=CtyString()).validate(["a"])
    # Use object.__setattr__ to modify a frozen, slotted instance for testing.
    object.__setattr__(list_val, "value", "not-a-list")
    with pytest.raises(TypeError, match="CtyList value is not a list/tuple"):
        _ = list_val[0]


def test_hash_on_collection_value_raises_error() -> None:
    """Covers the error path for hashing collection-type CtyValues."""
    list_val = CtyList(element_type=CtyString()).validate(["a"])
    obj_val = CtyObject({"a": CtyString()}).validate({"a": "b"})

    with pytest.raises(TypeError, match="unhashable type: 'CtyValue\\[list\\]'"):
        hash(list_val)

    with pytest.raises(TypeError, match="unhashable type: 'CtyValue\\[object\\]'"):
        hash(obj_val)


def test_is_empty_on_non_collection() -> None:
    """Covers the .is_empty() method on a value without a __len__."""
    num_val = CtyNumber().validate(123)
    assert not num_val.is_empty()
