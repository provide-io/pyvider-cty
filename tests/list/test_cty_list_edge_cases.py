#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#



from pyvider.cty.types.collections import CtyList
from pyvider.cty.types.primitives import CtyString
from pyvider.cty.values.markers import UNREFINED_UNKNOWN


def test_list_validation_with_unrefined_unknown_value():
    """A bare unknown marker validates to an unknown list.

    This used to raise, with an error naming circular references. It is not an error:
    terraform sends unknown for every attribute that depends on for_each, a data
    source or another resource, and an outer type unwrapping its CtyValue leaves the
    marker bare. Raising here made any list attribute unusable in those
    configurations.
    """
    list_type = CtyList(element_type=CtyString())

    result = list_type.validate(UNREFINED_UNKNOWN)

    assert result.is_unknown
    assert result.type.equal(list_type)


# 🌊🪢🔚
