#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Property-based test to ensure any future caching in the type inference
logic is safe and does not cause correctness regressions."""

import unicodedata

from hypothesis import given, strategies as st

from pyvider.cty.conversion import infer_cty_type_from_raw
from pyvider.cty.types import (
    CtyObject,
    CtyString,
)


# A strategy that generates two dictionaries that share the same keys
# but have values of different, incompatible types. This is the exact
# scenario that would break a naive, key-only caching mechanism.
@st.composite
def same_keys_different_types(draw):
    keys = draw(st.lists(st.text(min_size=1, max_size=10), min_size=1, max_size=5, unique=True))
    dict1 = {key: draw(st.text()) for key in keys}
    dict2 = {key: draw(st.lists(st.integers())) for key in keys}
    return (dict1, dict2)


@given(data=same_keys_different_types())
def test_inference_is_correct_for_same_keys_different_types(data) -> None:
    """
    Ensures that inferring types for two dicts with identical keys but
    different value types produces two distinct and correct schemas.
    """
    dict1, dict2 = data

    # Infer type for the first dictionary (all string keys)
    type1 = infer_cty_type_from_raw(dict1)

    # Infer type for the second dictionary (all string keys)
    type2 = infer_cty_type_from_raw(dict2)

    # The inferred types must be different CtyObject schemas.
    assert not type1.equal(type2)

    # Verify the correctness of each inferred type.
    assert isinstance(type1, CtyObject)
    assert all(v.equal(CtyString()) for v in type1.attribute_types.values())

    assert isinstance(type2, CtyObject)

    # DEFINITIVE FIX:
    # The test must use the same NFC normalization for key lookups that the
    # inference function uses internally. This prevents KeyErrors for
    # characters with multiple Unicode representations.
    for key, raw_value in dict2.items():
        expected_attr_type = infer_cty_type_from_raw(raw_value)
        normalized_key = unicodedata.normalize("NFC", key)
        actual_attr_type = type2.attribute_types[normalized_key]
        assert actual_attr_type.equal(expected_attr_type)


# 🌊🪢🔚
