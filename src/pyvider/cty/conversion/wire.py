# pyvider/conversion/wire_format.py
"""
Wire format registry and interface definitions for Pyvider.
"""

from collections.abc import Callable
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

T = TypeVar("T")
S = TypeVar("S", bound="WireFormat")
WFR = TypeVar("R", bound="WireFormatRegistry")


@unique
class WireFormatType(Enum):
    """
    Enumerates the supported wire formats for CTY value serialization.
    """
    TERRAFORM = auto()
    STANDARD = auto()
    MSGPACK = auto()
    JSON = auto()
    CUSTOM = auto()


@runtime_checkable
class StateConvertible(Protocol):
    """
    Protocol for objects that can be converted to a dictionary representation,
    typically for serialization as part of a CTY value.
    """
    def to_dict(self) -> dict[str, object]: ...


@runtime_checkable
class TypeConvertible(Protocol):
    """
    Protocol for objects that can provide their CTY type information.
    """
    @property
    def type_info(self) -> dict[str, object]: ...


def is_state_convertible(obj: object) -> TypeGuard[StateConvertible]:
    """Checks if an object conforms to the StateConvertible protocol."""
    return hasattr(obj, "to_dict") and callable(obj.to_dict)


def is_type_convertible(obj: object) -> TypeGuard[TypeConvertible]:
    """Checks if an object conforms to the TypeConvertible protocol."""
    return hasattr(obj, "type_info") and isinstance(
        getattr(obj, "type_info", None), property
    )


@final
class WireFormatRegistry:
    """
    A singleton registry for CTY wire format encoder/decoder implementations.

    Provides methods to register and retrieve formatters based on WireFormatType.
    """
    _instance: ClassVar[WFR | None] = None
    _formats: ClassVar[dict[WireFormatType, type[S]]] = {}

    def __new__(cls) -> WFR:
        """Ensures only one instance of WireFormatRegistry exists."""
        if cls._instance is None:
            logger.debug("🧰🔄🔧 Creating WireFormatRegistry singleton")
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(
        cls, format_type: WireFormatType
    ) -> Callable[[type["WireFormat"]], type["WireFormat"]]:
        """
        Decorator to register a WireFormat implementation for a specific WireFormatType.

        Args:
            format_type: The WireFormatType the decorated class handles.

        Returns:
            A decorator function.
        """
        logger.debug(f"🧰🔄🔧 Preparing registration for {format_type.name}")

        def decorator(impl_class: type["WireFormat"]) -> type["WireFormat"]:
            if not issubclass(impl_class, WireFormat):
                raise TypeError(f"{impl_class.__name__} must extend WireFormat")
            if format_type in cls._formats:
                logger.warning(f"🧰🔄⚠️ Replacing wire format for {format_type.name}")
            cls._formats[format_type] = impl_class
            logger.debug(
                f"🧰🔄✅ Registered wire format for {format_type.name}: {impl_class.__name__}"
            )
            return impl_class

        return decorator

    @classmethod
    def get_formatter(cls, format_type: WireFormatType) -> type["WireFormat"]:
        """
        Retrieves the registered WireFormat class for a given WireFormatType.

        Args:
            format_type: The WireFormatType to look up.

        Returns:
            The registered WireFormat class.

        Raises:
            WireFormatError: If no formatter is registered for the given type.
        """
        if format_type not in cls._formats:
            raise WireFormatError(
                f"No wire format registered for {format_type.name}",
                format_type=format_type,
            )
        return cls._formats[format_type]


class WireFormat:
    """
    Interface for CTY wire format encoders/decoders.

    Concrete implementations of this class handle the specifics of marshalling
    CTY values to a byte representation for a particular wire format (e.g., JSON,
    Terraform's native format) and unmarshalling them back.
    """
    @classmethod
    def marshal(
        cls,
        value: object,
        *,
        operation: OperationContext | None = None,
        **options: object,
    ) -> bytes:
        """
        Marshals a Python/CTY value into bytes for this wire format.

        Args:
            value: The value to marshal.
            operation: The operational context, influencing serialization.
            **options: Formatter-specific options.

        Returns:
            The marshalled value as bytes.
        """
        raise NotImplementedError(f"{cls.__name__}.marshal() must be implemented")

    @classmethod
    def unmarshal(
        cls,
        data: bytes,
        expected_type: type[T] | None = None,
        *,
        operation: OperationContext | None = None,
        **options: object,
    ) -> object:
        """
        Unmarshals bytes in this wire format into a Python object.

        Args:
            data: The bytes to unmarshal.
            expected_type: The expected Python type or CtyType of the result.
            operation: The operational context, influencing deserialization.
            **options: Formatter-specific options.

        Returns:
            The unmarshalled Python object.
        """
        raise NotImplementedError(f"{cls.__name__}.unmarshal() must be implemented")

    @classmethod
    def get_format_type(cls) -> WireFormatType:
        """
        Determines the WireFormatType associated with this WireFormat class.

        This method iterates through the registered formatters to find which
        WireFormatType corresponds to this specific class.

        Returns:
            The WireFormatType for this class, or WireFormatType.CUSTOM if not explicitly registered.
        """
        for fmt_type, impl in WireFormatRegistry._formats.items():
            if impl == cls:
                return fmt_type
        return WireFormatType.CUSTOM


logger.debug("🧰🔄🔧 Wire format registry and interfaces initialized")

# 🐍🏗️
