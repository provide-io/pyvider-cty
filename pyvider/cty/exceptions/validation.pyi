from _typeshed import Incomplete
from pyvider.cty.exceptions.base import CtyError as CtyError
from pyvider.cty.path import CtyPath as CtyPath
from pyvider.cty.types import CtyType as CtyType
from typing import Any

class CtyValidationError(CtyError):
    value: Incomplete
    type_name: Incomplete
    path: Incomplete
    message: Incomplete
    def __init__(self, message: str, value: object = None, type_name: str | None = None, path: CtyPath | None = None) -> None: ...

class CtyBoolValidationError(CtyValidationError):
    def __init__(self, message: str, value: object = None, path: CtyPath | None = None) -> None: ...

class CtyNumberValidationError(CtyValidationError):
    def __init__(self, message: str, value: object = None, path: CtyPath | None = None) -> None: ...

class CtyStringValidationError(CtyValidationError):
    def __init__(self, message: str, value: object = None, path: CtyPath | None = None) -> None: ...

class CtyCollectionValidationError(CtyValidationError): ...

class CtyListValidationError(CtyCollectionValidationError):
    def __init__(self, message: str, value: object = None, path: CtyPath | None = None, *, original_exception: CtyValidationError | None = None) -> None: ...

class CtyMapValidationError(CtyCollectionValidationError):
    def __init__(self, message: str, value: object = None, path: CtyPath | None = None, *, original_exception: CtyValidationError | None = None) -> None: ...

class CtySetValidationError(CtyCollectionValidationError):
    def __init__(self, message: str, value: object = None, path: CtyPath | None = None, *, original_exception: CtyValidationError | None = None) -> None: ...

class CtyTupleValidationError(CtyCollectionValidationError):
    def __init__(self, message: str, value: object = None, path: CtyPath | None = None, *, original_exception: CtyValidationError | None = None) -> None: ...

class CtyAttributeValidationError(CtyValidationError):
    def __init__(self, message: str, value: object = None, path: CtyPath | None = None, *, original_exception: CtyValidationError | None = None) -> None: ...

class CtyTypeValidationError(CtyValidationError):
    def __init__(self, message: str, type_name: str | None = None, path: CtyPath | None = None) -> None: ...

class CtyTypeMismatchError(CtyValidationError):
    actual_type: Incomplete
    expected_type: Incomplete
    def __init__(self, message: str, actual_type: CtyType[Any] | None = None, expected_type: CtyType[Any] | None = None, path: CtyPath | None = None) -> None: ...
