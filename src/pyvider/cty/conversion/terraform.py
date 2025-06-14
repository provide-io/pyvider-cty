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
    if isinstance(value, list) and len(value) == 2:
        type_name_candidate = value[0]
        # Check if type_name_candidate is a valid type string recognized by TFC
        is_type_payload_pair = isinstance(type_name_candidate, str) and \
                              any(type_name_candidate.lower() == const_val
                                  for const_key, const_val in vars(TerraformWireFormatConstants).items()
                                  if not const_key.startswith('_') and isinstance(const_val, str))

        if is_type_payload_pair:
            type_name, payload = value
            match str(type_name).lower():
                case TerraformWireFormatConstants.STRING: return str(payload) if payload is not None else ""
                case TerraformWireFormatConstants.NUMBER:
                    if payload is None: return None
                    try:
                        d = Decimal(str(payload))
                        # Return as int if it's an integer, otherwise float.
                        if d == d.to_integral_value():
                            return int(d)
                        return float(d)
                    except: return payload # Return as is if not a valid Decimal
                case TerraformWireFormatConstants.BOOL: return bool(payload) if payload is not None else False
                case TerraformWireFormatConstants.NULL: return None
                case TerraformWireFormatConstants.TUPLE | TerraformWireFormatConstants.LIST | TerraformWireFormatConstants.SET:
                    return [extract_value(item) for item in payload] if isinstance(payload, list) else payload
                case TerraformWireFormatConstants.OBJECT | TerraformWireFormatConstants.MAP:
                    return {str(k): extract_value(v) for k, v in payload.items()} if isinstance(payload, dict) else payload
                case TerraformWireFormatConstants.DYNAMIC: return extract_value(payload)
                case _: # Should not happen if is_type_payload_pair is correct, but as a fallback
                    return payload
        else: # It's a list of two items, but not a [type, payload] structure that we recognize for Terraform. Extract each item.
            return [extract_value(item) for item in value]
    elif isinstance(value, list): # General list of items (not len 2 or not matched above)
        return [extract_value(item) for item in value]
    elif isinstance(value, dict): # General dictionary of items
        return {str(k): extract_value(v) for k, v in value.items()}
    # Primitive or already extracted, or some other type not handled by lists/dicts above
    return value

# Ensure @functools.singledispatch is correctly placed before serialize_value
# The orphaned match block below this comment will be implicitly removed by this overwrite
# if it's not part of the REPLACE section.

logger.debug("🧰🔄✅ Terraform wire format converter registered.")

# 🐍🏗️
