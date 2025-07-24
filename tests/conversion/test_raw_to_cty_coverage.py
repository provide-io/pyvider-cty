from pyvider.cty import CtyMap, CtyNumber, CtySet, CtyString
from pyvider.cty.conversion.raw_to_cty import infer_cty_type_from_raw


def test_infer_set_of_strings() -> None:
    inferred_type = infer_cty_type_from_raw({"a", "b"})
    assert isinstance(inferred_type, CtySet)
    assert isinstance(inferred_type.element_type, CtyString)


def test_infer_map_with_non_identifier_keys() -> None:
    inferred_type = infer_cty_type_from_raw({"a-b": 1})
    assert isinstance(inferred_type, CtyMap)
    assert isinstance(inferred_type.element_type, CtyNumber)


def test_infer_empty_dict() -> None:
    from pyvider.cty import CtyObject

    inferred_type = infer_cty_type_from_raw({})
    assert isinstance(inferred_type, CtyObject)
    assert inferred_type.attribute_types == {}
