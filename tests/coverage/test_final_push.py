import pytest
from pyvider.cty import CtyNumber, CtyString, CtyValue, CtyList, CtyBool, CtyDynamic, CtyObject, CtySet, CtyTuple
from pyvider.cty.exceptions import CtyValidationError
from pyvider.cty.marks import CtyMark
from pyvider.cty.values.base import CtyValue
from pyvider.cty.types.primitives.bool import CtyBool
from pyvider.cty.types.primitives.number import CtyNumber
from pyvider.cty.types.primitives.string import CtyString
from pyvider.cty.types.collections.list import CtyList
from pyvider.cty.types.collections.map import CtyMap
from pyvider.cty.types.collections.set import CtySet
from pyvider.cty.types.structural.object import CtyObject
from pyvider.cty.types.structural.tuple import CtyTuple
from pyvider.cty.types.structural.dynamic import CtyDynamic
from pyvider.cty.types.capsule import CtyCapsule
from pyvider.cty.path import CtyPath, GetAttrStep, IndexStep, KeyStep
from pyvider.cty.exceptions.encoding import (
    TransformationError,
    InvalidTypeError,
    AttributePathError,
)

def test_marks_coverage():
    # Test for marks branches that are not covered
    mark = CtyMark("a", {"b": "c"})
    assert mark.details == frozenset([("b", "c")])
    mark = CtyMark("a", ["b", "c"])
    assert mark.details == frozenset(["b", "c"])
    mark = CtyMark("a", "b")
    assert mark.details == frozenset(["b"])
    mark = CtyMark("a")
    assert repr(mark) == "CtyMark('a')"


def test_path_coverage_more():
    path = CtyPath([GetAttrStep("a")])
    assert str(path) == "a"
    path = CtyPath([IndexStep(0)])
    assert str(path) == "[0]"
    path = CtyPath([KeyStep("a")])
    assert str(path) == "['a']"
    with pytest.raises(AttributePathError):
        CtyPath([GetAttrStep("a")]).apply_path_type(CtyNumber())
    with pytest.raises(AttributePathError):
        CtyPath([IndexStep(0)]).apply_path_type(CtyString())
    with pytest.raises(AttributePathError):
        CtyPath([KeyStep("a")]).apply_path_type(CtyString())
    with pytest.raises(AttributePathError):
        CtyPath([GetAttrStep("a")]).apply_path(CtyValue.null(CtyObject({"a": CtyString()})))
    assert CtyPath([GetAttrStep("a")]).apply_path(CtyValue.unknown(CtyObject(attribute_types={"a": CtyString()}))).is_unknown
    with pytest.raises(AttributePathError):
        CtyPath([IndexStep(0)]).apply_path(CtyValue.null(CtyList(element_type=CtyString())))
    assert CtyPath([IndexStep(0)]).apply_path(CtyValue.unknown(CtyList(element_type=CtyString()))).is_unknown
    with pytest.raises(AttributePathError):
        CtyPath([KeyStep("a")]).apply_path(CtyValue.null(CtyMap(element_type=CtyString())))
    assert CtyPath([KeyStep("a")]).apply_path(CtyValue.unknown(CtyMap(element_type=CtyString()))).is_unknown


def test_types_coverage_more():
    with pytest.raises(CtyValidationError):
        CtyBool().validate(set())
    with pytest.raises(CtyValidationError):
        CtyNumber().validate(set())
    with pytest.raises(CtyValidationError):
        CtyString().validate(set())
    with pytest.raises(CtyValidationError):
        CtyList(element_type=CtyString()).validate(set())
    with pytest.raises(CtyValidationError):
        CtyList(element_type=CtyString()).validate(set())
    with pytest.raises(CtyValidationError):
        CtyMap(element_type=CtyString()).validate(1)
    with pytest.raises(CtyValidationError):
        CtySet(element_type=CtyString()).validate(1)
    with pytest.raises(CtyValidationError):
        CtyObject(attribute_types={"a": CtyString()}).validate(set())
    with pytest.raises(CtyValidationError):
        CtyCapsule("a", int).validate(set())
    with pytest.raises(CtyValidationError):
        CtyDynamic().validate(set())
    assert CtyCapsule("a", int).equal(CtyCapsule("b", int)) is False
    assert CtyCapsule("a", int).equal(CtyCapsule("a", str)) is False
    assert CtyCapsule("a", int).usable_as(CtyCapsule("b", int)) is False
    assert CtyCapsule("a", int).usable_as(CtyCapsule("a", str)) is False
    assert CtyCapsule("a", int)._to_wire_json() is None


def test_exceptions_coverage():
    with pytest.raises(TransformationError):
        raise TransformationError("a", schema=1, target_type=int)
    with pytest.raises(InvalidTypeError):
        raise InvalidTypeError("a", invalid_type=int)
    with pytest.raises(AttributePathError):
        raise AttributePathError("a", path="a", value=1)
