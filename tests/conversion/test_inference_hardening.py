#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TDD Test Suite for Hardening Type Inference Logic.

This suite defines the required strict behavior for:
1. Correct primitive type inference precedence (bool vs. int).
2. Correct structural type inference for dictionaries (object vs. map)."""

import attrs

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyString,
)
from pyvider.cty.conversion import infer_cty_type_from_raw


@attrs.define
class MyAttrsClass:
    """A simple attrs class for testing."""

    name: str
    value: int


class TestInferenceHardening:
    """TDD tests to enforce correct type inference logic."""

    def test_bool_is_inferred_before_int(self) -> None:
        """
        TDD: Ensures that a Python `bool` is inferred as CtyBool, not CtyNumber.
        This tests the precedence in the inference logic.
        """
        inferred_type = infer_cty_type_from_raw(True)
        assert isinstance(inferred_type, CtyBool), "Boolean value was incorrectly inferred as CtyNumber."

    def test_string_keyed_dict_inference_logic(self) -> None:
        """
        TDD: A dictionary with all-string keys should be inferred as a CtyObject
        to preserve the named attributes.
        """
        # Case 1: Uniform value types (should still be CtyObject)
        uniform_dict = {"key1": "value1", "key2": "value2"}
        inferred_uniform = infer_cty_type_from_raw(uniform_dict)
        assert isinstance(inferred_uniform, CtyObject), (
            "String-keyed dict with uniform values was not inferred as an Object."
        )
        assert inferred_uniform.attribute_types["key1"].equal(CtyString())

        # Case 2: Mixed value types (should be CtyObject)
        mixed_dict = {"key1": "value1", "key2": 123}
        inferred_mixed = infer_cty_type_from_raw(mixed_dict)
        assert isinstance(inferred_mixed, CtyObject), (
            "String-keyed dict with mixed values was not inferred as an Object."
        )
        assert inferred_mixed.attribute_types["key1"].equal(CtyString())
        assert inferred_mixed.attribute_types["key2"].equal(CtyNumber())

    def test_non_string_keyed_dict_is_map(self) -> None:
        """
        TDD: A dictionary with any non-string keys MUST be inferred as a CtyMap.
        The element type should be unified from the value types.
        """
        # Case: Mixed value types
        mixed_dict = {1: "value1", "key2": 123}
        inferred_mixed = infer_cty_type_from_raw(mixed_dict)
        assert isinstance(inferred_mixed, CtyMap)
        assert isinstance(inferred_mixed.element_type, CtyDynamic), (
            "Map with mixed values should have a CtyDynamic element type."
        )


# 🌊🪢🔚
