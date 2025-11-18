#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

import pytest

from pyvider.cty import (
    CtyValidationError,
    parse_type_string_to_ctytype,
)

# This test now uses the more general CtyValidationError, as the parser
# raises specific subtypes of it, but this makes the test more robust.
INVALID_TYPE_STRINGS = [
    ("list(string, number)"),
    ("map(string, number)"),
    ("object(string)"),
    ("list(string"),
    ("object({name=})"),
]


@pytest.mark.parametrize("invalid_str", INVALID_TYPE_STRINGS)
def test_parser_failures(invalid_str: str) -> None:
    """Tests that the parser raises a validation error for malformed strings."""
    with pytest.raises(CtyValidationError):
        parse_type_string_to_ctytype(invalid_str)


# 🌊🪢🔚
