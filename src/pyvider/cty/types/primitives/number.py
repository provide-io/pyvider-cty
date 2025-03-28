# pyvider/cty/types/primitives/number.py

from decimal import Decimal
from typing import Any, ClassVar, Union

from attrs import define, evolve, field

from pyvider.cty.exceptions import ValidationError
from pyvider.cty.logger import logger

from ..base import CtyType


@define(frozen=True, slots=True)
class CtyNumber(CtyType[Union[int, float, Decimal]]):
    """
    CtyNumber represents a number type in the Cty type system.

    Numbers can be integers, floats, or Decimal objects.
    This matches the Go-CTY number semantics.
    """
    ctype: ClassVar[str] = "number"
    value: Union[int, Decimal] = field(default=0)

    def validate(self, value: Any) -> "CtyNumber":
        """
        Validate that the given value is a number.

        Args:
            value: The value to validate

        Returns:
            A new CtyNumber with the validated value

        Raises:
            ValidationError: If the value is not a number
        """
        logger.debug(f"🔢🔍🔄 Validating value as number: {value}")

        # Handle None as 0
        if value is None:
            logger.debug("🔢🔍✅ None value converted to 0")
            return evolve(self, value=0)

        # Accept numeric types: int, float, Decimal
        if isinstance(value, (int, float, Decimal)):
            logger.debug(f"🔢🔍✅ Value is valid number type: {type(value).__name__}")
            return evolve(self, value=value)

        # Try to convert strings that look like numbers
        if isinstance(value, str):
            try:
                # Try to convert to a Decimal first for precision
                decimal_val = Decimal(value)
                logger.debug(f"🔢🔍✅ String converted to Decimal: {decimal_val}")
                return evolve(self, value=decimal_val)
            except (ValueError, ArithmeticError):
                pass

        # If we get here, the value is not a valid number
        logger.debug(f"🔢❗❌ Value must be a number, got {type(value).__name__}")
        raise ValidationError(f"Value must be a number.")

    def equal(self, other: "CtyType") -> bool:
        """
        Check if this type is equal to another type.

        Args:
            other: The other type to check against

        Returns:
            True if the types are equal
        """
        result = isinstance(other, CtyNumber)
        logger.debug(f"🔢🔍✅ CtyNumber.equal: {result}")
        return result

    def usable_as(self, other: "CtyType") -> bool:
        """
        Check if this type can be used as another type.

        Args:
            other: The other type to check against

        Returns:
            True if this type can be used as the other type
        """
        result = isinstance(other, CtyNumber)
        logger.debug(f"🔢🔍✅ CtyNumber.usable_as: {result}")
        return result

    def __eq__(self, other):
        """
        Check if this number is equal to another number.

        Args:
            other: The other number to check against

        Returns:
            True if the numbers are equal
        """
        if not isinstance(other, CtyNumber):
            return False

        # Compare values, being careful with different numeric types
        if isinstance(self.value, Decimal) or isinstance(other.value, Decimal):
            # Convert to Decimal for exact comparison
            try:
                self_decimal = Decimal(str(self.value)) if not isinstance(self.value, Decimal) else self.value
                other_decimal = Decimal(str(other.value)) if not isinstance(other.value, Decimal) else other.value
                return self_decimal == other_decimal
            except (ValueError, ArithmeticError):
                return False

        # Regular comparison for int/float
        return self.value == other.value

    def __lt__(self, other):
        """
        Check if this number is less than another number.

        Args:
            other: The other number to compare with

        Returns:
            True if this number is less than the other number
        """
        if not isinstance(other, CtyNumber):
            return NotImplemented

        # Handle Decimal comparisons
        if isinstance(self.value, Decimal) or isinstance(other.value, Decimal):
            try:
                self_decimal = Decimal(str(self.value)) if not isinstance(self.value, Decimal) else self.value
                other_decimal = Decimal(str(other.value)) if not isinstance(other.value, Decimal) else other.value
                return self_decimal < other_decimal
            except (ValueError, ArithmeticError):
                return NotImplemented

        return self.value < other.value

    def __gt__(self, other):
        """
        Check if this number is greater than another number.

        Args:
            other: The other number to compare with

        Returns:
            True if this number is greater than the other number
        """
        if not isinstance(other, CtyNumber):
            return NotImplemented

        # Handle Decimal comparisons
        if isinstance(self.value, Decimal) or isinstance(other.value, Decimal):
            try:
                self_decimal = Decimal(str(self.value)) if not isinstance(self.value, Decimal) else self.value
                other_decimal = Decimal(str(other.value)) if not isinstance(other.value, Decimal) else other.value
                return self_decimal > other_decimal
            except (ValueError, ArithmeticError):
                return NotImplemented

        return self.value > other.value

    def __repr__(self):
        """
        Get a detailed string representation of this number.

        Returns:
            A detailed string representation
        """
        return f"{self.__class__.__name__}(value={self.value!r})"

    def __hash__(self):
        """
        Get a hash value for this number.

        Returns:
            A hash value
        """
        return hash((self.__class__, self.value))

    def __str__(self):
        """
        Get a string representation of this number type.

        Returns:
            A string representation
        """
        return "number"
