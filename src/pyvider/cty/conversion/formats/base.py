# pyvider/cty/conversion/formats/base.py
from enum import Enum, auto
from typing import ClassVar, Dict, Optional, Type, TypeVar, Any, Final

from pyvider.telemetry import logger
from pyvider.cty.conversion.wire import WireFormatType

T = TypeVar('T')
JSON = WireFormatType.JSON
MSGPACK = WireFormatType.MSGPACK

class FormatEncoder:
    @classmethod
    def format_type(cls) -> WireFormatType:
        raise NotImplementedError(f"{cls.__name__}.format_type() must be implemented")
    @classmethod
    def encode(cls, value: Any, **options) -> bytes:
        raise NotImplementedError(f"{cls.__name__}.encode() must be implemented")
    @classmethod
    def decode(cls, data: bytes, **options) -> Any:
        raise NotImplementedError(f"{cls.__name__}.decode() must be implemented")

_ENCODERS: Dict[WireFormatType, Type[FormatEncoder]] = {}

def register_formatter(format_type: WireFormatType):
    def decorator(encoder_class: Type[FormatEncoder]):
        if not issubclass(encoder_class, FormatEncoder):
            raise TypeError(f"Format encoder {encoder_class.__name__} must extend FormatEncoder")
        _ENCODERS[format_type] = encoder_class
        return encoder_class
    return decorator

def get_formatter(format_type: WireFormatType) -> Optional[Type[FormatEncoder]]:
    return _ENCODERS.get(format_type)

def list_formatters() -> Dict[WireFormatType, str]:
    return {fmt: encoder.__name__ for fmt, encoder in _ENCODERS.items()}

# 🐍🏗️
