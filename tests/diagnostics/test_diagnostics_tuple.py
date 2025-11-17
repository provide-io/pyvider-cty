#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

from pyvider.cty import CtyBool, CtyList, CtyNumber, CtyString, CtyTuple
from pyvider.cty.exceptions import CtyTupleValidationError

from ._helpers import assert_diagnostic


class TestTupleDiagnostics:
    def test_incorrect_element_count(self) -> None:
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
            expected_error_message="Expected 2 elements, got 1",
        )

    def test_wrong_type_at_tuple_index(self) -> None:
        """
        Tests that a tuple with the wrong element type at a specific index
        produces a correctly formatted diagnostic.
        """
        schema = CtyTuple((CtyString(), CtyNumber(), CtyBool()))
        config = ["hostname.com", 8080, "not-a-bool"]

        assert_diagnostic(
            schema_type=schema,
            invalid_config=config,
            expected_error_type=CtyTupleValidationError,
            expected_error_message="At [2]: Boolean validation error: Cannot convert str to bool",
        )

    def test_error_in_collection_within_tuple(self) -> None:
        """
        Tests that a diagnostic for a nested collection within a tuple
        has the correct path.
        """
        schema = CtyTuple(
            (
                CtyString(),
                CtyList(element_type=CtyNumber()),
            )
        )
        config = ["list-name", [1, "two", 3]]

        assert_diagnostic(
            schema_type=schema,
            invalid_config=config,
            expected_error_type=CtyTupleValidationError,
            expected_error_message="At [1][1]: Number validation error: Cannot represent str value 'two' as Decimal",
        )


# 🌊🪢🔚
