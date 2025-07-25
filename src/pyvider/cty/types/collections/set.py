from __future__ import annotations

from typing import Any, ClassVar, TypeVar, final

from attrs import define, field

from pyvider.cty.exceptions import CtySetValidationError, CtyValidationError
from pyvider.cty.types.base import CtyType
from pyvider.cty.values import CtyValue

T = TypeVar("T")


@final
@define(frozen=True, slots=True)
class CtySet[T](CtyType[frozenset[T]]):
    ctype: ClassVar[str] = "set"
    element_type: CtyType[T] = field(kw_only=True)

    def __attrs_post_init__(self) -> None:
        if not isinstance(self.element_type, CtyType):
            raise CtySetValidationError(
                f"Expected CtyType for element_type, got {type(self.element_type)}"
            )

    def validate(self, value: object) -> CtyValue[frozenset[T]]:
        if value is None: return CtyValue.null(self)
        if isinstance(value, CtyValue):
            if value.is_unknown: return CtyValue.unknown(self)
            if value.is_null: return CtyValue.null(self)
            if isinstance(value.type, CtySet) and value.type.equal(self): return value
            value = value.value

        if not isinstance(value, list | tuple | set | frozenset):
            raise CtySetValidationError(f"Expected a Python set, frozenset, list, or tuple, got {type(value).__name__}")

        validated_items: set[CtyValue[Any]] = set()
        for raw_item in value:
            try:
                validated_item = self.element_type.validate(raw_item)
                validated_items.add(validated_item)
            except TypeError as e:
                raise CtySetValidationError(f"Input collection contains unhashable elements: {e}") from e
            except CtyValidationError as e:
                raise CtySetValidationError(e.message, value=raw_item) from e

        return CtyValue(vtype=self, value=frozenset(validated_items))

    def equal(self, other: CtyType[Any]) -> bool:
        if not isinstance(other, CtySet): return False
        return self.element_type.equal(other.element_type)

    def usable_as(self, other: CtyType[Any]) -> bool:
        from pyvider.cty.types.structural import CtyDynamic
        if isinstance(other, CtyDynamic): return True
        if not isinstance(other, CtySet): return False
        return self.element_type.usable_as(other.element_type)

    def _to_wire_json(self) -> Any:
        return [self.ctype, self.element_type._to_wire_json()]

    def __str__(self) -> str:
        return f"set({self.element_type})"
