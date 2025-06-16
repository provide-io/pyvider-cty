from __future__ import annotations

#
# pyvider/cty/conversion/formats/json.py
#

"""
JSON encoder for CTY wire format.

This module provides a comprehensive implementation of the FormatEncoder
interface for JSON serialization. It handles conversion between CTY values
and JSON-encoded bytes with full preservation of type information, state,
and other metadata.

The implementation supports both compact and pretty-printed output,
custom encoders for CTY-specific types, and robust error handling.
"""

from decimal import Decimal
import json
from typing import ClassVar, TypeVar, cast

from pyvider.cty.conversion.formats.base import FormatEncoder, register_formatter
from pyvider.cty.conversion.wire import WireFormatType
from pyvider.cty.exceptions import (  # Added CtyValidationError
    CtyValidationError,
    EncodingError,
)

# Import Cty types for type checking
from pyvider.cty.types import (  # Added all types for _create_type_from_name
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
)
from pyvider.cty.values import CtyValue
from pyvider.telemetry import logger

T = TypeVar("T")


@register_formatter(WireFormatType.JSON)
class JsonEncoder(FormatEncoder):
    """
    JSON encoder implementation for CTY wire format.

    This class handles serialization and deserialization between CTY values
    and JSON-encoded bytes. It includes special handling for CTY-specific
    concepts like unknown values, null values, marks, and type information.

    The encoder supports both compact and pretty-printed output, and includes
    comprehensive validation and error handling.
    """

    # Type marker constants for encoding
    TYPE_MARKER: ClassVar[str] = "type_name"  # Changed from "type"
    UNKNOWN_MARKER: ClassVar[str] = "is_unknown"
    NULL_MARKER: ClassVar[str] = "is_null"
    MARKS_MARKER: ClassVar[str] = "marks"

    @classmethod
    def format_type(cls) -> WireFormatType:
        """
        Get the wire format type for this encoder.

        Returns:
            WireFormatType.JSON
        """
        return WireFormatType.JSON

    @classmethod
    def encode(cls, value: object, **options) -> bytes:
        """
        Encode a CTY value to JSON bytes.
        """
        logger.debug(f"🧩📝🔄 Encoding to JSON: {type(value).__name__}")
        indent = options.get("indent")
        sort_keys = options.get("sort_keys", False)
        preserve_type = options.get("preserve_type", True)
        compact = options.get("compact", True)

        try:
            if not isinstance(value, CtyValue):
                error_msg = f"Expected CtyValue, got {type(value).__name__}"
                logger.error(f"🧩📝❌ {error_msg}")
                raise TypeError(error_msg)
            value_dict = cls._value_to_dict(value, preserve_type=preserve_type)
            json_bytes = json.dumps(
                value_dict,
                indent=None if compact else indent,
                sort_keys=sort_keys,
                default=cls._json_default,
            ).encode("utf-8")
            logger.debug(f"🧩📝✅ Encoded to {len(json_bytes)} bytes of JSON")
            return json_bytes
        except Exception as e:
            if isinstance(e, EncodingError):
                raise
            error_msg = f"Failed to encode to JSON: {e}"
            logger.error(f"🧩📝❌ {error_msg}", exc_info=True)
            raise EncodingError(error_msg, encoding="json", data=value) from e

    @classmethod
    def decode(cls, data: bytes, **options) -> object:
        """
        Decode JSON bytes to a CTY value.
        """
        logger.debug(f"🧩🔍🔄 Decoding from JSON: {len(data)} bytes")
        preserve_type = options.get("preserve_type", True)
        try:
            # ADD DEBUG LOGS HERE
            logger.debug(f"JULES_JSON_LOADS_INPUT_BYTES (first 150): {data[:150]!r}")
            decoded_string_preview = "ERROR_DECODING_BYTE_INPUT_FOR_PREVIEW"
            try:
                decoded_string_preview = data.decode(
                    "utf-8"
                )  # Attempt to decode for logging
                logger.debug(
                    f"JULES_JSON_LOADS_INPUT_STR (first 150): {decoded_string_preview[:150]}"
                )
            except Exception as e_decode_preview:
                logger.debug(
                    f"JULES_JSON_LOADS_INPUT_STR: Preview decode error: {e_decode_preview!r}"
                )

            try:
                json_dict = json.loads(data)  # THE ACTUAL CALL

                # ADD DEBUG LOG HERE
                logger.debug(f"JULES_JSON_LOADS_OUTPUT_DICT: {json_dict!r}")
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON: {e}"
                logger.error(f"🧩🔍❌ {error_msg}")
                raise EncodingError(error_msg, encoding="json", data=data) from e
            result = cls._dict_to_value(json_dict, preserve_type=preserve_type)
            logger.debug(f"🧩🔍✅ Decoded JSON to {type(result).__name__}")
            return result
        except Exception as e:
            if isinstance(e, EncodingError):
                raise
            error_msg = f"Failed to decode from JSON: {e}"
            logger.error(f"🧩🔍❌ {error_msg}", exc_info=True)
            raise EncodingError(error_msg, encoding="json", data=data) from e

    @classmethod
    def _value_to_dict(
        cls, value: CtyValue, preserve_type: bool = True
    ) -> dict[str, object]:
        result = {}
        if preserve_type:
            result[cls.TYPE_MARKER] = value.type.__class__.__name__
            if (
                hasattr(value.type, "element_type")
                and value.type.element_type is not None
            ):
                result["element_type"] = value.type.element_type.__class__.__name__
            elif hasattr(value.type, "value_type"):  # CtyMap
                result["key_type"] = value.type.key_type.__class__.__name__
                result["value_type"] = value.type.value_type.__class__.__name__

        if value.is_unknown:
            result[cls.UNKNOWN_MARKER] = True
            return result
        if value.is_null:
            result[cls.NULL_MARKER] = True
            return result

        raw_internal_value = value.value
        is_current_value_collection = isinstance(value.type, CtyList | CtyMap)

        def recursively_encode_value(
            item: object, is_direct_collection_member: bool = False
        ) -> object:
            # Types are already imported at module level. No need for local import here if module level is sufficient.
            # from pyvider.cty.types import CtyDynamic, CtyString, CtyNumber, CtyBool

            logger.debug(
                f"RECURSE_ENCODE: item={item!r}, item_type={type(item)!r}, is_direct_collection_member={is_direct_collection_member}"
            )

            if isinstance(item, CtyValue):
                # Handle unknown and null CtyValues first
                if item.is_unknown:
                    logger.debug("RECURSE_ENCODE: item is unknown.")
                    temp_res = {cls.UNKNOWN_MARKER: True}
                    if preserve_type:  # preserve_type is from the outer scope
                        temp_res[cls.TYPE_MARKER] = item.type.__class__.__name__
                    return temp_res
                if item.is_null:
                    logger.debug("RECURSE_ENCODE: item is null.")
                    temp_res = {cls.NULL_MARKER: True}
                    if preserve_type:  # preserve_type is from the outer scope
                        temp_res[cls.TYPE_MARKER] = item.type.__class__.__name__
                    return temp_res

                logger.debug(
                    f"RECURSE_ENCODE: CtyValue detected. item.type={item.type!r}, item.value={item.value!r}, item.is_unknown={item.is_unknown}, item.is_null={item.is_null}"
                )

                # Now, the simplification logic
                if is_direct_collection_member:
                    logger.debug(
                        f"RECURSE_ENCODE: is_direct_collection_member is True. item.type={item.type!r}"
                    )
                    actual_value = item.value  # Raw Python value
                    logger.debug(
                        f"RECURSE_ENCODE: actual_value={actual_value!r}, type(actual_value)={type(actual_value)!r}"
                    )

                    is_item_type_dynamic = isinstance(item.type, CtyDynamic)
                    logger.debug(
                        f"RECURSE_ENCODE: isinstance(item.type, CtyDynamic) = {is_item_type_dynamic}"
                    )

                    is_actual_value_primitive = isinstance(
                        actual_value, str | int | float | bool | Decimal
                    )
                    logger.debug(
                        f"RECURSE_ENCODE: isinstance(actual_value, PyPrimitive) = {is_actual_value_primitive}"
                    )

                    if is_item_type_dynamic:
                        # If the dynamic value holds a CtyValue (actual_value), process that CtyValue.
                        if isinstance(actual_value, CtyValue):
                            # If the inner CtyValue is a primitive, simplify to its Python value.
                            if isinstance(
                                actual_value.type, CtyString | CtyNumber | CtyBool
                            ):
                                logger.debug(
                                    "RECURSE_ENCODE: Simplifying CtyDynamic holding a CtyPrimitive."
                                )
                                inner_py_value = actual_value.value
                                if isinstance(inner_py_value, Decimal):
                                    return str(inner_py_value)
                                return inner_py_value
                            # If the inner CtyValue is another collection/object, encode it directly,
                            # effectively "unwrapping" the CtyDynamic for the JSON structure.
                            elif isinstance(
                                actual_value.type,
                                CtyList | CtyMap | CtySet | CtyObject | CtyTuple,
                            ):
                                logger.debug(
                                    "RECURSE_ENCODE: Simplifying CtyDynamic holding a CtyCollection/Object by unwrapping."
                                )
                                return cls._value_to_dict(
                                    actual_value, preserve_type
                                )  # Use preserve_type from outer scope
                        # If the dynamic value directly holds a Python primitive
                        elif is_actual_value_primitive:
                            logger.debug(
                                "RECURSE_ENCODE: Simplifying CtyDynamic with direct primitive."
                            )
                            if isinstance(actual_value, Decimal):
                                return str(actual_value)
                            return actual_value
                        # Else, if actual_value is not a CtyValue and not a primitive (e.g. a raw list/dict within dynamic),
                        # let it be processed by the later dict/list handlers or fallback.
                        # This case might indicate an unusual setup for CtyDynamic.

                    is_item_type_primitive = isinstance(
                        item.type, CtyString | CtyNumber | CtyBool
                    )
                    logger.debug(
                        f"RECURSE_ENCODE: isinstance(item.type, CtyPrimitive) = {is_item_type_primitive}"
                    )

                    if is_item_type_primitive:
                        logger.debug("RECURSE_ENCODE: Simplifying direct CtyPrimitive.")
                        if isinstance(actual_value, Decimal):
                            return str(actual_value)
                        return actual_value

                    logger.debug(
                        "RECURSE_ENCODE: Did not meet simplification criteria for direct collection member."
                    )

                logger.debug(
                    f"RECURSE_ENCODE: Defaulting to full cls._value_to_dict for CtyValue item: {item!r}"
                )
                return cls._value_to_dict(item, preserve_type)  # Fallback

            elif isinstance(item, dict):
                logger.debug("RECURSE_ENCODE: item is dict, processing items...")
                return {
                    k: recursively_encode_value(
                        v,
                        is_direct_collection_member=(
                            is_current_value_collection
                            and isinstance(value.type, CtyMap)
                        ),
                    )
                    for k, v in item.items()
                }
            elif isinstance(item, list | tuple):
                logger.debug(
                    "RECURSE_ENCODE: item is list/tuple, processing elements..."
                )
                return [
                    recursively_encode_value(
                        elem,
                        is_direct_collection_member=(
                            is_current_value_collection
                            and isinstance(value.type, CtyList)
                        ),
                    )
                    for elem in item
                ]
            elif isinstance(item, Decimal):
                logger.debug("RECURSE_ENCODE: item is Decimal, converting to str.")
                return str(item)

            logger.debug(
                f"RECURSE_ENCODE: item is raw primitive, returning as is: {item!r}"
            )
            return item

        result["value"] = recursively_encode_value(
            raw_internal_value, is_direct_collection_member=is_current_value_collection
        )

        if value._marks:
            result[cls.MARKS_MARKER] = sorted([str(m) for m in value._marks])
        return result

    @classmethod
    def _dict_to_value(
        cls, data: dict[str, object], preserve_type: bool = True
    ) -> CtyValue:
        logger.debug("🧩🔍🔄 Converting dictionary to CtyValue")

        # Jules's debug logging
        logger.debug(f"JULES_DEBUG_JSON_DECODE: _dict_to_value received data: {data!r}")
        logger.debug(
            f"JULES_DEBUG_JSON_DECODE: data has is_null? {cls.NULL_MARKER in data}. Value: {data.get(cls.NULL_MARKER)}"
        )
        logger.debug(
            f"JULES_DEBUG_JSON_DECODE: data has is_unknown? {cls.UNKNOWN_MARKER in data}. Value: {data.get(cls.UNKNOWN_MARKER)}"
        )
        logger.debug(
            f"JULES_DEBUG_JSON_DECODE: data has wire_type_marker ('{cls.TYPE_MARKER}')? {cls.TYPE_MARKER in data}. Value: {data.get(cls.TYPE_MARKER)}"
        )
        logger.debug(
            f"JULES_DEBUG_JSON_DECODE: data has comparable_type_marker ('type_name')? {'type_name' in data}. Value: {data.get('type_name')}"
        )
        logger.debug(
            f"JULES_DEBUG_JSON_DECODE: data has value? {'value' in data}. Value: {data.get('value')!r}"
        )

        try:
            # Order of checks: UNKNOWN, then NULL, then typed, then untyped.
            if data.get(cls.UNKNOWN_MARKER, False):  # checks for "is_unknown": true
                return cls._create_unknown_value(data, preserve_type=preserve_type)
            if data.get(cls.NULL_MARKER, False):  # checks for "is_null": true
                return cls._create_null_value(data, preserve_type=preserve_type)

            type_key_to_use = None
            if preserve_type:
                if "type_name" in data:
                    type_key_to_use = "type_name"
                elif cls.TYPE_MARKER in data:
                    type_key_to_use = cls.TYPE_MARKER

            if type_key_to_use:
                return cls._create_typed_value(data, type_key_to_use)
            else:
                return cls._create_untyped_value(data)
        except Exception as e:
            error_msg = f"Failed to convert dictionary to CtyValue: {e}"
            logger.error(f"🧩🔍❌ {error_msg}", exc_info=True)  # Added exc_info
            raise EncodingError(error_msg, encoding="json") from e

    @classmethod
    def _create_unknown_value(
        cls, data: dict[str, object], preserve_type: bool = True
    ) -> CtyValue:
        logger.debug("🧩🔍🔄 Creating unknown CtyValue")
        type_name_str = "CtyDynamic"
        if preserve_type:
            type_name_str = data.get(
                "type_name", data.get(cls.TYPE_MARKER, "CtyDynamic")
            )

        cty_type = cls._create_type_from_name(
            str(type_name_str), data
        )  # Ensure type_name_str is str
        return CtyValue.unknown(cty_type)

    @classmethod
    def _create_null_value(
        cls, data: dict[str, object], preserve_type: bool = True
    ) -> CtyValue:
        logger.debug("🧩🔍🔄 Creating null CtyValue")
        type_name_str = "CtyDynamic"
        if preserve_type:
            type_name_str = data.get(
                "type_name", data.get(cls.TYPE_MARKER, "CtyDynamic")
            )

        cty_type = cls._create_type_from_name(
            str(type_name_str), data
        )  # Ensure type_name_str is str
        return CtyValue.null(cty_type)

    @classmethod
    def _create_typed_value(cls, data: dict[str, object], type_key: str) -> CtyValue:
        logger.debug(f"JULES_CREATE_TYPED_VALUE: Input data: {data!r}")
        type_name_str = str(data.get(type_key, "CtyDynamic"))
        value_data = data.get("value")

        cty_type = cls._create_type_from_name(type_name_str, data)
        logger.debug(
            f"JULES_CREATE_TYPED_VALUE: Determined cty_type: {cty_type!r}, value_data: {value_data!r}"
        )

        if (
            value_data is None
            and not isinstance(cty_type, CtyDynamic)
            and not data.get(cls.NULL_MARKER, False)
        ):
            logger.warning(
                f"JULES_CREATE_TYPED_VALUE: Non-null typed value has None in 'value' field. Type: {type_name_str}. Data: {data!r}"
            )
            # Proceeding, validate will likely handle this (e.g. create default empty for collections if appropriate, or error)
            pass

        # Recursive decoding for complex types needs to consider the type_key for elements/attributes if they are full CTY dicts
        # However, the JSON comparable format usually has primitive values or fully specified CTY dicts for elements/attributes.
        # The _dict_to_value called recursively will use its own logic to determine type_key.

        if isinstance(cty_type, CtyList) and isinstance(value_data, list):
            processed_elements = []
            for elem in value_data:
                if isinstance(elem, dict) and (
                    "type_name" in elem
                    or cls.TYPE_MARKER in elem
                    or cls.UNKNOWN_MARKER in elem
                    or cls.NULL_MARKER in elem
                ):
                    processed_elements.append(
                        cls._dict_to_value(elem, preserve_type=True)
                    )
                else:
                    processed_elements.append(elem)
            return cty_type.validate(processed_elements)

        elif isinstance(cty_type, CtyMap | CtyObject) and isinstance(value_data, dict):
            processed_items = {}
            for k, v_item in value_data.items():
                if isinstance(v_item, dict) and (
                    "type_name" in v_item
                    or cls.TYPE_MARKER in v_item
                    or cls.UNKNOWN_MARKER in v_item
                    or cls.NULL_MARKER in v_item
                ):
                    processed_items[k] = cls._dict_to_value(v_item, preserve_type=True)
                else:
                    processed_items[k] = v_item
            return cty_type.validate(processed_items)

        elif isinstance(cty_type, CtyTuple) and isinstance(
            value_data, list
        ):  # Handle CtyTuple elements
            processed_elements = []
            if len(value_data) == len(cty_type.element_types):
                for _i, elem_data in enumerate(value_data):
                    # Determine the actual type of the element based on the tuple's schema
                    # This assumes elem_data is the CTY JSON comparable dict for the element
                    if isinstance(elem_data, dict) and (
                        "type_name" in elem_data
                        or cls.TYPE_MARKER in elem_data
                        or cls.UNKNOWN_MARKER in elem_data
                        or cls.NULL_MARKER in elem_data
                    ):
                        processed_elements.append(
                            cls._dict_to_value(elem_data, preserve_type=True)
                        )
                    else:  # Primitive value, assume it matches the element type
                        processed_elements.append(elem_data)
            else:
                # Length mismatch, let validate handle the error
                logger.warning(
                    f"Tuple length mismatch during typed value creation. Expected {len(cty_type.element_types)}, got {len(value_data)} for {type_name_str}"
                )
                # Fall through to direct validation which should raise an error
                pass  # Let validate below handle it

            # If elements were processed, use them for validation
            if len(processed_elements) == len(cty_type.element_types):
                return cty_type.validate(
                    tuple(processed_elements)
                )  # CtyTuple.validate expects a tuple

        try:
            return cty_type.validate(value_data)
        except CtyValidationError:  # Make sure CtyValidationError is imported
            if isinstance(value_data, dict) and (
                "type_name" in value_data or cls.TYPE_MARKER in value_data
            ):
                return cls._dict_to_value(value_data, preserve_type=True)
            raise

    @classmethod
    def _create_untyped_value(cls, data: dict[str, object]) -> CtyValue:
        logger.debug("🧩🔍🔄 Creating untyped CtyValue")
        value = data.get("value")
        match value:
            case bool():
                return CtyValue.bool(value)
            case int() | float():
                return CtyValue.number(value)
            case str():
                return CtyValue.string(value)
            case list():
                return CtyValue.list(
                    CtyDynamic(), value
                )  # Elements will be validated by CtyList
            case dict():
                return CtyValue.map(
                    CtyString(), CtyDynamic(), value
                )  # Values will be validated by CtyMap
            case None:
                return CtyValue.null(CtyDynamic())
            case _:
                error_msg = f"Cannot infer type for value: {value}"
                logger.error(f"🧩🔍❌ {error_msg}")
                raise EncodingError(
                    f"Cannot infer type for value: {value}", encoding="json"
                )

    @classmethod
    def _create_type_from_name(
        cls, type_name_str: str, data_dict_for_extra_type_info: dict[str, object]
    ) -> CtyType:
        logger.debug(
            f"🧩🔍🔄 Creating type from name string: '{type_name_str}' with extra info from: {data_dict_for_extra_type_info!r}"
        )

        # Handle direct CtyType class names (e.g., from cls.TYPE_MARKER or recursive calls)
        if type_name_str == "CtyBool":
            return CtyBool()
        if type_name_str == "CtyNumber":
            return CtyNumber()
        if type_name_str == "CtyString":
            return CtyString()
        if type_name_str == "CtyDynamic":
            return CtyDynamic()
        if type_name_str == "CtyList":
            element_type_name = cast(
                str, data_dict_for_extra_type_info.get("element_type", "CtyDynamic")
            )
            return CtyList(
                element_type=cls._create_type_from_name(element_type_name, {})
            )
        if type_name_str == "CtyMap":
            key_type_name = cast(
                str, data_dict_for_extra_type_info.get("key_type", "CtyString")
            )
            value_type_name = cast(
                str, data_dict_for_extra_type_info.get("value_type", "CtyDynamic")
            )
            return CtyMap(
                key_type=cls._create_type_from_name(key_type_name, {}),
                value_type=cls._create_type_from_name(value_type_name, {}),
            )
        if type_name_str == "CtySet":
            element_type_name = cast(
                str, data_dict_for_extra_type_info.get("element_type", "CtyDynamic")
            )
            return CtySet(
                element_type=cls._create_type_from_name(element_type_name, {})
            )
        if (
            type_name_str == "CtyObject"
        ):  # Added for completeness if "type":"CtyObject" is used
            # This path expects attributes to be in data_dict_for_extra_type_info if it's our own encoding
            # However, JSON comparable format embeds attributes in the type_name_str.
            # The string parsing below handles the JSON comparable format.
            # If data_dict_for_extra_type_info has 'attributes', use it.
            if "attributes" in data_dict_for_extra_type_info and isinstance(
                data_dict_for_extra_type_info["attributes"], dict
            ):
                attr_types = {
                    k: cls._create_type_from_name(v, {})
                    for k, v in data_dict_for_extra_type_info["attributes"].items()
                }
                return CtyObject(attr_types)
            # Fall through to string parsing if not our "type":"CtyObject" format.
        if type_name_str == "CtyTuple":  # Added for completeness
            if "element_types" in data_dict_for_extra_type_info and isinstance(
                data_dict_for_extra_type_info["element_types"], list
            ):
                el_types = tuple(
                    cls._create_type_from_name(et_name, {})
                    for et_name in data_dict_for_extra_type_info["element_types"]
                )
                return CtyTuple(el_types)
            # Fall through

        # Handle stringified types (e.g., from 'type_name' in JSON comparable format)
        if type_name_str == "string":
            return CtyString()
        if type_name_str == "number":
            return CtyNumber()
        if type_name_str == "bool":
            return CtyBool()
        if type_name_str == "dynamic":
            return CtyDynamic()

        if type_name_str.startswith("list(") and type_name_str.endswith(")"):
            return CtyList(
                element_type=cls._create_type_from_name(
                    type_name_str[len("list(") : -1], {}
                )
            )
        if type_name_str.startswith("map(") and type_name_str.endswith(")"):
            return CtyMap(
                key_type=CtyString(),
                value_type=cls._create_type_from_name(
                    type_name_str[len("map(") : -1], {}
                ),
            )
        if type_name_str.startswith("set(") and type_name_str.endswith(")"):
            return CtySet(
                element_type=cls._create_type_from_name(
                    type_name_str[len("set(") : -1], {}
                )
            )

        if type_name_str.startswith("object({") and type_name_str.endswith("})"):
            attrs_str = type_name_str[len("object({") : -2]
            if not attrs_str:
                return CtyObject({})
            attr_map = {}
            try:
                attr_pairs_strs = (
                    _split_by_delimiter_respecting_nesting_for_json_decode(
                        attrs_str, ","
                    )
                )
                for pair_str in attr_pairs_strs:
                    name, t_str = pair_str.split("=", 1)
                    attr_map[name.strip()] = cls._create_type_from_name(
                        t_str.strip(), {}
                    )
            except Exception as e_parse:
                logger.warning(
                    f"Could not parse object attributes from '{attrs_str}': {e_parse}. Falling back to CtyDynamic."
                )
                return CtyDynamic()
            return CtyObject(attr_map)

        if type_name_str.startswith("tuple([") and type_name_str.endswith("])"):
            elems_str = type_name_str[len("tuple([") : -2]
            if not elems_str:
                return CtyTuple(tuple())
            try:
                elem_types_strs = (
                    _split_by_delimiter_respecting_nesting_for_json_decode(
                        elems_str, ","
                    )
                )
                return CtyTuple(
                    tuple(
                        cls._create_type_from_name(s.strip(), {})
                        for s in elem_types_strs
                    )
                )
            except Exception as e_parse:
                logger.warning(
                    f"Could not parse tuple elements from '{elems_str}': {e_parse}. Falling back to CtyDynamic."
                )
                return CtyDynamic()

        logger.warning(
            f"Failed to fully parse type string '{type_name_str}', falling back to CtyDynamic."
        )
        return CtyDynamic()

    @classmethod
    def _json_default(cls, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


# Helper for _create_type_from_name, simplified for this context
def _split_by_delimiter_respecting_nesting_for_json_decode(
    text: str, delimiter: str
) -> list[str]:
    if not text:
        return []
    parts = []
    balance = 0
    current_part_start = 0
    nesting_chars = {"(": ")", "[": "]", "{": "}"}
    opening_chars = nesting_chars.keys()
    closing_chars = nesting_chars.values()
    for i, char in enumerate(text):
        if char in opening_chars:
            balance += 1
        elif char in closing_chars:
            balance -= 1
        elif char == delimiter and balance == 0:
            parts.append(text[current_part_start:i].strip())
            current_part_start = i + len(delimiter)
    parts.append(text[current_part_start:].strip())
    return [p for p in parts if p]


# 🐍🏗️🐣
