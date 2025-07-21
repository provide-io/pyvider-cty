import msgpack
import pytest

from pyvider.cty import CtyDynamic, CtyString, CtyValue
from pyvider.cty.codec import _ext_hook, _serialize_unknown, cty_from_msgpack
from pyvider.cty.exceptions import DeserializationError
from pyvider.cty.values import RefinedUnknownValue


def test_ext_hook_with_invalid_code() -> None:
    ext = msgpack.ExtType(99, b"")
    assert _ext_hook(ext.code, ext.data) == ext


def test_ext_hook_with_malformed_refined_unknown() -> None:
    with pytest.raises(DeserializationError):
        _ext_hook(12, b"invalid")


def test_cty_from_msgpack_with_empty_data() -> None:
    val = cty_from_msgpack(b"", CtyString())
    assert val.is_null


def test_serialize_dynamic_with_non_cty_value() -> None:
    schema = CtyDynamic()
    value = "hello"
    from pyvider.cty.codec import cty_to_msgpack

    # The value "hello" is not a CtyValue, so we need to wrap it in one
    # for the cty_to_msgpack function.
    packed = cty_to_msgpack(schema.validate(value), schema)
    unpacked = cty_from_msgpack(packed, schema)
    assert unpacked.value == "hello"


def test_serialize_unsupported_type() -> None:
    from pyvider.cty.codec import _msgpack_default_handler

    with pytest.raises(TypeError):
        _msgpack_default_handler(object())


def test_serialize_unknown_with_no_refinements() -> None:
    val = CtyValue.unknown(CtyString())
    serialized = _serialize_unknown(val)
    assert serialized.code == 0


def test_serialize_refined_unknown_with_no_payload() -> None:
    val = CtyValue.unknown(CtyString(), value=RefinedUnknownValue())
    serialized = _serialize_unknown(val)
    assert serialized.code == 0
