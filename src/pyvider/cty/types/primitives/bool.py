from decimal import Decimal, InvalidOperation
from typing import Any, ClassVar
from attrs import define, field
from pyvider.cty.exceptions import CtyBoolValidationError
from pyvider.cty.types.base import CtyType
from pyvider.cty.values import CtyValue
from pyvider.cty.values.base import UnknownValue
from pyvider.telemetry import logger
from pyvider.cty.types.structural import CtyDynamic

TRUE_STRINGS: frozenset[str] = frozenset(("true", "t", "yes", "y", "1"))
FALSE_STRINGS: frozenset[str] = frozenset(("false", "f", "no", "n", "0"))

@define(frozen=True, slots=True)
class CtyBool(CtyType[bool]):
    ctype: ClassVar[str] = "bool"
    value: bool = field(default=False)

    def validate(self, value: object) -> CtyValue:
        if value is None: return CtyValue.null(self)
        if isinstance(value, UnknownValue): return CtyValue.unknown(self)
        if isinstance(value, CtyValue):
            if value.is_unknown: return CtyValue.unknown(self)
            if value.is_null: return CtyValue.null(self)
            if isinstance(value.type, CtyBool): return value
            value = value.value
        if isinstance(value, bool): return CtyValue(vtype=self, value=value)
        if isinstance(value, str):
            val_lower = value.lower()
            if val_lower in TRUE_STRINGS: return CtyValue(vtype=self, value=True)
            if val_lower in FALSE_STRINGS: return CtyValue(vtype=self, value=False)
            raise CtyBoolValidationError(f"Cannot convert string {value!r} to boolean")
        if isinstance(value, (int, float, Decimal)):
            try:
                dec_val = Decimal(value)
                if dec_val == Decimal(1): return CtyValue(vtype=self, value=True)
                if dec_val == Decimal(0): return CtyValue(vtype=self, value=False)
                raise CtyBoolValidationError(f"Numeric value {value!r} is not 0 or 1")
            except (InvalidOperation, ValueError) as e:
                raise CtyBoolValidationError(str(e)) from e
        raise CtyBoolValidationError(f"Cannot convert {type(value).__name__} to boolean")

    def equal(self, other: "CtyType") -> bool: return isinstance(other, CtyBool)
    def usable_as(self, other: "CtyType") -> bool:
        from pyvider.cty.types.structural import CtyDynamic
        return isinstance(other, (CtyBool, CtyDynamic))
    
    def _to_wire_json(self) -> Any:
        return self.ctype

    def __str__(self) -> str: return "bool"
    def is_primitive_type(self) -> bool: return True
