from decimal import Decimal

import pytest

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtySet,
    CtyString,
    CtyValue,
)


# Type Fixtures
@pytest.fixture
def string_type() -> CtyString:
    return CtyString()


@pytest.fixture
def number_type() -> CtyNumber:
    return CtyNumber()


@pytest.fixture
def bool_type() -> CtyBool:
    return CtyBool()


@pytest.fixture
def list_type(string_type: CtyString) -> CtyList:
    return CtyList(element_type=string_type)


@pytest.fixture
def map_type(string_type: CtyString, number_type: CtyNumber) -> CtyMap:
    return CtyMap(key_type=string_type, value_type=number_type)


@pytest.fixture
def set_type(string_type: CtyString) -> CtySet:
    return CtySet(element_type=string_type)


@pytest.fixture
def dynamic_type() -> CtyDynamic:
    return CtyDynamic()


# Tests for is_true()
def test_is_true_with_true_value(bool_type: CtyBool):
    val = CtyValue(bool_type, True)
    assert val.is_true() is True
    assert val.is_false() is False


def test_is_true_with_false_value(bool_type: CtyBool):
    val = CtyValue(bool_type, False)
    assert val.is_true() is False
    assert val.is_false() is True


def test_is_true_with_non_boolean_known_values(
    string_type: CtyString,
    number_type: CtyNumber,
    list_type: CtyList,
    map_type: CtyMap,
    set_type: CtySet,
    dynamic_type: CtyDynamic,
    bool_type: CtyBool,  # Added bool_type fixture
):
    # String
    str_val_true_like = CtyValue(string_type, "true")  # String "true" is not bool True
    assert str_val_true_like.is_true() is False
    assert str_val_true_like.is_false() is False

    str_val_empty = CtyValue(string_type, "")
    assert str_val_empty.is_true() is False
    assert str_val_empty.is_false() is False

    # Number
    num_val_one = CtyValue(number_type, Decimal(1))  # Number 1 is not bool True
    assert num_val_one.is_true() is False
    assert num_val_one.is_false() is False

    num_val_zero = CtyValue(number_type, Decimal(0))
    assert num_val_zero.is_true() is False
    assert num_val_zero.is_false() is False

    # List
    list_val_empty = CtyValue(list_type, [])
    assert list_val_empty.is_true() is False
    assert list_val_empty.is_false() is False

    list_val_non_empty = CtyValue(list_type, [CtyValue(string_type, "a")])
    assert list_val_non_empty.is_true() is False
    assert list_val_non_empty.is_false() is False

    # Map
    map_val_empty = CtyValue(map_type, {})
    assert map_val_empty.is_true() is False
    assert map_val_empty.is_false() is False

    map_val_non_empty = CtyValue(map_type, {"key": CtyValue(number_type, Decimal(1))})
    assert map_val_non_empty.is_true() is False
    assert map_val_non_empty.is_false() is False

    # Set
    set_val_empty = CtyValue(set_type, frozenset())
    assert set_val_empty.is_true() is False
    assert set_val_empty.is_false() is False

    set_val_non_empty = CtyValue(set_type, frozenset([CtyValue(string_type, "a")]))
    assert set_val_non_empty.is_true() is False
    assert set_val_non_empty.is_false() is False

    # Dynamic holding True
    dyn_true_val = CtyValue(
        dynamic_type, CtyValue(bool_type, True)
    )  # Use bool_type fixture
    assert dyn_true_val.is_true() is True  # Should look into the wrapped value
    assert dyn_true_val.is_false() is False

    # Dynamic holding False
    dyn_false_val = CtyValue(
        dynamic_type, CtyValue(bool_type, False)
    )  # Use bool_type fixture
    assert dyn_false_val.is_true() is False
    assert dyn_false_val.is_false() is True  # Should look into the wrapped value

    # Dynamic holding non-boolean
    dyn_str_val = CtyValue(
        dynamic_type, CtyValue(string_type, "text")
    )  # Use string_type fixture
    assert dyn_str_val.is_true() is False
    assert dyn_str_val.is_false() is False


def test_is_true_with_null_value(bool_type: CtyBool, dynamic_type: CtyDynamic):
    null_bool_val = CtyValue.null(bool_type)
    assert null_bool_val.is_true() is False
    assert null_bool_val.is_false() is False

    null_dynamic_val = CtyValue.null(dynamic_type)
    assert null_dynamic_val.is_true() is False
    assert null_dynamic_val.is_false() is False


def test_is_true_with_unknown_value(bool_type: CtyBool, dynamic_type: CtyDynamic):
    unknown_bool_val = CtyValue.unknown(bool_type)
    assert unknown_bool_val.is_true() is False
    assert unknown_bool_val.is_false() is False

    unknown_dynamic_val = CtyValue.unknown(dynamic_type)
    assert unknown_dynamic_val.is_true() is False
    assert unknown_dynamic_val.is_false() is False


# Tests for is_false() are implicitly covered by the is_true() tests,
# as each test asserts both conditions. Explicit is_false tests can be added
# if more specific scenarios for is_false (not covered by is_true checks) are needed.
