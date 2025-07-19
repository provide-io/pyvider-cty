from typing import TYPE_CHECKING, Any, ClassVar
import unicodedata

from attrs import define

from pyvider.cty.exceptions import CtyStringValidationError
from pyvider.cty.types.base import CtyType

if TYPE_CHECKING:
    from pyvider.cty.values import CtyValue


@define(frozen=True, slots=True)
class CtyString(CtyType[str]):
    ctype: ClassVar[str] = "string"

    def validate(self, value: object) -> "CtyValue[str]":
        from pyvider.cty.values import CtyValue
        from pyvider.cty.values.base import UnknownValue

        if isinstance(value, UnknownValue):
            return CtyValue.unknown(self)

        if isinstance(value, CtyValue):
            if value.is_null:
                return CtyValue.null(self)
            if value.is_unknown:
                return CtyValue.unknown(self)
            raw_value = value.value
        else:
            raw_value = value

        if raw_value is None:
            raise CtyStringValidationError("Cannot convert null to string.")

        # FIX: Make validation stricter. Only accept strings or bytes.
        if not isinstance(raw_value, str | bytes):
            raise CtyStringValidationError(f"Cannot convert {type(raw_value).__name__} to string.")

        try:
            str_value = str(raw_value)
            normalized_value = unicodedata.normalize("NFC", str_value)
            return CtyValue(vtype=self, value=normalized_value)
        except Exception as e:
            raise CtyStringValidationError(f"Cannot convert {type(raw_value).__name__} to string: {e}") from e

    def equal(self, other: "CtyType[object]") -> bool:
        return isinstance(other, CtyString)

    def usable_as(self, other: "CtyType[object]") -> bool:
        from pyvider.cty.types.structural import CtyDynamic
        return isinstance(other, CtyString | CtyDynamic)

    def _to_wire_json(self) -> Any:
        return self.ctype

    def __str__(self) -> str:
        return "string"

    def is_primitive_type(self) -> bool:
        return True
