#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

import pytest

from pyvider.cty import CtyType, CtyValidationError


def normalize_whitespace(text: str) -> str:
    """Collapses all whitespace into single spaces for robust comparison."""
    return " ".join(text.split())


def assert_diagnostic(
    *,
    schema_type: CtyType,
    invalid_config: object,
    expected_error_type: type[CtyValidationError],
    expected_error_message: str,
) -> None:
    """
    Asserts that validating a config against a schema raises a specific
    CtyValidationError with the expected message, ignoring whitespace differences.
    """
    with pytest.raises(expected_error_type) as exc_info:
        schema_type.validate(invalid_config)

    actual_message = str(exc_info.value)

    # Normalize both strings before comparison
    normalized_actual = normalize_whitespace(actual_message)
    normalized_expected = normalize_whitespace(expected_error_message)

    # Allow partial matching if expected message is a prefix of actual
    assert normalized_expected in normalized_actual or normalized_actual == normalized_expected, (
        f"\nNormalized messages do not match:"
        f"\n- Expected (substring): '{normalized_expected}'"
        f"\n- Got:                  '{normalized_actual}'"
        f"\n---"
        f"\n- Original Expected:\n{expected_error_message}"
        f"\n- Original Got:\n{actual_message}"
    )


# 🌊🪢🔚
