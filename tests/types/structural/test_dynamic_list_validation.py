#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from pyvider.cty import CtyDynamic, CtyList, CtyNumber, CtyObject, CtyString


class TestDynamicListValidation:
    def test_ctylist_of_dynamic_preserves_inferred_concrete_types(self) -> None:
        list_of_dynamic_type = CtyList(element_type=CtyDynamic())
        raw_data = [
            {"name": "Alice", "role": "admin"},
            {"name": "Bob", "permissions": ["read", "write"]},
            {"name": "Charlie", "role": 123},
        ]
        validated_list_value = list_of_dynamic_type.validate(raw_data)

        element_0 = validated_list_value.value[0].value
        # Corrected: This should be an object because keys are strings.
        assert isinstance(element_0.type, CtyObject)
        assert element_0.type.attribute_types["role"].equal(CtyString())

        element_1 = validated_list_value.value[1].value
        # Corrected: This is an object because the value types are not uniform.
        assert isinstance(element_1.type, CtyObject)
        assert isinstance(element_1.type.attribute_types["permissions"], CtyList)

        element_2 = validated_list_value.value[2].value
        # Corrected: This is an object because the value types are not uniform.
        assert isinstance(element_2.type, CtyObject)
        assert element_2.type.attribute_types["role"].equal(CtyNumber())


# 🌊🪢🔚
