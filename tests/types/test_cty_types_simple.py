#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


import pytest

from pyvider.cty import CtyBool, CtyNumber, CtyString
from pyvider.cty.exceptions import (
    CtyBoolValidationError,
    CtyNumberValidationError,
    CtyStringValidationError,
)


class TestCtyStringType:
    def setup_method(self) -> None:
        self.string_type = CtyString()

    def test_validate_invalid_string(self) -> None:
        with pytest.raises(CtyStringValidationError):
            self.string_type.validate(123)

    def test_validate_none_returns_null(self) -> None:
        # FIX: This test now asserts the correct behavior: validating None
        # should return a null CtyValue, not raise an error.
        result = self.string_type.validate(None)
        assert result.is_null

    def test_validate_valid_string(self) -> None:
        result = self.string_type.validate("hello")
        assert result.value == "hello"


class TestCtyNumberType:
    def setup_method(self) -> None:
        self.number_type = CtyNumber()

    def test_validate_invalid_number(self) -> None:
        with pytest.raises(CtyNumberValidationError):
            self.number_type.validate("hello")

    def test_validate_valid_number(self) -> None:
        result = self.number_type.validate(123)
        assert result.value == 123


class TestCtyBoolType:
    def setup_method(self) -> None:
        self.bool_type = CtyBool()

    def test_validate_invalid_bool(self) -> None:
        with pytest.raises(CtyBoolValidationError):
            self.bool_type.validate(123)

    def test_validate_valid_bool(self) -> None:
        result = self.bool_type.validate(True)
        assert result.value is True


# 🌊🪢🔚
