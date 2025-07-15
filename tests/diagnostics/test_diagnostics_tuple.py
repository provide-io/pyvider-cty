import pytest
from pyvider.cty import CtyTuple, CtyString, CtyNumber, CtyBool, CtyList, CtyTupleValidationError
from ._helpers import assert_diagnostic

class TestTupleDiagnostics:
    def test_incorrect_element_count(self):
        """
        Tests that a tuple with the wrong number of elements produces a
        correctly formatted diagnostic.
        """
        schema = CtyTuple(element_types=(CtyString(), CtyNumber()))
        config = ["just-one-element"]

        assert_diagnostic(
            schema_type=schema,
            invalid_config=config,
            expected_error_type=CtyTupleValidationError,
            expected_error_message="Expected 2 elements, got 1"
        )

    def test_wrong_type_at_tuple_index(self):
        """
        Tests that a tuple with the wrong element type at a specific index
        produces a correctly formatted diagnostic.
        """
        schema = CtyTuple(element_types=(CtyString(), CtyNumber(), CtyBool()))
        config = ["hostname.com", 8080, "not-a-bool"]

        assert_diagnostic(
            schema_type=schema,
            invalid_config=config,
            expected_error_type=CtyTupleValidationError,
            expected_error_message="At [2]: Boolean validation error: Cannot convert string 'not-a-bool' to boolean"
        )

    def test_error_in_collection_within_tuple(self):
        """
        Tests that an error deep inside a nested collection within a tuple
        produces a correctly formatted diagnostic with a full path.
        """
        schema = CtyTuple(element_types=(
            CtyString(),
            CtyList(element_type=CtyNumber())
        ))
        config = ("metadata", [10, 20, "thirty"])

        assert_diagnostic(
            schema_type=schema,
            invalid_config=config,
            expected_error_type=CtyTupleValidationError,
            expected_error_message="At [1][2]: Number validation error: Cannot represent str value 'thirty' as Decimal"
        )
