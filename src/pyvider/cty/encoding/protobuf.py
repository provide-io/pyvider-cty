
# pyvider/cty/encoding/protobuf.py

"""
Protobuf encoding and decoding for Pyvider Cty.
"""

import struct
from typing import Any, Union

from pyvider.cty.logger import logger

class ProtobufCodec:
    """
    Provides a Terraform-compatible Protobuf-like encoding/decoding mechanism.
    """

    @staticmethod
    def encode(value: Union[str, bytes]) -> bytes:
        """
        Encode a string into a Terraform-compatible Protobuf-like format.
        This is a utility function and not meant for DynamicValue encoding.

        Args:
            value: The string value to encode

        Returns:
            bytes: Encoded Protobuf-like bytes
        """
        logger.debug(f"🧰📝🔄 ProtobufCodec.encode called with value of type {type(value).__name__}")
        
        # Handle None case
        if value is None:
            logger.warning("🧰📝⚠️ None value passed to encode, returning empty bytes")
            return struct.pack(">I", 0)  # 4-byte length prefix of 0
            
        # Convert string to bytes if needed
        if isinstance(value, str):
            encoded_value = value.encode("utf-8")
        elif isinstance(value, bytes):
            encoded_value = value
        else:
            error_msg = f"Expected str or bytes, got {type(value).__name__}"
            logger.error(f"🧰📝❌ {error_msg}")
            raise TypeError(error_msg)
            
        # Add length prefix
        try:
            length_prefix = struct.pack(">I", len(encoded_value))  # 4-byte big-endian length
            result = length_prefix + encoded_value
            logger.debug(f"🧰📝✅ Encoded {len(encoded_value)} bytes with 4-byte length prefix")
            return result
        except Exception as e:
            logger.error(f"🧰📝❌ Error encoding value: {e}", exc_info=True)
            raise

    @staticmethod
    def decode(data: bytes) -> str:
        """
        Decode a Terraform-compatible Protobuf-like byte stream.
        This is a utility function and not meant for DynamicValue decoding.

        Args:
            data: The Protobuf-encoded data

        Returns:
            str: Decoded string

        Raises:
            ValueError: If decoding fails
        """
        logger.debug(f"🧰🔍🔄 ProtobufCodec.decode called with {len(data)} bytes")
        
        # Validate input
        if not isinstance(data, bytes):
            error_msg = f"Expected bytes, got {type(data).__name__}"
            logger.error(f"🧰🔍❌ {error_msg}")
            raise TypeError(error_msg)
            
        # Check minimum length
        if len(data) < 4:
            error_msg = "Invalid data: Too short to contain a length prefix"
            logger.error(f"🧰🔍❌ {error_msg}")
            raise ValueError(error_msg)

        try:
            # Extract length prefix
            length = struct.unpack(">I", data[:4])[0]  # Extract 4-byte length prefix
            encoded_value = data[4:]

            # Validate length
            if len(encoded_value) != length:
                error_msg = f"Invalid data: Expected {length} bytes, got {len(encoded_value)}"
                logger.error(f"🧰🔍❌ {error_msg}")
                raise ValueError(error_msg)

            # Decode to string
            result = encoded_value.decode("utf-8")
            logger.debug(f"🧰🔍✅ Decoded {length} bytes successfully")
            return result
            
        except UnicodeDecodeError as e:
            error_msg = f"Unicode decode error: {e}"
            logger.error(f"🧰🔍❌ {error_msg}")
            raise ValueError(error_msg) from e
        except Exception as e:
            error_msg = f"Error decoding data: {e}"
            logger.error(f"🧰🔍❌ {error_msg}", exc_info=True)
            raise ValueError(error_msg) from e

# 🐍🏗️
