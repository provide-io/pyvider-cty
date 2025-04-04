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
from pyvider.cty.logger import logger
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
            # --- Allow conversion from known, non-null CtyValue using str() ---
            # --- This is a common pattern, but be mindful if it causes issues ---
            if not value._is_unknown and not value._is_null:
                 try:
                     str_val = str(value.value)
                     logger.debug(f"🔤🔍✅ Converted known CtyValue's inner value to string: {str_val!r}")
                     return CtyValue(vtype=self, value=str_val)
                 except Exception as e:
                     error_msg = f"Failed to convert CtyValue's inner value to string: {e}"
                     logger.error(f"🔤❗❌ {error_msg}")
                     raise CtyStringValidationError(error_msg) from e
            # --- End CtyValue Handling ---

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

    def __eq__(self, other):
        """
        Check equality with another object using Python's equality operator.

        This implements the == operator for CtyString objects, making it possible
        to compare string types directly.

        Args:
            other: The object to compare with.

        Returns:
            bool: True if the other object is also a CtyString, False otherwise.
        """
        return isinstance(other, CtyString)

    def __hash__(self) -> int:
        """
        Calculate a hash value for this string type.

        This makes CtyString instances usable as dictionary keys and in sets.
        All CtyString instances have the same hash value since they represent
        the same type.

        Returns:
            int: A hash value for this type.
        """
        return hash((self.__class__,))

    def __repr__(self) -> str:
        """
        Get a detailed string representation of this string type.

        This representation is useful for debugging and introspection.

        Returns:
            str: A string representation showing the class name.
        """
        return f"{self.__class__.__name__}()"

    def __str__(self) -> str:
        """
        Get a simple string representation of this type.

        Returns:
            str: The string "CtyString".
        """
        return "CtyString"

# 🐍🏗️🐣
