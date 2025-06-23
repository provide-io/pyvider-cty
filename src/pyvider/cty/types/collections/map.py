# pyvider/cty/types/collections/map.py
from typing import ClassVar, Generic, TypeVar
from attrs import define, field
from pyvider.cty.exceptions import CtyMapValidationError
from pyvider.cty.types.base import CtyType
from pyvider.cty.types.primitives import CtyString
from pyvider.cty.values import CtyValue
from pyvider.telemetry import logger

V = TypeVar("V")

@define(frozen=True, slots=True)
class CtyMap(CtyType[dict[str, V]], Generic[V]):
    ctype: ClassVar[str] = "map"
    key_type: CtyType[str] = field(kw_only=True, default=CtyString())
    value_type: CtyType[V] = field(kw_only=True)

    def __attrs_post_init__(self) -> None:
        if not isinstance(self.key_type, CtyType) or not isinstance(self.value_type, CtyType):
            raise CtyMapValidationError("key_type and value_type must be CtyType instances.")

    def validate(self, value: object) -> "CtyValue":
        # Handle None input directly by creating a null CtyMap value.
        if value is None:
            return CtyValue.null(self)

        if isinstance(value, CtyValue):
            if value.is_null: return CtyValue.null(self)
            if value.is_unknown: return CtyValue.unknown(self)
            if isinstance(value.type, CtyMap) and self.equal(value.type): return value
            value = value.value

        if not isinstance(value, dict):
            raise CtyMapValidationError(f"Expected dict or CtyValue map, got {type(value).__name__}")

        if not value:
            return CtyValue(vtype=self, value={}, key_mapping={})

        validated_map: dict[str, CtyValue] = {}
        key_mapping: dict[str, CtyValue] = {}
        validation_errors = []

        for k, v in value.items():
            try:
                validated_key_cty = self.key_type.validate(k)
                if validated_key_cty.is_null or validated_key_cty.is_unknown:
                    raise CtyMapValidationError("Map keys cannot be null or unknown")
                map_key_str = str(validated_key_cty.value)
                validated_value_cty = self.value_type.validate(v)
                validated_map[map_key_str] = validated_value_cty
                key_mapping[map_key_str] = validated_key_cty
            except Exception as e:
                validation_errors.append(f"Error processing item '{k}': {e}")

        if validation_errors:
            raise CtyMapValidationError("Map validation failed:\\n - " + "\\n - ".join(validation_errors))

        return CtyValue(vtype=self, value=validated_map, key_mapping=key_mapping)
    
    def equal(self, other: "CtyType") -> bool:
        from pyvider.cty.types.structural.dynamic import CtyDynamic
        if not isinstance(other, CtyMap): return False
        return self.key_type.equal(other.key_type) and self.value_type.equal(other.value_type)

    def usable_as(self, other: "CtyType") -> bool:
        from pyvider.cty.types.structural.dynamic import CtyDynamic
        if isinstance(other, CtyDynamic): return True
        if not isinstance(other, CtyMap): return False
        return self.key_type.usable_as(other.key_type) and self.value_type.usable_as(other.value_type)

    def __str__(self) -> str: return f"map({self.value_type!s})"
    def is_collection_type(self) -> bool: return True
    def is_map_type(self) -> bool: return True
