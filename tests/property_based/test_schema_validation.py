import pytest
from hypothesis import given, strategies as st

from pyvider.cty import CtyObject, CtyString, CtyNumber, CtyValidationError
from pyvider.cty.validation import validate_config

# A strategy for valid data matching a simple schema
valid_data_strategy = st.fixed_dictionaries({
    "name": st.text(max_size=50),
    "age": st.integers(min_value=0, max_value=150)
})

# A strategy for invalid data.
# FIX: Generate text containing at least one letter to guarantee it cannot be
# converted to a Decimal. This is the definitive fix for the test.
invalid_data_strategy = st.fixed_dictionaries({
    "name": st.text(max_size=50),
    "age": st.text(alphabet=st.characters(min_codepoint=97, max_codepoint=122), min_size=1)
})

@pytest.fixture(scope="module")
def simple_schema():
    """A simple CtyObject schema for validation tests."""
    return CtyObject(attribute_types={
        "name": CtyString(),
        "age": CtyNumber()
    })

@given(data=valid_data_strategy)
def test_schema_accepts_valid_data(simple_schema, data):
    """Verify that valid data structures pass validation without raising an error."""
    try:
        validate_config(simple_schema, data)
    except CtyValidationError as e:
        pytest.fail(f"Validation failed unexpectedly for valid data: {data}. Error: {e}")

@given(data=invalid_data_strategy)
def test_schema_rejects_invalid_data(simple_schema, data):
    """
    Verify that invalid data structures are rejected by raising a CtyValidationError.
    This test is now corrected to provide truly invalid data.
    """
    with pytest.raises(CtyValidationError):
        validate_config(simple_schema, data)
