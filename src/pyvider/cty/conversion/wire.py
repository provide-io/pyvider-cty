from collections.abc import Callable
from typing import Any

# pyvider/conversion/wire_format.py
"""
Wire format registry and interface definitions for Pyvider.
"""
from enum import Enum, auto, unique
from typing import (
    ClassVar,
    Protocol,
    TypeGuard,
    TypeVar,
    final,
    runtime_checkable,
)

from pyvider.cty.context import OperationContext
from pyvider.cty.exceptions import WireFormatError
from pyvider.telemetry import logger

T = TypeVar('T')
S = TypeVar('S', bound='WireFormat')
WFR = TypeVar('R', bound='WireFormatRegistry')

@unique
class WireFormatType(Enum):
    TERRAFORM = auto()
    STANDARD = auto()
    MSGPACK = auto()
    JSON = auto()
    CUSTOM = auto()

@runtime_checkable
class StateConvertible(Protocol):
    def to_dict(self) -> dict[str, Any]: ...

@runtime_checkable
class TypeConvertible(Protocol):
    @property
    def type_info(self) -> dict[str, Any]: ...

def is_state_convertible(obj: Any) -> TypeGuard[StateConvertible]:
    return hasattr(obj, "to_dict") and callable(obj.to_dict)

def is_type_convertible(obj: Any) -> TypeGuard[TypeConvertible]:
    return hasattr(obj, "type_info") and isinstance(getattr(obj, "type_info", None), property)

@final
class WireFormatRegistry:
    _instance: ClassVar[WFR | None] = None
    _formats: ClassVar[dict[WireFormatType, type[S]]] = {}

    def __new__(cls) -> WFR:
        if cls._instance is None:
            logger.debug("🧰🔄🔧 Creating WireFormatRegistry singleton")
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, format_type: WireFormatType) -> Callable[[type['WireFormat']], type['WireFormat']]:
        logger.debug(f"🧰🔄🔧 Preparing registration for {format_type.name}")
        def decorator(impl_class: type['WireFormat']) -> type['WireFormat']:
            if not issubclass(impl_class, WireFormat):
                raise TypeError(f"{impl_class.__name__} must extend WireFormat")
            if format_type in cls._formats:
                logger.warning(f"🧰🔄⚠️ Replacing wire format for {format_type.name}")
            cls._formats[format_type] = impl_class
            logger.debug(f"🧰🔄✅ Registered wire format for {format_type.name}: {impl_class.__name__}")
            return impl_class
        return decorator

    @classmethod
    def get_formatter(cls, format_type: WireFormatType) -> type['WireFormat']:
        if format_type not in cls._formats:
            raise WireFormatError(f"No wire format registered for {format_type.name}", format_type=format_type)
        return cls._formats[format_type]

class WireFormat:
    @classmethod
    def marshal(cls, value: Any, *, operation: OperationContext | None = None, **options: Any) -> bytes:
        raise NotImplementedError(f"{cls.__name__}.marshal() must be implemented")

    @classmethod
    def unmarshal(cls, data: bytes, expected_type: type[T] | None = None, *, operation: OperationContext | None = None, **options: Any) -> Any:
        raise NotImplementedError(f"{cls.__name__}.unmarshal() must be implemented")

    @classmethod
    def get_format_type(cls) -> WireFormatType:
        for fmt_type, impl in WireFormatRegistry._formats.items():
            if impl == cls:
                return fmt_type
        return WireFormatType.CUSTOM

logger.debug("🧰🔄🔧 Wire format registry and interfaces initialized")

# 🐍🏗️
