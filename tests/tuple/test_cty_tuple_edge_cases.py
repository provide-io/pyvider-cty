#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from pyvider.cty import CtyString, CtyTuple
from pyvider.cty.values.markers import UNREFINED_UNKNOWN


def test_tuple_validation_with_unrefined_unknown_value() -> None:
    """A bare unknown marker validates to an unknown tuple.

    Terraform sends unknown for every attribute that depends on for_each, a data
    source or another resource, and an outer type unwrapping its CtyValue leaves
    the marker bare. Raising here made any tuple attribute unusable in those
    configurations. See issue #3.
    """
    tuple_type = CtyTuple((CtyString(),))

    result = tuple_type.validate(UNREFINED_UNKNOWN)

    assert result.is_unknown
    assert result.type.equal(tuple_type)


# 🌊🪢🔚
