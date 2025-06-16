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

from attrs import define, field

from pyvider.cty.exceptions import CtyStringValidationError
from pyvider.cty.types.base import CtyType
from pyvider.telemetry import logger

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
        from pyvider.cty.types.structural import CtyDynamic
        logger.debug(f"🔤🔍🔄 ENTER CtyString.validate with value type: {type(value)}, value: {value!r}")

        if isinstance(value, CtyValue):
            logger.debug(f"🔤🔍 CtyString.validate received CtyValue. value.type is {value.type!r} (class: {value.type.__class__.__name__})")

            is_type_string = isinstance(value.type, CtyString)
            logger.debug(f"🔤🔍 Condition: isinstance(value.type, CtyString) is {is_type_string}")
            if is_type_string:
                logger.debug("🔤🔍✅ Path 1: Value is CtyValue(CtyString)")
                return value

            is_type_dynamic = isinstance(value.type, CtyDynamic)
            logger.debug(f"🔤🔍 Condition: isinstance(value.type, CtyDynamic) is {is_type_dynamic}")
            if is_type_dynamic:
                logger.debug(f"🔤🔍 Path 2: Handling CtyDynamic. Unknown: {value.is_unknown}, Null: {value.is_null}")
                if value.is_unknown:
                    logger.debug("🔤🔍✅ CtyDynamic input is unknown, returning unknown CtyString")
                    return CtyValue.unknown(self)
                if value.is_null:
                    logger.debug("🔤🔍✅ CtyDynamic input is null, returning CtyString('')")
                    return CtyValue(vtype=self, value="")
                try:
                    str_val = str(value.value)
                    logger.debug(f"🔤🔍✅ Converted CtyDynamic's inner value ({value.value!r}) to string: {str_val!r}")
                    return CtyValue(vtype=self, value=str_val)
                except Exception as e:
                    error_msg = f"Failed to convert CtyDynamic's inner value ({value.value!r}) to string: {e}"
                    logger.error(f"🔤❗❌ {error_msg}")
                    raise CtyStringValidationError(error_msg) from e
            else: # Path 3: CtyValue of other type (e.g. CtyNumber)
                error_msg = f"Value is a CtyValue of type {value.type.__class__.__name__}, which cannot be automatically converted to CtyString. Expected CtyString or CtyDynamic."
                logger.error(f"🔤❗❌ Path 3 RAISING ERROR: {error_msg}")
                raise CtyStringValidationError(error_msg)

        # Path 4: Raw Python types
        logger.debug(f"🔤🔍 Path 4: Handling as raw Python type: {value!r}")
        if value is None:
            error_msg = "String value cannot be None."
            logger.error(f"🔤❗❌ {error_msg}")
            raise CtyStringValidationError(error_msg)

        if isinstance(value, str):
            logger.debug("🔤🔍✅ Value is a raw string")
            return CtyValue(vtype=self, value=value)

        # Path 5: Other raw types (int, bool etc.)
        error_msg = f"Value must be a string, got {type(value).__name__}"
        logger.error(f"🔤❗❌ RAISING ERROR (raw type path): {error_msg}")
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

        A string type is usable as another string type or as CtyDynamic.
        This method is used for type compatibility checking.

        Args:
            other: The target type to check compatibility with.

        Returns:
            bool: True if this type can be used as the other type, False otherwise.
        """
        from pyvider.cty.types.structural import CtyDynamic  # Import locally
        if isinstance(other, CtyDynamic):
            logger.debug("🔤🔍✅ CtyString.usable_as(CtyDynamic): True")
            return True
        result = isinstance(other, CtyString)
        logger.debug(f"🔤🔍✅ CtyString.usable_as({other.__class__.__name__}): {result}") # Use other.__class__.__name__ for safety
        return result

    def __str__(self) -> str:
        return "string"

    def is_primitive_type(self) -> bool:
        """Check if this type is a primitive type."""
        return True

# 🐍🏗️🐣
