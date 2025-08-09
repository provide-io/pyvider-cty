import pytest
from pyvider.cty import (
    CtyMap,
    CtyNumber,
    CtySet,
    CtyString,
    CtyList,
    CtyDynamic,
    CtyObject,
    CtyTuple,
    CtyValue,
    CtyType,
    CtyBool,
)
from pyvider.cty.conversion.raw_to_cty import infer_cty_type_from_raw, _attrs_to_dict_safe


def test_infer_from_none():
    assert isinstance(infer_cty_type_from_raw(None), CtyDynamic)


def test_infer_from_list_of_mixed_types():
    inferred = infer_cty_type_from_raw([1, "a"])
    assert isinstance(inferred, CtyList)
    assert isinstance(inferred.element_type, CtyDynamic)


def test_infer_from_map_with_non_string_keys():
    inferred = infer_cty_type_from_raw({1: "a"})
    assert isinstance(inferred, CtyMap)
    # The value types are uniform (all string), so the element type should be CtyString.
    assert isinstance(inferred.element_type, CtyString)


def test_attrs_to_dict_safe_with_cty_type():
    with pytest.raises(TypeError):
        _attrs_to_dict_safe(CtyString())


def test_attrs_to_dict_safe_with_cty_value():
    with pytest.raises(TypeError):
        _attrs_to_dict_safe(CtyString().validate("h"))


def test_infer_from_unsupported_type():
    class Foo:
        pass
    assert isinstance(infer_cty_type_from_raw(Foo()), CtyDynamic)


def test_infer_from_list_of_lists():
    inferred = infer_cty_type_from_raw([[1], [2]])
    assert isinstance(inferred, CtyList)
    assert isinstance(inferred.element_type, CtyList)
    assert isinstance(inferred.element_type.element_type, CtyNumber)


# 🐍🎯🧪🪄
