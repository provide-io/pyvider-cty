#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from pyvider.cty.types.collections.map import CtyMap
from pyvider.cty.types.primitives import CtyString
from pyvider.cty.values.markers import UNREFINED_UNKNOWN


def test_map_validation_with_unrefined_unknown_value() -> None:
    """A bare unknown marker validates to an unknown map.

    Terraform sends unknown for every attribute that depends on for_each, a data
    source or another resource, and an outer type unwrapping its CtyValue leaves
    the marker bare. Raising here made any map attribute unusable in those
    configurations.
    """
    map_type = CtyMap(element_type=CtyString())

    result = map_type.validate(UNREFINED_UNKNOWN)

    assert result.is_unknown
    assert result.type.equal(map_type)


# 🌊🪢🔚
