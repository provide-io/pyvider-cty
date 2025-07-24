from pyvider.cty.functions.string_functions import (
    lower,
    upper,
)
from pyvider.cty.types import CtyString
from pyvider.cty.values import CtyValue


def test_upper_with_null_and_unknown() -> None:
    assert upper(CtyValue.null(CtyString())).is_null
    assert upper(CtyValue.unknown(CtyString())).is_unknown


def test_lower_with_null_and_unknown() -> None:
    assert lower(CtyValue.null(CtyString())).is_null
    assert lower(CtyValue.unknown(CtyString())).is_unknown
