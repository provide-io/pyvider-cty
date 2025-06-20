# src/pyvider/cty/conversion/formats/json.py
"""
JSON specific CTY <-> Python value encoder/decoder.

This module implements the `FormatEncoder` interface for handling
CTY value serialization to and from JSON-encoded bytes. It ensures
that CTY type information, null/unknown states, and marks are
preserved or appropriately represented in the JSON format.
"""
from decimal import Decimal
import json
from typing import ClassVar, TypeVar, cast

from pyvider.cty.conversion.formats.base import FormatEncoder # Remove register_formatter
from pyvider.cty.conversion.wire import WireFormatType, WireFormatRegistry # Import WireFormatRegistry
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
    CtyType,  # Added CtyType
)
from pyvider.cty.values import CtyValue
from pyvider.telemetry import logger

T = TypeVar("T")


@WireFormatRegistry.register(WireFormatType.JSON) # Use WireFormatRegistry
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
    TYPE_MARKER: ClassVar[str] = "type_name"
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
    def encode(cls, value: object, **options: object) -> bytes:
        """
        Internal method to encode a CTY value to JSON bytes.
        Prefer using `marshal`.
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
    def decode(cls, data: bytes, **options: object) -> object:
        """
        Internal method to decode JSON bytes to a CTY value.
        Prefer using `unmarshal`.
        """
        logger.debug(f"🧩🔍🔄 Decoding from JSON: {len(data)} bytes")
        preserve_type = options.get("preserve_type", True)
        expected_type = cast(CtyType | None, options.get("expected_type")) # Get expected_type

        try:
            try:
                json_dict = json.loads(data)  # THE ACTUAL CALL

            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON: {e}"
                logger.error(f"🧩🔍❌ {error_msg}")
                raise EncodingError(error_msg, encoding="json", data=data) from e
            result = cls._dict_to_value(json_dict, preserve_type=preserve_type, expected_type=expected_type) # Pass expected_type
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
            result[cls.TYPE_MARKER] = str(value.type) # Store the full string representation of the type

        if value.is_unknown:
            # If type was already added, UNKNOWN_MARKER is just a flag on top of it.
            # If not preserve_type, it's crucial TYPE_MARKER is not added here if not already.
            # The original logic for UNKNOWN_MARKER didn't add TYPE_MARKER if preserve_type was false.
            # This behavior is maintained: TYPE_MARKER is only added if preserve_type is True.
            result[cls.UNKNOWN_MARKER] = True
            return result
        if value.is_null:
            result[cls.NULL_MARKER] = True
            # Similar to UNKNOWN_MARKER, TYPE_MARKER is only added if preserve_type is True.
            return result

        raw_internal_value = value.value
        # Determine if the current value being processed is a direct member of a list or map,
        # as this affects simplification logic within recursively_encode_value.
        # This check needs to be based on the *parent* CtyValue's type if we are inside recursion,
        # but for the top-level call, value.type is appropriate.
        is_top_level_value_collection = isinstance(value.type, CtyList | CtyMap)


        def recursively_encode_value(
            item: object, is_direct_collection_member: bool = False # This flag indicates if `item` is a direct element of a List/Map
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
                        temp_res[cls.TYPE_MARKER] = str(item.type) # Use full type string
                    return temp_res
                if item.is_null:
                    logger.debug("RECURSE_ENCODE: item is null.")
                    temp_res = {cls.NULL_MARKER: True}
                    if preserve_type:  # preserve_type is from the outer scope
                        temp_res[cls.TYPE_MARKER] = str(item.type) # Use full type string
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
                            if isinstance(actual_value.type, CtyString) or isinstance(actual_value.type, CtyBool):
                                # For CtyString and CtyBool, simplify to their Python values
                                logger.debug(
                                    "RECURSE_ENCODE: Simplifying CtyDynamic holding a CtyString or CtyBool."
                                )
                                return actual_value.value
                            elif isinstance(actual_value.type, CtyNumber):
                                # For CtyNumber, do not simplify to a string. Serialize the CtyNumber value fully.
                                # This ensures type information is preserved for CtyDynamic(CtyNumber(...)).
                                logger.debug(f"RECURSE_ENCODE: CtyDynamic(CtyNumber) detected. Serializing inner CtyNumber fully: {actual_value!r}")
                                return cls._value_to_dict(actual_value, preserve_type) # preserve_type is from the outer scope's options
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
                            if isinstance(actual_value, Decimal): # This will be a string representation of Decimal
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
                        actual_value_to_return = item.value # Use item.value which is already processed for CtyNumber (Decimal)
                        if isinstance(actual_value_to_return, Decimal):
                            return str(actual_value_to_return)
                        return actual_value_to_return

                    logger.debug(
                        "RECURSE_ENCODE: Did not meet simplification criteria for direct collection member."
                    )

                logger.debug(
                    f"RECURSE_ENCODE: Defaulting to full cls._value_to_dict for CtyValue item: {item!r}"
                )
                return cls._value_to_dict(item, preserve_type)

            elif isinstance(item, dict):
                logger.debug("RECURSE_ENCODE: item is dict, processing items...")
                return {
                    k: recursively_encode_value(
                        v,
                        # For map items, is_direct_collection_member should be True if the parent `value` is a CtyMap
                        is_direct_collection_member=isinstance(value.type, CtyMap)
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
                         # For list/tuple elements, is_direct_collection_member should be True if the parent `value` is a CtyList or CtyTuple
                        is_direct_collection_member=(isinstance(value.type, CtyList) or isinstance(value.type, CtyTuple))
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
            raw_internal_value, is_direct_collection_member=is_top_level_value_collection
        )

        if value._marks:
            result[cls.MARKS_MARKER] = sorted([str(m) for m in value._marks])
        return result

    @classmethod
    def _dict_to_value(
        cls, data: dict[str, object], preserve_type: bool = True, expected_type: CtyType | None = None
    ) -> CtyValue:
        logger.debug(f"🧩🔍🔄 Converting dictionary to CtyValue, expected_type: {expected_type!r}")

        try:
            # Order of checks: UNKNOWN, then NULL, then typed, then untyped.
            if data.get(cls.UNKNOWN_MARKER, False):  # checks for "is_unknown": true
                return cls._create_unknown_value(data, preserve_type=preserve_type, expected_type=expected_type)
            if data.get(cls.NULL_MARKER, False):  # checks for "is_null": true
                return cls._create_null_value(data, preserve_type=preserve_type, expected_type=expected_type)

            type_key_to_use = None
            if preserve_type:
                if "type_name" in data:
                    type_key_to_use = "type_name"
                elif cls.TYPE_MARKER in data:
                    type_key_to_use = cls.TYPE_MARKER

            if type_key_to_use:
                return cls._create_typed_value(data, type_key_to_use, expected_type=expected_type)
            else:
                # If no type info in data and preserve_type is false,
                # try to use expected_type if available, otherwise infer.
                if expected_type and not preserve_type: # Check preserve_type here
                    logger.debug(f"🧩🔍🔄 No type in data, using provided expected_type: {expected_type!r} for untyped value creation path.")
                    # This path assumes _create_untyped_value can leverage expected_type or its _create_type_from_name can.
                    # For now, _create_untyped_value does not use expected_type, it infers.
                    # We might need a new path or modify _create_typed_value to handle this.
                    # Let's assume for now that if type_key_to_use is None, we always infer.
                    # The change will be more in _create_type_from_name to use expected_type.
                    # This specific call to _create_untyped_value might still be okay if data['value'] is a primitive.
                    # If data['value'] is complex, _create_untyped_value will create dynamic collections.
                    # This is where expected_type would be most useful.
                    #
                    # Re-evaluating: if preserve_type is False, and we have an expected_type,
                    # we should probably try to validate against expected_type directly.
                    # The current structure of _create_typed_value relies on a type_key from data.
                    # Let's pass expected_type to _create_untyped_value and see if it can use it.
                    # For now, no change to this specific call, rely on _create_type_from_name enhancement.
                    pass # Fall through to _create_untyped_value which infers.
                return cls._create_untyped_value(data) # `expected_type` not used by this path currently
        except Exception as e:
            error_msg = f"Failed to convert dictionary to CtyValue: {e}"
            logger.error(f"🧩🔍❌ {error_msg}", exc_info=True)  # Added exc_info
            raise EncodingError(error_msg, encoding="json") from e

    @classmethod
    def _create_unknown_value(
        cls, data: dict[str, object], preserve_type: bool = True, expected_type: CtyType | None = None
    ) -> CtyValue:
        logger.debug(f"🧩🔍🔄 Creating unknown CtyValue, expected_type: {expected_type!r}")
        type_name_str = "CtyDynamic" # Default if no type info
        if preserve_type:
            type_name_str = data.get(
                "type_name", data.get(cls.TYPE_MARKER, "CtyDynamic")
            )

        cty_type = cls._create_type_from_name(
            str(type_name_str), data, expected_cty_type=expected_type # Pass expected_type
        )
        return CtyValue.unknown(cty_type)

    @classmethod
    def _create_null_value(
        cls, data: dict[str, object], preserve_type: bool = True, expected_type: CtyType | None = None
    ) -> CtyValue:
        logger.debug(f"🧩🔍🔄 Creating null CtyValue, expected_type: {expected_type!r}")
        type_name_str = "CtyDynamic" # Default if no type info
        if preserve_type:
            type_name_str = data.get(
                "type_name", data.get(cls.TYPE_MARKER, "CtyDynamic")
            )

        cty_type = cls._create_type_from_name(
            str(type_name_str), data, expected_cty_type=expected_type # Pass expected_type
        )
        return CtyValue.null(cty_type)

    @classmethod
    def _create_typed_value(cls, data: dict[str, object], type_key: str, expected_type: CtyType | None = None) -> CtyValue:
        type_name_str = str(data.get(type_key, "CtyDynamic"))
        value_data = data.get("value")

        # Pass expected_type to _create_type_from_name
        cty_type = cls._create_type_from_name(type_name_str, data, expected_cty_type=expected_type)

        if (
            value_data is None
            and not isinstance(cty_type, CtyDynamic)
            and not data.get(cls.NULL_MARKER, False)
        ):
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
                        cls._dict_to_value(elem, preserve_type=True, expected_type=cty_type.element_type)
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
                    current_expected_type = None
                    if isinstance(cty_type, CtyMap):
                        current_expected_type = cty_type.value_type
                    elif isinstance(cty_type, CtyObject) and k in cty_type.attribute_types:
                        current_expected_type = cty_type.attribute_types[k]
                    processed_items[k] = cls._dict_to_value(v_item, preserve_type=True, expected_type=current_expected_type)
                else:
                    processed_items[k] = v_item
            return cty_type.validate(processed_items)

        elif isinstance(cty_type, CtyTuple) and isinstance(
            value_data, list
        ):  # Handle CtyTuple elements
            processed_elements = []
            if len(value_data) == len(cty_type.element_types):
                for i, elem_data in enumerate(value_data): # Changed _i to i
                    # Determine the actual type of the element based on the tuple's schema
                    # This assumes elem_data is the CTY JSON comparable dict for the element
                    if isinstance(elem_data, dict) and (
                        "type_name" in elem_data
                        or cls.TYPE_MARKER in elem_data
                        or cls.UNKNOWN_MARKER in elem_data
                        or cls.NULL_MARKER in elem_data
                    ):
                        processed_elements.append(
                            cls._dict_to_value(elem_data, preserve_type=True, expected_type=cty_type.element_types[i])
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
        cls, type_name_str: str, data_dict_for_extra_type_info: dict[str, object], expected_cty_type: CtyType | None = None
    ) -> "CtyType":
        """
        Internal helper to create a CtyType instance from a type name string
        and potentially a dictionary containing details for complex types (like collection
        element types or object attribute types).
        If an `expected_cty_type` is provided, it can be used to more accurately
        reconstruct the type, especially for generic class names like "CtyObject".
        """
        logger.debug(
            f"🧩🔍🔄 Creating type from name string: '{type_name_str}' with extra info from: {data_dict_for_extra_type_info!r}, expected_cty_type: {expected_cty_type!r}"
        )

        # If expected_cty_type is provided and matches the type_name_str,
        # use its detailed structure.
        if expected_cty_type:
            if type_name_str == "CtyObject" and isinstance(expected_cty_type, CtyObject):
                logger.debug(f"🧩🔍🔄 Using expected_cty_type for CtyObject: {expected_cty_type!r}")
                return CtyObject(attribute_types=expected_cty_type.attribute_types, optional_attributes=expected_cty_type.optional_attributes)
            if type_name_str == "CtyMap" and isinstance(expected_cty_type, CtyMap):
                logger.debug(f"🧩🔍🔄 Using expected_cty_type for CtyMap: {expected_cty_type!r}")
                return CtyMap(key_type=expected_cty_type.key_type, value_type=expected_cty_type.value_type)
            if type_name_str == "CtyList" and isinstance(expected_cty_type, CtyList):
                logger.debug(f"🧩🔍🔄 Using expected_cty_type for CtyList: {expected_cty_type!r}")
                return CtyList(element_type=expected_cty_type.element_type)
            if type_name_str == "CtySet" and isinstance(expected_cty_type, CtySet):
                logger.debug(f"🧩🔍🔄 Using expected_cty_type for CtySet: {expected_cty_type!r}")
                return CtySet(element_type=expected_cty_type.element_type)
            if type_name_str == "CtyTuple" and isinstance(expected_cty_type, CtyTuple):
                logger.debug(f"🧩🔍🔄 Using expected_cty_type for CtyTuple: {expected_cty_type!r}")
                return CtyTuple(element_types=expected_cty_type.element_types)
            # For other types, or if type_name_str doesn't match expected_cty_type's class,
            # continue with normal parsing logic. This might happen if expected_type
            # is a broader type (like CtyDynamic) but the data has more specific info.

        # Handle direct CtyType class names (e.g., from cls.TYPE_MARKER or recursive calls from _value_to_dict)
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
            # Pass expected_type's element_type if available and current expected_type is a list
            nested_expected_type = expected_cty_type.element_type if isinstance(expected_cty_type, CtyList) else None
            return CtyList(
                element_type=cls._create_type_from_name(element_type_name, {}, expected_cty_type=nested_expected_type)
            )
        if type_name_str == "CtyMap":
            key_type_name = cast(
                str, data_dict_for_extra_type_info.get("key_type", "CtyString")
            )
            value_type_name = cast(
                str, data_dict_for_extra_type_info.get("value_type", "CtyDynamic")
            )
            nested_expected_key_type = expected_cty_type.key_type if isinstance(expected_cty_type, CtyMap) else None
            nested_expected_value_type = expected_cty_type.value_type if isinstance(expected_cty_type, CtyMap) else None
            return CtyMap(
                key_type=cls._create_type_from_name(key_type_name, {}, expected_cty_type=nested_expected_key_type),
                value_type=cls._create_type_from_name(value_type_name, {}, expected_cty_type=nested_expected_value_type),
            )
        if type_name_str == "CtySet":
            element_type_name = cast(
                str, data_dict_for_extra_type_info.get("element_type", "CtyDynamic")
            )
            nested_expected_type = expected_cty_type.element_type if isinstance(expected_cty_type, CtySet) else None
            return CtySet(
                element_type=cls._create_type_from_name(element_type_name, {}, expected_cty_type=nested_expected_type)
            )
        if (
            type_name_str == "CtyObject" # This branch might be less used if expected_cty_type hits first
        ):
            if "attributes" in data_dict_for_extra_type_info and isinstance(
                data_dict_for_extra_type_info["attributes"], dict
            ):
                attr_types = {}
                for k, v_type_name_or_def in data_dict_for_extra_type_info["attributes"].items():
                    # If expected_cty_type is an object, try to get the specific expected attribute type
                    nested_expected_attr_type = None
                    if isinstance(expected_cty_type, CtyObject) and k in expected_cty_type.attribute_types:
                        nested_expected_attr_type = expected_cty_type.attribute_types[k]
                    attr_types[k] = cls._create_type_from_name(v_type_name_or_def, {}, expected_cty_type=nested_expected_attr_type)
                return CtyObject(attr_types)
        if type_name_str == "CtyTuple": # This branch might be less used
            if "element_types" in data_dict_for_extra_type_info and isinstance(
                data_dict_for_extra_type_info["element_types"], list
            ):
                el_types = []
                for i, et_name_or_def in enumerate(data_dict_for_extra_type_info["element_types"]):
                    nested_expected_el_type = None
                    if isinstance(expected_cty_type, CtyTuple) and i < len(expected_cty_type.element_types):
                        nested_expected_el_type = expected_cty_type.element_types[i]
                    el_types.append(cls._create_type_from_name(et_name_or_def, {}, expected_cty_type=nested_expected_el_type))
                return CtyTuple(tuple(el_types))
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
            # If expected_cty_type was a CtyList, its element type would have been passed recursively.
            return CtyList(
                element_type=cls._create_type_from_name(type_name_str[len("list("):-1], {}, expected_cty_type=None) # No specific expected type for element if top one wasn't List
            )
        if type_name_str.startswith("map(") and type_name_str.endswith(")"):
            nested_expected_value_type = expected_cty_type.value_type if isinstance(expected_cty_type, CtyMap) else None
            # Assuming string keys for maps parsed from "map(...)" string format
            return CtyMap(
                key_type=CtyString(), # Default key type for this format
                value_type=cls._create_type_from_name(type_name_str[len("map("):-1], {}, expected_cty_type=nested_expected_value_type),
            )
        if type_name_str.startswith("set(") and type_name_str.endswith(")"):
            nested_expected_element_type = expected_cty_type.element_type if isinstance(expected_cty_type, CtySet) else None
            return CtySet(
                element_type=cls._create_type_from_name(type_name_str[len("set("):-1], {}, expected_cty_type=nested_expected_element_type)
            )

        if type_name_str.startswith("object({") and type_name_str.endswith("})"):
            attrs_str = type_name_str[len("object({") : -2]
            if not attrs_str: # Empty object definition like "object({})"
                return CtyObject({})
            attr_map = {}
            try:
                attr_pairs_strs = _split_by_delimiter_respecting_nesting_for_json_decode(attrs_str, ",")
                for pair_str in attr_pairs_strs:
                    name, t_str = pair_str.split("=", 1)
                    name = name.strip()
                    # If we have an expected_cty_type that is an object, pass the specific expected type for this attribute
                    nested_expected_attr_type = None
                    if isinstance(expected_cty_type, CtyObject) and name in expected_cty_type.attribute_types:
                        nested_expected_attr_type = expected_cty_type.attribute_types[name]
                    attr_map[name] = cls._create_type_from_name(t_str.strip(), {}, expected_cty_type=nested_expected_attr_type)
            except Exception as e_parse: # pylint: disable=broad-except
                logger.warning(
                    f"Could not parse object attributes from '{attrs_str}': {e_parse}. Falling back to CtyDynamic for the entire object."
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
                        cls._create_type_from_name(
                            s.strip(),
                            {},
                            expected_cty_type=(expected_cty_type.element_types[i] if isinstance(expected_cty_type, CtyTuple) and i < len(expected_cty_type.element_types) else None)
                        )
                        for i, s in enumerate(elem_types_strs)
                    )
                )
            except Exception as e_parse: # pylint: disable=broad-except
                logger.warning(
                    f"Could not parse tuple elements from '{elems_str}': {e_parse}. Falling back to CtyDynamic for the entire tuple."
                )
                return CtyDynamic()

        logger.warning(
            f"Failed to fully parse type string '{type_name_str}', falling back to CtyDynamic."
        )
        return CtyDynamic()

    @classmethod
    def _json_default(cls, obj: object) -> str:
        if isinstance(obj, Decimal):
            return str(obj)
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    @classmethod
    def marshal(
        cls,
        value: object,
        *,
        operation: object | None = None, # CTY OperationContext
        **options: object,
    ) -> bytes:
        """
        Marshals a Python/CTY value into JSON bytes using CTY conventions.
        """
        # `operation` from WireFormat is Cty.OperationContext, not used directly by JsonEncoder's core logic
        # but could be passed via options if JsonEncoder's _encode were to use it.
        return cls.encode(value, **options)

    @classmethod
    def unmarshal(
        cls,
        data: bytes,
        expected_type: type | None = None, # CTY CtyType
        *,
        operation: object | None = None, # CTY OperationContext
        **options: object,
    ) -> object:
        """
        Unmarshals JSON bytes into a Python object/CtyValue using CTY conventions.
        """
        # `expected_type` and `operation` are not directly used by the core
        # _dict_to_value logic but could be if further integration is needed.
        return cls.decode(data, **options)


# Helper for _create_type_from_name, simplified for this context
def _split_by_delimiter_respecting_nesting_for_json_decode(
    text: str, delimiter: str
) -> list[str]:
    """
    Splits a string by a delimiter, respecting nested parentheses, brackets, and braces.
    Used for parsing object attribute strings and tuple element type strings.
    """
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
