from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from attrs import define
from provide.foundation.config.parsers.primitives import parse_bool_strict

from pyvider.cty.exceptions import CtyBoolValidationError
from pyvider.cty.types.base import CtyType

if TYPE_CHECKING:
    from pyvider.cty.values import CtyValue


@define(frozen=True, slots=True)
class CtyBool(CtyType[bool]):
    ctype: ClassVar[str] = "bool"
    _type_order: ClassVar[int] = 2  # Correct go-cty order

    def validate(self, value: object) -> CtyValue[bool]:
        from pyvider.cty.values import CtyValue, UnknownValue

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
            return CtyValue.null(self)

        if isinstance(raw_value, bool):
            return CtyValue(vtype=self, value=raw_value)

        # Delegate to foundation's parse_bool_strict for all other types
        if isinstance(raw_value, str | int | float):
            try:
                parsed = parse_bool_strict(raw_value)
                return CtyValue(vtype=self, value=parsed)
            except (ValueError, TypeError) as e:
                raise CtyBoolValidationError(f"Cannot convert {type(raw_value).__name__} to bool: {e}") from e

        raise CtyBoolValidationError(f"Cannot convert {type(raw_value).__name__} to bool.")

    def equal(self, other: CtyType[Any]) -> bool:
        return isinstance(other, CtyBool)

    def usable_as(self, other: CtyType[Any]) -> bool:
        from pyvider.cty.types.structural import CtyDynamic

        return isinstance(other, CtyBool | CtyDynamic)

    def _to_wire_json(self) -> Any:
        return self.ctype

    def __str__(self) -> str:
        return "bool"

    def is_primitive_type(self) -> bool:
        return True
