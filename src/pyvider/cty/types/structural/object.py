# pyvider/cty/types/structural/object.py
from collections.abc import Iterator
from typing import ClassVar

from attrs import define, field, evolve

from pyvider.cty.exceptions import (
    CtyAttributeValidationError,
    CtyTypeMismatchError,
    CtyValidationError,
    InvalidTypeError,
)
from pyvider.cty.types.base import CtyType
from pyvider.cty.values import CtyValue
from pyvider.telemetry import logger


@define(frozen=True, slots=True)
class CtyObject(CtyType[dict[str, object]]):
    """Represents a Cty object type with a fixed set of attributes."""
    ctype: ClassVar[str] = "object"
    attribute_types: dict[str, CtyType] = field(factory=dict)
    optional_attributes: frozenset[str] = field(factory=frozenset)

    def __attrs_post_init__(self) -> None:
        if not isinstance(self.attribute_types, dict):
            raise InvalidTypeError(f"Expected dict for attribute_types, got {type(self.attribute_types).__name__}")
        invalid_types = [name for name, vtype in self.attribute_types.items() if not isinstance(vtype, CtyType)]
        if invalid_types:
            raise CtyAttributeValidationError(f"Invalid types for attributes: {', '.join(invalid_types)}")
        unknown_optional = set(self.optional_attributes) - set(self.attribute_types)
        if unknown_optional:
            raise CtyValidationError(f"Unknown optional attributes: {', '.join(unknown_optional)}")

    def validate(self, value: object) -> CtyValue:
        if isinstance(value, CtyValue):
            if isinstance(value.type, CtyObject) and value.type.equal(self):
                return value
            if value.is_unknown:
                return CtyValue.unknown(self)
            value = value.value
        if value is None:
            return CtyValue.null(self)
        if not isinstance(value, dict):
            raise CtyValidationError(f"Expected a dictionary for CtyObject, got {type(value).__name__}")

        logger.debug("CtyObject.validate: Validating input object", input_value=value, object_type=self)

        validated_attrs, validation_errors = {}, []
        unknown_attrs = set(value.keys()) - set(self.attribute_types.keys())
        if unknown_attrs:
            validation_errors.append(f"Unknown attributes: {', '.join(unknown_attrs)}")

        for name, attr_type in self.attribute_types.items():
            logger.debug(f"CtyObject.validate: Processing attribute '{name}' of type {attr_type}")
            if name not in value:
                if name in self.optional_attributes:
                    validated_attrs[name] = CtyValue.null(attr_type)
                else:
                    validation_errors.append(f"Missing required attribute: '{name}'")
                continue

            try:
                validated_attrs[name] = attr_type.validate(value[name])
            except CtyValidationError as e:
                logger.error(f"CtyObject.validate: Validation error for attribute '{name}'", error_message=str(e), raw_value_for_attr=value[name])
                validation_errors.append(f"Invalid value for attribute '{name}': {e}")
        
        if validation_errors:
            raise CtyValidationError("Object validation failed:\n" + "\n".join(f" - {e}" for e in validation_errors))
        return CtyValue(vtype=self, value=validated_attrs)

    def get_attribute(self, obj_value: CtyValue, name: str) -> CtyValue:
        if not isinstance(obj_value, CtyValue):
            raise CtyTypeMismatchError(f"Expected a CtyValue, but got {type(obj_value).__name__}")
        if not self.has_attribute(name):
            raise CtyAttributeValidationError(f"Object has no attribute '{name}'")
        if obj_value.is_unknown:
            return CtyValue.unknown(self.attribute_types[name])
        if obj_value.is_null:
            return CtyValue.null(self.attribute_types[name])
        internal_attrs = obj_value.value
        if not isinstance(internal_attrs, dict):
            raise CtyAttributeValidationError(f"Internal error: CtyObject's CtyValue does not wrap a dict, got {type(internal_attrs).__name__}")
        attr_cty_value = internal_attrs.get(name)
        if attr_cty_value is None:
            if name in self.optional_attributes:
                 return CtyValue.null(self.attribute_types[name])
            raise CtyAttributeValidationError(f"Required attribute '{name}' missing from object value post-validation.")
        return attr_cty_value

    def required_attributes(self) -> frozenset[str]:
        return frozenset(name for name in self.attribute_types if name not in self.optional_attributes)

    def has_attribute(self, name: str) -> bool:
        return name in self.attribute_types

    def equal(self, other: CtyType) -> bool:
        if not isinstance(other, CtyObject): return False
        if set(self.attribute_types) != set(other.attribute_types): return False
        if self.optional_attributes != other.optional_attributes: return False
        return all(vtype.equal(other.attribute_types[name]) for name, vtype in self.attribute_types.items())

    def usable_as(self, other: CtyType) -> bool:
        from pyvider.cty.types.structural import CtyDynamic
        if isinstance(other, CtyDynamic): return True
        if not isinstance(other, CtyObject): return False
        self_attrs, other_attrs = set(self.attribute_types), set(other.attribute_types)
        if not other_attrs.issubset(self_attrs): return False
        if not other.required_attributes().issubset(self.required_attributes()): return False
        return all(self.attribute_types[name].usable_as(other.attribute_types[name]) for name in other_attrs)
    
    def __iter__(self) -> Iterator[str]:
        return iter(self.attribute_types)

    def __len__(self) -> int:
        return len(self.attribute_types)

    def __str__(self) -> str:
        parts = []
        for name, vtype in sorted(self.attribute_types.items()):
            part_str = f"{name}={vtype!s}"
            parts.append(part_str)
        return f"object({{{', '.join(parts)}}})"
