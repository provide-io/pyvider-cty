#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Regression tests for CtyObject handling of unknown field values.

These tests ensure that CtyObject with mixed known/unknown fields maintains
correct is_unknown status at the object level. This is critical for proper
handling during Terraform plan/apply cycles where computed fields are unknown
during planning but the object structure itself is known."""

from pyvider.cty import CtyObject, CtyString, CtyValue
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack


def test_object_with_unknown_field_is_not_unknown() -> None:
    """Test that CtyObject with unknown fields is not marked as unknown at object level.

    Regression test for bug where CtyObject.validate() didn't explicitly set
    is_unknown=False, causing objects with unknown fields to be treated as
    entirely unknown.
    """
    # Create an object type with two string fields
    obj_type = CtyObject(
        attribute_types={
            "input_value": CtyString(),
            "computed_value": CtyString(),
        }
    )

    # Create object with one known field and one unknown field
    obj_value = {
        "input_value": CtyValue(vtype=CtyString(), value="known-value"),
        "computed_value": CtyValue.unknown(CtyString()),
    }

    # Validate the object
    validated = obj_type.validate(obj_value)

    # The object itself should NOT be unknown
    assert not validated.is_unknown, "Object with unknown fields should not be marked as unknown"

    # The object value should be a dict
    assert isinstance(validated.value, dict), "Object value should be a dict"

    # Individual fields should maintain their unknown status
    assert not validated.value["input_value"].is_unknown, "Known field should not be unknown"
    assert validated.value["computed_value"].is_unknown, "Unknown field should remain unknown"

    # Known field should have correct value
    assert validated.value["input_value"].value == "known-value"


def test_object_unknown_fields_marshal_unmarshal() -> None:
    """Test that object-level is_unknown status is preserved through marshal/unmarshal.

    This simulates what happens during Terraform plan/apply cycle where
    planned_state is marshaled to msgpack then unmarshaled in the apply phase.
    """
    # Create an object type
    obj_type = CtyObject(
        attribute_types={
            "input_value": CtyString(),
            "computed_value": CtyString(),
        }
    )

    # Create object with mixed known/unknown fields
    obj_value = {
        "input_value": CtyValue(vtype=CtyString(), value="test-value"),
        "computed_value": CtyValue.unknown(CtyString()),
    }

    # Validate to create CtyValue
    cty_val = obj_type.validate(obj_value)

    # Verify object is not unknown before marshal
    assert not cty_val.is_unknown, "Object should not be unknown before marshal"

    # Marshal to msgpack
    marshaled = cty_to_msgpack(cty_val, obj_type)

    # Unmarshal from msgpack
    unmarshaled = cty_from_msgpack(marshaled, obj_type)

    # Object should STILL not be unknown after unmarshal
    assert not unmarshaled.is_unknown, "Object should not be unknown after marshal/unmarshal"

    # Object value should still be a dict
    assert isinstance(unmarshaled.value, dict), "Object value should still be a dict"

    # Individual fields should maintain their status
    assert not unmarshaled.value["input_value"].is_unknown, "Known field should remain known"
    assert unmarshaled.value["computed_value"].is_unknown, "Unknown field should remain unknown"

    # Known field should have correct value
    assert unmarshaled.value["input_value"].value == "test-value"


def test_object_all_fields_unknown() -> None:
    """Test that object with all unknown fields is still not unknown at object level.

    Even when all fields are unknown, the object structure itself is known,
    so the object should not be marked as unknown.
    """
    obj_type = CtyObject(
        attribute_types={
            "field1": CtyString(),
            "field2": CtyString(),
        }
    )

    obj_value = {
        "field1": CtyValue.unknown(CtyString()),
        "field2": CtyValue.unknown(CtyString()),
    }

    validated = obj_type.validate(obj_value)

    # Object should not be unknown even though all fields are
    assert not validated.is_unknown, "Object should not be unknown even with all unknown fields"
    assert isinstance(validated.value, dict), "Object value should be a dict"
    assert validated.value["field1"].is_unknown, "Field 1 should be unknown"
    assert validated.value["field2"].is_unknown, "Field 2 should be unknown"


def test_explicitly_unknown_object() -> None:
    """Test that explicitly unknown CtyValue objects are handled correctly.

    When a CtyValue is explicitly created as unknown (not just containing
    unknown fields), it should remain unknown.
    """
    obj_type = CtyObject(
        attribute_types={
            "field": CtyString(),
        }
    )

    # Create explicitly unknown object
    unknown_obj = CtyValue.unknown(obj_type)

    # This should be unknown
    assert unknown_obj.is_unknown, "Explicitly unknown object should be unknown"

    # Validating an explicitly unknown object should preserve unknown status
    validated = obj_type.validate(unknown_obj)
    assert validated.is_unknown, "Explicitly unknown object should remain unknown after validation"


# 🌊🪢🔚
