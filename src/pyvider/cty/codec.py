#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

from decimal import Decimal
import json
from typing import Any, cast

import msgpack

from pyvider.cty.config.defaults import (
    ERR_DECODE_DYNAMIC_TYPE,
    ERR_DECODE_REFINED_UNKNOWN,
    ERR_DYNAMIC_MALFORMED,
    ERR_NAN_NOT_SERIALIZABLE,
    ERR_OBJECT_NOT_MSGPACK_SERIALIZABLE,
    ERR_VALUE_FOR_LIST_SET,
    ERR_VALUE_FOR_MAP,
    ERR_VALUE_FOR_OBJECT,
    ERR_VALUE_FOR_TUPLE,
    MSGPACK_EXT_TYPE_CTY,
    MSGPACK_EXT_TYPE_REFINED_UNKNOWN,
    MSGPACK_RAW_FALSE,
    MSGPACK_STRICT_MAP_KEY_FALSE,
    MSGPACK_USE_BIN_TYPE_TRUE,
    REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND,
    REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND,
    REFINEMENT_IS_KNOWN_NULL,
    REFINEMENT_NUMBER_LOWER_BOUND,
    REFINEMENT_NUMBER_UPPER_BOUND,
    REFINEMENT_STRING_PREFIX,
    TWO_VALUE,
)
from pyvider.cty.conversion import encode_cty_type_to_wire_json
from pyvider.cty.exceptions import (
    CtyMarksSerializationError,
    DeserializationError,
    SerializationError,
)
from pyvider.cty.marks import collect_marks_deep
from pyvider.cty.parser import parse_tf_type_to_ctytype
from pyvider.cty.types import (
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyObject,
    CtySet,
    CtyTuple,
    CtyType,
)
from pyvider.cty.values import CtyValue
from pyvider.cty.values.markers import (
    UNREFINED_UNKNOWN,
    RefinedUnknownValue,
    UnknownValue,
)
from pyvider.cty.values.set_order import order_key as set_order_key


def _decode_number_value(val: Any) -> Decimal:
    """Decode a numeric value from bytes or other format to Decimal."""
    if isinstance(val, bytes):
        return Decimal(val.decode("utf-8"))
    return Decimal(val)


def _checked(value: Any, expected: type, what: str) -> Any:
    """A refinement field, checked against the type the protocol gives it.

    These bytes come from whatever is on the other end of the wire, and this is
    the one refinement path that does not go through RefinementBuilder -- whose
    stated purpose is to refuse an inconsistent refinement rather than record
    one. Unchecked, a malformed field was stored verbatim and surfaced later as
    an AttributeError from inside the encoder: outside the CtyError taxonomy, so
    a provider's `except CtyError` missed it and bad input read as a crash.
    go-cty rejects these at the door -- "string prefix refinement is not
    string".
    """
    # bool is a subclass of int in Python, so an int field would accept True and
    # a bool field would accept 1 without this.
    if isinstance(value, bool) != (expected is bool) or not isinstance(value, expected):
        raise DeserializationError(f"{what} refinement is not {expected.__name__}")
    return value


def _checked_length(value: Any, what: str) -> int:
    """A collection-length bound: an integer, and not a negative one."""
    length = _checked(value, int, what)
    if length < 0:
        raise DeserializationError(f"{what} refinement is negative")
    return cast(int, length)


def _extract_refinements_from_payload(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = _checked(payload[REFINEMENT_IS_KNOWN_NULL], bool, "is known null")
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = _checked(payload[REFINEMENT_STRING_PREFIX], str, "string prefix")
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = _checked_length(
            payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND], "collection length lower bound"
        )
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = _checked_length(
            payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND], "collection length upper bound"
        )

    return refinements


def _decode_refined_unknown_payload(data: bytes) -> RefinedUnknownValue:
    """Decode a refined unknown value from msgpack data."""
    try:
        payload = msgpack.unpackb(data, raw=MSGPACK_RAW_FALSE, strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE)
        refinements = _extract_refinements_from_payload(payload)
        return RefinedUnknownValue(**refinements)
    except Exception as e:
        error_message = ERR_DECODE_REFINED_UNKNOWN.format(error=e)
        raise DeserializationError(error_message) from e


