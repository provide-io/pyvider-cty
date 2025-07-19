import pytest

from pyvider.cty import CtyMap, CtyString
from pyvider.cty.exceptions import CtyTypeMismatchError


def test_map_get_on_non_map_value() -> None:
    map_type = CtyMap(element_type=CtyString())
    str_val = CtyString().validate("hello")
    with pytest.raises(CtyTypeMismatchError):
        map_type.get(str_val, "key")
