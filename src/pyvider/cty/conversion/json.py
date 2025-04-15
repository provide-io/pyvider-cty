#
# pyvider/cty/conversion/json.py
#

"""
JSON format converter implementation.

This module provides conversion between Python/CTY values and JSON format.
"""

import json
from typing import Any, Optional, Union

from pyvider.telemetry import logger

from pyvider.core.exceptions import ConversionError
from pyvider.core.conversion.base import FormatKind
from pyvider.core.conversion.registry import register_converter

from pyvider.cty.types import CtyType
from pyvider.cty.values import CtyValue

def marshal_json(value: Any, options: Optional[dict[str, Any]] = None) -> bytes:
    """
    Encode a Python/CTY value to JSON bytes.
    Args:
        value: The value to marshal
        options: Encoding options
            - indent: Indentation level (default: None)
            - separators: Item separators (default: None)
            - sort_keys: Whether to sort dictionary keys (default: False)
    Returns:
        bytes: The JSON-encoded bytes
    Raises:
        ConversionError: If encoding fails
    """
    logger.debug(f"🧰📝🔄 Encoding to JSON: {type(value).__name__}")
    # Process options
    options = options or {}
    indent = options.get('indent')
    separators = options.get('separators')
    sort_keys = options.get('sort_keys', False)
    try:
        # Extract raw value from CtyValue if needed
        if isinstance(value, CtyValue):
            # Handle special cases
            if not value.is_known:
                logger.debug("🧰📝🔄 Encoding unknown value as null")
                return b"null"  # Use null for unknown values in JSON
            if value.is_null:
                logger.debug("🧰📝🔄 Encoding null value")
                return b"null"
            # Extract raw value
            raw_value = value.value
        else:
            raw_value = value
        # Handle objects with to_dict method
        if hasattr(raw_value, 'to_dict') and callable(getattr(raw_value, 'to_dict')):
            raw_value = raw_value.to_dict()
        # Handle special types
        if isinstance(raw_value, set):
            raw_value = list(raw_value)
        # Encode to JSON
        json_bytes = json.dumps(
            raw_value,
            indent=indent,
            separators=separators,
            sort_keys=sort_keys
        ).encode('utf-8')
        logger.debug(f"🧰📝✅ Encoded to {len(json_bytes)} bytes of JSON")
        return json_bytes
    except Exception as e:
        logger.error(f"🧰📝❌ Error encoding to JSON: {e}", exc_info=True)
        raise ConversionError(f"Failed to marshal to JSON: {e}") from e

def unmarshal_json(marshalled: Union[bytes, str],
           expected_type: Optional[CtyType] = None,
           options: Optional[dict[str, Any]] = None) -> Any:
    """
    Decode JSON bytes or string to a Python/CTY value.
    Args:
        marshalled: The JSON bytes or string to unmarshal
        expected_type: Optional CTY type to validate against
        options: Decoding options
    Returns:
        The unmarshalled Python/CTY value
    Raises:
        ConversionError: If decoding fails
    """
    logger.debug("🧰🔍🔄 Decoding from JSON")
    # Process options
    options = options or {}
    try:
        # Convert bytes to string if needed
        if isinstance(marshalled, bytes):
            marshalled = encoded.decode('utf-8')
        # Decode JSON
        value = json.loads(marshalled)
        logger.debug(f"🧰🔍✅ Decoded JSON to {type(value).__name__}")
        # Validate against expected type if provided
        if expected_type is not None:
            logger.debug(f"🧰🔍🔄 Validating against {expected_type.__class__.__name__}")
            try:
                validated_value = expected_type.validate(value)
                logger.debug("🧰🔍✅ Validation successful")
                return validated_value
            except Exception as e:
                logger.warning(f"🧰🔍⚠️ Type validation failed: {e}")
                # Return unvalidated value as fallback
                return value
        return value
    except json.JSONDecodeError as e:
        logger.error(f"🧰🔍❌ Failed to unmarshal JSON: {e}")
        raise ConversionError(f"Failed to unmarshal JSON: {e}") from e
    except Exception as e:
        logger.error(f"🧰🔍❌ Error decoding from JSON: {e}", exc_info=True)
        raise ConversionError(f"Failed to unmarshal from JSON: {e}") from e

# 🐍🏗️🐣
