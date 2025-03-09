"""
TFObject type implementation for Terraform.

The TFObject type represents a complex value with a fixed set of attributes,
where each attribute has its own type. Unlike maps, objects have a predefined
schema and support different types for different attributes.

Examples:
    Define an address type:
    >>> address_type = TFObject({
    ...     "street": Types.string(),
    ...     "city": Types.string(),
    ...     "postal_code": Types.string(),
    ...     "country": Types.string(),
    ...     "is_primary": Types.boolean()
    ... }, optional_attributes={"is_primary"})

    Create and validate an address:
    >>> addr = address_type.validate({
    ...     "street": "123 Main St",
    ...     "city": "Springfield",
    ...     "postal_code": "12345",
    ...     "country": "US"
    ... })
"""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, FrozenSet, TypeVar, final

from pyvider.exceptions import AttributeValidationError, InvalidTypeError, SchemaValidationError, ValidationError

from ..base import TFType

T = TypeVar('T')

def _extract_ctype(value):
    """Helper to unwrap AttributeValue to extract the raw TFType."""
    return value.ctype if isinstance(value, AttributeValue) else value

@final
@dataclass(frozen=True)
class TFObject(TFType[dict[str, Any]]):
    """
    TFObject represents a Terraform object type.

    An object is a collection of attributes where each attribute has its own type.
    Unlike maps, objects have a schema - you can't add arbitrary keys, and each
    key has its own type which may be different from other keys.
    """

    attribute_types: dict[str, TFType]
    optional_attributes: FrozenSet[str] = field(default_factory=frozenset)
    computed_attributes: FrozenSet[str] = field(default_factory=frozenset)  # Added computed attributes
    block_attributes: FrozenSet[str] = field(default_factory=frozenset)
    mutable: bool = True  # Default to mutable


    def __post_init__(self):
        """Validate object type configuration."""
        # Unlike Go, Python's dataclass can't do this in a frozen pre-init state
        # so we validate attributes instead
        if not isinstance(self.attribute_types, dict):
            raise InvalidTypeError("attribute_types must be a dictionary")

        # Validate that all types are TFType instances
        invalid_types = [
            name for name, type_ in self.attribute_types.items()
            if not isinstance(type_, TFType)
        ]
        if invalid_types:
            raise AttributeValidationError(f"Invalid types for attributes: {', '.join(invalid_types)}")

        # Validate optional attributes
        unknown_optional = (
            set(self.optional_attributes) - set(self.attribute_types)
        )
        if unknown_optional:
            raise AttributeValidationError(
                f"Unknown optional attributes: {', '.join(unknown_optional)}"
            )

    def validate(self, value: dict[str, Any]) -> dict[str, Any]:
        """
        Validate a dictionary against the object schema.

        Args:
            value (dict[str, Any]): The dictionary to validate.

        Returns:
            dict[str, Any]: The validated dictionary.

        Raises:
            ValidationError: If the validation fails.
        """

        if value is None:
           return None

        if not isinstance(value, dict):
            raise ValidationError(f"TFObject value must be a dictionary, got {type(value).__name__}.")

        validated = {}
        for name, attr_type in self.attribute_types.items():
            if name not in value:
                if name not in self.optional_attributes:
                    raise ValidationError(f"Missing required attribute: {name}.")
                continue

            try:
                validated[name] = attr_type.validate(value[name])
            except ValidationError as e:
                original_message = str(e).split(": ", 1)[-1]
                raise ValidationError(f"Invalid value for attribute '{name}': {original_message}")

        # Enforce immutability if required
        if not self.mutable:
            return MappingProxyType(validated)

        return validated

    # def __eq__(self, other):
    #     if not isinstance(other, TFObject):
    #         return False
    #     return (
    #         self.attribute_types == other.attribute_types and
    #         self.optional_attributes == other.optional_attributes
    #     )

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def get_attribute(self, value: dict[str, Any], name: str) -> Any:
        """
        Get a validated attribute value by name.

        Args:
            value: TFObject value to access
            name: Name of attribute to get

        Returns:
            Attribute value

        Raises:
            AttributeValidationError: If attribute doesn't exist
            ValidationError: If value is not a valid object
        """
        if not isinstance(value, dict):
            raise ValidationError(f"Expected dict, got {type(value).__name__}")

        if name not in self.attribute_types:
            raise AttributeValidationError(f"Unknown attribute: {name}")

        return value.get(name)

    def with_optional(self, *names: str) -> "TFObject":
        """
        Create new object type with additional optional attributes.

        Args:
            *names: Names of attributes to mark as optional

        Returns:
            New TFObject type with updated optional attributes

        Raises:
            SchemaValidationError: If any name is not a valid attribute
        """
        unknown = set(names) - set(self.attribute_types)
        if unknown:
            raise SchemaValidationError(f"Unknown attributes: {', '.join(unknown)}")

        return TFObject(
            self.attribute_types,
            self.optional_attributes | set(names),
            self.block_attributes,
            self.computed_attributes
        )

    def with_blocks(self, *names: str) -> "TFObject":
        """
        Create new object type with attributes marked as blocks.

        Args:
            *names: Names of attributes to mark as blocks

        Returns:
            New TFObject type with updated block attributes

        Raises:
            SchemaValidationError: If any name is not a valid attribute
        """
        unknown = set(names) - set(self.attribute_types)
        if unknown:
            raise SchemaValidationError(f"Unknown attributes: {', '.join(unknown)}")

        return TFObject(
            self.attribute_types,
            self.optional_attributes,
            self.block_attributes | set(names),
            self.computed_attributes
        )

    def with_computed(self, *names: str) -> "TFObject":
        """
        Create new object type with computed attributes.

        Args:
            *names: Names of attributes to mark as computed

        Returns:
            New TFObject type with updated computed attributes

        Raises:
            SchemaValidationError: If any name is not a valid attribute
        """
        unknown = set(names) - set(self.attribute_types)
        if unknown:
            raise SchemaValidationError(f"Unknown attributes: {', '.join(unknown)}")

        return TFObject(
            self.attribute_types,
            self.optional_attributes,
            self.block_attributes,
            self.computed_attributes | set(names)
        )

    def equal(self, other: "TFType") -> bool:
        """Check if types are equal."""
        if not isinstance(other, TFObject):
            return False

        if set(self.attribute_types) != set(other.attribute_types):
            return False

        return all(
            self.attribute_types[name].equal(other.attribute_types[name])
            for name in self.attribute_types
        )

    def usable_as(self, other: "TFType") -> bool:
        """Check if this type can be used as another type."""
        if not isinstance(other, TFObject):
            return False

        # Check that all required attributes are present and compatible
        return all(
            name in self.attribute_types
            and self.attribute_types[name].usable_as(attr_type)
            for name, attr_type in other.attribute_types.items()
        )

    def attributes(self) -> frozenset[str]:
        """Get all attribute names."""
        return frozenset(self.attribute_types)

    def required_attributes(self) -> frozenset[str]:
        """Get names of required attributes."""
        return (
            set(self.attribute_types) -
            self.optional_attributes -
            self.computed_attributes
        )

    def __hash__(self):
        # Optional: Implement if the object needs to be used in sets/dicts
        return hash(frozenset(self.attribute_types.items()))

    def __str__(self) -> str:
        """Get string representation of the type."""
        parts = []
        for name, type_ in sorted(self.attribute_types.items()):
            part = f"{name}: {type_}"
            if name in self.optional_attributes:
                part += "?"
            if name in self.computed_attributes:
                part += " (computed)"
            if name in self.block_attributes:
                part += " (block)"
            parts.append(part)

        return f"object({', '.join(parts)})"

    def __repr__(self):
        return f"{self.__class__.__name__}()"
