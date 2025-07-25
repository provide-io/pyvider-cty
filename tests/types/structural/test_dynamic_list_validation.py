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

        # The list contains CtyDynamic values, each wrapping a concrete CtyObject.
        element_0 = validated_list_value.value[0].value
        assert isinstance(element_0.type, CtyObject)
        assert element_0.type.attribute_types["role"].equal(CtyString())

        element_1 = validated_list_value.value[1].value
        assert isinstance(element_1.type, CtyObject)
        assert isinstance(element_1.type.attribute_types["permissions"], CtyList)

        element_2 = validated_list_value.value[2].value
        assert isinstance(element_2.type, CtyObject)
        assert element_2.type.attribute_types["role"].equal(CtyNumber())
