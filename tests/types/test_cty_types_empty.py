#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

from pyvider.cty.types import CtyBool, CtyList, CtyMap, CtyNumber, CtySet, CtyString


def test_empty_value_for_collections() -> None:
    assert CtyList(element_type=CtyString()).validate([]).is_empty() is True
    assert CtyMap(element_type=CtyNumber()).validate({}).is_empty() is True
    assert CtySet(element_type=CtyBool()).validate(set()).is_empty() is True


# 🌊🪢🔚
