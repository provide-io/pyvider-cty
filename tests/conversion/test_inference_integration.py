import attrs
import msgpack
import pytest

from pyvider.cty import CtyDynamic, CtyObject, CtyValue
from pyvider.cty.codec import cty_from_msgpack


@attrs.define
class MyComponentState:
    name: str
    count: int


def test_validate_raw_attrs_object_with_ctydynamic() -> None:
    raw_state_obj = MyComponentState(name="test", count=123)
    packed_data = msgpack.packb(attrs.asdict(raw_state_obj), use_bin_type=True)

    try:
        cty_val = cty_from_msgpack(packed_data, CtyDynamic())
        assert isinstance(cty_val, CtyValue)
        assert isinstance(cty_val.type, CtyObject)
        assert "name" in cty_val.type.attribute_types
        assert "count" in cty_val.type.attribute_types
        assert cty_val["name"].value == "test"
        assert cty_val["count"].value == 123
    except RecursionError:
        pytest.fail("cty_from_msgpack() caused a RecursionError on an attrs object.")
