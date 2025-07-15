import pytest
from pyvider.cty import (
    CtyObject, CtyList, CtyMap, CtyTuple, CtyString, CtyNumber, CtyBool,
    CtyAttributeValidationError, CtyListValidationError,
    CtyMapValidationError, CtyTupleValidationError
)
# Import the new helper from its canonical location.
from tests.diagnostics._helpers import assert_diagnostic

class TestValidationExceptionStructure:
    """
    TDD: These tests now use the assertion helper to verify the required
    structure and content for validation exceptions.
    """

    def test_attribute_validation_error_structure(self):
        """Verifies missing required attribute error message and type."""
        schema = CtyObject(attribute_types={"name": CtyString()})
        assert_diagnostic(
            schema_type=schema,
            invalid_config={},
            expected_error_type=CtyAttributeValidationError,
            expected_error_message="At name: Missing required attribute"
        )

    def test_list_validation_error_structure(self):
        """Verifies list element type mismatch error message and type."""
        schema = CtyList(element_type=CtyNumber())
        assert_diagnostic(
            schema_type=schema,
            invalid_config=[10, "twenty", 30],
            expected_error_type=CtyListValidationError,
            expected_error_message="At [1]: Number validation error: Cannot represent str value 'twenty' as Decimal"
        )

    def test_map_validation_error_structure(self):
        """Verifies map element type mismatch error message and type."""
        schema = CtyMap(element_type=CtyBool())
        assert_diagnostic(
            schema_type=schema,
            invalid_config={"a": True, "b": "not-a-bool"},
            expected_error_type=CtyMapValidationError,
            expected_error_message="At ['b']: Boolean validation error: Cannot convert string 'not-a-bool' to boolean"
        )

    def test_tuple_validation_error_structure(self):
        """Verifies tuple element type mismatch error message and type."""
        schema = CtyTuple(element_types=(CtyString(), CtyNumber()))
        assert_diagnostic(
            schema_type=schema,
            invalid_config=("valid", "not-a-number"),
            expected_error_type=CtyTupleValidationError,
            expected_error_message="At [1]: Number validation error: Cannot represent str value 'not-a-number' as Decimal"
        )
