#
# pyvider/cty/types/primitives/string.py
#

from typing import Any, ClassVar, TypeVar

from attrs import define, evolve, field

from pyvider.cty.exceptions import CtyValidationError
from pyvider.cty.logger import logger
from pyvider.cty.types.base import CtyType

T = TypeVar('T', bound=str)

@define(frozen=True, slots=True)
class CtyString(CtyType[str]):
    """
    CtyString represents a string type in the Cty type system.
    
    Strings are sequences of Unicode characters.
    """
    ctype: ClassVar[str] = "string"
    value: str = field(default="")

    def validate(self, value: Any) -> "CtyValue":
        """
        Validate that the given value is a string. Stricter validation.
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
            if value.is_known and not value.is_null:
                 try:
                     str_val = str(value.value)
                     logger.debug(f"🔤🔍✅ Converted known CtyValue's inner value to string: {str_val!r}")
                     return CtyValue(type_=self, value=str_val)
                 except Exception as e:
                     error_msg = f"Failed to convert CtyValue's inner value to string: {e}"
                     logger.error(f"🔤❗❌ {error_msg}")
                     raise CtyValidationError(error_msg) from e
            # --- End CtyValue Handling ---

        # Handle None as empty string (consistent with go-cty)
        if value is None:
            logger.debug("🔤🔍✅ None value converted to empty string")
            return CtyValue(type_=self, value="")

        # Handle direct string
        if isinstance(value, str):
            logger.debug("🔤🔍✅ Value is a string")
            return CtyValue(type_=self, value=value)

        # --- REJECT ALL OTHER TYPES ---
        error_msg = f"Value must be a string, got {type(value).__name__}"
        logger.error(f"🔤❗❌ {error_msg}")
        raise CtyValidationError(error_msg)

    def equal(self, other: CtyType[Any]) -> bool:
        """
        Check equality with another type.

        Args:
            other: The type to compare with.

        Returns:
            bool: True if the other type is a CtyString type.
        """
        result = isinstance(other, CtyString)
        logger.debug(f"🔤🔍✅ CtyString.equal: {result}")
        return result

    def usable_as(self, other: CtyType[Any]) -> bool:
        """
        Check if this type can be used as another type.

        Args:
            other: The type to check compatibility with.

        Returns:
            bool: True if this type can be used as the other type.
        """
        result = isinstance(other, CtyString)
        logger.debug(f"🔤🔍✅ CtyString.usable_as: {result}")
        return result

    def __eq__(self, other):
        return isinstance(other, CtyString)

    def __hash__(self) -> int:
        return hash((self.__class__,))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __str__(self) -> str:
        return "CtyString"

# 🐍🏗️🐣
