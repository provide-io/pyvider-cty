from decimal import Decimal, InvalidOperation
from typing import ClassVar  # Added TYPE_CHECKING, Union removed

from attrs import define, field

from pyvider.cty.exceptions import CtyNumberValidationError
from pyvider.cty.types.base import CtyType
from pyvider.cty.types.structural import CtyDynamic
from pyvider.cty.values import CtyValue
from pyvider.telemetry import logger

#
# pyvider/cty/types/primitives/number.py
#

"""Numeric type implementation for the Cty type system."""


@define(frozen=True, slots=True)
class CtyNumber(CtyType[int | float | Decimal]):
    """
    Represents a numeric type in the Cty type system.

    CtyNumber handles arbitrary-precision numbers using Python's Decimal type
    internally. It validates and converts various numeric inputs (integers,
    floats, Decimals, and numeric strings) into a standard Decimal representation.

    This type ensures that all numeric operations within the Cty system are
    performed with consistent precision and behavior, avoiding common pitfalls
    of floating-point arithmetic.

    Attributes:
        ctype (ClassVar[str]): Type identifier constant, always "number"
        value (int | Decimal): The numeric value (default: 0)
    """

    ctype: ClassVar[str] = "number"
    value: int | Decimal = field(default=0)

    def validate(self, value: object) -> CtyValue:  # Ensured string literal
        """
        Validate that the given value is a number or can be converted to one.

        Accepts integers, floats, Decimals, and numeric strings. Converts valid
        inputs to Decimal to maintain precision. Non-numeric types or strings
        that cannot be parsed as numbers will raise a validation error.

        Args:
            value: The value to validate

        Returns:
            CtyValue: A CtyValue instance with the validated Decimal value

        Raises:
            CtyNumberValidationError: If value cannot be validated as a number
        """
        logger.debug(f"🔢✅🔄 Validating value as CtyNumber: {type(value).__name__}")

        # Import locally to avoid circular imports
        from pyvider.cty.values import CtyValue

        # --- NULL / UNKNOWN ---
        if value is None:
            return CtyValue.null(self)
        if isinstance(value, CtyValue):
            if value.is_null:
                return CtyValue.null(self)
            if value.is_unknown:
                return CtyValue.unknown(self)

            # --- COMPATIBLE CTYVALUE ---
            # If it's already a number or dynamic type, try to use its value
            if isinstance(value.type, (CtyNumber, CtyDynamic)):
                # Re-validate inner value to ensure it's a valid Decimal representation
                # This handles cases like CtyValue(CtyDynamic, "123") -> CtyValue(CtyNumber, Decimal("123"))
                value = value.value  # Unbox
            elif isinstance(value.type, CtyType) and value.type.is_primitive_type():
                # Allow conversion from other primitive CtyValues if their value is numeric string
                # e.g. CtyValue(CtyString, "123.45")
                if isinstance(value.value, str):
                    try:
                        decimal_value = Decimal(value.value)
                        return CtyValue(vtype=self, value=decimal_value)
                    except InvalidOperation:
                        error_msg = f"String value '{value.value}' inside CtyValue is not a valid number"
                        logger.error(f"🔢❗❌ {error_msg}")
                        raise CtyNumberValidationError(error_msg)
                # else: fall through to raise error for other inner types
            # --- End CtyValue Handling ---

        # --- PYTHON PRIMITIVES ---
        if isinstance(value, (int, float, Decimal)):
            try:
                decimal_value = Decimal(value)
                logger.debug(f"🔢✅🔄 Converted to Decimal: {decimal_value}")
                return CtyValue(vtype=self, value=decimal_value)
            except (InvalidOperation, TypeError, ValueError) as e:
                error_msg = f"Cannot represent {type(value).__name__} value {value!r} as Decimal: {e}"
                logger.error(f"🔢❗❌ {error_msg}")
                raise CtyNumberValidationError(error_msg)

        # Try to convert strings that look like numbers
        if isinstance(value, str):
            try:
                decimal_value = Decimal(value)
                logger.debug(
                    f"🔢✅🔄 Converted string '{value}' to Decimal: {decimal_value}"
                )
                return CtyValue(vtype=self, value=decimal_value)
            except InvalidOperation:
                error_msg = f"Cannot convert string '{value}' to number"
                logger.debug(f"🔢❗❌ {error_msg}")
                raise CtyNumberValidationError(error_msg)

        # --- REJECT ALL OTHER TYPES ---
        error_msg = f"Cannot convert {type(value).__name__} to number"
        logger.error(f"🔢❗❌ {error_msg}")
        raise CtyNumberValidationError(error_msg)

    def equal(self, other: CtyType[int | float | Decimal]) -> bool:
        """Check if this type is equal to another number type."""
        result = isinstance(other, CtyNumber)
        logger.debug("🔢✅🔄 CtyNumber.equal: %s to %s -> %s", self, other, result)
        return result

    def usable_as(self, other: CtyType[int | float | Decimal]) -> bool:
        """Check if this number type can be used as another type."""
        # A number can be used as dynamic or another number.
        result = isinstance(other, (CtyNumber, CtyDynamic))
        logger.debug("🔢✅🔄 CtyNumber.usable_as: %s to %s -> %s", self, other, result)
        return result

    def __str__(self) -> str:
        return "number"

    def is_primitive_type(self) -> bool:
        return True


# 🐍🏗️🐣
