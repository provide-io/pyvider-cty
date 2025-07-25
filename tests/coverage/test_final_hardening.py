"""
Comprehensive test suite targeting remaining code coverage gaps to achieve 100%.

This suite focuses on error paths, edge cases, and type mismatch scenarios
across the entire library, particularly within the standard functions.
"""

import re
import pytest

from pyvider.cty import (
    BytesCapsule, CtyBool, CtyDynamic, CtyList, CtyMap, CtyNumber, CtyObject,
    CtySet, CtyString, CtyTuple, CtyValue, CtyCapsule
)
from pyvider.cty.exceptions import CtyConversionError, CtyFunctionError, CtyValidationError
from pyvider.cty.functions import (
    byteslen, bytesslice, chunklist, coalesce, coalescelist, compact,
    csvdecode, element, formatdate, jsondecode, jsonencode, lookup, max_fn,
    merge, min_fn, setproduct, timeadd, zipmap
)
from pyvider.cty.types import CtyCapsuleWithOps
from pyvider.cty.conversion import cty_to_native, convert

# Helper functions for creating CtyValues to improve test readability
S = CtyString().validate
N = CtyNumber().validate
B = CtyBool().validate
L = lambda t, v: CtyList(element_type=t).validate(v)
M = lambda t, v: CtyMap(element_type=t).validate(v)


class TestFunctionsCoverage:
    """Tests for uncovered branches in the `functions` modules."""

    def test_bytes_functions_errors(self):
        with pytest.raises(CtyFunctionError, match="byteslen: argument must be a Bytes capsule"):
            byteslen(S("not bytes"))
        with pytest.raises(CtyFunctionError, match="bytesslice: arguments must be Bytes capsule, number, number"):
            bytesslice(S("not bytes"), N(0), N(1))

    def test_collection_functions_errors(self):
        with pytest.raises(CtyFunctionError, match="coalescelist: no non-empty list"):
            coalescelist(L(CtyString(), []), L(CtyString(), []))
        with pytest.raises(CtyFunctionError, match="compact: argument must be a list, set, or tuple of strings"):
            compact(L(CtyNumber(), [1, 2]))
        with pytest.raises(CtyFunctionError, match="chunklist: size must be a positive number"):
            chunklist(L(CtyString(), ["a"]), N(0))
        with pytest.raises(CtyFunctionError, match="element: cannot use element function with an empty list"):
            element(L(CtyString(), []), N(0))
        with pytest.raises(CtyFunctionError, match="lookup: collection must be a map or object"):
            lookup(L(CtyString(), []), S("a"), S("default"))
        with pytest.raises(CtyFunctionError, match="merge: all arguments must be maps or objects"):
            merge(M(CtyString(), {}), L(CtyString(), []))
        with pytest.raises(CtyFunctionError, match="setproduct: all arguments must be collections"):
            setproduct(S("not a collection"))
        with pytest.raises(CtyFunctionError, match="zipmap: arguments must be lists or tuples"):
            zipmap(S("keys"), S("values"))

    def test_comparison_functions_errors(self):
        with pytest.raises(CtyFunctionError, match="max requires at least one argument"):
            max_fn()
        with pytest.raises(CtyFunctionError, match="min requires at least one argument"):
            min_fn()
        with pytest.raises(CtyFunctionError, match="All arguments to max must be of the same type"):
            max_fn(S("a"), N(1))

    def test_datetime_functions_errors(self):
        with pytest.raises(CtyFunctionError, match="formatdate: arguments must be strings"):
            formatdate(N(123), S("ts"))
        with pytest.raises(CtyFunctionError, match="formatdate: invalid timestamp format"):
            formatdate(S("YYYY"), S("invalid-timestamp"))
        with pytest.raises(CtyFunctionError, match="timeadd: arguments must be strings"):
            timeadd(N(123), S("1h"))
        with pytest.raises(CtyFunctionError, match="timeadd: invalid argument format"):
            timeadd(S("invalid-timestamp"), S("1h"))
        with pytest.raises(CtyFunctionError, match="timeadd: invalid argument format"):
            timeadd(S("2020-01-01T00:00:00Z"), S("invalid-duration"))

    def test_encoding_functions_errors(self):
        class Unserializable: pass
        unserializable_capsule = CtyCapsule("Unserializable", Unserializable).validate(Unserializable())
        with pytest.raises(CtyFunctionError, match="jsonencode: failed to encode value"):
            jsonencode(unserializable_capsule)
        with pytest.raises(CtyFunctionError, match="jsondecode: argument must be a string"):
            jsondecode(N(123))
        with pytest.raises(CtyFunctionError, match="jsondecode: failed to decode JSON"):
            jsondecode(S("{not-json}"))
        with pytest.raises(CtyFunctionError, match="csvdecode: argument must be a string"):
            csvdecode(N(123))
        with pytest.raises(CtyFunctionError, match="csvdecode: failed to decode CSV"):
            # This input has more columns in a data row than the header, which causes csv.Error
            csvdecode(S('header1,header2\nval1,val2,val3'))

    def test_structural_functions_errors(self):
        with pytest.raises(CtyFunctionError, match="coalesce must have at least one argument"):
            coalesce()

