# pyvider/cty/types/primitives/string.py
from typing import TYPE_CHECKING, ClassVar

from attrs import define, field

from pyvider.cty.exceptions import CtyStringValidationError
from pyvider.cty.types.base import CtyType
from pyvider.telemetry import logger

if TYPE_CHECKING:
    from pyvider.cty.values import CtyValue


@define(frozen=True, slots=True)
class CtyString(CtyType[str]):
    ctype: ClassVar[str] = "string"
    value: str = field(default="")

    def validate(self, value: object) -> "CtyValue":
        from pyvider.cty.values import CtyValue
        
        # Handle None input directly by creating a null CtyString value.
        if value is None:
            return CtyValue.null(self)

        if isinstance(value, CtyValue):
            if isinstance(value.type, CtyString): return value
            if value.is_unknown: return CtyValue.unknown(self)
            if value.is_null: return CtyValue.null(self)
            return CtyValue(vtype=self, value=str(value.value))

        if isinstance(value, str):
            return CtyValue(vtype=self, value=value)

        try:
            return CtyValue(vtype=self, value=str(value))
        except Exception as e:
            raise CtyStringValidationError(f"Value of type {type(value).__name__} cannot be converted to a string.") from e

    def equal(self, other: "CtyType[object]") -> bool:
        return isinstance(other, CtyString)

    def usable_as(self, other: "CtyType[object]") -> bool:
        from pyvider.cty.types.structural import CtyDynamic
        return isinstance(other, (CtyString, CtyDynamic))

    def __str__(self) -> str:
        return "string"

    def is_primitive_type(self) -> bool:
        return True
