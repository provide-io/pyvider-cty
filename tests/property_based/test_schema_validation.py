#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from hypothesis import given, settings, strategies as st
import pytest

from pyvider.cty import CtyNumber, CtyObject, CtyString, CtyValidationError
from pyvider.cty.validation import validate_config

# A strategy for valid data matching a simple schema
valid_data_strategy = st.fixed_dictionaries(
    {"name": st.text(max_size=50), "age": st.integers(min_value=0, max_value=150)}
)

# A strategy for invalid data.
invalid_data_strategy = st.fixed_dictionaries(
    {
        "name": st.text(max_size=50),
        "age": st.text(alphabet=st.characters(min_codepoint=97, max_codepoint=122), min_size=1),
    }
)


@pytest.fixture(scope="module")
def simple_schema():
    """A simple CtyObject schema for validation tests."""
    return CtyObject(attribute_types={"name": CtyString(), "age": CtyNumber()})


@settings(deadline=5000)
@given(data=valid_data_strategy)
def test_schema_accepts_valid_data(simple_schema, data) -> None:
    """Verify that valid data structures pass validation without raising an error."""
    try:
        validate_config(simple_schema, data)
    except CtyValidationError as e:
        pytest.fail(f"Validation failed unexpectedly for valid data: {data}. Error: {e}")


@settings(deadline=5000)
@given(data=invalid_data_strategy)
def test_schema_rejects_invalid_data(simple_schema, data) -> None:
    """
    Verify that invalid data structures are rejected by raising a CtyValidationError.
    This test is now corrected to provide truly invalid data.
    """
    with pytest.raises(CtyValidationError):
        validate_config(simple_schema, data)


# 🌊🪢🔚
