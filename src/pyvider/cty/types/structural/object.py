#
# pyvider/cty/types/structural/object.py
#

"""
CtyObject implementation for Cty object values.

This module provides the CtyObject type implementation which represents an object
with named attributes of specific types. Objects have a predefined schema with
strictly typed attributes and support for optional attributes.

CtyObject follows the design principles of go-cty's Object type, ensuring type
consistency throughout the validation process and maintaining proper type information
in nested structures.
"""

from typing import Any, ClassVar, FrozenSet, Optional, Self, Union

from attrs import define, evolve, field

from pyvider.telemetry import logger
from pyvider.cty.types.base import CtyType
from pyvider.cty.values import CtyValue
from pyvider.cty.exceptions import (
    CtyAttributeValidationError,
    InvalidTypeError,
    CtyValidationError,
)


@define(frozen=True, slots=True)
class CtyObject(CtyType[dict[str, Any]]):
    """
    Represents a Cty object type with a fixed set of attributes.

    An object has a predefined schema with strictly typed attributes.
    Each attribute has a name and a specific type, and may be marked
    as optional.

    Attributes:
        attribute_types: dictionary mapping attribute names to their types
        optional_attributes: Set of attribute names that are optional
    """
    ctype: ClassVar[str] = "object"
    attribute_types: dict[str, CtyType] = field(factory=dict)
    optional_attributes: FrozenSet[str] = field(factory=frozenset)

    def __attrs_post_init__(self) -> None:
        """Validate object type configuration."""
        logger.debug("🧩🔍🔄 Validating CtyObject configuration on initialization")

        # Validate attribute_types is a dictionary
        if not isinstance(self.attribute_types, dict):
            error_msg = f"Expected dict for attribute_types, got {type(self.attribute_types).__name__}"
            logger.error(f"🧩❌🔄 {error_msg}")
            raise InvalidTypeError(error_msg)

        # Validate all types are CtyType instances
        invalid_types = [
            name for name, vtype in self.attribute_types.items()
            if not isinstance(vtype, CtyType)
        ]
        if invalid_types:
            error_msg = f"Invalid types for attributes: {', '.join(invalid_types)}"
            logger.error(f"🧩❌🔄 {error_msg}")
            raise CtyAttributeValidationError(error_msg)

        # Validate optional attributes exist in the type definition
        unknown_optional = set(self.optional_attributes) - set(self.attribute_types)
        if unknown_optional:
            error_msg = f"Unknown optional attributes: {', '.join(unknown_optional)}"
            logger.error(f"🧩❌🔄 {error_msg}")
            raise CtyAttributeValidationError(error_msg)

        logger.debug(f"🧩✅🔄 CtyObject configuration validated successfully with {len(self.attribute_types)} attributes")

    def validate(self, value: Any) -> CtyValue:
        """
        Validate a value against this object type.

        Args:
            value: Value to validate (dictionary or None)

        Returns:
            CtyValue: The validated object value wrapped in a CtyValue

        Raises:
            CtyValidationError: If the value doesn't match this type
        """
        # CtyValue is already imported at the module level
        # from pyvider.cty.values import CtyValue
        logger.debug(f"🧩🔍🔄 Validating value against CtyObject: {value}")

        from pyvider.cty.values import CtyValue # Make sure this import is available at the top of the file or method

        if isinstance(value, dict) and not value: # Explicitly an empty dictionary
            is_truly_empty_compatible = True
            for attr_name in self.attribute_types: # No need for .items() if only checking names
                if attr_name not in self.optional_attributes:
                    is_truly_empty_compatible = False
                    break

            if is_truly_empty_compatible:
                logger.debug("JULES_OBJECT_VALIDATE: Explicitly handling empty dict {} input for compatible object type, returning NON-NULL empty object.")
                return CtyValue(vtype=self, value={})
            else:
                logger.debug("JULES_OBJECT_VALIDATE: Empty dict {} input for object type with required attrs, proceeding to normal validation which should fail.")
                # Let normal validation proceed by not returning early.
                # The existing logic below will handle raising CtyValidationError for missing required attributes.

        if isinstance(value, CtyValue):
            if isinstance(value.type, CtyObject) and value.type.equal(self):
                logger.debug(f"🧩🔍✅ Input is already a CtyValue of the correct CtyObject type, returning as is.")
                return value
            if value.is_unknown and value.type.usable_as(self):
                logger.debug(f"🧩🔍✅ Propagating unknown CtyValue of a compatible type through object validation.")
                return CtyValue.unknown(self)

            logger.debug(f"🧩🔍🔄 Input is a CtyValue of type {value.type!r}; unwrapping to validate its inner content: {value.value!r}")
            value = value.value # Unwrap to proceed with dict validation for the match statement

        # Handle different input types
        match value:
            case None:
                logger.debug("🧩🔍✅ Received null value, returning null CtyValue")
                return CtyValue.null(self)
            case dict():
                # Continue with dictionary validation
                pass
            case _:
                type_name = type(value).__name__
                error_msg = f"Expected a dictionary, got {type_name}: {value}"
                logger.error(f"🧩🔍❌ {error_msg}")
                raise CtyValidationError(error_msg)

        # Check for required attributes
        required_attrs = self.required_attributes()
        logger.debug(f"🧩🔍🔄 Required attributes: {required_attrs}")

        for name in required_attrs:
            if name not in value:
                error_msg = f"Missing required attribute: {name}"
                logger.error(f"🧩🔍❌ {error_msg}")
                raise CtyValidationError(error_msg)

        # Check for unknown attributes
        unknown_attrs = set(value.keys()) - set(self.attribute_types.keys())
        if unknown_attrs:
            error_msg = f"Unknown attributes: {', '.join(unknown_attrs)}"
            logger.error(f"🧩🔍❌ {error_msg}")
            raise CtyValidationError(error_msg)

        # Validate each attribute
        validated_attrs = {}
        validation_errors = []

        # Process each attribute in attribute_types
        for name, attr_type in self.attribute_types.items():
            logger.debug(f"🧩🔍🔄 Validating attribute {name} with type {attr_type}")

            try:
                # Handle missing attributes (optional ones become null)
                if name not in value:
                    if name in self.optional_attributes:
                        logger.debug(f"🧩🔍✅ Optional attribute {name} is missing, setting to null")
                        validated_attrs[name] = CtyValue.null(attr_type)
                        continue
                    else:
                        # This should never happen due to the required check above
                        error_msg = f"Missing required attribute: {name}"
                        logger.error(f"🧩🔍❌ {error_msg}")
                        raise CtyValidationError(error_msg)

                # Get the attribute value
                attr_value = value[name]

                # Explicitly check for None in required attributes
                if attr_value is None and name not in self.optional_attributes:
                    error_msg = f"Attribute '{name}' is required and cannot be None"
                    logger.error(f"🧩🔍❌ {error_msg}")
                    validation_errors.append(error_msg)
                    continue # Skip further validation for this attribute

                # Handle special cases
                match attr_value:
                    case None if name in self.optional_attributes:
                        # None for optional attribute
                        logger.debug(f"🧩🔍✅ Optional attribute {name} is None, using null CtyValue")
                        validated_attrs[name] = CtyValue.null(attr_type)
                        continue
                    case CtyValue() as cty_value:
                        # Already a CtyValue, check type compatibility
                        logger.debug(f"🧩🔍🔄 Attribute {name} is already a CtyValue, checking type compatibility")
                        if not attr_type.equal(cty_value.type) and not cty_value.type.usable_as(attr_type):
                            error_msg = f"Invalid type for attribute '{name}': expected {attr_type}, got {cty_value.type}"
                            logger.error(f"🧩🔍❌ {error_msg}")
                            validation_errors.append(error_msg)
                            continue
                        
                        # Use the CtyValue directly
                        validated_attrs[name] = cty_value
                        logger.debug(f"🧩🔍✅ Used existing CtyValue for attribute {name}")
                        continue
                    case _:
                        # Regular value, validate it
                        try:
                            validated_value = attr_type.validate(attr_value)
                            validated_attrs[name] = validated_value
                            logger.debug(f"🧩🔍✅ Validated attribute {name}")

                        except CtyValidationError as e:
                            # Add context about which attribute failed
                            # Ensure detail even if str(e) is empty
                            err_detail = str(e) if str(e).strip() else f"(CtyValidationError: {e!r})" 
                            error_msg = f"Invalid value for attribute '{name}': {err_detail}"
                            logger.error(f"🧩🔍❌ {error_msg}")
                            validation_errors.append(error_msg)
                        except Exception as e:
                             # Ensure detail even if str(e) is empty
                            err_detail = str(e) if str(e).strip() else f"({type(e).__name__}: {e!r})"
                            error_msg = f"Error validating attribute '{name}': {err_detail}"
                            logger.error(f"🧩🔍❌ {error_msg}")
                            validation_errors.append(error_msg)

            # Update the outer except block within the loop as well:
            except Exception as e:
                # Ensure detail even if str(e) is empty
                err_detail = str(e) if str(e).strip() else f"({type(e).__name__}: {e!r})" 
                error_msg = f"Unexpected error processing attribute '{name}': {err_detail}"
                logger.error(f"🧩🔍❌ {error_msg}")
                validation_errors.append(error_msg)

        # If we had any validation errors, raise an exception with all the details
        if validation_errors:
            error_msg = "Object validation failed:\n" + "\n".join(validation_errors)
            logger.error(f"🧩🔍❌ {error_msg}")
            raise CtyValidationError(error_msg)

        logger.debug(f"🧩🔍✅ Successfully validated object with {len(validated_attrs)} attributes")
        
        # Return the validated attributes wrapped in a CtyValue
        return CtyValue(vtype=self, value=validated_attrs)

    def get_attribute(self, value: Union[dict[str, Any], CtyValue], name: str) -> CtyValue:
        """
        Get an attribute value by name.

        Args:
            value: Object value to access (dict or CtyValue)
            name: Name of attribute to get

        Returns:
            CtyValue: The attribute value

        Raises:
            CtyAttributeValidationError: If attribute doesn't exist
            CtyValidationError: If value is not a valid object
        """
        logger.debug(f"🧩🔍🔄 Getting attribute {name} from object")

        # First, handle CtyValue input and unwrap it
        if isinstance(value, CtyValue):
            if value.is_null:
                error_msg = "Cannot get attribute from null value"
                logger.error(f"🧩❌🔄 {error_msg}")
                raise CtyAttributeValidationError(error_msg)

            # Key fix: For unknown values, return unknown of attribute type
            if value.is_unknown:
                if name not in self.attribute_types:
                    error_msg = f"Unknown attribute: {name}"
                    logger.error(f"🧩❌🔄 {error_msg}")
                    raise CtyAttributeValidationError(error_msg)

                return CtyValue.unknown(self.attribute_types[name])

            value = value.value

        # Then check if the value is a dictionary
        if not isinstance(value, dict):
            error_msg = f"Expected a dictionary, got {type(value).__name__}: {value}"
            logger.error(f"🧩❌🔄 {error_msg}")
            raise CtyValidationError(error_msg)

        # Check attribute exists in schema
        if name not in self.attribute_types:
            error_msg = f"Unknown attribute: {name}"
            logger.error(f"🧩❌🔄 {error_msg}")
            raise CtyAttributeValidationError(error_msg)

        # Handle optional attributes
        if name not in value and name in self.optional_attributes:
            logger.debug(f"🧩🔍✅ Optional attribute {name} not found, returning null value")
            return CtyValue.null(self.attribute_types[name])

        # Get attribute from dict
        attr_value = value.get(name)

        # Ensure it's a CtyValue
        if not isinstance(attr_value, CtyValue):
            logger.debug(f"🧩🔍✅ Wrapping raw value in CtyValue for {name}")
            attr_value = CtyValue(vtype=self.attribute_types[name], value=attr_value)

        return attr_value

    def required_attributes(self) -> FrozenSet[str]:
        """
        Get the set of required attribute names.

        Returns:
            FrozenSet[str]: Names of all required attributes
        """
        required = frozenset(
            name for name in self.attribute_types
            if name not in self.optional_attributes
        )
        logger.debug(f"🧩🔍🔄 Calculated required attributes: {required}")
        return required

    def has_attribute(self, name: str) -> bool:
        """
        Check if an attribute exists in this object type.

        Args:
            name: Attribute name to check

        Returns:
            bool: True if the attribute exists
        """
        result = name in self.attribute_types
        logger.debug(f"🧩🔍🔄 Checking if attribute {name} exists: {result}")
        return result

    def is_structured_type(self) -> bool:
        """Check if this type is a structured type."""
        return True

    def is_object_type(self) -> bool:
        """Check if this type is an object type."""
        return True

    def equal(self, other: CtyType) -> bool:
        """
        Check if this type equals another type.

        Args:
            other: Another type to compare

        Returns:
            True if the types are equal
        """
        logger.debug(f"🧩🔍🔄 Checking equality with {other.__class__.__name__}")

        # Must be a CtyObject
        if not isinstance(other, CtyObject):
            logger.debug(f"🧩🔍❌ Not equal: {other.__class__.__name__} is not CtyObject")
            return False

        # Must have same attribute names
        if set(self.attribute_types) != set(other.attribute_types):
            logger.debug("🧩🔍❌ Not equal: attribute names differ")
            return False

        # Must have same attribute types
        for name, vtype in self.attribute_types.items():
            other_type = other.attribute_types[name]
            if not vtype.equal(other_type):
                logger.debug(f"🧩🔍❌ Not equal: attribute {name} types differ")
                return False

        # Must have same optional attributes
        if self.optional_attributes != other.optional_attributes:
            logger.debug("🧩🔍❌ Not equal: optional attributes differ")
            return False

        logger.debug("🧩🔍✅ Objects are equal")
        return True

    def usable_as(self, other: CtyType) -> bool:
        """
        Check if this type can be used as another type.

        Args:
            other: Target type to check

        Returns:
            bool: True if usable as the target type
        """
        logger.debug(f"🧩🔍🔄 Checking usability as {other.__class__.__name__}")

        # Must be a CtyObject
        if not isinstance(other, CtyObject):
            logger.debug(f"🧩🔍❌ Not usable as {other.__class__.__name__}")
            return False

        # Other type must not have attributes that we don't have
        other_attrs = set(other.attribute_types)
        self_attrs = set(self.attribute_types)
        missing_attrs = other_attrs - self_attrs
        if missing_attrs:
            logger.debug(f"🧩🔍❌ Not usable: missing attributes {missing_attrs}")
            return False

        # For attributes in both, our type must be usable as other's type
        for name in other_attrs:
            self_type = self.attribute_types[name]
            other_type = other.attribute_types[name]
            if not self_type.usable_as(other_type):
                logger.debug(f"🧩🔍❌ Not usable: attribute {name} type not compatible")
                return False

        # Required attributes: other's required must be subset of ours
        other_required = other.required_attributes()
        self_required = self.required_attributes()
        if not other_required.issubset(self_required):
            extra_required = other_required - self_required
            logger.debug(f"🧩🔍❌ Not usable: other requires attributes we don't: {extra_required}")
            return False

        logger.debug("🧩🔍✅ Object is usable as target type")
        return True

    def __str__(self) -> str:
        """Get string representation of the type."""
        parts = []
        for name, vtype in sorted(self.attribute_types.items()):
            part = f"{name}: {vtype.__class__.__name__}"

            flags = []
            if name in self.optional_attributes:
                flags.append("optional")

            if flags:
                part += f" ({', '.join(flags)})"

            parts.append(part)

        return f"object({{{ ', '.join(parts) }}})"

    def with_attribute(self, name: str, vtype: CtyType, *, optional: bool = False) -> "CtyObject":
        """
        Create a new object type with an additional attribute.

        Args:
            name: Name of the new attribute
            vtype: Type of the new attribute
            optional: Whether the attribute is optional

        Returns:
            CtyObject: New object type with the additional attribute

        Raises:
            CtyAttributeValidationError: If the name already exists
        """
        logger.debug(f"🧩🔧🔄 Creating new object type with attribute: {name} ({vtype.__class__.__name__})")

        # Validate attribute doesn't already exist
        if name in self.attribute_types:
            error_msg = f"Attribute already exists: {name}"
            logger.error(f"🧩🔧❌ {error_msg}")
            raise CtyAttributeValidationError(error_msg)

        # Create new attribute_types dict
        new_attrs = dict(self.attribute_types)
        new_attrs[name] = vtype

        # Update optional attributes if needed
        new_optional = set(self.optional_attributes)
        if optional:
            new_optional.add(name)

        logger.debug(f"🧩🔧✅ Created new object type with attribute: {name}")
        return evolve(
            self,
            attribute_types=new_attrs,
            optional_attributes=frozenset(new_optional)
        )

    def with_optional_attributes(self, *names: str) -> "CtyObject":
        """
        Create a new object type with additional optional attributes.

        Args:
            *names: Names of attributes to mark as optional

        Returns:
            CtyObject: New object type with updated optional attributes

        Raises:
            CtyAttributeValidationError: If any name is not a valid attribute
        """
        logger.debug(f"🧩🔧🔄 Creating new object type with optional attributes: {names}")

        # Validate all names exist in attribute_types
        unknown = set(names) - set(self.attribute_types)
        if unknown:
            error_msg = f"Unknown attributes: {', '.join(unknown)}"
            logger.error(f"🧩🔧❌ {error_msg}")
            raise CtyAttributeValidationError(error_msg)

        # Create new optional set
        new_optional = frozenset(set(self.optional_attributes) | set(names))

        return evolve(
            self,
            attribute_types=self.attribute_types,
            optional_attributes=frozenset(new_optional)
        )

    def with_required_attributes(self, *names: str) -> "CtyObject":
        """
        Create a new object type with additional required attributes.

        Args:
            *names: Names of attributes to mark as required

        Returns:
            CtyObject: New object type with updated required attributes

        Raises:
            CtyAttributeValidationError: If any name is not a valid attribute or already required
        """
        logger.debug(f"🧩🔧🔄 Creating new object type with required attributes: {names}")

        # Validate all names exist in attribute_types and are currently optional
        unknown = set(names) - set(self.attribute_types)
        if unknown:
            error_msg = f"Unknown attributes: {', '.join(unknown)}"
            logger.error(f"🧩🔧❌ {error_msg}")
            raise CtyAttributeValidationError(error_msg)

        not_optional = set(names) - set(self.optional_attributes)
        if not_optional:
            error_msg = f"Attributes already required: {', '.join(not_optional)}"
            logger.error(f"🧩🔧❌ {error_msg}")
            raise CtyAttributeValidationError(error_msg)

        # Create new optional set
        new_optional = frozenset(set(self.optional_attributes) - set(names))

        logger.debug(f"🧩🔧✅ Created new object type with required attributes: {names}")
        return evolve(
            self,
            attribute_types=self.attribute_types,
            optional_attributes=frozenset(new_optional)
        )

    def __iter__(self):
        """Enable iteration over attribute names."""
        return iter(self.attribute_types.keys())

    def __len__(self):
        """Return number of attributes."""
        return len(self.attribute_types)

# 🐍🏗️🐣
