#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


import unicodedata

from hypothesis import given, settings, strategies as st
import pytest

from pyvider.cty import CtyDynamic
from pyvider.cty.conversion import cty_to_native, infer_cty_type_from_raw

# Define a strategy for basic JSON-like data types that our CTY system can handle.
# This includes None, booleans, numbers (integers/floats), and text.
primitives = (
    st.none()
    | st.booleans()
    | st.floats(allow_nan=False, allow_infinity=False, width=32)
    | st.integers()
    | st.text()
)

# Define a recursive strategy for generating arbitrarily nested data structures.
# A `json_data` value can be a primitive, a list of `json_data`, or a dictionary
# with string keys and `json_data` values.
json_data = st.recursive(
    primitives,
    lambda children: st.lists(children) | st.dictionaries(st.text().filter(lambda x: x != ""), children),
    max_leaves=10,
)


def deep_prepare_for_comparison(data):
    """
    Recursively prepares data for comparison by:
    - Normalizing string keys and values to NFC form.
    - Wrapping floats in pytest.approx to handle precision differences.
    """
    if isinstance(data, dict):
        # CORRECTED: Normalize keys in addition to values.
        return {unicodedata.normalize("NFC", k): deep_prepare_for_comparison(v) for k, v in data.items()}
    if isinstance(data, list):
        return [deep_prepare_for_comparison(v) for v in data]
    if isinstance(data, float):
        return pytest.approx(data)
    if isinstance(data, str):
        return unicodedata.normalize("NFC", data)
    return data


@settings(deadline=500)
@given(native_data=json_data)
def test_conversion_roundtrip_is_lossless(native_data) -> None:
    """
    This property-based test verifies that for any generated native Python
    data structure, the conversion to a CtyValue and back to a native type
    results in a semantically identical data structure.

    This ensures the core data plane (`infer_cty_type_from_raw` and
    `cty_to_native`) is robust and correct.
    """
    try:
        # 1. Convert the native Python data into the CTY system.
        cty_value = CtyDynamic().validate(native_data)

        # 2. Convert the CtyValue back to a native Python object.
        roundtrip_native_data = cty_to_native(cty_value)

        # 3. Assert that the result is identical to the original input,
        #    after preparing both for a semantic comparison.
        assert deep_prepare_for_comparison(roundtrip_native_data) == deep_prepare_for_comparison(native_data)

    except Exception as e:
        pytest.fail(f"Conversion roundtrip failed for input:\n{native_data!r}\nError: {type(e).__name__}: {e}")


def test_infer_type_of_list_of_mixed_objects() -> None:
    """
    A specific regression test to ensure that a list of objects with
    varying keys correctly infers a list of dynamic objects, which
    is a common and important edge case.
    """
    mixed_list = [
        {"name": "Alice", "role": "admin"},
        {"name": "Bob", "permissions": ["read"]},
    ]

    inferred_type = infer_cty_type_from_raw(mixed_list)

    cty_value = inferred_type.validate(mixed_list)
    native_result = cty_to_native(cty_value)

    assert native_result == mixed_list


# 🌊🪢🔚
