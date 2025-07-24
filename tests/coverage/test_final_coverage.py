"""
This test suite specifically targets remaining edge cases and error paths
to bring code coverage as close to 100% as possible.
"""
import re
import pytest

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyTuple,
    CtyValue,
)
from pyvider.cty.marks import CtyMark
from pyvider.cty.types.base import CtyType
from pyvider.cty.types.capsule import CtyCapsuleWithOps
from pyvider.cty.types.types_base import CtyTypeProtocol


class TestFinalCoverage:
    """Targeted tests for remaining uncovered lines."""

    def test_value_base_coverage(self) -> None:
        """Covers remaining lines in src/pyvider/cty/values/base.py"""
        val_null_with_value = CtyValue(vtype=CtyString(), is_null=True, value="should be removed")
        assert val_null_with_value.is_null and val_null_with_value.value is None

        class Opaque: pass
        ops_type = CtyCapsuleWithOps("Opaque", Opaque, equal_fn=lambda a, b: a is b)
        val1 = ops_type.validate(Opaque())
        val2 = ops_type.validate(Opaque())
        assert val1 != val2 and val1 == val1

        list_val = CtyList(element_type=CtyString()).validate(["a", "b"])
        dynamic_val = CtyDynamic().validate(list_val)
        assert len(dynamic_val) == 2

        map_val = CtyMap(element_type=CtyString()).validate({"a": "val_a", "b": "val_b"})
        iterated_values = {v.value for v in map_val}
        assert iterated_values == {"val_a", "val_b"}
        obj_val = CtyObject({"a": CtyString()}).validate({"a": "b"})
        with pytest.raises(TypeError, match="is not iterable"): list(obj_val)

        ops_type_hash = CtyCapsuleWithOps("Opaque", Opaque, hash_fn=lambda v: 12345)
        val_hash = ops_type_hash.validate(Opaque())
        assert hash(val_hash) == 12345

        true_val = CtyDynamic().validate(CtyBool().validate(True))
        false_val = CtyDynamic().validate(CtyBool().validate(False))
        assert true_val.is_true() and not true_val.is_false()
        assert not false_val.is_true() and false_val.is_false()

        # DEFINITIVE FIX: Use re.escape to handle special characters in the match string.
        with pytest.raises(TypeError, match=re.escape("'.without_key()' can only be used on CtyMap values.")):
            list_val.without_key("a")

    def test_types_base_coverage(self) -> None:
        """Covers remaining lines in src/pyvider/cty/types/types_base.py"""
        class MyType(CtyType):
            def validate(self, value): return CtyValue(self, value)
            def equal(self, other): return isinstance(other, MyType)
            def usable_as(self, other): return self.equal(other)
            def _to_wire_json(self): return "mytype"
        
        my_instance = MyType()
        assert isinstance(my_instance, CtyTypeProtocol)
        assert my_instance == MyType()
        assert my_instance != CtyString()
        assert hash(my_instance) == hash(MyType())
        assert repr(my_instance) == "MyType()"
