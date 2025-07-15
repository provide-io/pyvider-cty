import pytest
from decimal import Decimal
from pyvider.cty import CtyNumber, CtyString, CtyValue
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import numeric_functions, string_functions

class TestNumericFunctionsCoverage:
    def test_log_fn_errors(self):
        num = CtyNumber().validate(10)
        base = CtyNumber().validate(1)
        with pytest.raises(CtyFunctionError, match="base cannot be 1"):
            numeric_functions.log_fn(num, base)

    def test_parseint_fn_errors(self):
        s = CtyString().validate("10")
        base = CtyNumber().validate(99) # Invalid base
        with pytest.raises(CtyFunctionError, match="base must be 0 or between 2 and 36"):
            numeric_functions.parseint_fn(s, base)

class TestStringFunctionsCoverage:
    def test_substr_errors(self):
        s = CtyString().validate("hello")
        offset = CtyNumber().validate(0)
        length = CtyNumber().validate(-5) # Invalid length
        with pytest.raises(CtyFunctionError, match="length cannot be negative"):
            string_functions.substr(s, offset, length)

    def test_regex_errors(self):
        s = CtyString().validate("hello")
        pattern = CtyString().validate("[") # Invalid regex
        with pytest.raises(CtyFunctionError, match="invalid regular expression"):
            string_functions.regex(pattern, s)
