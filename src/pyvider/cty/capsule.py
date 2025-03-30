#
# pyvider/cty/capsule.py
#

"""
Helper functions for working with capsule types and values.
"""

from typing import Any, Callable, Dict, Optional, Type, TypeVar

from pyvider.cty.types.capsule import CtyCapsule, CapsuleOperation
from pyvider.cty.logger import logger

T = TypeVar('T')

def capsule_type(friendly_name: str, encapsulated_type: Type[T]) -> CtyCapsule:
    """
    Create a new capsule type for the given Python type.
    
    Args:
        friendly_name: User-friendly name for the type
        encapsulated_type: Python type to encapsulate
        
    Returns:
        A new capsule type
    """
    logger.debug(f"🧩🔧🔄 Creating capsule type: {friendly_name}")
    return CtyCapsule(
        friendly_name=friendly_name,
        encapsulated_type=encapsulated_type
    )


def capsule_type_with_ops(
    friendly_name: str, 
    encapsulated_type: Type[T],
    operations: Dict[str, CapsuleOperation]
) -> CtyCapsule:
    """
    Create a new capsule type with custom operations.
    
    Args:
        friendly_name: User-friendly name for the type
        encapsulated_type: Python type to encapsulate
        operations: Dict of operation name to function
        
    Returns:
        A new capsule type with operations
    """
    logger.debug(f"🧩🔧🔄 Creating capsule type with operations: {friendly_name}")
    return CtyCapsule(
        friendly_name=friendly_name,
        encapsulated_type=encapsulated_type,
        operations=operations
    )


def capsule_val(capsule_type: CtyCapsule, value: Any) -> "CtyValue":
    """
    Create a capsule value encapsulating the given value.
    
    Args:
        capsule_type: The capsule type to use
        value: The value to encapsulate
        
    Returns:
        A CtyValue containing the encapsulated value
        
    Raises:
        ValidationError: If the value is not compatible with the capsule type
    """
    logger.debug(f"🧩🔧🔄 Creating capsule value for type: {capsule_type.friendly_name}")
    from pyvider.cty.values import CtyValue
    
    # Handle None specially as null
    if value is None:
        return CtyValue(type_=capsule_type, is_null=True)
        
    # Validate against the capsule type
    if not isinstance(value, capsule_type.encapsulated_type):
        error_msg = (
            f"Value of type {type(value).__name__} is not compatible with "
            f"capsule type {capsule_type.friendly_name} expecting {capsule_type.encapsulated_type.__name__}"
        )
        logger.error(f"🧩❌🔄 {error_msg}")
        from pyvider.cty.exceptions import ValidationError
        raise ValidationError(error_msg)
        
    # Create the value
    return CtyValue(type_=capsule_type, value=value)

# 🐍🏗️🐣
