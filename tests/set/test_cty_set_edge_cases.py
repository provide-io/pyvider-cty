#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from pyvider.cty.types.collections import CtySet
from pyvider.cty.types.primitives import CtyString
from pyvider.cty.values.markers import UNREFINED_UNKNOWN


def test_set_validation_with_unrefined_unknown_value() -> None:
    """A bare unknown marker validates to an unknown set.

    Terraform sends unknown for every attribute that depends on for_each, a data
    source or another resource, and an outer type unwrapping its CtyValue leaves
    the marker bare. Raising here made any set attribute unusable in those
    configurations.
    """
    set_type = CtySet(element_type=CtyString())

    result = set_type.validate(UNREFINED_UNKNOWN)

    assert result.is_unknown
    assert result.type.equal(set_type)


# 🌊🪢🔚
