#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TDD Test Suite for Deserialization Robustness and Go-Cty Compatibility.

These tests are designed to fail with the current implementation and define
the desired, more robust behavior for the MessagePack deserializer."""

from decimal import Decimal
import json

import msgpack  # type: ignore
import pytest

from pyvider.cty import (
    CtyDynamic,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyValue,
)
from pyvider.cty.codec import cty_from_msgpack
from pyvider.cty.exceptions import CtyValidationError


# --- TDD Tests for Issue #7: Dynamic Deserialization Robustness ---
class TestDynamicDeserializationRobustness:
    """
    These tests ensure cty_from_msgpack fails on malformed
    dynamic value payloads, matching go-cty's strictness.
    """

    def test_dynamic_deserialization_with_invalid_type_structure(self) -> None:
        """
        TDD: If the type spec is valid JSON but not a valid cty type structure,
        it should raise a specific error.
        """
        # `["list"]` is valid JSON but invalid as a cty type spec (needs 2 elements).
        type_spec_bytes = json.dumps(["list"]).encode("utf-8")
        payload = [type_spec_bytes, ["a", "b"]]
        packed_bytes = msgpack.packb(payload, use_bin_type=True)

        # This should fail during the type parsing stage.
        with pytest.raises(CtyValidationError, match="Invalid Terraform type specification"):
            cty_from_msgpack(packed_bytes, CtyDynamic())

    def test_dynamic_deserialization_with_value_mismatch(self) -> None:
        """
        TDD: If the type spec is valid but the value does not conform to it,
        a validation error should be raised.
        """
        type_spec_bytes = json.dumps("number").encode("utf-8")
        payload = [type_spec_bytes, "this-is-not-a-number"]
        packed_bytes = msgpack.packb(payload, use_bin_type=True)

        # This should fail during the final `actual_type.validate(value)` step.
        with pytest.raises(CtyValidationError, match="Cannot represent str"):
            cty_from_msgpack(packed_bytes, CtyDynamic())


# --- TDD Tests for Issue #3: MessagePack Compatibility ---
class TestGoCtyCompatibility:
    """
    These tests define compatibility requirements for deserializing payloads
    as they are typically encoded by go-cty.
    """

    def test_deserialization_of_go_cty_number_as_bytes(self) -> None:
        """
        TDD: go-cty often encodes numbers as UTF-8 bytes to preserve precision.
        Our deserializer must handle this.
        """
        # Simulate a `go-cty` number encoded as msgpack bytes.
        packed_bytes = msgpack.packb(b"123.456789", use_bin_type=True)

        # This will fail if CtyNumber.validate does not accept bytes.
        deserialized_val = cty_from_msgpack(packed_bytes, CtyNumber())

        assert deserialized_val.type.equal(CtyNumber())
        assert deserialized_val.value == Decimal("123.456789")

    def test_deserialization_of_go_cty_object_with_missing_optional_attr(self) -> None:
        """
        TDD: go-cty omits optional attributes that are null. Our deserializer
        must correctly reconstruct the object with a null value for that attribute.
        """
        schema = CtyObject(
            attribute_types={"name": CtyString(), "age": CtyNumber()},
            optional_attributes={"age"},
        )

        # This payload simulates a go-cty object where the optional 'age' is omitted.
        payload = {"name": "Alice"}
        packed_bytes = msgpack.packb(payload, use_bin_type=True)

        # This will fail if the CtyObject.validate logic does not correctly
        # inject a null value for the missing optional attribute.
        deserialized_val = cty_from_msgpack(packed_bytes, schema)

        assert isinstance(deserialized_val, CtyValue)
        assert deserialized_val.is_null is False
        assert deserialized_val.is_unknown is False

        # Check that the 'age' attribute exists and is null.
        assert "age" in deserialized_val.value
        assert deserialized_val["age"].is_null is True
        assert deserialized_val["name"].value == "Alice"


# 🌊🪢🔚
