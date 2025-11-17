#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

import pytest

from pyvider.cty.exceptions import CtyStringValidationError
from pyvider.cty.types.primitives.string import CtyString
from pyvider.cty.values import UnknownValue


def test_validate_unknown_value() -> None:
    string_type = CtyString()
    unknown_value = UnknownValue()
    result = string_type.validate(unknown_value)
    assert result.is_unknown, "Validating unknown value should return unknown CtyValue"
    assert result.type.equal(string_type), "Result type should equal the original string type"


def test_validate_with_bytes() -> None:
    string_type = CtyString()
    value = b"hello"
    result = string_type.validate(value)
    assert result.value == "hello", f"Expected 'hello', but got {result.value}"


def test_validate_with_exception() -> None:
    string_type = CtyString()

    class BadString:
        def __str__(self) -> str:
            raise ValueError("bad string")

    with pytest.raises(CtyStringValidationError, match=r"Cannot convert BadString to string\."):
        string_type.validate(BadString())


# 🌊🪢🔚
