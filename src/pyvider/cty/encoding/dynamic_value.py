#!/usr/bin/env python3
# pyvider/cty/encoding/dynamic_value.py

"""
Terraform DynamicValue Encoding for Pyvider

This module implements Terraform's DynamicValue, which encodes and decodes
arbitrary Terraform values using Protobuf, independent of tfprotov6.

Key Features:
- Encodes CtyValue into a Protobuf-compatible DynamicValue format.
- Decodes DynamicValue back into a CtyValue.
- Detailed structured logging for debugging Terraform serialization issues.
"""

import json
from typing import Any, Union

from pyvider.cty.types import CtyDynamic
from pyvider.cty.values import CtyValue
from pyvider.cty.encoding.protobuf import ProtobufCodec
from pyvider.exceptions import TransformationError
from pyvider.cty.logger import logger


class CtyDynamicValue:
    """
    Implements Terraform's DynamicValue for encoding/decoding arbitrary values.
    """

    @staticmethod
    def encode(value: Union[CtyValue, CtyDynamic]) -> bytes:
        """
        Encode a CtyValue into a Terraform-compatible DynamicValue.

        Args:
            value (CtyValue | CtyDynamic): The value to encode.

        Returns:
            bytes: Protobuf-encoded DynamicValue.

        Raises:
            TransformationError: If encoding fails.
        """
        logger.debug(f"🧰📝🔄 Encoding DynamicValue for: {repr(value)[:100]}")

        if not isinstance(value, (CtyValue, CtyDynamic)):
            error_msg = f"Expected CtyValue or CtyDynamic, got {type(value).__name__}"
            logger.error(f"🧰📝❌ {error_msg}")
            raise TransformationError(error_msg)

        try:
            json_repr = json.dumps(value.to_dict())  # Ensure serialization compatibility
            encoded_data = ProtobufCodec.encode(json_repr)

            logger.debug(f"🧰📝✅ Successfully encoded DynamicValue ({len(encoded_data)} bytes)")
            return encoded_data
        except Exception as e:
            error_msg = f"Failed to encode DynamicValue: {e}"
            logger.error(f"🧰📝❌ {error_msg}")
            raise TransformationError(error_msg) from e

    @staticmethod
    def decode(data: bytes) -> CtyValue:
        """
        Decode a Terraform-compatible DynamicValue into a CtyValue.

        Args:
            data (bytes): The Protobuf-encoded DynamicValue.

        Returns:
            CtyValue: The decoded value.

        Raises:
            TransformationError: If decoding fails.
        """
        logger.debug(f"🧰🔍🔄 Decoding DynamicValue ({len(data)} bytes)")

        if not isinstance(data, bytes):
            error_msg = f"Expected bytes, got {type(data).__name__}: {repr(data)[:100]}"
            logger.error(f"🧰🔍❌ {error_msg}")
            raise TransformationError(error_msg)

        try:
            json_repr = ProtobufCodec.decode(data)
            logger.debug(f"🧰🔍✅ Decoded JSON from Protobuf: {json_repr[:100]}")

            value_dict = json.loads(json_repr)
            decoded_value = CtyValue.from_dict(value_dict)

            logger.debug(f"🧰🔍✅ Successfully decoded DynamicValue into CtyValue: {repr(decoded_value)[:100]}")
            return decoded_value
        except json.JSONDecodeError as e:
            error_msg = f"JSON decoding failed: {e}"
            logger.error(f"🧰🔍❌ {error_msg}")
            raise TransformationError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error decoding DynamicValue: {e}"
            logger.error(f"🧰🔍❌ {error_msg}")
            raise TransformationError(error_msg) from e
