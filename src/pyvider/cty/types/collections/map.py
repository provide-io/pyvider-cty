from typing import Any, ClassVar, TypeVar

from attrs import define, field

from pyvider.cty.exceptions import (
    CtyMapValidationError,
    CtyTypeMismatchError,
    CtyValidationError,
    InvalidTypeError,
)
from pyvider.cty.path import CtyPath, KeyStep
from pyvider.cty.types.base import CtyType
from pyvider.cty.values import CtyValue

V = TypeVar("V")


@define(frozen=True, slots=True)
class CtyMap[V](CtyType[dict[str, V]]):
    ctype: ClassVar[str] = "map"
    element_type: CtyType[V] = field(kw_only=True)

    def __attrs_post_init__(self) -> None:
        if not isinstance(self.element_type, CtyType):
            raise InvalidTypeError(
                f"element_type must be a CtyType instance, got {type(self.element_type).__name__}"
            )

    def validate(self, value: object) -> "CtyValue[dict[str, V]]":
        if value is None:
            return CtyValue.null(self)
        if isinstance(value, CtyValue):
            if value.is_null:
                return CtyValue.null(self)
            if value.is_unknown:
                return CtyValue.unknown(self)
            if isinstance(value.type, CtyMap) and self.equal(value.type):
                return value
            value = value.value
        if not isinstance(value, dict):
            raise CtyMapValidationError(
                f"Input must be a dictionary, got {type(value).__name__}."
            )
        validated_map: dict[str, CtyValue[V]] = {}
        for k, v in value.items():
            if not isinstance(k, str):
                raise CtyMapValidationError(
                    f"Map keys must be strings, but got key of type {type(k).__name__}"
                )
            try:
                validated_map[k] = self.element_type.validate(v)
            except CtyValidationError as e:
                new_path = CtyPath(
                    steps=[KeyStep(k)] + (e.path.steps if e.path else [])
                )
                raise CtyMapValidationError(
                    e.message, value=v, path=new_path, original_exception=e
                ) from e
        return CtyValue(vtype=self, value=validated_map)

    def get(
        self,
        map_value: "CtyValue[dict[str, V]]",
        key: object,
        default: "CtyValue[V] | None" = None,
    ) -> "CtyValue[V]":
        if not isinstance(map_value, CtyValue) or not isinstance(
            map_value.type, CtyMap
        ):
            raise CtyTypeMismatchError("get operation called on non-map CtyValue")
        if map_value.is_null or map_value.is_unknown:
            return default if default is not None else CtyValue.null(self.element_type)
        internal_dict = map_value.value
        if not isinstance(internal_dict, dict):
            raise CtyMapValidationError(
                f"Internal error: CtyValue of CtyMap type does not wrap a dict, got {type(internal_dict).__name__}"
            )
        result = internal_dict.get(str(key))
        if result is not None:
            return self.element_type.validate(result)
        return default if default is not None else CtyValue.null(self.element_type)

    def equal(self, other: "CtyType[Any]") -> bool:
        if not isinstance(other, CtyMap):
            return False
        return self.element_type.equal(other.element_type)

    def usable_as(self, other: "CtyType[Any]") -> bool:
        from pyvider.cty.types.structural import CtyDynamic

        if isinstance(other, CtyDynamic):
            return True
        if not isinstance(other, CtyMap):
            return False
        return self.element_type.usable_as(other.element_type)

    def _to_wire_json(self) -> Any:
        return [self.ctype, self.element_type._to_wire_json()]

    def __str__(self) -> str:
        return f"map({self.element_type})"
