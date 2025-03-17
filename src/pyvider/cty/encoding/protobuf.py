#!/usr/bin/env python3
# pyvider/cty/encoding/protobuf.py

"""
Protobuf encoding and decoding for Pyvider Cty.

This module provides Protobuf serialization independent of Terraform's tfprotov6.
"""

import struct
from typing import Any


class ProtobufCodec:
    """
    Provides a Terraform-independent Protobuf encoding/decoding mechanism.
    """

    @staticmethod
    def encode(value: str) -> bytes:
        """
        Encode a string into a Terraform-compatible Protobuf-like format.

        Args:
            value (str): The string value to encode.

        Returns:
            bytes: Encoded Protobuf-like bytes.
        """
        encoded_value = value.encode("utf-8")
        length_prefix = struct.pack(">I", len(encoded_value))  # 4-byte big-endian length
        return length_prefix + encoded_value

    @staticmethod
    def decode(data: bytes) -> str:
        """
        Decode a Terraform-compatible Protobuf-like byte stream.

        Args:
            data (bytes): The Protobuf-encoded data.

        Returns:
            str: Decoded string.

        Raises:
            ValueError: If decoding fails.
        """
        if len(data) < 4:
            raise ValueError("Invalid data: Too short to contain a length prefix")

        length = struct.unpack(">I", data[:4])[0]  # Extract 4-byte length prefix
        encoded_value = data[4:]

        if len(encoded_value) != length:
            raise ValueError("Invalid data: Length mismatch")

        return encoded_value.decode("utf-8")
