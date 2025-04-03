#
# pyvider/cty/types/primitives/bool.py
#

"""
Boolean type implementation for the Cty type system.

This module provides CtyBool, representing Boolean values in the Cty type system.
It handles validation, conversion from various input types to boolean values,
and implements type compatibility checking with strong validation guarantees.
"""

from typing import Any, ClassVar

from attrs import define, field

from pyvider.cty.exceptions import CtyBoolValidationError
from pyvider.cty.logger import logger
from pyvider.cty.types.base import CtyType

@define(frozen=True, slots=True)
class CtyBool(CtyType[bool]):
    """
    Boolean type representation in the Cty type system.

    Represents boolean (True/False) values with validation and type checking.
    Boolean values are immutable and support standard logical operations.
    CtyBool can convert various input types to boolean values according to
    specific conversion rules that match go-cty's semantics.

    Attributes:
        ctype: Class variable identifying this as a boolean type
        value: The default value for this type (False)
    """
    ctype: ClassVar[str] = "bool"
    value: bool = field(default=False)

    def validate(self, value: Any) -> "CtyValue":
        """
        Validate and convert a value to a boolean CtyValue.

        Performs type checking and conversion of various input types to boolean.
        Handles special cases like string representations ('true', 'false', etc.)
        and numeric values (0 = False, non-0 = True).

        Args:
            value: Value to validate and convert to boolean

        Returns:
            CtyValue with validated boolean value

        Raises:
            CtyBoolValidationError: If the value cannot be converted to boolean
        """
        # Import locally to avoid circular imports
        from pyvider.cty.values import CtyValue
        logger.debug(f"🔄🔍🔄 Validating value as boolean: {value!r}")

        # Handle CtyValue inputs
        if isinstance(value, CtyValue):
            if isinstance(value.type, CtyBool):
                logger.debug(f"🔄🔍✅ Value is already a CtyValue with CtyBool type")
                return value
            # --- Allow conversion from known, non-null CtyValue ---
            if value._is_unknown and not value._is_null:
                 inner_val = value.value
                 # Try direct bool
                 if isinstance(inner_val, bool):
                     return CtyValue(type_=self, value=inner_val)
                 # Try string conversion
                 if isinstance(inner_val, str):
                     if inner_val.lower() in ('true', 't', 'yes', 'y', '1'):
                         return CtyValue(type_=self, value=True)
                     elif inner_val.lower() in ('false', 'f', 'no', 'n', '0'):
                         return CtyValue(type_=self, value=False)
                 # Try numeric conversion
                 if isinstance(inner_val, (int, float)):
                     return CtyValue(type_=self, value=bool(inner_val))
                 # else: fall through to raise error for other inner types
            # --- End CtyValue Handling ---

        # Handle direct boolean
        if isinstance(value, bool):
            logger.debug(f"🔄🔍✅ Value is a boolean: {value}")
            return CtyValue(type_=self, value=value)

        # Handle specific string representations
        if isinstance(value, str):
            low_val = value.lower()
            if low_val in ('true', 't', 'yes', 'y', '1'):
                logger.debug(f"🔄🔍✅ String '{value}' converted to True")
                return CtyValue(type_=self, value=True)
            elif low_val in ('false', 'f', 'no', 'n', '0'):
                logger.debug(f"🔄🔍✅ String '{value}' converted to False")
                return CtyValue(type_=self, value=False)
            # else: fall through to raise error for other strings

        # Handle numbers (0 = False, non-0 = True)
        if isinstance(value, (int, float)):
            # Note: float conversion might be unexpected, but aligns with Python bool()
            bool_val = bool(value)
            logger.debug(f"🔄🔍✅ Number {value} converted to boolean: {bool_val}")
            return CtyValue(type_=self, value=bool_val)

        if isinstance(value, (int, float)):
            error_msg = f"Cannot convert number {value} to boolean"
            logger.error(f"🔄❗❌ {error_msg}")
            raise CtyBoolValidationError(error_msg)



        # --- REJECT ALL OTHER TYPES ---
        error_msg = f"Value must be a boolean or a specific convertible string/number, got {type(value).__name__}"
        logger.error(f"🔄❗❌ {error_msg}")
        raise CtyBoolValidationError(error_msg)

    def equal(self, other: "CtyType[bool]") -> bool:
        """
        Check if this type is equal to another type.

        For boolean types, equality means the other type is also a CtyBool.
        This implements type identity checking for the type system.

        Args:
            other: The type to compare with

        Returns:
            True if the other type is a CtyBool, False otherwise
        """
        result = isinstance(other, CtyBool)
        logger.debug(f"🔄🔍✅ CtyBool.equal: {result}")
        return result

    def usable_as(self, other: "CtyType[bool]") -> bool:
        """
        Check if this type can be used in place of another type.

        For boolean types, usability means the other type is also a CtyBool.
        This implements type compatibility checking for the type system.

        Args:
            other: The target type to check compatibility with

        Returns:
            True if this type can be used as the target type, False otherwise
        """
        result = isinstance(other, CtyBool)
        logger.debug(f"🔄🔍✅ CtyBool.usable_as: {result}")
        return result

    def __eq__(self, other):
        """
        Equality operator for direct comparison.

        Compares this boolean type with another object for equality.

        Args:
            other: Object to compare with

        Returns:
            True if other is a CtyBool, False otherwise
        """
        return isinstance(other, CtyBool)

    def __repr__(self):
        """
        Get a detailed string representation of this boolean type.

        Returns:
            A string representation for debugging purposes
        """
        return f"{self.__class__.__name__}()"

    def __hash__(self):
        """
        Get a hash value for this boolean type.

        Makes CtyBool instances usable as dictionary keys and in sets.

        Returns:
            A hash value based on the class identity
        """
        return hash(self.__class__)

# 🐍🏗️🐣
