#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


import pytest

from pyvider.cty import CtyBool, CtyDynamic, CtyString, CtyValue
from pyvider.cty.exceptions import CtyBoolValidationError


class TestCtyBool:
    def setup_method(self) -> None:
        self.bool_type = CtyBool()

    @pytest.mark.parametrize(
        "input_val, expected",
        [
            (True, True),
            (False, False),
            ("true", True),
            ("false", False),
            ("TRUE", True),
            ("FALSE", False),
            (1, True),
            (0, False),
            (1.0, True),
            (0.0, False),
        ],
    )
    def test_validate_valid_values(self, input_val, expected) -> None:
        result = self.bool_type.validate(input_val)
        assert result.value is expected, f"Expected {expected}, but got {result.value}"

    @pytest.mark.parametrize(
        "input_val",
        [
            "not a bool",
            123,
            -1,
            2.0,
            [],
            {},
        ],
    )
    def test_validate_invalid_values(self, input_val) -> None:
        with pytest.raises(CtyBoolValidationError):
            self.bool_type.validate(input_val)

    def test_validate_none_returns_null(self) -> None:
        # FIX: This test now asserts the correct behavior: validating None
        # should return a null CtyValue, not raise an error.
        result = self.bool_type.validate(None)
        assert result.is_null, "Validating None should return a null CtyValue"

    def test_validate_cty_value(self) -> None:
        assert self.bool_type.validate(self.bool_type.validate(True)).value is True, (
            "Double validation of True should preserve the value"
        )
        assert self.bool_type.validate(self.bool_type.validate(False)).value is False, (
            "Double validation of False should preserve the value"
        )
        assert self.bool_type.validate(CtyValue.null(CtyBool())).is_null, (
            "Validating null CtyValue should remain null"
        )
        assert self.bool_type.validate(CtyValue.unknown(CtyBool())).is_unknown, (
            "Validating unknown CtyValue should remain unknown"
        )

    def test_equal(self) -> None:
        assert self.bool_type.equal(CtyBool()), "CtyBool instances should be equal to each other"
        assert not self.bool_type.equal(CtyString()), "CtyBool should not be equal to CtyString"

    def test_usable_as(self) -> None:
        assert self.bool_type.usable_as(CtyBool()), "CtyBool should be usable as CtyBool"
        assert self.bool_type.usable_as(CtyDynamic()), "CtyBool should be usable as CtyDynamic"
        assert not self.bool_type.usable_as(CtyString()), "CtyBool should not be usable as CtyString"


# 🌊🪢🔚
