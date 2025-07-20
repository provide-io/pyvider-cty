import pytest
from pyvider.cty.functions.string_functions import (
    upper,
    lower,
)
from pyvider.cty.values import CtyValue
from pyvider.cty.types import CtyString
from pyvider.cty.exceptions import CtyFunctionError

def test_upper_with_null_and_unknown():
    assert upper(CtyValue.null(CtyString())).is_null
    assert upper(CtyValue.unknown(CtyString())).is_unknown

def test_lower_with_null_and_unknown():
    assert lower(CtyValue.null(CtyString())).is_null
    assert lower(CtyValue.unknown(CtyString())).is_unknown
