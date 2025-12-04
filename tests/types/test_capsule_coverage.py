#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


import pytest

from pyvider.cty.exceptions import CtyValidationError
from pyvider.cty.types.capsule import CtyCapsule


class MyObject:
    pass


class MyOtherObject:
    pass


def test_validate_with_cty_value_different_capsule_type() -> None:
    capsule_type = CtyCapsule("MyObject", MyObject)
    other_capsule_type = CtyCapsule("MyOtherObject", MyOtherObject)
    value = other_capsule_type.validate(MyOtherObject())
    with pytest.raises(CtyValidationError):
        capsule_type.validate(value)


def test_to_wire_json() -> None:
    capsule_type = CtyCapsule("MyObject", MyObject)
    assert capsule_type._to_wire_json() is None


# 🌊🪢🔚
