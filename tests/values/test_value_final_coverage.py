"""
This test suite specifically targets all remaining edge cases and error paths
in the CtyValue class to ensure 100% test coverage.
"""
import re
import pytest

from pyvider.cty import (
    CtyBool, CtyDynamic, CtyList, CtyMap, CtyNumber, CtyObject,
    CtyString, CtyTuple, CtyValue
)
from pyvider.cty.marks import CtyMark
from pyvider.cty.types.capsule import CtyCapsuleWithOps

class TestFinalValueCoverage:
    """Targeted tests for remaining uncovered lines in src/pyvider/cty/values/base.py."""

    def test_post_init_null_with_value(self) -> None:
        val = CtyValue(vtype=CtyString(), is_null=True, value="should be removed")
        assert val.is_null and val.value is None

    def test_eq_with_capsule_ops(self) -> None:
        class Opaque: pass
        ops_type = CtyCapsuleWithOps("Opaque", Opaque, equal_fn=lambda a, b: a is b)
        val1 = ops_type.validate(Opaque())
        val2 = ops_type.validate(Opaque())
        assert val1 != val2 and val1 == val1

    def test_len_on_dynamic_value(self) -> None:
        list_val = CtyList(element_type=CtyString()).validate(["a", "b"])
        dynamic_val = CtyDynamic().validate(list_val)
        assert len(dynamic_val) == 2

    def test_iter_on_map_and_uniterable(self) -> None:
        map_val = CtyMap(element_type=CtyString()).validate({"a": "val_a", "b": "val_b"})
        iterated_values = {v.value for v in map_val}
        assert iterated_values == {"val_a", "val_b"}
        obj_val = CtyObject({"a": CtyString()}).validate({"a": "b"})
        with pytest.raises(TypeError, match="is not iterable"): list(obj_val)

    def test_hash_with_capsule_ops(self) -> None:
        class Opaque: pass
        ops_type = CtyCapsuleWithOps("Opaque", Opaque, hash_fn=lambda v: 12345)
        val = ops_type.validate(Opaque())
        assert hash(val) == 12345

    def test_is_true_false_on_dynamic(self) -> None:
        true_val = CtyDynamic().validate(CtyBool().validate(True))
        false_val = CtyDynamic().validate(CtyBool().validate(False))
        assert true_val.is_true() and not true_val.is_false()
        assert not false_val.is_true() and false_val.is_false()

    def test_helpers_on_wrong_type(self) -> None:
        list_val = CtyList(element_type=CtyString()).validate(["a"])
        map_val = CtyMap(element_type=CtyString()).validate({"a": "b"})
        
        # Test map helpers on list
        with pytest.raises(TypeError, match=re.escape("'.with_key()' can only be used on CtyMap values.")):
            list_val.with_key("b", "c")
        with pytest.raises(TypeError, match=re.escape("'.without_key()' can only be used on CtyMap values.")):
            list_val.without_key("a")

        # Test list helpers on map
        with pytest.raises(TypeError, match=re.escape("'.append()' can only be used on CtyList values.")):
            map_val.append("c")
        with pytest.raises(TypeError, match=re.escape("'.with_element_at()' can only be used on CtyList values.")):
            map_val.with_element_at(0, "d")

    def test_with_element_at_out_of_bounds(self) -> None:
        list_val = CtyList(element_type=CtyString()).validate(["a"])
        with pytest.raises(IndexError):
            list_val.with_element_at(5, "z")
