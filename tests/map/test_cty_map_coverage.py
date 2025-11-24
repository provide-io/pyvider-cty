#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

import pytest

from pyvider.cty.exceptions import CtyMapValidationError, InvalidTypeError
from pyvider.cty.types import CtyNumber, CtyString
from pyvider.cty.types.collections.map import CtyMap
from pyvider.cty.values import CtyValue


def test_attrs_post_init_invalid_element_type() -> None:
    with pytest.raises(InvalidTypeError):
        CtyMap(element_type="not_a_type")


def test_validate_with_cty_value_different_type() -> None:
    map_type = CtyMap(element_type=CtyString())
    other_map_type = CtyMap(element_type=CtyNumber())
    value = other_map_type.validate({"a": 1})
    with pytest.raises(CtyMapValidationError):
        map_type.validate(value)


def test_get_on_null_or_unknown_with_default() -> None:
    map_type = CtyMap(element_type=CtyString())
    null_value = CtyValue.null(map_type)
    unknown_value = CtyValue.unknown(map_type)
    default_value = CtyString().validate("default")

    assert map_type.get(null_value, "a", default=default_value) == default_value
    assert map_type.get(unknown_value, "a", default=default_value) == default_value


def test_get_on_null_or_unknown_without_default() -> None:
    map_type = CtyMap(element_type=CtyString())
    null_value = CtyValue.null(map_type)
    unknown_value = CtyValue.unknown(map_type)

    assert map_type.get(null_value, "a").is_null
    assert map_type.get(unknown_value, "a").is_null


def test_map_constructor_with_value_type_keyword() -> None:
    """Tests that the CtyMap constructor correctly handles the `element_type` keyword."""
    # This test corrects a failure where a test was using an old keyword `value_type`.
    map_type = CtyMap(element_type=CtyNumber())
    val = map_type.validate({"a": 123})
    assert val["a"].value == 123


# 🌊🪢🔚
