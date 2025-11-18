#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TDD: Ensures that key lookups and comparisons are aware of Unicode normalization."""

from pyvider.cty import CtyMap, CtyObject, CtyString
from pyvider.cty.functions import lookup


class TestUnicodeNormalizationConsistency:
    # NFD (e + combining acute) vs NFC (é)
    NFD_KEY = "e\u0301"
    NFC_KEY = "\u00e9"

    def test_object_validation_is_normalization_aware(self) -> None:
        """TDD: Object validation should treat NFD and NFC keys as identical."""
        schema = CtyObject(attribute_types={self.NFC_KEY: CtyString()})
        # The input dict uses the NFD form of the key.
        validated_obj = schema.validate({self.NFD_KEY: "value"})
        # The internal representation should use the canonical NFC form.
        assert self.NFC_KEY in validated_obj.value
        assert validated_obj.value[self.NFC_KEY].value == "value"

    def test_map_validation_is_normalization_aware(self) -> None:
        """TDD: Map validation should treat NFD and NFC keys as identical."""
        schema = CtyMap(element_type=CtyString())
        validated_map = schema.validate({self.NFD_KEY: "value"})
        assert self.NFC_KEY in validated_map.value
        assert validated_map.value[self.NFC_KEY].value == "value"

    def test_lookup_function_is_normalization_aware(self) -> None:
        """TDD: The `lookup` function should find keys regardless of normalization form."""
        schema = CtyMap(element_type=CtyString())
        # The map is created with the canonical NFC key.
        map_val = schema.validate({self.NFC_KEY: "found"})
        # We look up using the NFD key.
        lookup_key = CtyString().validate(self.NFD_KEY)
        default_val = CtyString().validate("default")

        result = lookup(map_val, lookup_key, default_val)
        assert result.value == "found"


# 🌊🪢🔚
