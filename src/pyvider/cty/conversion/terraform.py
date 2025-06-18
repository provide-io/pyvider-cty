# pyvider/conversion/terraform.py
from decimal import Decimal
import functools
import json
from typing import TypeVar  # REVIEW_TYPING, cast

from pyvider.cty.context.operation_context import (
    OperationContext,
    get_current_operation,
)
from pyvider.cty.conversion.wire import (
    StateConvertible,
    WireFormat,
    WireFormatRegistry,
    WireFormatType,
    is_state_convertible,
)
from pyvider.cty.exceptions import WireFormatError
from pyvider.telemetry import logger

try:
    import msgpack

    HAS_MSGPACK = True
except ImportError:
    HAS_MSGPACK = False

T = TypeVar("T")


class TerraformWireFormatConstants:
    STRING, NUMBER, BOOL, NULL, TUPLE, LIST, SET, OBJECT, MAP, DYNAMIC = (
        "string",
        "number",
        "bool",
        "null",
        "tuple",
        "list",
        "set",
        "object",
        "map",
        "dynamic",
    )


@WireFormatRegistry.register(WireFormatType.TERRAFORM)
class TerraformFormatConverter(WireFormat):
    @staticmethod
    def _json_default(obj: object) -> object:
        if isinstance(obj, Decimal):
            return str(obj)
        raise TypeError(
            f"Object of type {obj.__class__.__name__} is not JSON serializable"
        )

    @staticmethod
    def _msgpack_default(obj: object) -> object:
        if isinstance(obj, Decimal):
            return str(obj)
        raise TypeError(
            f"Object of type {obj.__class__.__name__} is not msgpack serializable"
        )

    @classmethod
    def marshal(
        cls,
        value: object,
        *,
        operation: OperationContext | None = None,
        use_msgpack: bool = False,
        **options: object,
    ) -> bytes:
        op_ctx = operation or get_current_operation()
        try:
            intermediate = serialize_value(value, operation=op_ctx)
            if use_msgpack:
                if not HAS_MSGPACK:
                    raise WireFormatError(
                        "Failed to marshal with msgpack: msgpack module not available",
                        format_type=WireFormatType.TERRAFORM,
                        operation="marshal",
                        source_value=value,
                    )
                return msgpack.packb(
                    intermediate, default=cls._msgpack_default, use_bin_type=True
                )
            else:
                return json.dumps(
                    intermediate, default=cls._json_default, ensure_ascii=False
                ).encode("utf-8")
        except Exception as e:
            raise WireFormatError(
                f"Marshal failed: {e}",
                format_type=WireFormatType.TERRAFORM,
                operation="marshal",
                source_value=value,
            ) from e

    @classmethod
    def unmarshal(
        cls,
        data: bytes | object,
        expected_type: type[T] | None = None,
        *,
        operation: OperationContext | None = None,
        **options: object,
    ) -> object:
        op_ctx = operation or get_current_operation()
        raw_value: object = None
        try:
            # Check if data is a DynamicValue protobuf object
            if hasattr(data, "__class__") and "DynamicValue" in data.__class__.__name__:
                if data.msgpack:  # If msgpack field is populated
                    logger.debug("Attempting to unmarshal from DynamicValue.msgpack")
                    try:
                        if not HAS_MSGPACK:
                            logger.error(
                                "Cannot unmarshal msgpack from DynamicValue: msgpack module not available"
                            )
                            raise WireFormatError(
                                "Cannot unmarshal msgpack: msgpack module not available",
                                format_type=WireFormatType.TERRAFORM,
                                operation="unmarshal",
                                target_type=expected_type,
                            )
                        raw_value = msgpack.unpackb(data.msgpack, raw=False)
                    except Exception as e_msgpack:
                        logger.error(
                            f"Failed to unmarshal from DynamicValue.msgpack: {e_msgpack}",
                            exc_info=True,
                        )
                        raise WireFormatError(
                            f"Failed to unmarshal from DynamicValue.msgpack: {e_msgpack}",
                            format_type=WireFormatType.TERRAFORM,
                            operation="unmarshal",
                            target_type=expected_type,
                        ) from e_msgpack
                elif data.json:  # If msgpack is not populated, but json is
                    logger.debug("Attempting to unmarshal from DynamicValue.json")
                    try:
                        raw_value = json.loads(data.json.decode("utf-8"))
                    except Exception as e_json:
                        logger.error(
                            f"Failed to unmarshal from DynamicValue.json: {e_json}",
                            exc_info=True,
                        )
                        raise WireFormatError(
                            f"Failed to unmarshal from DynamicValue.json: {e_json}",
                            format_type=WireFormatType.TERRAFORM,
                            operation="unmarshal",
                            target_type=expected_type,
                        ) from e_json
                else:  # DynamicValue has neither msgpack nor json data
                    logger.debug(
                        "DynamicValue has neither msgpack nor json data. Returning None."
                    )
                    # Ensure extract_value can handle None if this path is taken, or return appropriate null value.
                    # For now, assigning None to raw_value which extract_value should process.
                    raw_value = (
                        None  # Explicitly set to None, extract_value will handle it.
                    )
            elif isinstance(data, bytes):  # data is raw bytes
                source_bytes = data
                logger.debug(
                    "Attempting to unmarshal from raw bytes (msgpack first, then JSON fallback)"
                )
                raw_value = None  # Initialize before attempting decodes

                if HAS_MSGPACK:
                    try:
                        raw_value = msgpack.unpackb(source_bytes, raw=False)
                        logger.debug(
                            "Successfully unmarshalled raw bytes using msgpack"
                        )
                    except Exception as e_msgpack_raw:
                        logger.warn(
                            f"Raw bytes decoding as msgpack failed: {e_msgpack_raw}. Will attempt JSON fallback."
                        )
                        raw_value = None  # Ensure JSON fallback is attempted
                else:
                    logger.debug(
                        "msgpack module not available. Skipping msgpack decoding for raw bytes, will attempt JSON fallback."
                    )

                if raw_value is None:  # Try JSON if msgpack was not available or failed
                    try:
                        raw_value = json.loads(source_bytes.decode("utf-8"))
                        logger.debug("Successfully unmarshalled raw bytes using JSON")
                    except Exception as e_json_raw:
                        logger.error(
                            f"Raw bytes decoding as JSON also failed: {e_json_raw}",
                            exc_info=True,
                        )
                        raise WireFormatError(
                            f"Failed to unmarshal raw bytes as msgpack or JSON: {e_json_raw}",
                            format_type=WireFormatType.TERRAFORM,
                            operation="unmarshal",
                            target_type=expected_type,
                        ) from e_json_raw
            else:  # data is already some other Python object
                logger.debug(
                    "Data is already a Python object, no direct unmarshalling needed here."
                )
                raw_value = data

            # The call to extract_value should remain as it processes the raw_value
            return extract_value(raw_value)
        except Exception as e:
            # Avoid re-wrapping WireFormatError
            if isinstance(e, WireFormatError):
                raise
            # Wrap other exceptions in WireFormatError
            raise WireFormatError(
                f"Unmarshal failed: {e}",
                format_type=WireFormatType.TERRAFORM,
                operation="unmarshal",
                target_type=expected_type,
            ) from e


