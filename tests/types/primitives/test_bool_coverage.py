#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from pyvider.cty.types.primitives.bool import CtyBool
from pyvider.cty.values import UnknownValue


def test_validate_unknown_value() -> None:
    bool_type = CtyBool()
    unknown_value = UnknownValue()
    result = bool_type.validate(unknown_value)
    assert result.is_unknown, "Validating unknown value should return unknown CtyValue"
    assert result.type.equal(bool_type), "Result type should equal the original bool type"


# 🌊🪢🔚
