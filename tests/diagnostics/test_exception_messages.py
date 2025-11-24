#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

from pyvider.cty import (
    CtyBool,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyTuple,
    CtyTypeMismatchError,
)
from pyvider.cty.exceptions import (
    CtyAttributeValidationError,
    CtyListValidationError,
    CtyMapValidationError,
    CtyTupleValidationError,
)
from tests.diagnostics._helpers import assert_diagnostic


class TestValidationExceptionStructure:
    def test_attribute_validation_error_structure(self) -> None:
        """Verifies object attribute error message and type."""
        schema = CtyObject({"name": CtyString(), "age": CtyNumber()})
        assert_diagnostic(
            schema_type=schema,
            invalid_config={"name": "test", "age": "not-a-number"},
            expected_error_type=CtyAttributeValidationError,
            expected_error_message="At age: Number validation error: Cannot represent str value 'not-a-number' as Decimal",
        )

    def test_list_validation_error_structure(self) -> None:
        """Verifies list element type mismatch error message and type."""
        schema = CtyList(element_type=CtyNumber())
        assert_diagnostic(
            schema_type=schema,
            invalid_config=[1, 2, "three"],
            expected_error_type=CtyListValidationError,
            expected_error_message="At [2]: Number validation error: Cannot represent str value 'three' as Decimal",
        )

    def test_map_validation_error_structure(self) -> None:
        """Verifies map element type mismatch error message and type."""
        schema = CtyMap(element_type=CtyBool())
        assert_diagnostic(
            schema_type=schema,
            invalid_config={"a": True, "b": "not-a-bool"},
            expected_error_type=CtyMapValidationError,
            expected_error_message="At ['b']: Boolean validation error: Cannot convert str to bool.",
        )

    def test_tuple_validation_error_structure(self) -> None:
        """Verifies tuple element type mismatch error message and type."""
        schema = CtyTuple((CtyString(), CtyNumber()))
        assert_diagnostic(
            schema_type=schema,
            invalid_config=["a", "b"],
            expected_error_type=CtyTupleValidationError,
            expected_error_message="At [1]: Number validation error: Cannot represent str value 'b' as Decimal",
        )

    def test_validation_exception_context_str(self) -> None:
        """Integrates and fixes tests for exception string formatting."""
        type_mismatch = CtyTypeMismatchError("mismatch", actual_type=CtyString(), expected_type=CtyNumber())
        assert "Expected number, got string" in str(type_mismatch)


# 🌊🪢🔚
