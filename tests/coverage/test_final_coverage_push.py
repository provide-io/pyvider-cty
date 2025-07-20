import pytest

from pyvider.cty import (
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyValue,
)
from pyvider.cty.exceptions import (
    AttributePathError,
    CtyAttributeValidationError,
    CtyListValidationError,
    CtyMapValidationError,
    CtySetValidationError,
    CtyTypeMismatchError,
    CtyValidationError,
)
from pyvider.cty.path import CtyPath, GetAttrStep
from pyvider.cty.types.capsule import CtyCapsule


def test_validation_exceptions_with_context() -> None:
    list_error = CtyListValidationError("bad list", path=CtyPath.index(0))
    assert "At [0]: bad list" in str(list_error)
    map_error = CtyMapValidationError("bad map", path=CtyPath.key("a"))
    assert "At ['a']: bad map" in str(map_error)
    type_mismatch = CtyTypeMismatchError(
        "mismatch", actual_type=CtyString(), expected_type=CtyNumber()
    )
    assert "Expected number, got string" in str(type_mismatch)
    attr_error = CtyAttributeValidationError(
        "bad attr", path=CtyPath.get_attr("user").child("name")
    )
    assert "At user.name: bad attr" in str(attr_error)


def test_path_edge_cases() -> None:
    with pytest.raises(ValueError):
        GetAttrStep("")
    obj_type = CtyObject(attribute_types={"name": CtyString()})
    path = CtyPath.get_attr("name")
    assert path.apply_path_type(obj_type) == CtyString()
    with pytest.raises(AttributePathError):
        path.apply_path_type(CtyString())
    with pytest.raises(AttributePathError):
        CtyPath.key("k").apply_path_type(CtyString())
    with pytest.raises(AttributePathError):
        CtyPath.key(1).apply_path(CtyString().validate("s"))


def test_capsule_type() -> None:
    class MyData:
        pass

    cap_type = CtyCapsule("MyData", MyData)
    assert cap_type.usable_as(CtyDynamic())
    assert not cap_type.usable_as(CtyString())
    assert cap_type.validate(CtyValue.null(cap_type)).is_null
    assert cap_type.validate(CtyValue.unknown(cap_type)).is_unknown
    with pytest.raises(CtyValidationError):
        cap_type.validate(CtyString().validate("foo"))


def test_collection_edge_cases() -> None:
    list_type = CtyList(element_type=CtyDynamic())
    val = list_type.validate([1, "s", True])
    assert len(val.value) == 3
    map_type = CtyMap(element_type=CtyNumber())
    with pytest.raises(CtyMapValidationError):
        map_type.validate({None: 1})
    set_type = CtySet(element_type=CtyDynamic())
    with pytest.raises(CtySetValidationError, match="unhashable"):
        set_type.validate([[]])


def test_value_base_edge_cases() -> None:
    val = CtyList(element_type=CtyList(element_type=CtyString())).validate([["a"]])
    with pytest.raises(TypeError, match="unhashable type: 'CtyValue\\[list\\]'"):
        hash(val)
    assert ("a" in CtyString().validate("abc")) is True
    assert (123 in CtyNumber().validate(123)) is True
