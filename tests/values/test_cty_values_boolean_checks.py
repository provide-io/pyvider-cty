#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

import pytest

from pyvider.cty import CtyBool, CtyDynamic, CtyString, CtyValue


@pytest.fixture
def bool_type() -> CtyBool:
    return CtyBool()


@pytest.fixture
def dynamic_type() -> CtyDynamic:
    return CtyDynamic()


def test_is_true_and_is_false_with_booleans(bool_type: CtyBool) -> None:
    true_val = CtyValue(bool_type, True)
    assert true_val.is_true() is True
    assert true_val.is_false() is False
    false_val = CtyValue(bool_type, False)
    assert false_val.is_true() is False
    assert false_val.is_false() is True


def test_is_true_and_is_false_with_dynamic_booleans(bool_type: CtyBool, dynamic_type: CtyDynamic) -> None:
    dyn_true_val = CtyValue(dynamic_type, CtyValue(bool_type, True))
    assert dyn_true_val.is_true() is True
    assert dyn_true_val.is_false() is False
    dyn_false_val = CtyValue(dynamic_type, CtyValue(bool_type, False))
    assert dyn_false_val.is_true() is False
    assert dyn_false_val.is_false() is True


def test_is_true_and_is_false_with_non_booleans() -> None:
    non_bool_values = [CtyString().validate("true"), CtyString().validate("")]
    for val in non_bool_values:
        assert val.is_true() is False
        assert val.is_false() is False


def test_is_true_and_is_false_with_null_and_unknown(bool_type: CtyBool) -> None:
    null_val = CtyValue.null(bool_type)
    assert null_val.is_true() is False
    assert null_val.is_false() is False
    unknown_val = CtyValue.unknown(bool_type)
    assert unknown_val.is_true() is False
    assert unknown_val.is_false() is False


# 🌊🪢🔚
