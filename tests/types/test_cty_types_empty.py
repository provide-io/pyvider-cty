from pyvider.cty.types import (
    CtyBool,
    CtyCapsule,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
)

# FIX: The `is_empty_type` method was removed during refactoring.
# The correct way to test for emptiness is on a CtyValue instance
# using the `is_empty()` method.

def test_empty_value_for_primitives():
    assert CtyString().validate("").is_empty() is True
    assert CtyString().validate("a").is_empty() is False
    # Numbers and Bools are never considered "empty"
    assert CtyNumber().validate(0).is_empty() is False
    assert CtyBool().validate(False).is_empty() is False

def test_empty_value_for_collections():
    assert CtyList(element_type=CtyString()).validate([]).is_empty() is True
    assert CtyMap(key_type=CtyString(), value_type=CtyNumber()).validate({}).is_empty() is True
    assert CtySet(element_type=CtyBool()).validate(set()).is_empty() is True

def test_empty_value_for_structural():
    assert CtyTuple(element_types=()).validate(()).is_empty() is True
    assert CtyObject(attribute_types={}).validate({}).is_empty() is True

def test_empty_value_for_dynamic():
    # A dynamic value is empty if the value it contains is empty.
    assert CtyDynamic().validate("").is_empty() is True
    assert CtyDynamic().validate([]).is_empty() is True
    assert CtyDynamic().validate({}).is_empty() is True
    assert CtyDynamic().validate("not empty").is_empty() is False

def test_empty_value_for_capsule():
    class MyData: pass
    # Capsule types are never considered empty unless they are null.
    assert CtyCapsule("MyDataCapsule", MyData).validate(MyData()).is_empty() is False
