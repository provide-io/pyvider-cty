"""
Comprehensive test suite for all standard library functions to ensure
parity with go-cty.
"""
import pytest

from pyvider.cty import (
    BytesCapsule, CtyBool, CtyDynamic, CtyList, CtyMap, CtyNumber, CtyObject,
    CtySet, CtyString, CtyTuple, CtyValue
)
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import (
    byteslen, bytesslice, chunklist, coalesce, coalescelist, compact,
    csvdecode, element, equal, formatdate, greater_than,
    greater_than_or_equal_to, hasindex, index, int_fn, join, jsondecode,
    jsonencode, less_than, less_than_or_equal_to, lookup, max_fn, merge, min_fn,
    not_equal, regexreplace, replace, reverse, setproduct, split, timeadd,
    zipmap
)

# Helper functions for creating CtyValues to improve test readability
def S(v): return CtyString().validate(v)
def N(v): return CtyNumber().validate(v)
def B(v): return CtyBool().validate(v)
def L(t, v): return CtyList(element_type=t).validate(v)
def M(t, v): return CtyMap(element_type=t).validate(v)
def Set(t, v): return CtySet(element_type=t).validate(v)

class TestComparisonFunctions:
    def test_equal(self):
        assert equal(N(5), N(5)).is_true()
        assert equal(S("a"), S("b")).is_false()
        assert equal(CtyValue.unknown(CtyNumber()), N(5)).is_unknown

    def test_not_equal(self):
        assert not_equal(N(5), N(5)).is_false()
        assert not_equal(S("a"), S("b")).is_true()
        assert not_equal(CtyValue.unknown(CtyNumber()), N(5)).is_unknown

    def test_less_than(self):
        assert less_than(N(5), N(10)).is_true()
        assert less_than(S("a"), S("b")).is_true()
        with pytest.raises(CtyFunctionError): less_than(N(1), S("a"))

    def test_max_min(self):
        assert max_fn(N(1), N(10), N(5)).value == 10
        assert min_fn(S("z"), S("a"), S("m")).value == "a"
        with pytest.raises(CtyFunctionError): min_fn(N(1), S("a"))

class TestNumericFunctions:
    def test_int_fn(self):
        assert int_fn(N(5.9)).value == 5
        assert int_fn(N(-5.9)).value == -5

class TestStringFunctions:
    def test_join(self):
        assert join(S(","), L(CtyString(), ["a", "b"])).value == "a,b"

    def test_split(self):
        assert split(S(","), S("a,b,c")).raw_value == ["a", "b", "c"]

    def test_replace(self):
        assert replace(S("a-b-c"), S("-"), S(":")).value == "a:b:c"

    def test_regexreplace(self):
        assert regexreplace(S("a1b2"), S(r"\d"), S("*")).value == "a*b*"

class TestCollectionFunctions:
    def test_reverse(self):
        assert reverse(L(CtyString(), ["a", "b", "c"])).raw_value == ["c", "b", "a"]

    def test_hasindex(self):
        assert hasindex(L(CtyString(), ["a"]), N(0)).is_true()
        assert hasindex(M(CtyString(), {"k": "v"}), S("k")).is_true()
        assert hasindex(M(CtyString(), {"k": "v"}), S("z")).is_false()

    def test_index(self):
        assert index(L(CtyString(), ["a", "b"]), N(1)).value == "b"
        with pytest.raises(CtyFunctionError): index(L(CtyString(), []), N(0))

    def test_element(self):
        assert element(L(CtyString(), ["a", "b"]), N(3)).value == "b" # wraps

    def test_coalescelist(self):
        l1, l2 = L(CtyString(), []), L(CtyString(), ["a"])
        assert coalescelist(l1, l2).raw_value == ["a"]

    def test_compact(self):
        assert compact(L(CtyString(), ["a", "", "b"])).raw_value == ["a", "b"]

    def test_chunklist(self):
        l = L(CtyString(), ["a", "b", "c", "d", "e"])
        assert chunklist(l, N(2)).raw_value == [["a", "b"], ["c", "d"], ["e"]]

    def test_lookup(self):
        m = M(CtyString(), {"a": "b"})
        assert lookup(m, S("a"), S("z")).value == "b"
        assert lookup(m, S("x"), S("z")).value == "z"

    def test_merge(self):
        m1 = M(CtyString(), {"a": "1", "b": "2"})
        m2 = M(CtyString(), {"b": "3", "c": "4"})
        assert merge(m1, m2).raw_value == {"a": "1", "b": "3", "c": "4"}

    def test_setproduct(self):
        s1 = Set(CtyString(), ["a", "b"])
        s2 = Set(CtyNumber(), [1, 2])
        prod = setproduct(s1, s2)
        assert isinstance(prod.type, CtySet)
        assert isinstance(prod.type.element_type, CtyTuple)
        result_set = {item.raw_value for item in prod.value}
        expected_set = {("a", 1), ("a", 2), ("b", 1), ("b", 2)}
        assert result_set == expected_set

    def test_zipmap(self):
        keys = L(CtyString(), ["a", "b"])
        vals = L(CtyNumber(), [1, 2])
        assert zipmap(keys, vals).raw_value == {"a": 1, "b": 2}

class TestEncodingFunctions:
    def test_jsonencode(self):
        val = M(CtyString(), {"a": "b"})
        assert jsonencode(val).value == '{"a": "b"}'

    def test_jsondecode(self):
        val = S('{"a": "b"}')
        decoded = jsondecode(val)
        assert isinstance(decoded.type, CtyDynamic)
        assert decoded.raw_value == {"a": "b"}

    def test_csvdecode(self):
        val = S("a,b\n1,2\n3,4")
        decoded = csvdecode(val)
        assert decoded.raw_value == [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}]

class TestDateTimeFunctions:
    def test_formatdate(self):
        ts = S("2020-02-03T04:05:06Z")
        assert formatdate(S("2006-01-02"), ts).value == "2020-02-03"

    def test_timeadd(self):
        ts = S("2020-01-02T03:04:05Z")
        dur = S("1h30m")
        assert "T04:34:05" in timeadd(ts, dur).value

class TestBytesFunctions:
    def test_byteslen(self):
        assert byteslen(BytesCapsule.validate(b"hello")).value == 5

    def test_bytesslice(self):
        assert bytesslice(BytesCapsule.validate(b"hello"), N(1), N(4)).value == b"ell"

class TestStructuralFunctions:
    def test_coalesce(self):
        val1 = S("a")
        val2 = S("b")
        null_val = CtyValue.null(CtyString())
        assert coalesce(val1, val2).value == "a"
        assert coalesce(null_val, val2).value == "b"
        assert coalesce(null_val, null_val, val1).value == "a"
