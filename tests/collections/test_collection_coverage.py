#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

import pytest

from pyvider.cty import CtyList, CtyMap, CtyNumber, CtyString
from pyvider.cty.exceptions import (
    CtyListValidationError,
    CtyMapValidationError,
    InvalidTypeError,
)


def test_list_validate_ctyvalue_wrong_type() -> None:
    list_type = CtyList(element_type=CtyString())
    map_value = CtyMap(element_type=CtyString()).validate({})
    with pytest.raises(CtyListValidationError):
        list_type.validate(map_value)


def test_map_validate_non_dict_input() -> None:
    map_type = CtyMap(element_type=CtyNumber())
    with pytest.raises(CtyMapValidationError):
        map_type.validate([1, 2, 3])


def test_map_constructor_validation() -> None:
    with pytest.raises(InvalidTypeError):
        CtyMap(element_type="not a type")


# 🌊🪢🔚
