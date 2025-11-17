#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

from hypothesis import given, strategies as st

from pyvider.cty.conversion.raw_to_cty import infer_cty_type_from_raw


@given(
    st.recursive(
        st.none()
        | st.booleans()
        | st.integers()
        | st.floats(allow_nan=False, allow_infinity=False)
        | st.text(),
        lambda children: st.lists(children) | st.dictionaries(st.text(), children),
        max_leaves=10,
    )
)
def test_infer_cty_type_from_raw_complex(value) -> None:
    """
    Tests that infer_cty_type_from_raw can handle complex, deeply nested data structures.
    """
    inferred_type = infer_cty_type_from_raw(value)
    assert inferred_type is not None


# 🌊🪢🔚
