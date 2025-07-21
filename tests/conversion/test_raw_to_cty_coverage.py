import pytest
from pyvider.cty import CtySet, CtyString
from pyvider.cty.conversion.raw_to_cty import infer_cty_type_from_raw


from pyvider.cty import CtyMap, CtyNumber


def test_infer_set_of_strings():
    inferred_type = infer_cty_type_from_raw({"a", "b"})
    assert isinstance(inferred_type, CtySet)
    assert isinstance(inferred_type.element_type, CtyString)


def test_infer_map_with_non_identifier_keys():
    inferred_type = infer_cty_type_from_raw({"a-b": 1})
    assert isinstance(inferred_type, CtyMap)
    assert isinstance(inferred_type.element_type, CtyNumber)


def test_infer_empty_dict():
    from pyvider.cty import CtyObject
    inferred_type = infer_cty_type_from_raw({})
    assert isinstance(inferred_type, CtyObject)
    assert inferred_type.attribute_types == {}
