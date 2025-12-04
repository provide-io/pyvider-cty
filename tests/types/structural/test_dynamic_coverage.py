#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


import pytest

from pyvider.cty.exceptions import DeserializationError
from pyvider.cty.types import CtyDynamic


def test_validate_with_wire_format_invalid_json() -> None:
    dynamic_type = CtyDynamic()
    value = [b"{not-json}", "hello"]
    # With the hardened validate method, this should now raise a DeserializationError,
    # not fall back to inference.
    with pytest.raises(
        DeserializationError,
        match="Failed to decode dynamic value type spec from JSON during validation",
    ):
        dynamic_type.validate(value)


# 🌊🪢🔚
