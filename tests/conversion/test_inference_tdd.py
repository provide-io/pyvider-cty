#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


import pytest

from pyvider.cty import (
    CtyDynamic,
    CtyList,
    CtyObject,
    CtyValue,
)
from pyvider.cty.conversion.raw_to_cty import infer_cty_type_from_raw
from pyvider.cty.exceptions import CtyValidationError


def test_infer_list_of_objects_with_optional_and_mismatched_types() -> None:
    list_of_objects = [
        {"id": 1, "name": "Alice", "status": "active"},
        {"id": 2, "name": "Bob", "role": "admin"},
        {"id": 3, "name": "Charlie", "status": 100},
    ]

    inferred_type = infer_cty_type_from_raw(list_of_objects)
    assert isinstance(inferred_type, CtyList)
    assert isinstance(inferred_type.element_type, CtyDynamic)

    try:
        validated_value = inferred_type.validate(list_of_objects)
        assert isinstance(validated_value, CtyValue)

        # Access the inner CtyValue objects directly (they are wrapped in CtyDynamic)
        element_0 = validated_value.value[0].value
        assert isinstance(element_0.type, CtyObject)
        assert "status" in element_0.type.attribute_types
        assert "role" not in element_0.type.attribute_types

        element_1 = validated_value.value[1].value
        assert isinstance(element_1.type, CtyObject)
        assert "role" in element_1.type.attribute_types
        assert "status" not in element_1.type.attribute_types
    except CtyValidationError as e:
        pytest.fail(f"Validation with the inferred type failed: {e}")


# 🌊🪢🔚
