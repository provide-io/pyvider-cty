#
# pyvider/cty/types/capsule.py
#

"""
CtyCapsule implementation for Cty capsule types.

Capsules encapsulate arbitrary Python objects, preserving their identity
and allowing them to pass through the Cty type system intact.
"""

from typing import Any, Callable, ClassVar, Dict, Optional, Type, TypeVar, cast
import weakref
import inspect

import attrs

from pyvider.cty.exceptions import ValidationError, SerializationError, CapsuleError, CapsuleTypeError, CapsuleValueError
from pyvider.cty.types.base import CtyType
from pyvider.cty.logger import logger

T = TypeVar('T')

# Operation type definition for custom capsule operations
CapsuleOperation = Callable[..., Any]

@attrs.define(frozen=True, slots=True)
class CtyCapsule(CtyType[Any]):
    """
    CtyCapsule represents a capsule type in the Cty type system.
    
    Capsules encapsulate arbitrary Python objects, preserving their identity
    and allowing them to pass through the Cty type system intact.
    """
    ctype: ClassVar[str] = "capsule"
    friendly_name: str = attrs.field()
    encapsulated_type: Type = attrs.field()
    operations: Dict[str, CapsuleOperation] = attrs.field(factory=dict)
    
    # Track all created capsule types for introspection and debugging
    _registry: ClassVar[Dict[str, 'CtyCapsule']] = dict()
    
    def __attrs_post_init__(self) -> None:
        """Validate capsule configuration and register the type."""
        logger.debug(f"🧩🔧🔄 Validating CtyCapsule configuration: {self.friendly_name}")
        
        # Validate friendly name
        if not self.friendly_name:
            error_msg = "Capsule friendly_name cannot be empty"
            logger.error(f"🧩❌🔄 {error_msg}")
            raise ValidationError(error_msg)
            
        # Check if encapsulated_type is valid
        if self.encapsulated_type is None:
            error_msg = "Capsule encapsulated_type cannot be None"
            logger.error(f"🧩❌🔄 {error_msg}")
            raise ValidationError(error_msg)
            
        # Validate operations if provided
        for name, op in self.operations.items():
            if not callable(op):
                error_msg = f"Operation '{name}' must be callable"
                logger.error(f"🧩❌🔄 {error_msg}")
                raise ValidationError(error_msg)
        
        # Register this type in the global registry
        self._registry[self.friendly_name] = self
        logger.debug(f"🧩✅🔄 Registered capsule type: {self.friendly_name}")
    
    def validate(self, value: Any) -> "CtyValue":
        """
        Validate that the given value can be encapsulated by this type.
        
        Args:
            value: The value to validate
            
        Returns:
            A CtyValue with the encapsulated value
            
        Raises:
            ValidationError: If the value is not compatible with this capsule type
        """
        # Import locally to avoid circular imports
        from pyvider.cty.values import CtyValue
        logger.debug(f"🧩🔍🔄 Validating value for capsule: {self.friendly_name}")
        
        # Handle None value - always valid for any capsule type
        if value is None:
            logger.debug("🧩🔍✅ None value is valid for any capsule")
            return CtyValue(type_=self, value=None, is_null=True)
        
        # Handle existing CtyValue of the same capsule type
        if (
            isinstance(value, CtyValue) and 
            isinstance(value.type, CtyCapsule) and
            value.type.friendly_name == self.friendly_name
        ):
            logger.debug("🧩🔍✅ Value is already a CtyValue with the correct capsule type")
            return value
        
        # Verify the value matches the encapsulated type
        if not isinstance(value, self.encapsulated_type):
            error_msg = (
                f"Value of type {type(value).__name__} is not compatible with "
                f"capsule type {self.friendly_name} expecting {self.encapsulated_type.__name__}"
            )
            logger.error(f"🧩❌🔄 {error_msg}")
            raise ValidationError(error_msg)
        
        # Wrap and return the validated value
        logger.debug(f"🧩🔍✅ Value successfully validated for capsule: {self.friendly_name}")
        return CtyValue(type_=self, value=value)
    
    def equal(self, other: CtyType) -> bool:
        """
        Check if this capsule type equals another type.
        
        Capsule types compare by identity - each capsule type is unique
        even if they encapsulate the same Python type.
        
        Args:
            other: The other type to compare with
            
        Returns:
            True if the other type is the same capsule type
        """
        # Capsule types compare by identity - this is intentional
        # to match go-cty's behavior
        result = self is other
        logger.debug(f"🧩🔍✅ CtyCapsule.equal: {result}")
        return result
    
    def usable_as(self, other: CtyType) -> bool:
        """
        Check if this type can be used as another type.
        
        Args:
            other: The other type to check compatibility with
            
        Returns:
            True if this type can be used as the other type
        """
        # Capsule types are only usable as themselves
        result = self is other
        logger.debug(f"🧩🔍✅ CtyCapsule.usable_as: {result}")
        return result
    
    def get_operation(self, name: str) -> Optional[CapsuleOperation]:
        """
        Get a custom operation by name.
        
        Args:
            name: Name of the operation to retrieve
            
        Returns:
            The operation function if it exists, None otherwise
        """
        logger.debug(f"🧩🔍🔄 Getting operation: {name}")
        operation = self.operations.get(name)
        if operation:
            logger.debug(f"🧩🔍✅ Found operation: {name}")
        else:
            logger.debug(f"🧩🔍⚠️ Operation not found: {name}")
        return operation
    
    def has_operation(self, name: str) -> bool:
        """
        Check if this capsule type supports a given operation.
        
        Args:
            name: Name of the operation to check
            
        Returns:
            True if the operation is supported
        """
        result = name in self.operations
        logger.debug(f"🧩🔍🔄 Checking for operation {name}: {result}")
        return result
    
    def execute_operation(self, name: str, value: Any, *args, **kwargs) -> Any:
        """
        Execute a custom operation on a value.
        
        Args:
            name: Name of the operation to execute
            value: The encapsulated value to operate on
            *args: Additional positional arguments for the operation
            **kwargs: Additional keyword arguments for the operation
            
        Returns:
            The result of the operation
            
        Raises:
            TypeError: If the operation doesn't exist
            ValueError: If the value is not compatible with this capsule type
        """
        logger.debug(f"🧩🔧🔄 Executing operation {name} on value")
        
        # Check if operation exists
        operation = self.get_operation(name)
        if operation is None:
            error_msg = f"Operation '{name}' not found for capsule type {self.friendly_name}"
            logger.error(f"🧩❌🔄 {error_msg}")
            raise TypeError(error_msg)
            
        # Validate value type
        if not isinstance(value, self.encapsulated_type):
            error_msg = (
                f"Value of type {type(value).__name__} is not compatible with "
                f"capsule type {self.friendly_name} expecting {self.encapsulated_type.__name__}"
            )
            logger.error(f"🧩❌🔄 {error_msg}")
            raise ValueError(error_msg)
            
        # Execute the operation
        try:
            result = operation(value, *args, **kwargs)
            logger.debug(f"🧩🔧✅ Operation {name} executed successfully")
            return result
        except Exception as e:
            error_msg = f"Error executing operation '{name}': {e}"
            logger.error(f"🧩❌🔄 {error_msg}")
            raise ValueError(error_msg) from e
    
    @classmethod
    def get_registered_type(cls, name: str) -> Optional['CtyCapsule']:
        """
        Get a registered capsule type by friendly name.
        
        Args:
            name: Friendly name of the capsule type
            
        Returns:
            The capsule type if found, None otherwise
        """
        registered_type = cls._registry.get(name)
        if registered_type:
            logger.debug(f"🧩🔍✅ Found registered capsule type: {name}")
        else:
            logger.debug(f"🧩🔍⚠️ Capsule type not found: {name}")
        return registered_type
    
    @classmethod
    def list_registered_types(cls) -> Dict[str, 'CtyCapsule']:
        """
        Get all registered capsule types.
        
        Returns:
            A dictionary of friendly name to CtyCapsule instance
        """
        logger.debug(f"🧩🔍🔄 Listing {len(cls._registry)} registered capsule types")
        return dict(cls._registry)
    
    def __hash__(self) -> int:
        """
        Get a hash value for this capsule type.
        
        Returns:
            Hash based on type identity
        """
        # Use identity hash since capsules compare by identity
        return id(self)
    
    def __repr__(self) -> str:
        """
        Get a detailed string representation of this capsule type.
        
        Returns:
            A detailed string representation
        """
        ops = ", ".join(self.operations.keys()) if self.operations else "none"
        return f"CtyCapsule(friendly_name={self.friendly_name!r}, encapsulated_type={self.encapsulated_type.__name__!r}, operations={ops})"
    
    def __str__(self) -> str:
        """
        Get a string representation of this capsule type.
        
        Returns:
            A string representation
        """
        return f"capsule({self.friendly_name})"

# 🐍🏗️🐣