def _ext_hook(code: int, data: bytes) -> Any:
    match code:
        case 0:
            return UNREFINED_UNKNOWN
        case 12:
            return _decode_refined_unknown_payload(data)
        case _:
            # Per protocol, any other extension code is an unrefined unknown.
            return UNREFINED_UNKNOWN


_UNKNOWN_EXT = msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"\x00")
"""An unknown with nothing known about it.

One data byte, whose value is irrelevant, because that makes the encoding a
msgpack *fixext1* -- `d4 00 00`, the three bytes go-cty names in a variable and
calls "the most compact possible representation". An empty payload is legal
msgpack and decodes to the same value, but it is `c7 00 00`: a different
serialization of the same unknown, and Terraform compares serialized state.
"""

_MAX_PREFIX_BYTES = 256
"""go-cty's cap on a string-prefix refinement, and its reason: the whole
refinement blob has to stay under the limit its own decoder enforces."""


def _serialize_unknown(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return _UNKNOWN_EXT
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = _bounded_prefix(value.value.string_prefix)
    # Bounds go through the ordinary number serializer. They used to be written
    # as raw UTF-8 bytes -- a msgpack *binary* string, where go-cty encodes the
    # tuple `(number, bool)` through its normal marshaller and so writes 3 as an
    # integer. go-cty reads our version back correctly, which is why this
    # survived: the values agreed and the bytes did not.
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [_serialize_decimal_value(num), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [_serialize_decimal_value(num), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return _UNKNOWN_EXT
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def _bounded_prefix(prefix: str) -> str:
    """A string prefix truncated to what the wire format allows.

    Truncating mid-cluster would leave a prefix that a later character could
    combine with, so the cut is followed by the same safe-prefix trim go-cty
    applies -- which is the one place where "shorten it" and "keep it correct"
    are the same operation.
    """
    if len(prefix.encode("utf-8")) <= _MAX_PREFIX_BYTES:
        return prefix

    from pyvider.cty.refinement import safe_known_prefix

    truncated = prefix.encode("utf-8")[: _MAX_PREFIX_BYTES - 1].decode("utf-8", errors="ignore")
    return safe_known_prefix(truncated)


def _serialize_dynamic(value: CtyValue[Any], path: str = "") -> list[Any] | Any:
    inner_value = value.value
    if not isinstance(inner_value, CtyValue):
        # Nothing concrete to name. A value that is unknown or null at the
        # dynamic level itself -- rather than holding an unknown of some known
        # type -- has no type to carry, and go-cty writes it bare.
        if value.is_unknown:
            return _serialize_unknown(value)
        if value.is_null:
            return None
        raise SerializationError(
            ERR_DYNAMIC_MALFORMED,
            value=value,
        )

    actual_type = inner_value.type
    serializable_inner = _convert_value_to_serializable(inner_value, actual_type, path)

    type_spec_json = encode_cty_type_to_wire_json(actual_type)
    type_spec_bytes = json.dumps(type_spec_json, separators=(",", ":")).encode("utf-8")
    return [type_spec_bytes, serializable_inner]


def _serialize_object_value(inner_val: Any, schema: CtyObject, path: str = "") -> dict[str, Any]:
    """Serialize a CtyObject value."""
    if not isinstance(inner_val, dict):
        raise TypeError(ERR_VALUE_FOR_OBJECT)
    return {
        k: _convert_value_to_serializable(v, schema.attribute_types[k], f"{path}.{k}")
        for k, v in sorted(inner_val.items())
    }


def _serialize_map_value(inner_val: Any, schema: CtyMap[Any], path: str = "") -> dict[str, Any]:
    """Serialize a CtyMap value."""
    if not isinstance(inner_val, dict):
        raise TypeError(ERR_VALUE_FOR_MAP)
    return {
        k: _convert_value_to_serializable(v, schema.element_type, f'{path}["{k}"]')
        for k, v in sorted(inner_val.items())
    }


def _serialize_collection_value(
    inner_val: Any, schema: CtyList[Any] | CtySet[Any], path: str = ""
) -> list[Any]:
    """Serialize a CtyList or CtySet value."""
    if not hasattr(inner_val, "__iter__"):
        raise TypeError(ERR_VALUE_FOR_LIST_SET)
    items = sorted(list(inner_val), key=set_order_key) if isinstance(schema, CtySet) else inner_val
    return [
        _convert_value_to_serializable(item, schema.element_type, f"{path}[{i}]")
        for i, item in enumerate(items)
    ]


def _serialize_tuple_value(inner_val: Any, schema: CtyTuple, path: str = "") -> list[Any]:
    """Serialize a CtyTuple value."""
    if not isinstance(inner_val, tuple):
        raise TypeError(ERR_VALUE_FOR_TUPLE)
    return [
        _convert_value_to_serializable(item, schema.element_types[i], f"{path}[{i}]")
        for i, item in enumerate(inner_val)
    ]


def _serialize_decimal_value(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.

    A NaN is refused. go-cty's number is a `big.Float`, which has no NaN --
    `SetFloat64` panics on one -- so `cty.NumberVal` cannot hold one and
    `convert("NaN", number)` is refused there. A `Decimal` can hold one, and
    this fell through to the "write the decimal text" branch below and emitted
    the string `"NaN"`: bytes go-cty reads as `number is required`. Emitting a
    value Terraform's own library cannot read back is worse than refusing it.

    Infinity is deliberately *not* refused here: go-cty has `+Inf` and `-Inf`,
    writes them as float64, and reads ours back. Only the JSON codec refuses an
    infinity, because JSON has no spelling for one -- and go-cty refuses there
    too.

    Construction is left alone. No stdlib function produces a NaN any more --
    `pow` and `log` answer `result is not a number`, `divide(0, 0)` refuses on
    both sides -- so a NaN only arrives from a caller who built one, and
    `format` still spells it the way Go's `fmt` does. The wire is the boundary
    that has to hold.
    """
    if decimal_val.is_nan():
        raise SerializationError(ERR_NAN_NOT_SERIALIZABLE)

    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # go-cty emits a float64 only when the conversion is *exact*
        # (`cty/msgpack/marshal.go:92`); otherwise it writes the decimal text.
        #
        # The exactness test has to compare against the float's true binary
        # value, `Decimal(float_val)`, not against `str(float_val)`. The latter
        # is the shortest repr that round-trips, so `str(0.1)` is "0.1" and the
        # comparison said "no precision lost" for a float that is really
        # 0.1000000000000000055511151231257827. We then wrote that float to the
        # wire where go-cty writes the string "0.1", so the two implementations
        # disagreed byte for byte, and Terraform read back a different number
        # than was written -- a perpetual diff on every non-integer attribute.
        float_val = float(decimal_val)
        try:
            is_exact = Decimal(float_val) == decimal_val
        except (ValueError, OverflowError, ArithmeticError):
            is_exact = False

        if is_exact:
            return float_val

        return _decimal_text(decimal_val)


def _decimal_text(decimal_val: Decimal) -> str:
    """Plain decimal notation without an exponent -- go-cty's `Text('f', -1)`."""
    text = format(decimal_val, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _reject_marks(value: CtyValue[Any], path: str) -> None:
    """Marks have no wire representation, so serializing one is an error.

    Checked at every level rather than only at the root, so the message can say
    *where* the mark is -- go-cty does the same, and for a marked attribute
    buried in a large object the location is most of the useful information.
    Shallow on purpose: the recursion reaches most nested values anyway, and a
    deep walk at every level would re-scan the whole structure repeatedly.

    "Most" is not "all", which is why `cty_to_msgpack` also asks once, deeply,
    before starting. A container is flagged unknown when any element is unknown
    (`list.py`, `tuple.py`, `set.py`), and an unknown serializes to a marker
    without the encoder ever descending -- so a list holding a marked unknown
    reached the wire with its top level unmarked and its mark silently dropped.
    """
    if value.marks:
        raise CtyMarksSerializationError(path=path or None)


def _convert_value_to_serializable(value: CtyValue[Any], schema: CtyType[Any], path: str = "") -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(value)
    _reject_marks(value, path)
    # The dynamic branch comes *first*, including for an unknown or a null.
    # go-cty writes the `[type, value]` envelope for every value in a dynamic
    # position, because the concrete type is the only thing carrying it across;
    # this checked knownness first, so an unknown-of-string went on the wire as
    # a bare `d40000` and a null-of-string as a bare `c0`. Reading those back at
    # a dynamic position, go-cty answers `type=dynamic` where its own bytes give
    # `type=string` -- and deferring as `string` and deferring as `dynamic` are
    # different answers to a Terraform plan, which is why the type is written.
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value, path)
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(inner_val, schema, path)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(inner_val, schema, path)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(CtyList[Any] | CtySet[Any], schema)  # type: ignore[redundant-cast]
        return _serialize_collection_value(inner_val, schema_narrowed, path)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(inner_val, schema, path)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def _msgpack_default_handler(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return _serialize_decimal_value(obj)
    error_message = ERR_OBJECT_NOT_MSGPACK_SERIALIZABLE.format(type_name=type(obj).__name__)
    raise TypeError(error_message)


def cty_to_msgpack(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    # Asked once, deeply, before encoding. The per-level check inside the
    # encoder gives the path to the offending value, but it only sees values
    # the encoder actually descends into -- and it does not descend into an
    # unknown, which a container becomes as soon as any element is unknown.
    # Without this a marked unknown inside a list, map or tuple serialized
    # silently, dropping exactly the flag this refusal exists to protect.
    if isinstance(value, CtyValue) and collect_marks_deep(value):
        _reject_marks(value, "")
        raise CtyMarksSerializationError()
    serializable_data = _convert_value_to_serializable(value, schema)
    result: bytes = msgpack.packb(
        serializable_data,
        default=_msgpack_default_handler,
        use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
    )
    return result


def _unpacked_to_cty(data: Any, schema: CtyType[Any]) -> CtyValue[Any]:
    if isinstance(data, UnknownValue):
        return CtyValue.unknown(schema, value=data)
    if data is None:
        return CtyValue.null(schema)
    return schema.validate(data)


def cty_from_msgpack(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    # go-cty answers EOF here. This used to answer a null of `cty_type`, which
    # erased the difference between "a null was encoded" (the byte 0xc0) and
    # "nothing arrived"; a truncated or missing payload became valid state.
    # Terraform core maps an *absent* DynamicValue to a null itself, and so does
    # pyvider's `marshaler.unmarshal`, so the codec can be strict.
    if not data:
        raise DeserializationError("cty_from_msgpack: empty input; a null is encoded as 0xc0, not as no bytes")
    # Every failure out of here is a CtyError: DeserializationError for bytes
    # that are not a MessagePack payload, the type's own CtyValidationError for a
    # payload that decodes but does not fit. msgpack's exceptions -- FormatError,
    # ExtraData, StackError, the bare ValueError for truncated input, a
    # UnicodeDecodeError inside a string -- used to escape as themselves, so a
    # caller wanting to catch every decode failure had to catch Exception.
    # `_ext_hook` raises DeserializationError itself and passes through.
    try:
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )
    except DeserializationError:
        raise
    except (ValueError, TypeError) as e:
        raise DeserializationError(f"cty_from_msgpack: not a MessagePack payload: {e}") from e

    if (
        isinstance(cty_type, CtyDynamic)
        and isinstance(raw_unpacked, list)
        and len(raw_unpacked) == TWO_VALUE
        and isinstance(raw_unpacked[0], bytes)
    ):
        try:
            type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
        actual_type = parse_tf_type_to_ctytype(type_spec)
        inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
        return CtyValue(vtype=cty_type, value=inner_value)

    return _unpacked_to_cty(raw_unpacked, cty_type)


# 🌊🪢🔚
