# pyvider/cty/types/primitives/string.py
import unicodedata
from typing import TYPE_CHECKING, ClassVar
from attrs import define, field
from pyvider.cty.exceptions import CtyStringValidationError
from pyvider.cty.types.base import CtyType
from pyvider.cty.values.base import UnknownValue

if TYPE_CHECKING:
    from pyvider.cty.values import CtyValue

@define(frozen=True, slots=True)
class CtyString(CtyType[str]):
    ctype: ClassVar[str] = "string"
    value: str = field(default="")

    def validate(self, value: object) -> "CtyValue":
        from pyvider.cty.values import CtyValue
        from pyvider.cty.types.structural.dynamic import CtyDynamic
        
        if value is None: return CtyValue.null(self)
        if isinstance(value, UnknownValue): return CtyValue.unknown(self)

        normalized_value: str
        if isinstance(value, CtyValue):
            if value.is_unknown: return CtyValue.unknown(self)
            if value.is_null: return CtyValue.null(self)
            if isinstance(value.type, CtyString):
                # Assuming the CtyValue[CtyString] already holds a normalized string
                return value
            if value.type.is_primitive_type():
                normalized_value = unicodedata.normalize('NFC', str(value.value))
                return CtyValue(self, normalized_value)
            if isinstance(value.type, CtyDynamic):
                inner_py_val = value.value.value if isinstance(value.value, CtyValue) else value.value
                if inner_py_val is None: return CtyValue.null(self)
                normalized_value = unicodedata.normalize('NFC', str(inner_py_val))
                return CtyValue(self, normalized_value)
            raise CtyStringValidationError(f"Cannot convert CtyValue of type {value.type.__class__.__name__} to CtyString.")

        if isinstance(value, (str, int, float, bool)):
             normalized_value = unicodedata.normalize('NFC', str(value))
             return CtyValue(vtype=self, value=normalized_value)

        raise CtyStringValidationError(f"Value of type {type(value).__name__} cannot be converted to a string.")

    def equal(self, other: "CtyType[object]") -> bool: return isinstance(other, CtyString)
    def usable_as(self, other: "CtyType[object]") -> bool:
        from pyvider.cty.types.structural import CtyDynamic
        return isinstance(other, (CtyString, CtyDynamic))
    def __str__(self) -> str: return "string"
    def is_primitive_type(self) -> bool: return True
