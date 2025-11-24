#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

import pytest

from pyvider.cty import (
    CtyBool,
    CtyList,
    CtyMap,
    CtyNumber,
    CtySet,
    CtyString,
)


@pytest.fixture
def string_type() -> CtyString:
    return CtyString()


@pytest.fixture
def list_of_string_type(string_type: CtyString) -> CtyList:
    return CtyList(element_type=string_type)


def test_empty_value_for_collections(list_of_string_type) -> None:
    assert CtyList(element_type=CtyString()).validate([]).is_empty() is True
    assert CtyMap(element_type=CtyNumber()).validate({}).is_empty() is True
    assert CtySet(element_type=CtyBool()).validate(set()).is_empty() is True


# 🌊🪢🔚
