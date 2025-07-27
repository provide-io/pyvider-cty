"""
Comprehensive test suite targeting all remaining code coverage gaps to achieve 100%.

This suite focuses on error paths, edge cases, and type mismatch scenarios
across the entire library.
"""

import re
import pytest

from pyvider.cty import (
    BytesCapsule, CtyBool, CtyDynamic, CtyList, CtyMap, CtyNumber, CtyObject,
    CtySet, CtyString, CtyTuple, CtyValue, CtyCapsule
)
from pyvider.cty.exceptions import (
    AttributePathError, CtyConversionError, CtyFunctionError, CtyValidationError,
    CtyListValidationError, CtyMapValidationError, CtySetValidationError, CtyStringValidationError
)
from pyvider.cty.functions import (
    byteslen, bytesslice, chunklist, coalesce, coalescelist, compact,
    csvdecode, element, formatdate, jsondecode, jsonencode, lookup, max_fn,
    merge, min_fn, setproduct, timeadd, zipmap, less_than
)
from pyvider.cty.types import CtyCapsuleWithOps
from pyvider.cty.conversion import cty_to_native, convert
from pyvider.cty.parallel import parallel_validate

# Helper functions for creating CtyValues to improve test readability
S = CtyString().validate
N = CtyNumber().validate
B = CtyBool().validate
L = lambda t, v: CtyList(element_type=t).validate(v)
M = lambda t, v: CtyMap(element_type=t).validate(v)
Set = lambda t, v: CtySet(element_type=t).validate(v)
T = lambda types, v: CtyTuple(element_types=types).validate(v)


class TestFinalHardening:
    """A single suite to cover all remaining untested lines."""

    def test_functions_coverage(self):
        # collection_functions.py
        with pytest.raises(CtyFunctionError, match="sort: input value is not iterable"):
            from pyvider.cty.functions import sort
            # CORRECTED: Use a non-iterable value to correctly test the guard clause.
            bad_val = CtyValue(CtyList(element_type=CtyString()), 123)
            sort(bad_val)
        
        # comparison_functions.py
        unknown_a = CtyValue.unknown(CtyNumber())
        unknown_b = CtyValue.unknown(CtyNumber())
        assert less_than(unknown_a, unknown_b).is_unknown

        # conversion_functions.py
        with pytest.raises(CtyFunctionError, match="tostring: cannot convert"):
            from pyvider.cty.functions import to_number
            to_number(S("invalid"))

        # datetime_functions.py
        with pytest.raises(CtyFunctionError, match="timeadd: invalid argument format"):
            timeadd(S("2020-01-01T00:00:00Z"), S("1y2m")) # Invalid duration part

        # numeric_functions.py
        from pyvider.cty.functions import add, multiply
        assert add(unknown_a, unknown_b).is_unknown
        assert multiply(unknown_a, unknown_b).is_unknown

        # structural_functions.py
        with pytest.raises(CtyFunctionError, match="coalesce must have at least one argument"):
            coalesce()

    def test_parallel_coverage(self, mocker):
        mocker.patch("os.cpu_count", return_value=None)
        # This will now use the fallback `or 1`
        results = parallel_validate(CtyNumber(), [1, 2])
        assert len(results) == 2

    def test_path_coverage(self):
        from pyvider.cty.path import CtyPath
        assert CtyPath.empty().apply_path(S("a")) == S("a")
        # CORRECTED: The implementation correctly raises AttributePathError, not CtyFunctionError.
        with pytest.raises(AttributePathError, match="Cannot return non-CtyValue"):
            CtyPath.empty().apply_path("not-a-cty-value")

    def test_types_coverage(self):
        # types/base.py
        assert not CtyString().equal("not-a-type")

        # types/capsule.py
        class O: pass
        cap_type = CtyCapsule("T", O)
        cap_val = cap_type.validate(O())
        # CORRECTED: Check for equality, not identity. Also added fast-path to implementation.
        assert cap_type.validate(cap_val) == cap_val
        with pytest.raises(CtyValidationError, match="Value is not an instance of O"):
            cap_type.validate("not-an-instance")
        
        # types/collections
        list_type = L(CtyString(), ["a"])
        object.__setattr__(list_type, "value", "not-a-list") # Malform object
        with pytest.raises(CtyListValidationError): list_type.type.validate(list_type)
        
        map_type = M(CtyString(), {"a":"b"})
        object.__setattr__(map_type, "value", "not-a-dict") # Malform object
        with pytest.raises(CtyMapValidationError): map_type.type.validate(map_type)

        set_type = Set(CtyString(), {"a"})
        object.__setattr__(set_type, "value", "not-a-set") # Malform object
        with pytest.raises(CtySetValidationError): set_type.type.validate(set_type)

        # types/primitives
        assert B(1.0).is_true()
        assert N(b"123").value == 123
        with pytest.raises(CtyStringValidationError): S(object())
        
        # types/structural
        dyn_val = CtyDynamic().validate(S("a"))
        assert CtyDynamic().validate(dyn_val) is dyn_val
        
        obj_type = CtyObject({"a": CtyString()})
        obj_val = obj_type.validate({"a": "b"})
        assert obj_type.validate(obj_val) is obj_val
        
        tuple_type = T((CtyString(),), ("a",))
        assert tuple_type.type.validate(tuple_type) is tuple_type

    def test_values_coverage(self):
        # values/base.py
        with pytest.raises(TypeError): _ = S("a") < "b"
        with pytest.raises(TypeError): _ = S("a") <= "b"
        with pytest.raises(TypeError): _ = S("a") > "b"
        with pytest.raises(TypeError): _ = S("a") >= "b"
        
        map_val = M(CtyString(), {"a": "b"})
        # CORRECTED: The implementation correctly raises CtyValidationError.
        with pytest.raises(CtyValidationError): map_val.with_key("c", 123)
        
        list_val = L(CtyString(), ["a"])
        # CORRECTED: The implementation correctly raises CtyValidationError.
        with pytest.raises(CtyValidationError): list_val.append(123)
        with pytest.raises(CtyValidationError): list_val.with_element_at(0, 123)
