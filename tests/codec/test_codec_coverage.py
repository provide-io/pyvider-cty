import msgpack
import pytest

from pyvider.cty import CtyDynamic, CtyString, CtyValue
from pyvider.cty.codec import _ext_hook, cty_from_msgpack, _serialize_unknown
from pyvider.cty.exceptions import DeserializationError
from pyvider.cty.values import RefinedUnknownValue, UNREFINED_UNKNOWN


def test_ext_hook_with_invalid_code():
    ext = msgpack.ExtType(99, b"")
    assert _ext_hook(ext.code, ext.data) == ext


def test_ext_hook_with_malformed_refined_unknown():
    with pytest.raises(DeserializationError):
        _ext_hook(12, b"invalid")


def test_cty_from_msgpack_with_empty_data():
    val = cty_from_msgpack(b"", CtyString())
    assert val.is_null


def test_serialize_dynamic_with_non_cty_value():
    schema = CtyDynamic()
    value = "hello"
    from pyvider.cty.codec import cty_to_msgpack
    # The value "hello" is not a CtyValue, so we need to wrap it in one
    # for the cty_to_msgpack function.
    packed = cty_to_msgpack(schema.validate(value), schema)
    unpacked = cty_from_msgpack(packed, schema)
    assert unpacked.value == "hello"

def test_serialize_unsupported_type():
    from pyvider.cty.codec import _msgpack_default_handler
    with pytest.raises(TypeError):
        _msgpack_default_handler(object())

def test_serialize_unknown_with_no_refinements():
    val = CtyValue.unknown(CtyString())
    serialized = _serialize_unknown(val)
    assert serialized.code == 0

def test_serialize_refined_unknown_with_no_payload():
    val = CtyValue.unknown(CtyString(), value=RefinedUnknownValue())
    serialized = _serialize_unknown(val)
    assert serialized.code == 0
