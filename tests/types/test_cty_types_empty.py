import pytest

from pyvider.cty.types import (
    CtyString,
    CtyNumber,
    CtyBool,
    CtyList,
    CtyMap,
    CtySet,
    CtyTuple,
    CtyObject,
    CtyDynamic,
    CtyCapsule, # Assuming CtyCapsule exists and should be tested
)


def test_empty_type_for_primitives():
    assert CtyString().is_empty_type() is False
    assert CtyNumber().is_empty_type() is False
    assert CtyBool().is_empty_type() is False


def test_empty_type_for_collections():
    assert CtyList(element_type=CtyString()).is_empty_type() is False
    assert CtyMap(key_type=CtyString(), value_type=CtyNumber()).is_empty_type() is False
    assert CtySet(element_type=CtyBool()).is_empty_type() is False


def test_empty_type_for_structural():
    assert CtyTuple((CtyString(), CtyNumber())).is_empty_type() is False
    assert CtyObject(attribute_types={"attr": CtyString()}).is_empty_type() is False


def test_empty_type_for_dynamic():
    assert CtyDynamic().is_empty_type() is True


def test_empty_type_for_capsule():
    # Assuming CtyCapsule is not an "empty" type by default
    # If CtyCapsule needs specific logic for is_empty_type, it should be implemented there.
    class MyData:
        pass
    assert CtyCapsule("MyDataCapsule", MyData).is_empty_type() is False
