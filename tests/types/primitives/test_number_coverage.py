#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

from pyvider.cty.types.primitives.number import CtyNumber
from pyvider.cty.values import UnknownValue


def test_validate_unknown_value() -> None:
    number_type = CtyNumber()
    unknown_value = UnknownValue()
    result = number_type.validate(unknown_value)
    assert result.is_unknown, "Validating unknown value should return unknown CtyValue"
    assert result.type.equal(number_type), "Result type should equal the original number type"


# 🌊🪢🔚
