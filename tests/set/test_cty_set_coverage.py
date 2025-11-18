#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

import pytest

from pyvider.cty.exceptions import CtySetValidationError
from pyvider.cty.types import CtyNumber, CtyString, CtyTuple
from pyvider.cty.types.collections.set import CtySet


def test_attrs_post_init_invalid_element_type() -> None:
    with pytest.raises(CtySetValidationError):
        CtySet(element_type="not_a_type")


def test_validate_with_unhashable_elements_in_list() -> None:
    """Verify that a set of tuples (which are unhashable CtyValues) can be created."""
    set_type = CtySet(element_type=CtyTuple((CtyString(),)))
    result = set_type.validate([("a",), ("b",)])
    assert len(result.value) == 2


def test_validate_with_cty_value_different_set_type() -> None:
    set_type = CtySet(element_type=CtyString())
    other_set_type = CtySet(element_type=CtyNumber())
    value = other_set_type.validate({1, 2, 3})
    with pytest.raises(CtySetValidationError):
        set_type.validate(value)


# 🌊🪢🔚
