#
# pyvider/cty/types/primitives/number.py
#

"""
Number type implementation for the Cty type system.

This module provides the CtyNumber type, representing numeric values in the Cty type system.
It handles validation and conversion of various numeric formats (int, float, Decimal) with
consistent precision handling. The implementation follows go-cty's number semantics,
using Decimal internally for precision and supporting conversion from various input types.
"""

from decimal import Decimal, InvalidOperation
from typing import Any, ClassVar

from attrs import define, field

from pyvider.cty.exceptions import CtyNumberValidationError
from pyvider.cty.types.base import CtyType
from pyvider.telemetry import logger


@define(frozen=True, slots=True)
class CtyNumber(CtyType[int | float, Decimal]):
    """
    Represents a numeric type in the Cty type system.

    CtyNumber handles validation and conversion of various numeric inputs including
    integers, floats, and Decimal objects. It ensures precise representation by using
    Decimal internally to avoid floating-point errors. This implementation matches
    go-cty's number semantics.

    The number type supports standard arithmetic operations with proper precision
    handling and can convert string representations of numbers when appropriate.

    Attributes:
        ctype (ClassVar[str]): Type identifier constant, always "number".
        value (int | Decimal): Default value for new instances, defaults to 0.
            This attribute is primarily used when creating numbers directly.

    Examples:
        Creating a number type:
        >>> number_type = CtyNumber()

        Validating integer values:
        >>> value = number_type.validate(42)
        >>> print(value.value)
        42

        Validating decimal values:
        >>> from decimal import Decimal
        >>> value = number_type.validate(Decimal("3.14159265359"))
        >>> print(value.value)
        3.14159265359
    """
    ctype: ClassVar[str] = "number"
    value: int | Decimal = field(default=0)

    def validate(self, value: Any) -> "CtyValue":
        """
        Validate that the given value is a number or can be converted to one.

        This method performs strict validation to ensure the value conforms to
        the number type requirements. It accepts integers, floats, Decimal objects,
        and strings that can be parsed as numbers. None values are converted to 0.

        For precision, numeric values are stored as Decimal objects internally.
        String values are converted to Decimal if they represent valid numbers.

        Args:
            value: The value to validate as a number. Can be an int, float, Decimal,
                string representation of a number, None, or a CtyValue instance.

        Returns:
            CtyValue: A CtyValue instance containing the validated number value.

        Raises:
            CtyNumberValidationError: If the value cannot be converted to a number.
        """
        logger.debug(f"🔢🔍🔄 Validating value as number: {value!r}")

        # Import locally to avoid circular imports
        from pyvider.cty.values import CtyValue

        # Handle CtyValue inputs
        if isinstance(value, CtyValue):
            if isinstance(value.type, CtyNumber):
                logger.debug("🔢🔍✅ Value is already a CtyValue with CtyNumber type")
                return value
            # --- Allow conversion from known, non-null CtyValue if numeric/string ---
            if not value._is_unknown and not value._is_null:
                 inner_val = value.value
                 if isinstance(inner_val, int | float | Decimal):
                      logger.debug(f"🔢🔍✅ Inner value is already numeric: {inner_val!r}")
                      return CtyValue(vtype=self, value=inner_val)
                 elif isinstance(inner_val, str):
                     try:
                         num_val = Decimal(inner_val)
                         logger.debug(f"🔢🔍✅ Converted inner string to Decimal: {num_val}")
                         return CtyValue(vtype=self, value=num_val)
                     except (InvalidOperation, ValueError):
                         error_msg = f"String value '{inner_val}' inside CtyValue is not a valid number"
                         logger.error(f"🔢❗❌ {error_msg}")
                         raise CtyNumberValidationError(error_msg)
                 # else: fall through to raise error for other inner types
            # --- End CtyValue Handling ---


        # Handle None as 0 (consistent with go-cty)
        if value is None:
            logger.debug("🔢🔍✅ None value converted to 0")
            return CtyValue(vtype=self, value=Decimal(0)) # Use Decimal for consistency

        # Accept numeric types: int, float, Decimal
        if isinstance(value, int | float | Decimal):
            # Convert int/float to Decimal for internal consistency
            try:
                 decimal_val = Decimal(value)
                 logger.debug(f"🔢🔍✅ Value is valid number type: {type(value).__name__}, stored as Decimal: {decimal_val}")
                 return CtyValue(vtype=self, value=decimal_val)
            except Exception as e: # Catch potential issues converting float inf/nan
                 error_msg = f"Cannot represent {type(value).__name__} value {value!r} as Decimal: {e}"
                 logger.error(f"🔢❗❌ {error_msg}")
                 raise CtyNumberValidationError(error_msg)


        # Try to convert strings that look like numbers
        if isinstance(value, str):
            try:
                # Try to convert to a Decimal first for precision
                decimal_val = Decimal(value)
                logger.debug(f"🔢🔍✅ String converted to Decimal: {decimal_val}")
                return CtyValue(vtype=self, value=decimal_val)
            except (InvalidOperation, ValueError): # Catch specific Decimal errors
                error_msg = f"Cannot convert string '{value}' to number"
                logger.debug(f"🔢❗❌ {error_msg}")
                raise CtyNumberValidationError(error_msg)

        # --- REJECT ALL OTHER TYPES ---
        error_msg = f"Value must be a number or a string representation of a number, got {type(value).__name__}"
        logger.error(f"🔢❗❌ {error_msg}")
        raise CtyNumberValidationError(error_msg)

    def equal(self, other: "CtyType") -> bool:
        """
        Check if this type is equal to another type.

        Two number types are considered equal if they are both instances of
        CtyNumber. This implements the type equality semantics for the Cty
        type system.

        Args:
            other: The type to compare with this number type.

        Returns:
            bool: True if the other type is also a CtyNumber, False otherwise.
        """
        result = isinstance(other, CtyNumber)
        logger.debug(f"🔢🔍✅ CtyNumber.equal: {result}")
        return result

    def usable_as(self, other: "CtyType") -> bool:
        """
        Check if this type can be used where the other type is expected.

        A number type is only usable as another number type. This method is used
        for type compatibility checking when values are passed between contexts
        with different type expectations.

        Args:
            other: The target type to check compatibility with.

        Returns:
            bool: True if this type can be used as the other type, False otherwise.
        """
        result = isinstance(other, CtyNumber)
        logger.debug(f"🔢🔍✅ CtyNumber.usable_as({other.__class__.__name__}): {result}")
        return result

    def __str__(self) -> str:
        return "number"

    def is_primitive_type(self) -> bool:
        """Check if this type is a primitive type."""
        return True

# 🐍🏗️🐣
