#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

from pyvider.cty import CtyObject, CtyString
from pyvider.cty.marks import CtyMark


def test_object_validation_preserves_marks() -> None:
    """
    TDD: Verifies that CtyObject.validate preserves marks from input CtyValues.
    This is the core contract for data fidelity.
    """
    schema = CtyObject(attribute_types={"data": CtyString()})

    # Create a CtyString that is already marked as sensitive.
    marked_string = CtyString().validate("secret").mark(CtyMark("sensitive"))

    # Create an input dictionary for the object validator.
    input_dict = {"data": marked_string}

    # Validate the object.
    validated_object = schema.validate(input_dict)

    # Assert that the mark on the inner value was preserved.
    inner_value = validated_object.value["data"]
    assert inner_value.has_mark(CtyMark("sensitive")), "Mark was lost during object validation"


# 🌊🪢🔚
