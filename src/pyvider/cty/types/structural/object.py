# pyvider/cty/types/structural/object.py
from collections.abc import Iterator
from typing import ClassVar

from attrs import define, field

from pyvider.cty.exceptions import (
    CtyAttributeValidationError,
    CtyValidationError,
)
from pyvider.cty.types.base import CtyType
from pyvider.cty.values import CtyValue


@define(frozen=True, slots=True)
class CtyObject(CtyType[dict[str, object]]):
    ctype: ClassVar[str] = "object"
    attribute_types: dict[str, CtyType] = field(factory=dict)
    optional_attributes: frozenset[str] = field(factory=frozenset)

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
            raise CtyValidationError(
                f"Expected a dictionary for CtyObject, got {type(value).__name__}"
            )

        validated_attrs = {}
        validation_errors = []

        # Check for unknown attributes provided in the input value
        unknown_attrs = set(value.keys()) - set(self.attribute_types.keys())
        if unknown_attrs:
            validation_errors.append(f"Unknown attributes: {', '.join(unknown_attrs)}")

        for name, attr_type in self.attribute_types.items():
            is_optional_or_computed = name in self.optional_attributes

            if name not in value:
                if not is_optional_or_computed:
                    validation_errors.append(f"Missing required attribute: '{name}'")
                else:
                    validated_attrs[name] = CtyValue.null(attr_type)
                continue

            attr_value = value[name]
            
            # This is the critical change:
            # We must validate the raw value against its specific CtyType from the schema.
            # This ensures that a raw dict for 'parsed_body' is validated against CtyDynamic,
            # and a raw dict for 'response_headers' is validated against CtyMap.
            try:
                validated_attrs[name] = attr_type.validate(attr_value)
            except CtyValidationError as e:
                validation_errors.append(f"Invalid value for attribute '{name}': {e}")

        if validation_errors:
            raise CtyValidationError(
                "Object validation failed:\n"
                + "\n".join(f" - {e}" for e in validation_errors)
            )

        return CtyValue(vtype=self, value=validated_attrs)

    def equal(self, other: CtyType) -> bool:
        if not isinstance(other, CtyObject):
            return False
        if set(self.attribute_types) != set(other.attribute_types):
            return False
        if self.optional_attributes != other.optional_attributes:
            return False
        return all(
            vtype.equal(other.attribute_types[name])
            for name, vtype in self.attribute_types.items()
        )

    def usable_as(self, other: CtyType) -> bool:
        # For now, require exact equality for usability.
        return self.equal(other)

    def has_attribute(self, name: str) -> bool:
        return name in self.attribute_types

    def get_attribute(self, obj_value: CtyValue, name: str) -> CtyValue:
        if not self.has_attribute(name):
            raise CtyAttributeValidationError(f"Object has no attribute '{name}'")
        if obj_value.is_null or obj_value.is_unknown:
            return CtyValue.unknown(self.attribute_types[name])
        return obj_value.value.get(name)
