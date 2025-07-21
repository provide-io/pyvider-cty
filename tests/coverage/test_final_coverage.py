"""
This test suite specifically targets remaining edge cases and error paths
to bring code coverage as close to 100% as possible.
"""
import pytest

from pyvider.cty import (
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyTuple,
    CtyValue,
)
from pyvider.cty.exceptions import CtyAttributeValidationError, CtyTypeMismatchError
from pyvider.cty.types.base import CtyType
from pyvider.cty.values import CtyValue

class TestFinalCoverage:
    """Targeted tests for remaining uncovered lines."""

    def test_string_coverage(self) -> None:
        """Covers remaining lines in src/pyvider/cty/types/primitives/string.py"""
        s_type = CtyString()
        assert s_type.validate(CtyValue.null(CtyDynamic())).is_null
        assert s_type.validate(CtyValue.unknown(CtyDynamic())).is_unknown
        assert not s_type.equal(CtyNumber())
        assert not s_type.usable_as(CtyNumber())

    def test_dynamic_coverage(self) -> None:
        """Covers remaining lines in src/pyvider/cty/types/structural/dynamic.py"""
        d_type = CtyDynamic()
        assert not d_type.usable_as(CtyString())
        assert d_type.is_dynamic_type()

    def test_object_coverage(self) -> None:
        """Covers remaining lines in src/pyvider/cty/types/structural/object.py"""
        o_type = CtyObject(attribute_types={"a": CtyString()})
        assert o_type.validate(CtyValue.null(CtyDynamic())).is_null
        assert o_type.validate(CtyValue.unknown(CtyDynamic())).is_unknown
        # FIX: Correctly test the error path by passing a non-CtyValue
        with pytest.raises(CtyTypeMismatchError):
             o_type.get_attribute("not a value", "a")
        assert not o_type.equal(CtyString())
        assert not o_type.usable_as(CtyString())
        assert not o_type.is_primitive_type()

    def test_tuple_coverage(self) -> None:
        """Covers remaining lines in src/pyvider/cty/types/structural/tuple.py"""
        t_type = CtyTuple(element_types=(CtyString(),))
        with pytest.raises(TypeError):
            t_type.element_at(t_type.validate(("a",)), "invalid")
        assert not t_type.equal(CtyString())
        assert not t_type.usable_as(CtyString())
        assert t_type[0].equal(CtyString())

    def test_value_base_coverage(self) -> None:
        """Covers remaining lines in src/pyvider/cty/values/base.py"""
        assert ("a" in CtyString().validate("a")) is True
        dyn_list = CtyDynamic().validate(CtyList(element_type=CtyString()).validate(["a"]))
        assert len(dyn_list) == 1
        map_val = CtyMap(element_type=CtyString()).validate({"a": "b"})
        assert [v.value for v in map_val] == ["b"]
        with pytest.raises(TypeError):
            map_val.append("c")
