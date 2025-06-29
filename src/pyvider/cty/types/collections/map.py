# pyvider/cty/types/collections/map.py
from typing import ClassVar, Generic, TypeVar, TYPE_CHECKING
from attrs import define, field
from pyvider.cty.exceptions import CtyMapValidationError, CtyTypeMismatchError, CtyValidationError
from pyvider.cty.types.base import CtyType
from pyvider.cty.types.primitives import CtyString, CtyNumber, CtyBool
from pyvider.cty.values import CtyValue
from pyvider.telemetry import logger
from pyvider.cty.types.structural.dynamic import CtyDynamic

if TYPE_CHECKING:
    from pyvider.cty.types.structural.object import CtyObject
    from pyvider.cty.types.collections.list import CtyList

V = TypeVar("V")

@define(frozen=True, slots=True)
class CtyMap(CtyType[dict[str, V]], Generic[V]):
    ctype: ClassVar[str] = "map"
    key_type: CtyType[str] = field(kw_only=True, default=CtyString())
    value_type: CtyType[V] = field(kw_only=True)

    def __attrs_post_init__(self) -> None:
        if not isinstance(self.key_type, CtyType):
            raise CtyMapValidationError(f"key_type must be a CtyType instance, got {type(self.key_type).__name__}")
        if not isinstance(self.value_type, CtyType):
            raise CtyMapValidationError(f"value_type must be a CtyType instance, got {type(self.value_type).__name__}")
        if not (self.key_type.is_primitive_type() or isinstance(self.key_type, CtyDynamic)):
            raise CtyMapValidationError(f"Map key_type must be a primitive type or CtyDynamic, got {self.key_type.__class__.__name__}")

    def validate(self, value: object) -> "CtyValue":
        if value is None: return CtyValue.null(self)
        if isinstance(value, CtyValue):
            if value.is_null: return CtyValue.null(self)
            if value.is_unknown: return CtyValue.unknown(self)
            if isinstance(value.type, CtyMap):
                if self.equal(value.type): return value
                if not value.type.usable_as(self):
                    raise CtyMapValidationError(f"Input CtyValue map type {str(value.type)} is not compatible with target type {str(self)}")
                value = value.value
            else:
                raise CtyMapValidationError(f"Input CtyValue has type {value.type.ctype}, expected compatible map type.")

        if not isinstance(value, dict):
            raise CtyMapValidationError(f"Input must be a dictionary, got {type(value).__name__}.")

        if not value:
            return CtyValue(vtype=self, value={}, key_mapping={})

        validated_map, key_mapping, errors = {}, {}, []
        for k, v in value.items():
            try:
                validated_key_cty_value = self.key_type.validate(k)
                if validated_key_cty_value.is_null or validated_key_cty_value.is_unknown:
                    errors.append(f"Invalid key {repr(k)}: Map keys cannot be null or unknown.")
                    continue
                
                map_key_str_internal = str(validated_key_cty_value.value)
                
                final_value_to_store = self.value_type.validate(v)
                
                validated_map[map_key_str_internal] = final_value_to_store
                key_mapping[map_key_str_internal] = validated_key_cty_value

            except CtyValidationError as e:
                errors.append(f"Invalid key-value pair ('{k}': '{v}'): {e}")
            except Exception as e_outer:
                 errors.append(f"Unexpected error processing pair ('{k}': '{v}'): {e_outer}")

        if errors:
            errors.sort()
            raise CtyMapValidationError("Map validation failed:\n - " + "\n - ".join(errors))
        return CtyValue(vtype=self, value=validated_map, key_mapping=key_mapping)
    
    def get(self, map_value: CtyValue, key: object, default: CtyValue | None = None) -> CtyValue:
        if not isinstance(map_value, CtyValue) or not isinstance(map_value.type, CtyMap):
            raise CtyTypeMismatchError(f"get operation called on non-map CtyValue or non-CtyValue: {type(map_value)}")

        if map_value.is_null or map_value.is_unknown:
            return default if default is not None else CtyValue.null(self.value_type)
        try:
            key_for_lookup = key.value if isinstance(key, CtyValue) else key
            validated_key_for_lookup = self.key_type.validate(key_for_lookup)
            if validated_key_for_lookup.is_null or validated_key_for_lookup.is_unknown:
                 return default if default is not None else CtyValue.null(self.value_type)
            str_key = str(validated_key_for_lookup.value)
            internal_dict = map_value.value
            if not isinstance(internal_dict, dict):
                 return default if default is not None else CtyValue.null(self.value_type)
            return internal_dict.get(str_key, default if default is not None else CtyValue.null(self.value_type))
        except Exception:
            return default if default is not None else CtyValue.null(self.value_type)

    def equal(self, other: "CtyType") -> bool:
        if not isinstance(other, CtyMap): return False
        key_types_equal = self.key_type.equal(other.key_type)
        value_types_equal = self.value_type.equal(other.value_type)
        return key_types_equal and value_types_equal

    def usable_as(self, other: "CtyType") -> bool:
        if isinstance(other, CtyDynamic): return True
        if not isinstance(other, CtyMap): return False
        key_usable = self.key_type.usable_as(other.key_type)
        value_usable = self.value_type.usable_as(other.value_type)
        return key_usable and value_usable

    def __str__(self) -> str:
        return f"map({self.value_type})"

    def is_collection_type(self) -> bool: return True
    def is_map_type(self) -> bool: return True
