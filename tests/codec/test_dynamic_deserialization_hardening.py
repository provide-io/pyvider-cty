#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TDD: Enforces strict deserialization for CtyDynamic values, failing on any
malformed payload as go-cty does."""

import json

import msgpack
import pytest

from pyvider.cty import CtyDynamic, CtyValidationError
from pyvider.cty.codec import cty_from_msgpack
from pyvider.cty.exceptions import DeserializationError


class TestStrictDynamicDeserialization:
    def test_dynamic_deserialization_with_malformed_type_json_raises_error(
        self,
    ) -> None:
        """TDD: A malformed type spec (invalid JSON) must raise DeserializationError."""
        payload = [b"{not-json", "some_value"]
        packed_bytes = msgpack.packb(payload, use_bin_type=True)

        with pytest.raises(
            DeserializationError,
            match="Failed to decode dynamic value type spec from JSON",
        ):
            cty_from_msgpack(packed_bytes, CtyDynamic())

    def test_dynamic_deserialization_with_invalid_type_structure_raises_error(
        self,
    ) -> None:
        """TDD: A valid JSON type spec that is not a valid cty type must raise CtyValidationError."""
        type_spec_bytes = json.dumps(["list"]).encode("utf-8")  # Missing element type
        payload = [type_spec_bytes, ["a", "b"]]
        packed_bytes = msgpack.packb(payload, use_bin_type=True)

        with pytest.raises(CtyValidationError, match="Invalid Terraform type specification"):
            cty_from_msgpack(packed_bytes, CtyDynamic())

    def test_dynamic_deserialization_with_value_mismatch_raises_error(self) -> None:
        """TDD: A valid type spec with a non-conforming value must raise CtyValidationError."""
        type_spec_bytes = json.dumps("number").encode("utf-8")
        payload = [type_spec_bytes, "this-is-not-a-number"]
        packed_bytes = msgpack.packb(payload, use_bin_type=True)

        with pytest.raises(CtyValidationError, match="Cannot represent str"):
            cty_from_msgpack(packed_bytes, CtyDynamic())


# 🌊🪢🔚
