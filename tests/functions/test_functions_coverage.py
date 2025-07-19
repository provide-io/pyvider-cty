import pytest
from decimal import Decimal
from pyvider.cty import CtyNumber, CtyString, CtyValue, CtyList, CtyBool
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import numeric_functions, string_functions, collection_functions

class TestNumericFunctionsCoverage:
    def test_log_fn_errors(self):
        num = CtyNumber().validate(10)
        neg_num = CtyNumber().validate(-1)
        base = CtyNumber().validate(1)
        with pytest.raises(CtyFunctionError, match="base cannot be 1"):
            numeric_functions.log_fn(num, base)
        with pytest.raises(CtyFunctionError, match="number must be positive"):
            numeric_functions.log_fn(neg_num, num)
        with pytest.raises(CtyFunctionError, match="base must be positive"):
            numeric_functions.log_fn(num, neg_num)

    def test_pow_fn_errors(self):
        neg_num = CtyNumber().validate(-4)
        frac_num = CtyNumber().validate(0.5)
        with pytest.raises(CtyFunctionError, match="invalid operation"):
            numeric_functions.pow_fn(neg_num, frac_num)

    def test_parseint_fn_errors(self):
        s = CtyString().validate("10")
        base_invalid = CtyNumber().validate(99)
        base_valid = CtyNumber().validate(10)
        s_invalid_type = CtyNumber().validate(10)

        with pytest.raises(CtyFunctionError, match="base must be 0 or between 2 and 36"):
            numeric_functions.parseint_fn(s, base_invalid)
        with pytest.raises(CtyFunctionError, match="input string must be a string"):
            numeric_functions.parseint_fn(s_invalid_type, base_valid)

class TestStringFunctionsCoverage:
    def test_substr_errors(self):
        s = CtyString().validate("hello")
        offset = CtyNumber().validate(0)
        length_neg = CtyNumber().validate(-5)
        length_null = CtyValue.null(CtyNumber())

        with pytest.raises(CtyFunctionError, match="length cannot be negative"):
            string_functions.substr(s, offset, length_neg)
        with pytest.raises(CtyFunctionError, match="cannot operate on null values"):
            string_functions.substr(s, offset, length_null)

    def test_regex_errors(self):
        s = CtyString().validate("hello")
        pattern_invalid = CtyString().validate("[")
        pattern_null = CtyValue.null(CtyString())

        with pytest.raises(CtyFunctionError, match="invalid regular expression"):
            string_functions.regex(pattern_invalid, s)
        with pytest.raises(CtyFunctionError, match="cannot operate on null values"):
            string_functions.regex(pattern_null, s)

    def test_regexall_errors(self):
        s = CtyString().validate("hello")
        pattern_invalid = CtyString().validate("[")
        pattern_null = CtyValue.null(CtyString())

        with pytest.raises(CtyFunctionError, match="invalid regular expression"):
            string_functions.regexall(pattern_invalid, s)
        with pytest.raises(CtyFunctionError, match="cannot operate on null values"):
            string_functions.regexall(pattern_null, s)

class TestCollectionFunctionsCoverage:
    def test_distinct_unhashable_error(self):
        # FIX: Corrected CtyList constructor call
        list_of_lists = CtyList(element_type=CtyList(element_type=CtyString())).validate([["a"], ["b"]])
        with pytest.raises(CtyFunctionError, match="not hashable"):
            collection_functions.distinct(list_of_lists)

    def test_flatten_type_error(self):
        # FIX: Corrected CtyList constructor call
        mixed_list = CtyList(element_type=CtyString()).validate(["a", "b"])
        with pytest.raises(CtyFunctionError, match="all elements must be lists or tuples"):
            collection_functions.flatten(mixed_list)

    def test_sort_errors(self):
        # FIX: Corrected CtyList constructor calls
        list_of_lists = CtyList(element_type=CtyList(element_type=CtyString())).validate([["c"], ["a"]])
        with pytest.raises(CtyFunctionError, match="elements must be string, number, or bool"):
            collection_functions.sort(list_of_lists)
        
        list_with_null = CtyList(element_type=CtyString()).validate(["a", None, "c"])
        with pytest.raises(CtyFunctionError, match="cannot sort list with null or unknown elements"):
            collection_functions.sort(list_with_null)
