#
# pyvider/cty/types/primitives/string.py
#

"""
String type implementation for the Cty type system.

This module provides the CtyString type, representing Unicode string values in the
Cty type system. Strings are immutable sequences of Unicode characters that can be
validated, compared, and manipulated. The string type serves as a foundation for
many operations, including serving as map keys and containing textual data.

This implementation follows the go-cty string semantics, ensuring type safety and
consistent behavior across the Cty ecosystem.
"""

from typing import Any, ClassVar, TypeVar

from attrs import define, evolve, field

from pyvider.cty.exceptions import CtyStringValidationError
from pyvider.telemetry import logger
from pyvider.cty.types.base import CtyType

T = TypeVar('T', bound=str)

@define(frozen=True, slots=True)
class CtyString(CtyType[str]):
    """
    Represents a string type in the Cty type system.

    CtyString handles validation, conversion, and type compatibility checking
    for string values. It ensures that any value assigned to it is a valid string
    or can be converted to one. None values are converted to empty strings.

    Attributes:
        ctype (ClassVar[str]): Type identifier constant, always "string".
        value (str): Default value for new instances, defaults to empty string.
            This attribute is primarily used when creating strings directly.

    Examples:
        Creating a string type:
        >>> string_type = CtyString()

        Validating a value:
        >>> value = string_type.validate("hello")
        >>> print(value.value)
        'hello'

        Converting None to empty string:
        >>> null_value = string_type.validate(None)
        >>> print(null_value.value)
        ''
    """
    ctype: ClassVar[str] = "string"
    value: str = field(default="")

    def validate(self, value: Any) -> "CtyValue":
        """
        Validate that the given value is a string or can be converted to one.

        This method performs strict validation to ensure the value conforms to
        the string type requirements. If the value is already a CtyValue with a
        CtyString type, it is returned as-is. If it's a known, non-null CtyValue
        of another type, it will be converted to a string if possible.

        Args:
            value: The value to validate as a string. Can be a raw string, None,
                or a CtyValue instance.

        Returns:
            CtyValue: A CtyValue instance containing the validated string value.

        Raises:
            CtyStringValidationError: If the value cannot be converted to a string.
        """
        # Import locally to avoid circular imports
        from pyvider.cty.values import CtyValue
        logger.debug(f"🔤🔍🔄 Validating value as string: {value!r}")

        # Handle CtyValue input
        if isinstance(value, CtyValue):
            if isinstance(value.type, CtyString):
                logger.debug("🔤🔍✅ Value is already a CtyValue with CtyString type")
                return value
            # If it's a CtyValue of another type, it's a type mismatch for string validation.
            # String conversion should be explicit via other mechanisms if needed, not implicit in validate.
            # unless it's dynamic.
            from pyvider.cty.types.structural import CtyDynamic
            if not isinstance(value.type, CtyDynamic): # Allow CtyDynamic to be validated as string by converting its value
                error_msg = f"Value is a CtyValue of type {value.type.__class__.__name__}, not CtyString or CtyDynamic"
                logger.error(f"🔤❗❌ {error_msg}")
                raise CtyStringValidationError(error_msg)

            # If it's CtyDynamic, proceed to validate its inner value as a string
            if not value._is_unknown and not value._is_null:
                try:
                    # Convert inner value of CtyDynamic to string
                    str_val = str(value.value)
                    logger.debug(f"🔤🔍✅ Converted CtyDynamic's inner value to string: {str_val!r}")
                    return CtyValue(vtype=self, value=str_val)
                except Exception as e:
                    error_msg = f"Failed to convert CtyDynamic's inner value to string: {e}"
                    logger.error(f"🔤❗❌ {error_msg}")
                    raise CtyStringValidationError(error_msg) from e
            elif value._is_unknown: # Propagate unknown
                 return CtyValue.unknown(self)
            elif value._is_null: # Convert null dynamic to empty string CtyValue
                 return CtyValue(vtype=self, value="")


        # Handle None as empty string (consistent with go-cty)
        if value is None:
            logger.debug("🔤🔍✅ None value converted to empty string")
            return CtyValue(vtype=self, value="")

        # Handle direct string
        if isinstance(value, str):
            logger.debug("🔤🔍✅ Value is a string")
            return CtyValue(vtype=self, value=value)

        # --- REJECT ALL OTHER TYPES ---
        error_msg = f"Value must be a string, got {type(value).__name__}"
        logger.error(f"🔤❗❌ {error_msg}")
        raise CtyStringValidationError(error_msg)

    def equal(self, other: CtyType[Any]) -> bool:
        """
        Check if this string type is equal to another type.

        Two string types are considered equal if they are both instances of
        CtyString. This implements the type equality semantics for the Cty
        type system.

        Args:
            other: The type to compare with this string type.

        Returns:
            bool: True if the other type is also a CtyString, False otherwise.
        """
        result = isinstance(other, CtyString)
        logger.debug(f"🔤🔍✅ CtyString.equal: {result}")
        return result

    def usable_as(self, other: CtyType[Any]) -> bool:
        """
        Check if this string type can be used where the other type is expected.

        A string type is only usable as another string type. This method is used
        for type compatibility checking when values are passed between contexts
        with different type expectations.

        Args:
            other: The target type to check compatibility with.

        Returns:
            bool: True if this type can be used as the other type, False otherwise.
        """
        result = isinstance(other, CtyString)
        logger.debug(f"🔤🔍✅ CtyString.usable_as: {result}")
        return result

    def __str__(self):
        return "string"

# 🐍🏗️🐣
