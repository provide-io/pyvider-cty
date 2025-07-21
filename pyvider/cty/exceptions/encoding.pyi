from _typeshed import Incomplete
from pyvider.cty.exceptions.base import CtyError as CtyError

class TransformationError(CtyError):
    schema: Incomplete
    target_type: Incomplete
    def __init__(self, message: str, schema: object = None, target_type: object = None, **kwargs: object) -> None: ...

class InvalidTypeError(CtyError):
    invalid_type: Incomplete
    def __init__(self, message: str, invalid_type: object = None) -> None: ...

class AttributePathError(CtyError):
    path: Incomplete
    value: Incomplete
    def __init__(self, message: str, path: object = None, value: object = None) -> None: ...

class EncodingError(CtyError):
    data: Incomplete
    encoding: Incomplete
    def __init__(self, message: str, data: object = None, encoding: str | None = None) -> None: ...

class SerializationError(EncodingError):
    value: Incomplete
    def __init__(self, message: str, value: object = None, format_name: str | None = None) -> None: ...

class DeserializationError(EncodingError):
    def __init__(self, message: str, data: object = None, format_name: str | None = None) -> None: ...

class DynamicValueError(SerializationError):
    def __init__(self, message: str, value: object = None) -> None: ...

class JsonEncodingError(EncodingError):
    operation: Incomplete
    args: Incomplete
    def __init__(self, message: str, data: object = None, operation: str | None = None) -> None: ...

class MsgPackEncodingError(EncodingError):
    operation: Incomplete
    args: Incomplete
    def __init__(self, message: str, data: object = None, operation: str | None = None) -> None: ...

class WireFormatError(TransformationError):
    format_type: Incomplete
    operation: Incomplete
    args: Incomplete
    def __init__(self, message: str, *, format_type: object = None, operation: str | None = None, **kwargs: object) -> None: ...
