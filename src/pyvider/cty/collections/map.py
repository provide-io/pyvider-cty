import copy
from collections.abc import Mapping
from dataclasses import field
from types import MappingProxyType
from typing import Any, ClassVar, Generic, Optional, TypeVar, final

import attrs

from pyvider.exceptions import ValidationError

from ..primitives import (
    TFBool,
    TFNumber,
    TFString,
)
from ..type import TFType

T = TypeVar("T")

@final
@attrs.define(frozen=True, slots=True)
class TFMap(TFType[dict[str, T]], Generic[T]):
    ctype: ClassVar[str] = "map"
    key_type: Optional[TFType] = None
    value_type: TFType = field()
    metadata: Optional[Mapping[str, Any]] = field(default=None)
    default: Optional[Mapping[str, T]] = field(default=None)
    mutable: bool = field(default=False)  # Default to immutable

    def __attrs_post_init__(self):
        if not isinstance(self.value_type, TFType):
            raise ValidationError("Expected a valid TFType for value_type")

        if self.key_type is not None and not isinstance(self.key_type, TFType):
            raise ValidationError("Expected a valid TFType for key_type")

        if self.key_type is None:
            from pyvider.cty import TFString
            object.__setattr__(self, "key_type", TFString())

        if isinstance(self.metadata, dict):
            metadata = copy.deepcopy(self.metadata)
            if not self.mutable:
                metadata = MappingProxyType(metadata)
            object.__setattr__(self, "metadata", metadata)

        if isinstance(self.default, dict):
            default = copy.deepcopy(self.default)
            if not self.mutable:
                default = MappingProxyType(default)
            object.__setattr__(self, "default", default)

    def validate(self, value: Any) -> dict[str, T]:
        if not isinstance(value, dict):
            raise ValidationError(f"Expected dict, got {type(value).__name__}")

        validated = {}
        for k, v in value.items():
            validated_key = self.key_type.validate(k)
            validated_value = self._wrap_value(v)

            if isinstance(validated_value, list):
                validated_value = [
                    item.value if isinstance(item, TFType) else item for item in validated_value
                ]
            else:
                validated_value = (
                    validated_value.value if isinstance(validated_value, TFType) else validated_value
                )

            validated[validated_key.value if isinstance(validated_key, TFType) else validated_key] = validated_value

        return MappingProxyType(validated) if not self.mutable else validated

    def _wrap_value(self, value: Any) -> TFType:
        if isinstance(value, TFType):
            return value

        if isinstance(value, list):
            return [self._wrap_value(item) for item in value]

        if isinstance(value, dict):
            if isinstance(self.value_type, TFMap):
                nested_map = TFMap(
                    key_type=self.key_type,
                    value_type=self.value_type.value_type,
                    metadata=self.metadata,
                    mutable=self.mutable,
                )
                return nested_map.validate(value)
            raise ValidationError(f"Invalid type for nested dict. Expected {self.value_type.__class__.__name__}.")

        if isinstance(value, str) and isinstance(self.value_type, TFMap):
            # Convert string to single-entry map if expected type is TFMap
            return self.value_type.validate({value: value})

        if isinstance(value, bool) and isinstance(self.value_type, TFBool):
            return TFBool(value)
        if isinstance(value, (int, float)) and isinstance(self.value_type, TFNumber):
            return TFNumber(value)
        if isinstance(value, str) and isinstance(self.value_type, TFString):
            return TFString(value)

        raise ValidationError(
            f"Invalid type for map value: {type(value).__name__}. Expected {self.value_type.__class__.__name__}."
        )

    def equal(self, other: "TFType") -> bool:
        return (
            isinstance(other, TFMap)
            and self.key_type.equal(other.key_type)
            and self.value_type.equal(other.value_type)
            and self.metadata == other.metadata
            and self.default == other.default
            and self.mutable == other.mutable
        )

    def usable_as(self, other: "TFType") -> bool:
        return isinstance(other, TFMap) and self.value_type.usable_as(other.value_type)

    def __eq__(self, other):
        if not isinstance(other, TFMap):
            return False
        return (
            self.key_type.equal(other.key_type)
            and self.value_type.equal(other.value_type)
            and self.metadata == other.metadata
            and self.default == other.default
        )
