#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TDD tests for fixing serialization of dynamic values containing lists.

This test suite focuses on the specific issue where CtyDynamic values
containing lists cause SerializationError during marshaling to protocol buffers."""

import pytest

from pyvider.cty import CtyDynamic
from pyvider.cty.codec import cty_to_msgpack
from pyvider.cty.exceptions import SerializationError
from pyvider.cty.values import CtyValue


class TestDynamicListSerialization:
    """
    TDD Contract: CtyDynamic values containing lists must serialize correctly
    to msgpack without causing SerializationError.
    """

    def test_dynamic_containing_simple_list_serializes_successfully(self) -> None:
        """
        TDD Contract: A CtyDynamic value wrapping a simple list of strings
        must serialize to msgpack without error.

        This is the core issue - lists in dynamic values are causing
        SerializationError in the Terraform provider workflow.
        """
        # Arrange: Create a dynamic value containing a list
        dynamic_type = CtyDynamic()
        list_value = ["web", "api", "production"]
        validated_dynamic = dynamic_type.validate(list_value)

        # Act & Assert: Serialization must succeed
        try:
            serialized = cty_to_msgpack(validated_dynamic, dynamic_type)
            assert serialized is not None
            assert isinstance(serialized, bytes)
        except SerializationError:
            pytest.fail("CtyDynamic containing list failed to serialize - this is the bug we need to fix")

    def test_dynamic_containing_nested_object_with_list_serializes_successfully(
        self,
    ) -> None:
        """
        TDD Contract: A CtyDynamic value wrapping an object that contains lists
        must serialize to msgpack without error.

        This tests the more complex case from the Terraform provider where
        configuration objects contain list attributes.
        """
        # Arrange: Create a dynamic value containing an object with a list
        dynamic_type = CtyDynamic()
        config_value = {
            "app_name": "my_app",
            "replicas": 3,
            "enabled": True,
            "tags": ["web", "api", "production"],  # This is the problematic list
        }
        validated_dynamic = dynamic_type.validate(config_value)

        # Act & Assert: Serialization must succeed
        try:
            serialized = cty_to_msgpack(validated_dynamic, dynamic_type)
            assert serialized is not None
            assert isinstance(serialized, bytes)
        except SerializationError:
            pytest.fail(
                "CtyDynamic containing object with list failed to serialize - this is the Terraform provider bug"
            )

    def test_dynamic_roundtrip_with_list_preserves_data(self) -> None:
        """
        TDD Contract: A CtyDynamic value containing a list must roundtrip
        through serialization/deserialization preserving the original data.
        """
        from pyvider.cty.codec import cty_from_msgpack

        # Arrange: Create a dynamic value containing a list
        dynamic_type = CtyDynamic()
        original_value = ["web", "api", "production"]
        validated_dynamic = dynamic_type.validate(original_value)

        # Act: Serialize and deserialize
        serialized = cty_to_msgpack(validated_dynamic, dynamic_type)
        deserialized = cty_from_msgpack(serialized, dynamic_type)

        # Assert: Data must be preserved
        assert deserialized.type.equal(dynamic_type)
        # The inner value should be a CtyValue wrapping a list
        inner_value = deserialized.value
        assert hasattr(inner_value, "value")
        # Convert back to native Python for comparison
        from pyvider.cty.conversion.adapter import cty_to_native

        native_result = cty_to_native(inner_value)
        assert native_result == original_value

    def test_dynamic_with_empty_list_serializes_successfully(self) -> None:
        """
        TDD Contract: A CtyDynamic value containing an empty list
        must serialize without error.
        """
        # Arrange: Create a dynamic value containing an empty list
        dynamic_type = CtyDynamic()
        empty_list = []
        validated_dynamic = dynamic_type.validate(empty_list)

        # Act & Assert: Serialization must succeed
        serialized = cty_to_msgpack(validated_dynamic, dynamic_type)
        assert serialized is not None
        assert isinstance(serialized, bytes)

    def test_dynamic_with_nested_lists_serializes_successfully(self) -> None:
        """
        TDD Contract: A CtyDynamic value containing nested lists
        must serialize without error.
        """
        # Arrange: Create a dynamic value containing nested lists
        dynamic_type = CtyDynamic()
        nested_list = [["env", "vars"], ["debug", "flags"]]
        validated_dynamic = dynamic_type.validate(nested_list)

        # Act & Assert: Serialization must succeed
        serialized = cty_to_msgpack(validated_dynamic, dynamic_type)
        assert serialized is not None
        assert isinstance(serialized, bytes)

    def test_dynamic_list_unknown_value_serializes_successfully(self) -> None:
        """
        TDD Contract: When recursion prevention returns CtyValue.unknown(),
        the unknown dynamic value must serialize correctly.

        This tests our recursion fix doesn't break serialization.
        """
        # Arrange: Create an unknown dynamic value (like our recursion prevention creates)
        dynamic_type = CtyDynamic()
        unknown_dynamic = CtyValue.unknown(dynamic_type)

        # Act & Assert: Serialization must succeed
        serialized = cty_to_msgpack(unknown_dynamic, dynamic_type)
        assert serialized is not None
        assert isinstance(serialized, bytes)

    def test_dynamic_validation_does_not_hit_recursion_limit_for_simple_list(
        self,
    ) -> None:
        """
        TDD Contract: Simple lists should not trigger recursion prevention.
        Our recursion fix should only activate for genuine infinite recursion,
        not for normal nested data structures.
        """
        # Arrange: Create a simple list that should validate normally
        dynamic_type = CtyDynamic()
        simple_list = ["tag1", "tag2", "tag3"]

        # Act: Validate the list
        validated_dynamic = dynamic_type.validate(simple_list)

        # Assert: Should not be unknown (which would indicate recursion prevention triggered)
        assert not validated_dynamic.is_unknown
        assert validated_dynamic.value is not None

        # And it should serialize successfully
        serialized = cty_to_msgpack(validated_dynamic, dynamic_type)
        assert serialized is not None


# 🌊🪢🔚
