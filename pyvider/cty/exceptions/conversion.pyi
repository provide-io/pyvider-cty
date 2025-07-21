from .base import CtyError
from _typeshed import Incomplete

__all__ = ['CtyConversionError', 'CtyTypeConversionError', 'CtyTypeParseError']

class CtyConversionError(CtyError):
    source_value: Incomplete
    target_type: Incomplete
    def __init__(self, message: str, *, source_value: object | None = None, target_type: object | None = None) -> None: ...

class CtyTypeConversionError(CtyConversionError):
    type_name: Incomplete
    def __init__(self, message: str, *, type_name: str | None = None, source_value: object | None = None, target_type: object | None = None) -> None: ...

class CtyTypeParseError(CtyConversionError):
    type_string: Incomplete
    def __init__(self, message: str, type_string: str) -> None: ...
