from decimal import Decimal, InvalidOperation
from typing import ClassVar
from attrs import define, field
from pyvider.cty.exceptions import CtyNumberValidationError
from pyvider.cty.types.base import CtyType
from pyvider.cty.types.structural import CtyDynamic
from pyvider.cty.values import CtyValue
from pyvider.cty.values.base import UnknownValue
from pyvider.telemetry import logger

@define(frozen=True, slots=True)
class CtyNumber(CtyType[int | float | Decimal]):
    ctype: ClassVar[str] = "number"
    value: int | Decimal = field(default=0)

    def validate(self, value: object) -> CtyValue:
        if value is None: return CtyValue.null(self)
        if isinstance(value, UnknownValue): return CtyValue.unknown(self)
        
        if isinstance(value, CtyValue):
            if value.is_unknown: return CtyValue.unknown(self)
            if value.is_null: return CtyValue.null(self)
            if isinstance(value.type, CtyNumber): return value
            value = value.value

        if isinstance(value, (int, float, Decimal)):
            try:
                return CtyValue(vtype=self, value=Decimal(value))
            except (InvalidOperation, TypeError, ValueError) as e:
                raise CtyNumberValidationError(f"Cannot represent {type(value).__name__} value {value!r} as Decimal: {e}")
        
        if isinstance(value, str):
            try:
                return CtyValue(vtype=self, value=Decimal(value))
            except InvalidOperation:
                raise CtyNumberValidationError(f"Cannot convert string '{value}' to number")

        raise CtyNumberValidationError(f"Cannot convert {type(value).__name__} to number")

    def equal(self, other: "CtyType") -> bool: return isinstance(other, CtyNumber)
    def usable_as(self, other: "CtyType") -> bool: return isinstance(other, (CtyNumber, CtyDynamic))
    def __str__(self) -> str: return "number"
    def is_primitive_type(self) -> bool: return True
