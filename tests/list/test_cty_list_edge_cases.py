#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

import pytest

from pyvider.cty.exceptions import CtyListValidationError
from pyvider.cty.types.collections import CtyList
from pyvider.cty.types.primitives import CtyString
from pyvider.cty.values.markers import UNREFINED_UNKNOWN


def test_list_validation_with_unrefined_unknown_value():
    """Test that UnrefinedUnknownValue produces a helpful error message."""
    list_type = CtyList(element_type=CtyString())

    with pytest.raises(CtyListValidationError) as exc_info:
        list_type.validate(UNREFINED_UNKNOWN)

    error_message = str(exc_info.value)

    # Check that the new helpful error message is present
    assert "Cannot use unknown/computed value" in error_message
    assert "Circular reference" in error_message
    assert "self-references" in error_message

    # Ensure the old unhelpful message is NOT present
    assert "UnrefinedUnknownValue" not in error_message


# 🌊🪢🔚