class TestValuesCoverage:
    """Tests for uncovered branches in `values/base.py`."""

    def test_lt_operator_errors(self):
        with pytest.raises(TypeError, match="Cannot compare null or unknown values"):
            _ = CtyValue.null(CtyNumber()) < N(1)
        with pytest.raises(TypeError, match="Cannot compare CtyValues of different types"):
            _ = N(1) < S("a")
        with pytest.raises(TypeError, match="Value of type bool is not comparable"):
            _ = B(True) < B(False)

    def test_getitem_list_error(self):
        with pytest.raises(TypeError, match="list indices must be integers or slices, not str"):
            _ = L(CtyString(), ["a"])["key"]

class TestTypesCoverage:
    """Tests for uncovered branches in `types` modules."""

    def test_capsule_equality_different_ops(self):
        class O: pass
        type1 = CtyCapsuleWithOps("T", O, equal_fn=lambda a, b: True)
        type2 = CtyCapsuleWithOps("T", O, equal_fn=lambda a, b: False)
        assert not type1.equal(type2)

    def test_map_validate_cty_value_different_type(self):
        map_type = CtyMap(element_type=CtyString())
        list_value = L(CtyString(), [])
        with pytest.raises(CtyValidationError):
            map_type.validate(list_value)

    def test_tuple_validate_cty_value_different_type(self):
        tuple_type = CtyTuple(())
        list_value = L(CtyString(), ["a"]) # Non-empty list
        with pytest.raises(CtyValidationError):
            tuple_type.validate(list_value)

    def test_string_validate_non_string_or_bytes(self):
        with pytest.raises(CtyValidationError, match="Cannot convert int to string"):
            S(123)

class TestConversionCoverage:
    """Tests for uncovered branches in `conversion` modules."""

    def test_explicit_convert_capsule_errors(self):
        class O: pass
        # Capsule with no convert_fn
        capsule_val = CtyCapsule("T", O).validate(O())
        with pytest.raises(CtyConversionError, match="Cannot convert from CtyCapsule"):
            convert(capsule_val, CtyString())
        
        # Capsule with convert_fn that returns non-CtyValue
        bad_converter = lambda v, t: "not a cty value"
        capsule_type = CtyCapsuleWithOps("T", O, convert_fn=bad_converter)
        with pytest.raises(CtyConversionError, match="returned a non-CtyValue object"):
            convert(capsule_type.validate(O()), CtyString())

        # Capsule with convert_fn that returns wrong CtyValue type
        wrong_type_converter = lambda v, t: N(123)
        capsule_type_2 = CtyCapsuleWithOps("T", O, convert_fn=wrong_type_converter)
        with pytest.raises(CtyConversionError, match="returned a value of the wrong type"):
            convert(capsule_type_2.validate(O()), CtyString())

    def test_adapter_cty_to_native_non_iterable_collection(self):
        # Create a malformed CtyValue to test the fallback path
        list_type = CtyList(element_type=CtyString())
        malformed_value = CtyValue(vtype=list_type, value=123) # Should be a list/tuple
        assert cty_to_native(malformed_value) == []
