#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

import unicodedata

import pytest

from pyvider.cty.types.primitives import CtyString
from pyvider.cty.values import CtyValue

# Test cases with strings that have different representations but normalize to the same NFC form
TEST_CASES = [
    ("e\u0301", "\u00e9"),  # NFD (e + combining acute) -> NFC (é)
    ("a\u0308", "\u00e4"),  # NFD (a + combining diaeresis) -> NFC (ä)
    ("\u212b", "\u00c5"),  # Angstrom Sign -> A-ring (via NFC compatibility)
    # Decomposed Hangul vs pre-composed
    ("한", "한"),  # These are the correct composable Jamo
    # FIX: Use the correct composable Jamo characters (U+1100, U+1173, U+11AF)
    # instead of the Compatibility Jamo which do not compose.
    ("\u1100\u1173\u11af", "글"),
    # String that is already NFC
    ("hello", "hello"),
]


@pytest.mark.parametrize("input_str, expected_normalized_str", TEST_CASES)
def test_string_normalization_on_validate(input_str: str, expected_normalized_str: str) -> None:
    """Tests that CtyString().validate() normalizes input strings."""
    cty_string_type = CtyString()
    validated_value: CtyValue = cty_string_type.validate(input_str)
    # The string should be normalized to NFC, which is the canonical form.
    assert validated_value.value == unicodedata.normalize("NFC", expected_normalized_str), (
        f"Expected normalized string {unicodedata.normalize('NFC', expected_normalized_str)!r}, but got {validated_value.value!r}"
    )


# 🌊🪢🔚
