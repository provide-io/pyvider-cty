from decimal import Decimal

import pytest

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyValue,
)


# Fixtures for basic types
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
def dynamic_type() -> CtyDynamic:
    return CtyDynamic()


# Fixtures for collection types
@pytest.fixture
def list_of_string_type(string_type: CtyString) -> CtyList:
    return CtyList(element_type=string_type)


@pytest.fixture
def map_string_to_number_type(string_type: CtyString, number_type: CtyNumber) -> CtyMap:
    return CtyMap(key_type=string_type, value_type=number_type)


@pytest.fixture
def set_of_string_type(string_type: CtyString) -> CtySet:
    return CtySet(element_type=string_type)


# Fixtures for structural types
@pytest.fixture
def tuple_type(string_type: CtyString, number_type: CtyNumber) -> CtyTuple:
    return CtyTuple((string_type, number_type))


@pytest.fixture
def object_type(string_type: CtyString, number_type: CtyNumber) -> CtyObject:
    return CtyObject({"name": string_type, "age": number_type})


# Tests for CtyValue.is_empty()
def test_empty_unknown_value(string_type: CtyString):
    unknown_value = CtyValue.unknown(string_type)
    assert unknown_value.is_empty() is True


def test_empty_null_value(string_type: CtyString):
    null_value = CtyValue.null(string_type)
    assert null_value.is_empty() is True


def test_empty_string(string_type: CtyString):
    empty_str_value = CtyValue(string_type, "")
    non_empty_str_value = CtyValue(string_type, "hello")
    assert empty_str_value.is_empty() is True
    assert non_empty_str_value.is_empty() is False


def test_empty_list(list_of_string_type: CtyList):
    empty_list_value = CtyValue(list_of_string_type, [])
    non_empty_list_value = CtyValue(list_of_string_type, [CtyValue(CtyString(), "a")])
    assert empty_list_value.is_empty() is True
    assert non_empty_list_value.is_empty() is False


def test_empty_map(map_string_to_number_type: CtyMap):
    empty_map_value = CtyValue(map_string_to_number_type, {})
    non_empty_map_value = CtyValue(
        map_string_to_number_type, {"key": CtyValue(CtyNumber(), Decimal(1))}
    )
    assert empty_map_value.is_empty() is True
    assert non_empty_map_value.is_empty() is False


def test_empty_set(set_of_string_type: CtySet):
    empty_set_value = CtyValue(set_of_string_type, frozenset())
    non_empty_set_value = CtyValue(
        set_of_string_type, frozenset([CtyValue(CtyString(), "a")])
    )
    assert empty_set_value.is_empty() is True
    assert non_empty_set_value.is_empty() is False


def test_non_empty_number(number_type: CtyNumber):
    num_value = CtyValue(number_type, Decimal(10))
    zero_num_value = CtyValue(number_type, Decimal(0))
    assert num_value.is_empty() is False
    assert zero_num_value.is_empty() is False  # Numbers are not empty by value


def test_non_empty_bool(bool_type: CtyBool):
    true_value = CtyValue(bool_type, True)
    false_value = CtyValue(bool_type, False)
    assert true_value.is_empty() is False
    assert false_value.is_empty() is False  # Bools are not empty by value


def test_non_empty_tuple(
    tuple_type: CtyTuple, string_type: CtyString, number_type: CtyNumber
):
    # Tuples are considered empty if their underlying list/tuple structure is empty.
    # However, CtyTuple validation might prevent creation of truly "empty" typed tuples
    # depending on its design. For this test, we assume a tuple value itself can be empty.
    empty_tuple_val = CtyValue(
        tuple_type, []
    )  # Assuming tuple_type can wrap an empty list for its value
    non_empty_tuple_val = CtyValue(
        tuple_type, [CtyValue(string_type, "a"), CtyValue(number_type, Decimal(1))]
    )
    assert empty_tuple_val.is_empty() is True
    assert non_empty_tuple_val.is_empty() is False


def test_non_empty_object(
    object_type: CtyObject, string_type: CtyString, number_type: CtyNumber
):
    # Objects (structs) are considered empty if their underlying map/dict structure is empty.
    empty_object_val = CtyValue(
        object_type, {}
    )  # Assuming object_type can wrap an empty dict
    non_empty_object_val = CtyValue(
        object_type,
        {
            "name": CtyValue(string_type, "test"),
            "age": CtyValue(number_type, Decimal(5)),
        },
    )
    assert empty_object_val.is_empty() is True
    assert non_empty_object_val.is_empty() is False


def test_empty_dynamic_value_holding_empty_string(
    dynamic_type: CtyDynamic, string_type: CtyString
):
    # CtyValue(CtyDynamic, CtyValue(CtyString, ""))
    # The outer CtyValue is dynamic, its _value is another CtyValue (string, "")
    # The is_empty() on the outer dynamic value should reflect the emptiness of its contained concrete value.
    # This requires is_empty() to potentially look inside if the _value is a CtyValue itself.
    # Current is_empty() checks `isinstance(self._value, str | list | tuple | dict | set | frozenset)`
    # This will be false if self._value is a CtyValue. So it will currently return False.
    # We need to adjust is_empty for this case.

    # Let's refine the is_empty logic for CtyDynamic values.
    # If a CtyValue has CtyDynamic type and its _value is another CtyValue,
    # its emptiness should depend on the emptiness of the inner CtyValue.

    # Create an empty string CtyValue
    inner_empty_string_value = CtyValue(string_type, "")
    # Wrap it in a CtyDynamic CtyValue
    dynamic_holding_empty_string = CtyValue(dynamic_type, inner_empty_string_value)
    assert dynamic_holding_empty_string.is_empty() is True

    # Create a non-empty string CtyValue
    inner_non_empty_string_value = CtyValue(string_type, "hello")
    # Wrap it in a CtyDynamic CtyValue
    dynamic_holding_non_empty_string = CtyValue(
        dynamic_type, inner_non_empty_string_value
    )
    assert dynamic_holding_non_empty_string.is_empty() is False

    # Test dynamic null
    dynamic_null = CtyValue.null(dynamic_type)
    assert dynamic_null.is_empty() is True

    # Test dynamic unknown
    dynamic_unknown = CtyValue.unknown(dynamic_type)
    assert dynamic_unknown.is_empty() is True

    # Test dynamic holding a number (which is not empty)
    inner_number_value = CtyValue(CtyNumber(), Decimal(0))
    dynamic_holding_number = CtyValue(dynamic_type, inner_number_value)
    assert dynamic_holding_number.is_empty() is False
