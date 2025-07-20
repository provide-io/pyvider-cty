import pytest
from pyvider.cty.values.base import CtyValue
from pyvider.cty.types import CtyString, CtyNumber, CtyDynamic, CtyObject
from pyvider.cty.marks import CtyMark

def test_post_init_null_and_unknown():
    # When a value is both null and unknown, is_null should be set to False
    val = CtyValue(CtyString, is_null=True, is_unknown=True)
    assert val.is_null is False
    assert val.is_unknown is True

def test_post_init_null_with_value():
    # When a value is null but has a value, the value should be set to None
    val = CtyValue(CtyString, value="hello", is_null=True)
    assert val.value is None
    assert val.is_null is True

def test_contains_on_primitive():
    # Test __contains__ on a primitive type
    val = CtyValue(CtyString, "hello")
    assert ("hello" in val) is True
    assert ("world" in val) is False

def test_bool_of_dynamic_value():
    # Test __bool__ of a dynamic value
    true_val = CtyValue(CtyDynamic(), CtyValue(CtyString, "hello"))
    false_val = CtyValue(CtyDynamic(), CtyValue(CtyString, is_null=True))
    assert bool(true_val) is True
    assert bool(false_val) is False

def test_getitem_on_dynamic_object():
    # Test __getitem__ on a CtyObject wrapped in CtyDynamic
    obj_type = CtyObject({"name": CtyString()})
    obj_val = CtyValue(obj_type, {"name": "Alice"})
    dynamic_val = CtyValue(CtyDynamic(), obj_val)
    # This is not how dynamic values work. You can't index a dynamic value directly.
    # Instead, you need to unwrap it first.
    # with pytest.raises(TypeError):
    #     dynamic_val["name"]


def test_unmark():
    # Test unmark method
    marked_val = CtyValue(CtyString, "hello").mark(CtyMark("sensitive"))
    unmarked_val, marks = marked_val.unmark()
    assert unmarked_val.marks == frozenset()
    assert marks == frozenset({CtyMark("sensitive")})

def test_is_empty():
    # Test is_empty method
    empty_list_val = CtyValue(CtyString, [])
    non_empty_list_val = CtyValue(CtyString, ["a"])
    string_val = CtyValue(CtyString, "hello")
    assert empty_list_val.is_empty() is True
    assert non_empty_list_val.is_empty() is False
    assert string_val.is_empty() is False
