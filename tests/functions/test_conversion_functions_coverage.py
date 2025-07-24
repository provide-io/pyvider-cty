from pyvider.cty import CtyNumber, CtyString, CtyValue
from pyvider.cty.functions import to_bool, to_number, to_string


def test_to_string_null_unknown() -> None:
    assert to_string(CtyValue.null(CtyNumber())).is_unknown
    assert to_string(CtyValue.unknown(CtyNumber())).is_unknown


def test_to_number_null_unknown() -> None:
    assert to_number(CtyValue.null(CtyString())).is_unknown
    assert to_number(CtyValue.unknown(CtyString())).is_unknown


def test_to_bool_null_unknown() -> None:
    assert to_bool(CtyValue.null(CtyString())).is_unknown
    assert to_bool(CtyValue.unknown(CtyString())).is_unknown
