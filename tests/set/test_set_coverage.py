#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


import pytest

from pyvider.cty import (
    CtyNumber,
    CtySet,
    CtyString,
)
from pyvider.cty.exceptions import CtySetValidationError


@pytest.fixture
def string_set_type():
    return CtySet(element_type=CtyString())


def test_validate_with_cty_value_different_set_type(string_set_type) -> None:
    number_set_type = CtySet(element_type=CtyNumber())
    number_set_value = number_set_type.validate({1, 2, 3})
    with pytest.raises(CtySetValidationError):
        string_set_type.validate(number_set_value)


def test_to_wire_json(string_set_type) -> None:
    wire_json = string_set_type._to_wire_json()
    assert wire_json == ["set", "string"]


# def test_validate_with_unhashable_element_in_set(string_set_type):
#     with pytest.raises(CtySetValidationError):
#         string_set_type.validate({"a", ("b",)})


# def test_validate_with_dynamic_element_type():
#     from pyvider.cty import CtyBool
#     set_type = CtySet(element_type=CtyDynamic())
#     validated = set_type.validate({"a", 1, True})
#     assert isinstance(validated, CtyValue)
#     assert isinstance(validated.type, CtySet)

#     # Extract types from the validated set for comparison
#     validated_types = {v.type for v in validated.value}

#     assert CtyString() in validated_types
#     assert CtyNumber() in validated_types
#     assert CtyBool() in validated_types
#     assert len(validated_types) == 3

# 🌊🪢🔚
