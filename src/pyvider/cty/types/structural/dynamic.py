#
# pyvider/cty/types/structural/dynamic.py
#

"""
Dynamic pseudo-type implementation for the Cty type system.

This module provides the CtyDynamic type, which serves as a placeholder for unknown
or not-yet-determined types in the Cty type system. Unlike concrete types, the
dynamic type doesn't constrain values to a specific representation, making it useful
for scenarios where type information is determined at runtime or for implementing
schema-less data structures.

The dynamic type follows go-cty's dynamic type semantics, supporting type compatibility
checks and special validation behavior for maximum flexibility.
"""

from typing import ClassVar, Any, Optional, TypeVar, cast

from attrs import define

from pyvider.cty.exceptions import CtyValidationError
from pyvider.cty.types.base import CtyType
from pyvider.telemetry import logger

T = TypeVar('T')

@define(frozen=True, slots=True)
class CtyDynamic(CtyType[Any]):
    """
    Dynamic pseudo-type representation in the Cty type system.

    CtyDynamic represents a special "any type" placeholder that can accept values
    of any supported type. Unlike concrete types, it doesn't constrain values to
    a specific representation, making it useful for:

    1. Schema-less data structures where type is determined at runtime
    2. Placeholder for not-yet-determined types during schema validation
    3. Flexible interfaces that can accept multiple types of values

    The dynamic type maintains go-cty compatibility by accepting primitive types,
    collections, and structural values while rejecting complex Python objects
    that don't map cleanly to the Cty type system.

    Attributes:
        ctype: Class variable identifying this as a dynamic type
    """
    ctype: ClassVar[str] = "dynamic"

    def validate(self, value: Any) -> "CtyValue":
        """
        Validate a value against the dynamic type.

        For dynamic types, validation is more permissive than for concrete types,
        accepting any value that can be represented within the Cty type system.
        This includes primitive types (bool, number, string), collections (list,
        dict), and null values.

        Complex Python objects that don't map cleanly to Cty types are rejected
        to maintain compatibility with the go-cty semantics.

        Args:
            value: Any value to validate against the dynamic type

        Returns:
            CtyValue: A CtyValue with this dynamic type and the provided value

        Raises:
            CtyValidationError: If the value cannot be represented in the Cty type system
        """
        from pyvider.cty.values import CtyValue

        logger.debug(f"🧩🔍🔄 Validating value against CtyDynamic: {type(value).__name__}")

        # Accept primitive types, collections, and None
        if isinstance(value, (dict, list, int, float, bool, str, type(None))):
            logger.debug(f"🧩🔍✅ Value is a supported type for CtyDynamic")
            return CtyValue(vtype=self, value=value)

        # Reject complex Python objects that don't map to Cty types
        error_msg = "Unsupported value for CtyDynamic. Acceptable types are primitive types, dict, list, or None."
        logger.error(f"🧩❗❌ {error_msg}")
        raise CtyValidationError(error_msg)

    def equal(self, other: CtyType) -> bool:
        """
        Check if this dynamic type equals another type.

        Two dynamic types are always considered equal to each other, but not to
        any other type. This implements the type equality semantics specified
        in the go-cty documentation.

        Args:
            other: The type to compare against

        Returns:
            bool: True if the other type is also a CtyDynamic, False otherwise
        """
        result = isinstance(other, CtyDynamic)
        logger.debug(f"🧩🔍🔄 CtyDynamic.equal check: {result}")
        return result

    def usable_as(self, other: CtyType) -> bool:
        """
        Check if this dynamic type can be used as another type.

        The dynamic type is only usable as another dynamic type. While it can
        theoretically hold any value, type system consistency requires that it
        only be used where another dynamic type is expected.

        Args:
            other: The target type to check compatibility with

        Returns:
            bool: True if the other type is also a CtyDynamic, False otherwise
        """
        result = isinstance(other, CtyDynamic)
        logger.debug(f"🧩🔍🔄 CtyDynamic.usable_as check: {result}")
        return result

    def to_python(self) -> Any:
        """
        Convert a dynamic type to its Python representation.
        
        For CtyDynamic, this performs minimal structural validation 
        but accepts any value that fits within the Cty type system.
        """
        logger.debug("🧩🔄🔍 Converting CtyDynamic to Python representation")
        
        # Return the value itself (or None as safe default when no value)
        # This matches the semantics of a dynamic type - it accepts any value
        if hasattr(self, 'value'):
            return self.value
        return None

    def __str__(self) -> str:
        """
        Get a string representation of this dynamic type.

        Returns:
            str: The string "CtyDynamic" representing this type
        """
        return "CtyDynamic"

    def __repr__(self) -> str:
        """
        Get a detailed string representation for debugging purposes.

        Returns:
            str: A string showing the class name in a format suitable for debugging
        """
        return "CtyDynamic()"

# 🐍🏗️🐣
