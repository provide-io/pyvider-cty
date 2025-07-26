import pytest
from pyvider.cty import (
    CtyList,
    CtySet,
    CtyString,
    CtyTuple,
    CtyValue,
    CtyNumber,
    CtyBool,
    CtyDynamic,
)
from pyvider.cty.functions import distinct, flatten
from pyvider.cty.exceptions import CtyFunctionError


class TestDistinct:
    def test_distinct_with_list(self):
        l = CtyList(element_type=CtyString()).validate(["a", "b", "a"])
        assert distinct(l).raw_value == ["a", "b"]

    def test_distinct_with_set(self):
        s = CtySet(element_type=CtyNumber()).validate({1, 2, 1})
        assert distinct(s).raw_value == [1, 2]

    def test_distinct_with_tuple(self):
        t = CtyTuple(element_types=(CtyString(), CtyString(), CtyString())).validate(
            ("a", "b", "a")
        )
        assert distinct(t).raw_value == ["a", "b"]

    def test_distinct_with_null_unknown(self):
        assert distinct(CtyValue.null(CtyList(element_type=CtyString()))).is_null
        assert distinct(CtyValue.unknown(CtyList(element_type=CtyString()))).is_unknown

    def test_distinct_with_unhashable(self):
        l = CtyList(element_type=CtyList(element_type=CtyString())).validate([["a"], ["a"]])
        with pytest.raises(CtyFunctionError, match="not hashable"):
            distinct(l)

    def test_distinct_wrong_type(self):
        with pytest.raises(CtyFunctionError):
            distinct(CtyString().validate("hello"))
