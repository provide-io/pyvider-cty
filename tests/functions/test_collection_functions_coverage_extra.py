import pytest

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtySet,
    CtyString,
    CtyTuple,
    CtyValue,
)
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import (
    concat,
    contains,
    distinct,
    flatten,
    keys,
    length,
    slice,
    values,
)


class TestCollectionFunctionsCoverage:
    def test_distinct_error_paths(self) -> None:
        with pytest.raises(CtyFunctionError, match="distinct: input must be a list, set, or tuple"):
            distinct(CtyString().validate("hello"))
        assert distinct(CtyValue.null(CtyList(element_type=CtyString()))).is_null

    def test_flatten_error_paths(self) -> None:
        with pytest.raises(CtyFunctionError, match="flatten: input must be a list or tuple"):
            flatten(CtyString().validate("hello"))
        assert flatten(CtyValue.null(CtyList(element_type=CtyDynamic()))).is_null
        
        # Test with unknown inner list
        unknown_inner_list = CtyList(element_type=CtyDynamic()).validate([CtyValue.unknown(CtyList(element_type=CtyString()))])
        assert flatten(unknown_inner_list).is_unknown

        # Test with empty inner lists
        empty_inner_lists = CtyList(element_type=CtyDynamic()).validate([[], []])
        assert flatten(empty_inner_lists).raw_value == []

    def test_length_error_paths(self) -> None:
        # This test now correctly checks that a truly invalid type (CtyNumber) fails.
        with pytest.raises(CtyFunctionError, match="length: input must be a collection or string"):
            length(CtyNumber().validate(123))
        assert length(CtyValue.unknown(CtyList(element_type=CtyString()))).is_unknown

    def test_slice_error_paths(self) -> None:
        with pytest.raises(CtyFunctionError, match="slice: input must be a list or tuple"):
            slice(CtyString().validate("abc"), CtyNumber().validate(0), CtyNumber().validate(1))
        
        list_val = CtyList(element_type=CtyString()).validate(["a", "b"])
        with pytest.raises(CtyFunctionError, match="slice: start and end must be numbers"):
            slice(list_val, CtyString().validate("0"), CtyNumber().validate(1))

        assert slice(CtyValue.unknown(CtyList(element_type=CtyString())), CtyNumber().validate(0), CtyNumber().validate(1)).is_unknown

    def test_concat_error_paths(self) -> None:
        with pytest.raises(CtyFunctionError, match="concat: all arguments must be lists or tuples"):
            concat(CtyString().validate("a"), CtyList(element_type=CtyString()).validate(["b"]))
        
        assert concat(CtyValue.unknown(CtyList(element_type=CtyString()))).is_unknown
        assert concat(CtyList(element_type=CtyString()).validate([])).raw_value == []

    def test_contains_error_paths(self) -> None:
        with pytest.raises(CtyFunctionError, match="contains: collection must be a list, set, or tuple"):
            contains(CtyString().validate("a"), CtyString().validate("a"))
        assert contains(CtyValue.unknown(CtyList(element_type=CtyString())), CtyString().validate("a")).is_unknown

    def test_keys_error_paths(self) -> None:
        with pytest.raises(CtyFunctionError, match="keys: input must be a map or object"):
            keys(CtyString().validate("a"))
        assert keys(CtyValue.unknown(CtyMap(element_type=CtyString()))).is_unknown

    def test_values_error_paths(self) -> None:
        with pytest.raises(CtyFunctionError, match="values: input must be a map or object"):
            values(CtyString().validate("a"))
        assert values(CtyValue.unknown(CtyMap(element_type=CtyString()))).is_unknown
        
        # Test with non-dict internal value
        map_type = CtyMap(element_type=CtyString())
        bad_val = CtyValue(map_type, "not-a-dict")
        with pytest.raises(CtyFunctionError, match="values: input value is not a map or object"):
            values(bad_val)
