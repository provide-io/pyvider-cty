# pyvider/conversion/terraform.py
import json
import functools
from decimal import Decimal
from typing import Mapping, Protocol, Literal, Type, TypeVar, cast, runtime_checkable
import collections.abc

from pyvider.telemetry import logger
from pyvider.cty.exceptions import CtyConversionError, WireFormatError
from pyvider.cty.conversion.wire import (
    WireFormat, WireFormatType, WireFormatRegistry, StateConvertible, is_state_convertible
)
from pyvider.cty.context.operation_context import OperationContext, get_current_operation

try:
    import msgpack
    HAS_MSGPACK = True
except ImportError:
    HAS_MSGPACK = False

T = TypeVar('T')

class TerraformWireFormatConstants:
    STRING, NUMBER, BOOL, NULL, TUPLE, LIST, SET, OBJECT, MAP, DYNAMIC = (
        "string", "number", "bool", "null", "tuple", "list", "set", "object", "map", "dynamic"
    )

@WireFormatRegistry.register(WireFormatType.TERRAFORM)
class TerraformFormatConverter(WireFormat):
    @staticmethod
    def _json_default(obj: object) -> object:
        if isinstance(obj, Decimal): return str(obj)
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    @staticmethod
    def _msgpack_default(obj: object) -> object:
        if isinstance(obj, Decimal): return str(obj)
        raise TypeError(f"Object of type {obj.__class__.__name__} is not msgpack serializable")

    @classmethod
    def marshal(cls, value: object, *, operation: OperationContext | None = None, use_msgpack: bool = False, **options: object) -> bytes:
        op_ctx = operation or get_current_operation()
        try:
            intermediate = serialize_value(value, operation=op_ctx)
            if use_msgpack and HAS_MSGPACK:
                return msgpack.packb(intermediate, default=cls._msgpack_default, use_bin_type=True)
            else:
                return json.dumps(intermediate, default=cls._json_default, ensure_ascii=False).encode('utf-8')
        except Exception as e:
            raise WireFormatError(f"Marshal failed: {e}", format_type=WireFormatType.TERRAFORM, operation="marshal", source_value=value) from e

    @classmethod
    def unmarshal(cls, data: bytes | object, expected_type: Type[T] | None = None, *, operation: OperationContext | None = None, **options: object) -> object:
        op_ctx = operation or get_current_operation()
        raw_value: object = None
        try:
            if hasattr(data, '__class__') and 'DynamicValue' in data.__class__.__name__:
                source_bytes = data.msgpack or data.json
                if not source_bytes: return None
            elif isinstance(data, bytes):
                source_bytes = data
            else:
                raw_value = data

            if raw_value is None:
                try:
                    raw_value = msgpack.unpackb(source_bytes, raw=False)
                except Exception:
                    raw_value = json.loads(source_bytes.decode('utf-8'))
            
            return extract_value(raw_value)
        except Exception as e:
            raise WireFormatError(f"Unmarshal failed: {e}", format_type=WireFormatType.TERRAFORM, operation="unmarshal", target_type=expected_type) from e

@functools.singledispatch
def serialize_value(value: object, operation: OperationContext) -> object:
    if value is None: return [TerraformWireFormatConstants.NULL, None]
    match value:
        case bool(): return [TerraformWireFormatConstants.BOOL, value]
        case int() | float(): return [TerraformWireFormatConstants.NUMBER, value]
        case Decimal(): return [TerraformWireFormatConstants.NUMBER, str(value)]
        case str(): return [TerraformWireFormatConstants.STRING, value]
        case list() | tuple(): return [TerraformWireFormatConstants.TUPLE, [serialize_value(item, operation) for item in value]]
        case set(): return [TerraformWireFormatConstants.SET, [serialize_value(item, operation) for item in sorted(list(value), key=repr)]]
        case dict():
            serialized = {str(k): serialize_value(v, operation) for k, v in value.items()}
            return [TerraformWireFormatConstants.OBJECT, serialized]
        case _ if is_state_convertible(value):
             return serialize_state_convertible(cast(StateConvertible, value), operation)
        case _:
            try: return [TerraformWireFormatConstants.STRING, str(value)]
            except: return [TerraformWireFormatConstants.NULL, None]

def serialize_state_convertible(value: StateConvertible, operation: OperationContext) -> object:
    raw_dict = value.to_dict()
    if operation in (OperationContext.STATE, OperationContext.CONFIG, OperationContext.READ, OperationContext.PLAN, OperationContext.APPLY):
        prepared = {}
        for k, v in raw_dict.items():
            if isinstance(v, (bool, int, float, str)):
                prepared[str(k)] = v
            elif isinstance(v, Decimal):
                prepared[str(k)] = str(v)
            else:
                prepared[str(k)] = serialize_value(v, operation)
        return prepared
    else:
        return [TerraformWireFormatConstants.OBJECT, {str(k): serialize_value(v, operation) for k, v in raw_dict.items()}]

def extract_value(value: object) -> object:
    if not isinstance(value, list) or len(value) != 2:
        if isinstance(value, list): return [extract_value(item) for item in value]
        if isinstance(value, dict): return {str(k): extract_value(v) for k, v in value.items()}
        return value
    
    type_name, payload = value
    match str(type_name).lower():
        case TerraformWireFormatConstants.STRING: return str(payload) if payload is not None else ""
        case TerraformWireFormatConstants.NUMBER:
            if payload is None: return None
            try:
                d = Decimal(str(payload))
                return int(d) if d == d.to_integral_value() else float(d)
            except: return payload
        case TerraformWireFormatConstants.BOOL: return bool(payload) if payload is not None else False
        case TerraformWireFormatConstants.NULL: return None
        case TerraformWireFormatConstants.TUPLE | TerraformWireFormatConstants.LIST | TerraformWireFormatConstants.SET:
            return [extract_value(item) for item in payload] if isinstance(payload, list) else payload
        case TerraformWireFormatConstants.OBJECT | TerraformWireFormatConstants.MAP:
            return {str(k): extract_value(v) for k, v in payload.items()} if isinstance(payload, dict) else payload
        case TerraformWireFormatConstants.DYNAMIC: return extract_value(payload)
        case _: return payload

logger.debug("🧰🔄✅ Terraform wire format converter registered.")

# 🐍🏗️
