#
# pyvider/cty/types/primitives/number.py
#

from decimal import Decimal, InvalidOperation

from typing import Any, ClassVar, Union

from attrs import define, evolve, field

from pyvider.cty.exceptions import ValidationError
from pyvider.cty.logger import logger

from pyvider.cty.types.base import CtyType

@define(frozen=True, slots=True)
class CtyNumber(CtyType[Union[int, float, Decimal]]):
    """
    CtyNumber represents a number type in the Cty type system.

    Numbers can be integers, floats, or Decimal objects.
    This matches the Go-CTY number semantics.
    """
    ctype: ClassVar[str] = "number"
    value: Union[int, Decimal] = field(default=0)

    def validate(self, value: Any) -> "CtyValue":
        """
        Validate that the given value is a number. Stricter validation.
        """
        logger.debug(f"🔢🔍🔄 Validating value as number: {value!r}")

        # Import locally to avoid circular imports
        from pyvider.cty.values import CtyValue

        # Handle CtyValue inputs
        if isinstance(value, CtyValue):
            if isinstance(value.type, CtyNumber):
                logger.debug(f"🔢🔍✅ Value is already a CtyValue with CtyNumber type")
                return value
            # --- Allow conversion from known, non-null CtyValue if numeric/string ---
            if value.is_known and not value.is_null:
                 inner_val = value.value
                 if isinstance(inner_val, (int, float, Decimal)):
                      logger.debug(f"🔢🔍✅ Inner value is already numeric: {inner_val!r}")
                      return CtyValue(type_=self, value=inner_val)
                 elif isinstance(inner_val, str):
                     try:
                         num_val = Decimal(inner_val)
                         logger.debug(f"🔢🔍✅ Converted inner string to Decimal: {num_val}")
                         return CtyValue(type_=self, value=num_val)
                     except (InvalidOperation, ValueError):
                         error_msg = f"String value '{inner_val}' inside CtyValue is not a valid number"
                         logger.error(f"🔢❗❌ {error_msg}")
                         raise ValidationError(error_msg)
                 # else: fall through to raise error for other inner types
            # --- End CtyValue Handling ---


        # Handle None as 0 (consistent with go-cty)
        if value is None:
            logger.debug("🔢🔍✅ None value converted to 0")
            return CtyValue(type_=self, value=Decimal(0)) # Use Decimal for consistency

        # Accept numeric types: int, float, Decimal
        if isinstance(value, (int, float, Decimal)):
            # Convert int/float to Decimal for internal consistency
            try:
                 decimal_val = Decimal(value)
                 logger.debug(f"🔢🔍✅ Value is valid number type: {type(value).__name__}, stored as Decimal: {decimal_val}")
                 return CtyValue(type_=self, value=decimal_val)
            except Exception as e: # Catch potential issues converting float inf/nan
                 error_msg = f"Cannot represent {type(value).__name__} value {value!r} as Decimal: {e}"
                 logger.error(f"🔢❗❌ {error_msg}")
                 raise ValidationError(error_msg)


        # Try to convert strings that look like numbers
        if isinstance(value, str):
            try:
                # Try to convert to a Decimal first for precision
                decimal_val = Decimal(value)
                logger.debug(f"🔢🔍✅ String converted to Decimal: {decimal_val}")
                return CtyValue(type_=self, value=decimal_val)
            except (InvalidOperation, ValueError): # Catch specific Decimal errors
                error_msg = f"Cannot convert string '{value}' to number"
                logger.debug(f"🔢❗❌ {error_msg}")
                raise ValidationError(error_msg)

        # --- REJECT ALL OTHER TYPES ---
        error_msg = f"Value must be a number or a string representation of a number, got {type(value).__name__}"
        logger.error(f"🔢❗❌ {error_msg}")
        raise ValidationError(error_msg)

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
        return isinstance(other, CtyNumber)

    def __repr__(self):
        """
        Get a detailed string representation of this number.

        Returns:
            A detailed string representation
        """
        return f"{self.__class__.__name__}()"

    def __hash__(self):
        """
        Get a hash value for this number.

        Returns:
            A hash value
        """
        return hash((self.__class__,))

    def __str__(self):
        """
        Get a string representation of this number type.

        Returns:
            A string representation
        """
        return "number"


# 🐍🏗️🐣