@functools.singledispatch
def serialize_value(value: object, operation: OperationContext) -> object:
    if value is None:
        return [TerraformWireFormatConstants.NULL, None]
    match value:
        case bool():
            return [TerraformWireFormatConstants.BOOL, value]
        case int() | float():
            return [TerraformWireFormatConstants.NUMBER, value]
        case Decimal():
            return [TerraformWireFormatConstants.NUMBER, str(value)]
        case str():
            return [TerraformWireFormatConstants.STRING, value]
        case list() | tuple():
            return [
                TerraformWireFormatConstants.TUPLE,
                [serialize_value(item, operation) for item in value],
            ]
        case set():
            return [
                TerraformWireFormatConstants.SET,
                [
                    serialize_value(item, operation)
                    for item in sorted(list(value), key=repr)
                ],
            ]
        case dict():
            serialized = {
                str(k): serialize_value(v, operation) for k, v in value.items()
            }
            return [TerraformWireFormatConstants.OBJECT, serialized]
        case _ if is_state_convertible(value):
            return serialize_state_convertible(cast(StateConvertible, value), operation)
        case _:
            try:
                return [TerraformWireFormatConstants.STRING, str(value)]
            except:
                return [TerraformWireFormatConstants.NULL, None]


def serialize_state_convertible(
    value: StateConvertible, operation: OperationContext
) -> object:
    raw_dict = value.to_dict()
    if operation in (
        OperationContext.STATE,
        OperationContext.CONFIG,
        OperationContext.READ,
        OperationContext.PLAN,
        OperationContext.APPLY,
    ):
        prepared = {}
        for k, v in raw_dict.items():
            if isinstance(v, bool | int | float | str):
                prepared[str(k)] = v
            elif isinstance(v, Decimal):
                prepared[str(k)] = str(v)
            else:
                prepared[str(k)] = serialize_value(v, operation)
        return prepared
    else:
        return [
            TerraformWireFormatConstants.OBJECT,
            {str(k): serialize_value(v, operation) for k, v in raw_dict.items()},
        ]


def extract_value(value: object) -> object:
    TFC = TerraformWireFormatConstants  # Alias for brevity

    if (
        isinstance(value, list)
        and len(value) == 2
        and isinstance(value[0], str)
        and hasattr(TFC, str(value[0]).upper())
    ):  # Check if first element is a valid type string from TFC
        type_name, payload = value

        match str(type_name).lower():
            case TFC.STRING:
                return str(payload) if payload is not None else ""
            case TFC.NUMBER:
                if payload is None:
                    return None
                try:
                    d = Decimal(str(payload))
                    # Return int if it's an integer, otherwise float
                    return int(d) if d == d.to_integral_value() else float(d)
                except:
                    return payload  # Or raise error, depending on strictness
            case TFC.BOOL:
                return bool(payload) if payload is not None else False
            case TFC.NULL:
                return None
            case TFC.TUPLE | TFC.LIST | TFC.SET:
                # Payload for these should be a list of items to be processed
                return (
                    [extract_value(item) for item in payload]
                    if isinstance(payload, list)
                    else payload
                )
            case TFC.OBJECT | TFC.MAP:
                # Payload for these should be a dict
                return (
                    {str(k): extract_value(v) for k, v in payload.items()}
                    if isinstance(payload, dict)
                    else payload
                )
            case TFC.DYNAMIC:
                # For a dynamic type, recursively call extract_value on its payload
                return extract_value(payload)
            case _:  # Should not be reached if TFC check above is comprehensive
                logger.warning(
                    f"Unexpected type_name '{type_name}' in extract_value match. Returning payload as is."
                )
                return payload

    elif isinstance(
        value, list
    ):  # It's a list of other things (e.g. list of serialized values)
        return [extract_value(item) for item in value]
    elif isinstance(value, dict):  # It's a map/object of other things
        return {str(k): extract_value(v) for k, v in value.items()}
    else:  # It's a primitive or already extracted value
        return value


logger.debug("🧰🔄✅ Terraform wire format converter registered.")

# 🐍🏗️
