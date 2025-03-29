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

    def validate(self, value: Any) -> "CtyValue":
        """
        Validate that the given value is a boolean.
        
        Args:
            value: The value to validate
            
        Returns:
            A CtyValue with the validated boolean
            
        Raises:
            ValidationError: If the value is not a boolean
        """
        # Import locally to avoid circular imports
        from pyvider.cty.values import CtyValue
        logger.debug(f"🔄🔍🔄 Validating value as boolean: {value}")
        
        # Handle CtyValue inputs
        if isinstance(value, CtyValue):
            if isinstance(value.type, CtyBool):
                logger.debug(f"🔄🔍✅ Value is already a CtyValue with CtyBool type")
                return value
                
            if value.is_known and not value.is_null:
                # Try to convert inner value to boolean
                inner_val = value.value
                if isinstance(inner_val, bool):
                    return CtyValue(type_=self, value=inner_val)
                # Try to use truthiness
                try:
                    bool_val = bool(inner_val)
                    logger.debug(f"🔄🔍✅ Converted inner value to boolean: {bool_val}")
                    return CtyValue(type_=self, value=bool_val)
                except Exception as e:
                    error_msg = f"Failed to convert CtyValue to boolean: {e}"
                    logger.error(f"🔄❗❌ {error_msg}")
                    raise ValidationError(error_msg)
        
        # Handle None
        if value is None:
            logger.debug("🔄🔍✅ None value converted to False")
            return CtyValue(type_=self, value=False)
        
        # Handle direct boolean
        if isinstance(value, bool):
            logger.debug(f"🔄🔍✅ Value is a boolean: {value}")
            return CtyValue(type_=self, value=value)
            
        # Handle string representations
        if isinstance(value, str):
            if value.lower() in ('true', 't', 'yes', 'y', '1'):
                logger.debug(f"🔄🔍✅ String '{value}' converted to True")
                return CtyValue(type_=self, value=True)
            elif value.lower() in ('false', 'f', 'no', 'n', '0'):
                logger.debug(f"🔄🔍✅ String '{value}' converted to False")
                return CtyValue(type_=self, value=False)
                
        # Handle numbers (0 = False, non-0 = True)
        if isinstance(value, (int, float)):
            bool_val = bool(value)
            logger.debug(f"🔄🔍✅ Number converted to boolean: {bool_val}")
            return CtyValue(type_=self, value=bool_val)
            
        # Try general conversion
        try:
            bool_val = bool(value)
            logger.debug(f"🔄🔍✅ Value converted to boolean using bool(): {bool_val}")
            return CtyValue(type_=self, value=bool_val)
        except Exception as e:
            error_msg = f"Value must be a boolean, got {type(value).__name__}"
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
