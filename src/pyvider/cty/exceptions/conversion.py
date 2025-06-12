# pyvider/cty/exceptions/conversion.py

from .base import CtyError

class CtyConversionError(CtyError):
    """Base for CTY value or type conversion errors."""
    def __init__(self, message: str, *, source_value: object = None, target_type: object = None) -> None:
        self.source_value = source_value
        self.target_type = target_type
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
        if context_parts:
            message = f"{message} ({", ".join(context_parts)})"
        super().__init__(message)

class CtyTypeConversionError(CtyConversionError):
    """CTY type representation conversion failure."""
    def __init__(self, message: str, *, type_name: str | None = None, source_value: object = None, target_type: object = None) -> None:
        self.type_name = type_name
        if type_name:
            message = f"CTY Type \"{type_name}\" representation conversion failed: {message}"
        super().__init__(message, source_value=source_value, target_type=target_type)

__all__ = ["CtyConversionError", "CtyTypeConversionError"]
