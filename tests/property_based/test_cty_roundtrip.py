#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from decimal import Decimal
import unicodedata

from hypothesis import given, settings, strategies as st
import pytest

from pyvider.cty import CtyDynamic
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack
from pyvider.cty.conversion import cty_to_native

# A hypothesis strategy for generating JSON-like data structures.
# This covers primitives, lists, and objects (dicts) recursively.
json_strategy = st.recursive(
    st.none() | st.booleans() | st.integers() | st.floats(allow_nan=False, allow_infinity=False) | st.text(),
    lambda children: st.lists(children) | st.dictionaries(st.text().filter(lambda s: s), children),
    max_leaves=15,
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
    if isinstance(data, Decimal):
        return pytest.approx(float(data))
    if isinstance(data, str):
        return unicodedata.normalize("NFC", data)
    return data


@settings(deadline=1000, max_examples=200)
@given(native_data=json_strategy)
def test_cty_wire_format_roundtrip(native_data) -> None:
    """
    Verifies that any JSON-like native Python data structure can be
    converted to a CtyValue, serialized to MessagePack, deserialized,
    and converted back to the original native structure without loss.

    This is the most critical property test for the data plane.
    """
    # Define a dynamic schema that can accept any inferred type.
    schema = CtyDynamic()

    try:
        # 1. Convert native Python data into the CTY type system.
        cty_value_original = schema.validate(native_data)

        # 2. Marshal the CtyValue to its MessagePack wire representation.
        msgpack_bytes = cty_to_msgpack(cty_value_original, schema)

        # 3. Unmarshal the MessagePack bytes back into a CtyValue.
        cty_value_deserialized = cty_from_msgpack(msgpack_bytes, schema)

        # 4. Convert the deserialized CtyValue back to a native Python object.
        native_data_roundtripped = cty_to_native(cty_value_deserialized)

        # 5. Assert that the final native object is equivalent to the original,
        #    after preparing both for a semantic comparison.
        assert deep_prepare_for_comparison(native_data_roundtripped) == deep_prepare_for_comparison(
            native_data
        )

    except Exception as e:
        pytest.fail(f"CTY round-trip failed for input:\n{native_data!r}\nError: {type(e).__name__}: {e}")


# 🌊🪢🔚
