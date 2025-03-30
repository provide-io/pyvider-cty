#
# pyvider/cty/types/primitives/bool.py
#

from typing import Any, ClassVar

from attrs import define, field

from pyvider.cty.exceptions import ValidationError
from pyvider.cty.logger import logger
from pyvider.cty.types.base import CtyType

@define(frozen=True, slots=True)
class CtyBool(CtyType[bool]):
    """
    CtyBool represents a boolean type in the Cty type system.
    
    Boolean values can be either true or false.
    """
    ctype: ClassVar[str] = "bool"
    value: bool = field(default=False)


# In google-pyv/pyvider-cty/types/primitives/bool.py

    def validate(self, value: Any) -> "CtyValue":
        """
        Validate that the given value is a boolean. Stricter validation.
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
            if value.is_known and not value.is_null:
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

        # Handle None (consistent with go-cty? Often false, but depends on context)
        # Let's make None invalid for bool unless explicitly handled elsewhere
        # if value is None:
        #     logger.debug("🔄🔍✅ None value converted to False") # Or raise error?
        #     return CtyValue(type_=self, value=False) # Let's make None an error for now

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

        # --- REJECT ALL OTHER TYPES ---
        error_msg = f"Value must be a boolean or a specific convertible string/number, got {type(value).__name__}"
        logger.error(f"🔄❗❌ {error_msg}")
        raise ValidationError(error_msg)

    def equal(self, other: "CtyType[bool]") -> bool:
        """Check equality with another type."""
        result = isinstance(other, CtyBool)
        logger.debug(f"🔄🔍✅ CtyBool.equal: {result}")
        return result

    def usable_as(self, other: "CtyType[bool]") -> bool:
        """Check if this type can be used as another type."""
        result = isinstance(other, CtyBool)
        logger.debug(f"🔄🔍✅ CtyBool.usable_as: {result}")
        return result

    def __eq__(self, other):
        return isinstance(other, CtyBool)

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def __hash__(self):
        return hash(self.__class__)

# 🐍🏗️🐣
