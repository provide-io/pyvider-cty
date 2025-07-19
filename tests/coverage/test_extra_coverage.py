import pytest
from pyvider.cty import CtyNumber, CtyString, CtyValue, CtyList, CtyBool
from pyvider.cty.functions import (
    abs_fn,
    ceil_fn,
    floor_fn,
    log_fn,
    pow_fn,
    signum_fn,
    parseint_fn,
    chomp,
    strrev,
    trimspace,
    indent,
    substr,
    trim,
    title,
    trimprefix,
    trimsuffix,
    regex,
    regexall,
    distinct,
    flatten,
    sort,
)
from pyvider.cty.exceptions import CtyFunctionError

def test_log_fn_errors():
    with pytest.raises(CtyFunctionError, match="log: number must be positive, got 0"):
        log_fn(CtyNumber().validate(0), CtyNumber().validate(10))
    with pytest.raises(CtyFunctionError, match="log: base must be positive, got 0"):
        log_fn(CtyNumber().validate(10), CtyNumber().validate(0))
    with pytest.raises(CtyFunctionError, match="log: base cannot be 1"):
        log_fn(CtyNumber().validate(10), CtyNumber().validate(1))

def test_pow_fn_errors():
    with pytest.raises(CtyFunctionError, match="pow: invalid operation"):
        pow_fn(CtyNumber().validate(-1), CtyNumber().validate(0.5))

def test_parseint_fn_errors():
    with pytest.raises(CtyFunctionError, match="parseint: base must be 0 or between 2 and 36, got 37"):
        parseint_fn(CtyString().validate("10"), CtyNumber().validate(37))

def test_substr_errors():
    with pytest.raises(CtyFunctionError, match="substr: length cannot be negative"):
        substr(CtyString().validate("hello"), CtyNumber().validate(0), CtyNumber().validate(-2))

def test_regex_errors():
    with pytest.raises(CtyFunctionError, match="regex: invalid regular expression"):
        regex(CtyString().validate("["), CtyString().validate("hello"))

def test_regexall_errors():
    with pytest.raises(CtyFunctionError, match="regexall: invalid regular expression"):
        regexall(CtyString().validate("["), CtyString().validate("hello"))

def test_distinct_unhashable_error():
    with pytest.raises(CtyFunctionError, match="distinct: element of type list is not hashable"):
        distinct(CtyList(element_type=CtyList(element_type=CtyString())).validate([["a"], ["b"], ["a"]]))

def test_flatten_type_error():
    with pytest.raises(CtyFunctionError, match="flatten: all elements must be lists or tuples"):
        flatten(CtyList(element_type=CtyString()).validate(["a", "b", "c"]))

def test_sort_errors():
    with pytest.raises(CtyFunctionError, match="sort: elements must be string, number, or bool"):
        sort(CtyList(element_type=CtyList(element_type=CtyString())).validate([["a"], ["b"]]))
    with pytest.raises(CtyFunctionError, match="sort: cannot sort list with null or unknown elements"):
        sort(CtyList(element_type=CtyString()).validate(["a", None, "c"]))
