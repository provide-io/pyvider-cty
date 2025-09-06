from __future__ import annotations

from typing import TYPE_CHECKING, Any

from provide.foundation.errors import ValidationError as FoundationValidationError
from pyvider.cty.exceptions.base import CtyError

if TYPE_CHECKING:
    from pyvider.cty.path import CtyPath
    from pyvider.cty.types import CtyType


class CtyValidationError(FoundationValidationError):
    """Base exception for all validation errors.
    
    Inherits from foundation's ValidationError for enhanced diagnostics
    and automatic retry/circuit breaker support where applicable.
    """

    def __init__(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message
        
        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault('context', {})
        
        # Core CTY context
        if type_name:
            context['cty.type'] = type_name
        if path:
            context['cty.path'] = str(path)
            context['cty.path_depth'] = len(path.steps) if path else 0
        
        # Value context with safe representation
        if value is not None:
            context['cty.value_type'] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context['cty.value_repr'] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context['cty.value_repr'] = f"<repr failed for {type(value).__name__}>"
        
        # Add validation context if available
        context['cty.validation_stage'] = 'type_validation'
            
        super().__init__(self.message, **kwargs)
    
    def _default_code(self) -> str:
        return "CTY_VALIDATION_ERROR"

    def __str__(self) -> str:
        """Creates a user-friendly, path-aware error message."""
        path_str = str(self.path) if self.path and self.path.steps else ""
        core_message = self.message

        if path_str and path_str != "(root)":
            return f"At {path_str}: {core_message}"

        return core_message


def _get_type_name_from_original(
    original_exc: CtyValidationError | None, default: str
) -> str:
    """Helper to safely extract type_name from an original exception."""
    if original_exc and original_exc.type_name:
        return original_exc.type_name
    return default


# --- Primitive Validation Errors ---
class CtyBoolValidationError(CtyValidationError):
    def __init__(
        self, message: str, value: object = None, path: CtyPath | None = None
    ) -> None:
        super().__init__(f"Boolean validation error: {message}", value, "Boolean", path)


class CtyNumberValidationError(CtyValidationError):
    def __init__(
        self, message: str, value: object = None, path: CtyPath | None = None
    ) -> None:
        super().__init__(f"Number validation error: {message}", value, "Number", path)


class CtyStringValidationError(CtyValidationError):
    def __init__(
        self, message: str, value: object = None, path: CtyPath | None = None
    ) -> None:
        super().__init__(f"String validation error: {message}", value, "String", path)


# --- Collection Validation Errors ---
class CtyCollectionValidationError(CtyValidationError):
    """Base for collection-related validation errors."""


class CtyListValidationError(CtyCollectionValidationError):
    def __init__(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault('context', {})
        context['cty.collection_type'] = 'list'
        
        if isinstance(value, (list, tuple)):
            context['cty.collection_length'] = len(value)
        
        if original_exception:
            context['cty.nested_error'] = type(original_exception).__name__
            
        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "List"),
            path,
            **kwargs
        )


class CtyMapValidationError(CtyCollectionValidationError):
    def __init__(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
    ) -> None:
        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Map"),
            path,
        )


class CtySetValidationError(CtyCollectionValidationError):
    def __init__(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
    ) -> None:
        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Set"),
            path,
        )


class CtyTupleValidationError(CtyCollectionValidationError):
    def __init__(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
    ) -> None:
        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
        )


# --- Structural and Type Definition Errors ---
class CtyAttributeValidationError(CtyValidationError):
    def __init__(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
    ) -> None:
        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
        )


class CtyTypeValidationError(CtyValidationError):
    def __init__(
        self, message: str, type_name: str | None = None, path: CtyPath | None = None
    ) -> None:
        super().__init__(message, type_name=type_name or "TypeDefinition", path=path)


class CtyTypeMismatchError(CtyValidationError):
    def __init__(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type
        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path)
