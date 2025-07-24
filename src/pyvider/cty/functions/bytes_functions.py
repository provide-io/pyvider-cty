from typing import Any

from pyvider.cty import CtyNumber, CtyValue
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.types import BytesCapsule


def byteslen(buffer: "CtyValue[Any]") -> "CtyValue[Any]":
    if not buffer.type.equal(BytesCapsule):
        raise CtyFunctionError(f"byteslen: argument must be a Bytes capsule, got {buffer.type.ctype}")
    if buffer.is_unknown or buffer.is_null:
        return CtyValue.unknown(CtyNumber())
    return CtyNumber().validate(len(buffer.value))


def bytesslice(buffer: "CtyValue[Any]", start: "CtyValue[Any]", end: "CtyValue[Any]") -> "CtyValue[Any]":
    if not buffer.type.equal(BytesCapsule) or not isinstance(start.type, CtyNumber) or not isinstance(end.type, CtyNumber):
        raise CtyFunctionError("bytesslice: arguments must be Bytes capsule, number, number")
    if buffer.is_unknown or buffer.is_null or start.is_unknown or start.is_null or end.is_unknown or end.is_null:
        return CtyValue.unknown(BytesCapsule)
    
    start_idx, end_idx = int(start.value), int(end.value)
    return BytesCapsule.validate(buffer.value[start_idx:end_idx])
