
# pyvider/cty/convert/convert.py

"""
Core type conversion system for Cty.

This module provides the infrastructure for converting between Cty types.
It implements a registry of conversion rules and functions for performing
type conversions with appropriate validation.

The conversion system is based on go-cty's design, with a registry of
conversion rules that can be queried to find paths between types. This
allows for complex conversions through intermediate types, as well as
safe vs. unsafe conversion paths.

Conversions can be:
- Safe: Guaranteed not to lose information
- Unsafe: May lose information or precision
- Impossible: No conversion path exists
"""

import asyncio
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Callable, Dict, Generic, List, Optional, Set, Tuple, Type, TypeVar, Union, cast

import attrs

from pyvider.cty.logger import logger
from pyvider.cty.types import (
    CtyType,
    CtyString,
    CtyNumber,
    CtyBool,
    CtyList,
    CtyMap,
    CtySet,
    CtyObject,
    CtyDynamic,
    CtyTuple,
)
from pyvider.cty.values import CtyValue

from pyvider.cty.exceptions import ConversionError

# Forward reference for Value to avoid circular imports
T = TypeVar('T')
S = TypeVar('S')

@attrs.define(frozen=True)
class Conversion:
    """
    Definition of a conversion between two Cty types.
    
    A conversion defines how to convert values from one Cty type to another,
    and whether that conversion is considered "safe" (no information loss)
    or "unsafe" (potential information loss).
    """
    source_type: Type[CtyType] = attrs.field()
    target_type: Type[CtyType] = attrs.field()
    converter: Callable[[CtyValue], CtyValue] = attrs.field()
    is_safe: bool = attrs.field(default=False)
    
    async def convert(self, value: CtyValue) -> CtyValue:
        """
        Convert a value from the source type to the target type.
        
        Args:
            value: The value to convert
            
        Returns:
            CtyValue: The converted value
            
        Raises:
            ConversionError: If conversion fails
        """
        logger.debug(f"🧰🔄✅ Converting from {self.source_type.__name__} to {self.target_type.__name__}")
        
        try:
            result = await asyncio.to_thread(self.converter, value)
            logger.debug(f"🧰🔄✅ Conversion successful: {result}")
            return result
        except Exception as e:
            logger.error(f"🧰🔄❌ Conversion failed: {e}")
            raise ConversionError(f"Failed to convert from {self.source_type.__name__} to {self.target_type.__name__}: {e}")

@attrs.define
class ConversionRegistry:
    """
    Registry of type conversions.
    
    This registry maintains a graph of possible conversions between Cty types,
    and provides methods for finding conversion paths and performing conversions.
    """
    # Maps (source_type, target_type) to a Conversion object
    _safe_conversions: Dict[Tuple[Type[CtyType], Type[CtyType]], Conversion] = attrs.field(factory=dict)
    _unsafe_conversions: Dict[Tuple[Type[CtyType], Type[CtyType]], Conversion] = attrs.field(factory=dict)
    
    def register(
        self, 
        source_type: Type[CtyType], 
        target_type: Type[CtyType],
        converter: Callable[[CtyValue], CtyValue],
        is_safe: bool = False
    ) -> None:
        """
        Register a conversion between two types.
        
        Args:
            source_type: The source type
            target_type: The target type
            converter: Function to convert values
            is_safe: Whether the conversion is safe (no data loss)
        """
        logger.debug(f"🧰📝✅ Registering conversion from {source_type.__name__} to {target_type.__name__} (safe={is_safe})")
        
        conversion = Conversion(
            source_type=source_type,
            target_type=target_type,
            converter=converter,
            is_safe=is_safe
        )
        
        key = (source_type, target_type)
        
        # Register in both collections if safe
        if is_safe:
            self._safe_conversions[key] = conversion
            
        # All conversions go into unsafe
        self._unsafe_conversions[key] = conversion
    
    def get_safe_conversion(
        self, 
        source_type: Type[CtyType], 
        target_type: Type[CtyType]
    ) -> Optional[Conversion]:
        """
        Get a safe conversion between two types.
        
        Args:
            source_type: The source type
            target_type: The target type
            
        Returns:
            Conversion: The conversion if found, None otherwise
        """
        # Identity conversion
        if source_type == target_type:
            return self._identity_conversion(source_type)
            
        # Direct conversion
        key = (source_type, target_type)
        return self._safe_conversions.get(key)
    
    def get_unsafe_conversion(
        self, 
        source_type: Type[CtyType], 
        target_type: Type[CtyType]
    ) -> Optional[Conversion]:
        """
        Get any conversion between two types, including unsafe ones.
        
        Args:
            source_type: The source type
            target_type: The target type
            
        Returns:
            Conversion: The conversion if found, None otherwise
        """
        # Identity conversion
        if source_type == target_type:
            return self._identity_conversion(source_type)
            
        # Direct conversion
        key = (source_type, target_type)
        return self._unsafe_conversions.get(key)
    
    def _identity_conversion(self, type_: Type[CtyType]) -> Conversion:
        """
        Create an identity conversion for a type.
        
        Args:
            type_: The type
            
        Returns:
            Conversion: An identity conversion
        """
        async def identity_converter(value: CtyValue) -> CtyValue:
            return value
            
        return Conversion(
            source_type=type_,
            target_type=type_,
            converter=identity_converter,
            is_safe=True
        )
    
    def find_conversion_path(
        self,
        source_type: Type[CtyType],
        target_type: Type[CtyType],
        allow_unsafe: bool = False
    ) -> Optional[List[Conversion]]:
        """
        Find a path of conversions between two types.
        
        This uses a breadth-first search to find the shortest path of
        conversions between the source and target types.
        
        Args:
            source_type: The source type
            target_type: The target type
            allow_unsafe: Whether to allow unsafe conversions
            
        Returns:
            List[Conversion]: A list of conversions to apply in order,
                             or None if no path exists
        """
        logger.debug(f"🧰🔍🔄 Finding conversion path from {source_type.__name__} to {target_type.__name__} (unsafe={allow_unsafe})")
        
        # Same type - identity conversion
        if source_type == target_type:
            return [self._identity_conversion(source_type)]
            
        # Conversions to search
        conversions = self._unsafe_conversions if allow_unsafe else self._safe_conversions
        
        # Breadth-first search
        queue = [(source_type, [])]
        visited = {source_type}
        
        while queue:
            current_type, path = queue.pop(0)
            
            for key, conversion in conversions.items():
                if key[0] != current_type:
                    continue
                    
                next_type = key[1]
                
                if next_type == target_type:
                    # Found a path to target
                    return path + [conversion]
                    
                if next_type not in visited:
                    visited.add(next_type)
                    queue.append((next_type, path + [conversion]))
                    
        # No path found
        logger.debug(f"🧰🔍❌ No conversion path found from {source_type.__name__} to {target_type.__name__}")
        return None
        
    async def convert(
        self,
        value: CtyValue,
        target_type: Type[CtyType],
        allow_unsafe: bool = False
    ) -> CtyValue:
        """
        Convert a value to a target type.
        
        Args:
            value: The value to convert
            target_type: The target type
            allow_unsafe: Whether to allow unsafe conversions
            
        Returns:
            CtyValue: The converted value
            
        Raises:
            ConversionError: If conversion fails or is impossible
        """
        from pyvider.cty.values import CtyValue
        
        source_type = type(value.type)
        logger.debug(f"🧰🔄🔍 Converting value from {source_type.__name__} to {target_type.__name__}")
        
        # Same type - no conversion needed
        if source_type == target_type:
            return value
            
        # Find conversion path
        path = self.find_conversion_path(source_type, target_type, allow_unsafe)
        if not path:
            raise ConversionError(
                f"Cannot convert from {source_type.__name__} to {target_type.__name__}"
            )
            
        # Apply conversions in sequence
        current_value = value
        for conversion in path:
            current_value = await conversion.convert(current_value)
            
        return current_value
    
    def unify(
        self,
        types: List[Type[CtyType]],
        allow_unsafe: bool = False
    ) -> Optional[Tuple[Type[CtyType], List[Optional[Conversion]]]]:
        """
        Find a common type that all given types can be converted to.
        
        This attempts to find a single target type that all the input types
        can be converted to, and returns that type along with the conversions
        needed for each input type.
        
        Args:
            types: The types to unify
            allow_unsafe: Whether to allow unsafe conversions
            
        Returns:
            Tuple containing:
                - The unified type
                - A list of conversions, one for each input type
            Or None if unification is impossible
        """
        logger.debug(f"🧰🔄🔍 Attempting to unify {len(types)} types")
        
        # Empty list - return dynamic
        if not types:
            from pyvider.cty.types import CtyDynamic
            return CtyDynamic, []

        # Single type - return it
        if len(types) == 1:
            return types[0], [self._identity_conversion(types[0])]
            
        # Try each type as the target
        for candidate in types:
            conversions = []
            valid = True
            
            for source in types:
                if source == candidate:
                    # Identity conversion
                    conversions.append(self._identity_conversion(source))
                else:
                    # Try to find a conversion path
                    path = self.find_conversion_path(source, candidate, allow_unsafe)
                    if not path:
                        valid = False
                        break
                    conversions.append(path[0])  # Just need the first conversion
                    
            if valid:
                logger.debug(f"🧰🔄✅ Unified to {candidate.__name__}")
                return candidate, conversions
                
        # No unification possible
        logger.debug(f"🧰🔄❌ Unable to unify types")
        return None

# Create global registry
registry = ConversionRegistry()

# Helper functions that use the global registry
async def convert(value: CtyValue, target_type: Type[CtyType]) -> CtyValue:
    """
    Convert a value to a target type using only safe conversions.
    
    Args:
        value: The value to convert
        target_type: The target type
        
    Returns:
        CtyValue: The converted value
        
    Raises:
        ConversionError: If conversion fails or is impossible
    """
    return await registry.convert(value, target_type, allow_unsafe=False)

async def convert_unsafe(value: CtyValue, target_type: Type[CtyType]) -> CtyValue:
    """
    Convert a value to a target type, allowing unsafe conversions.
    
    Args:
        value: The value to convert
        target_type: The target type
        
    Returns:
        CtyValue: The converted value
        
    Raises:
        ConversionError: If conversion fails or is impossible
    """
    return await registry.convert(value, target_type, allow_unsafe=True)

async def can_convert(source_type: CtyType, target_type: CtyType) -> bool:
    """
    Check if a source type can be safely converted to a target type.
    
    Args:
        source_type: The source type
        target_type: The target type
        
    Returns:
        bool: True if conversion is possible, False otherwise
    """
    path = registry.find_conversion_path(
        type(source_type), 
        type(target_type), 
        allow_unsafe=False
    )
    return path is not None

async def can_convert_unsafe(source_type: CtyType, target_type: CtyType) -> bool:
    """
    Check if a source type can be converted to a target type with unsafe conversions.
    
    Args:
        source_type: The source type
        target_type: The target type
        
    Returns:
        bool: True if conversion is possible, False otherwise
    """
    path = registry.find_conversion_path(
        type(source_type), 
        type(target_type), 
        allow_unsafe=True
    )
    return path is not None

async def unify(types: List[CtyType]) -> Optional[Tuple[Type[CtyType], List[Optional[Conversion]]]]:
    """
    Find a common type that all given types can be safely converted to.
    
    Args:
        types: The types to unify
        
    Returns:
        Tuple containing the unified type and conversions, or None if impossible
    """
    return registry.unify([type(t) for t in types], allow_unsafe=False)

async def unify_unsafe(types: List[CtyType]) -> Optional[Tuple[Type[CtyType], List[Optional[Conversion]]]]:
    """
    Find a common type that all given types can be converted to with unsafe conversions.
    
    Args:
        types: The types to unify
        
    Returns:
        Tuple containing the unified type and conversions, or None if impossible
    """
    return registry.unify([type(t) for t in types], allow_unsafe=True)

# Register built-in conversions

# String to Number
async def string_to_number(value: CtyValue) -> CtyValue:
    """Convert string to number."""
    from pyvider.cty.values import CtyValue
    
    if value.is_null or value.is_unknown:
        return CtyValue(type_=CtyNumber(), is_null=value.is_null, is_unknown=value.is_unknown)
        
    try:
        result = Decimal(value.value)
        return CtyValue(type_=CtyNumber(), value=result)
    except:
        raise ConversionError(f"Cannot convert string '{value.value}' to number")

# String to Bool
async def string_to_bool(value: CtyValue) -> CtyValue:
    """Convert string to bool."""
    from pyvider.cty.values import CtyValue
    
    if value.is_null or value.is_unknown:
        return CtyValue(type_=CtyBool(), is_null=value.is_null, is_unknown=value.is_unknown)
        
    string_value = str(value.value).lower()
    
    if string_value in ("true", "t", "yes", "y", "1"):
        return CtyValue(type_=CtyBool(), value=True)
    elif string_value in ("false", "f", "no", "n", "0"):
        return CtyValue(type_=CtyBool(), value=False)
    else:
        raise ConversionError(f"Cannot convert string '{value.value}' to bool")

# Number to String
async def number_to_string(value: CtyValue) -> CtyValue:
    """Convert number to string."""
    from pyvider.cty.values import CtyValue
    
    if value.is_null or value.is_unknown:
        return CtyValue(type_=CtyString(), is_null=value.is_null, is_unknown=value.is_unknown)
        
    return CtyValue(type_=CtyString(), value=str(value.value))

# Number to Bool
async def number_to_bool(value: CtyValue) -> CtyValue:
    """Convert number to bool."""
    from pyvider.cty.values import CtyValue
    
    if value.is_null or value.is_unknown:
        return CtyValue(type_=CtyBool(), is_null=value.is_null, is_unknown=value.is_unknown)
        
    return CtyValue(type_=CtyBool(), value=bool(value.value))

# Bool to String
async def bool_to_string(value: CtyValue) -> CtyValue:
    """Convert bool to string."""
    from pyvider.cty.values import CtyValue
    
    if value.is_null or value.is_unknown:
        return CtyValue(type_=CtyString(), is_null=value.is_null, is_unknown=value.is_unknown)
        
    return CtyValue(type_=CtyString(), value="true" if value.value else "false")

# Bool to Number
async def bool_to_number(value: CtyValue) -> CtyValue:
    """Convert bool to number."""
    from pyvider.cty.values import CtyValue
    
    if value.is_null or value.is_unknown:
        return CtyValue(type_=CtyNumber(), is_null=value.is_null, is_unknown=value.is_unknown)
        
    return CtyValue(type_=CtyNumber(), value=Decimal(1) if value.value else Decimal(0))

# List to Set
async def list_to_set(value: CtyValue) -> CtyValue:
    """Convert list to set."""
    from pyvider.cty.values import CtyValue
    
    if value.is_null or value.is_unknown:
        return CtyValue(
            type_=CtySet(element_type=value.type.element_type),
            is_null=value.is_null,
            is_unknown=value.is_unknown
        )
        
    # Convert list to set, removing duplicates
    result = set(value.value)
    return CtyValue(
        type_=CtySet(element_type=value.type.element_type),
        value=result
    )

# Set to List
async def set_to_list(value: CtyValue) -> CtyValue:
    """Convert set to list."""
    from pyvider.cty.values import CtyValue
    
    if value.is_null or value.is_unknown:
        return CtyValue(
            type_=CtyList(element_type=value.type.element_type),
            is_null=value.is_null,
            is_unknown=value.is_unknown
        )
        
    # Convert set to list
    result = list(value.value)
    return CtyValue(
        type_=CtyList(element_type=value.type.element_type),
        value=result
    )

# Tuple to List
async def tuple_to_list(value: CtyValue) -> CtyValue:
    """Convert tuple to list."""
    from pyvider.cty.values import CtyValue
    
    if value.is_null or value.is_unknown:
        # We need a common element type - use the first element's type
        if value.type.types:
            element_type = value.type.types[0]
        else:
            element_type = CtyDynamic()
            
        return CtyValue(
            type_=CtyList(element_type=element_type),
            is_null=value.is_null,
            is_unknown=value.is_unknown
        )
        
    # Convert tuple to list
    result = list(value.value)
    
    # Find a common element type
    if value.type.types:
        element_types = [t for t in value.type.types]
        unified = await unify_unsafe(element_types)
        if unified:
            element_type = unified[0]()  # Create an instance
        else:
            element_type = CtyDynamic()
    else:
        element_type = CtyDynamic()
        
    return CtyValue(
        type_=CtyList(element_type=element_type),
        value=result
    )

# Dynamic conversions
async def dynamic_to_any(value: CtyValue, target_type: Type[CtyType]) -> CtyValue:
    """Convert dynamic to any type."""
    from pyvider.cty.values import CtyValue
    
    if value.is_null or value.is_unknown:
        return CtyValue(
            type_=target_type(),
            is_null=value.is_null,
            is_unknown=value.is_unknown
        )
        
    # Try to validate value against target type
    target = target_type()
    try:
        converted = target.validate(value.value)
        return CtyValue(type_=target, value=converted)
    except Exception as e:
        raise ConversionError(f"Cannot convert dynamic value to {target_type.__name__}: {e}")

# Any to dynamic
async def any_to_dynamic(value: CtyValue) -> CtyValue:
    """Convert any type to dynamic."""
    from pyvider.cty.values import CtyValue
    
    if value.is_null or value.is_unknown:
        return CtyValue(
            type_=CtyDynamic(),
            is_null=value.is_null,
            is_unknown=value.is_unknown
        )
        
    # Just wrap the value in a dynamic type
    return CtyValue(type_=CtyDynamic(), value=value.value)

# Register conversions
def register_builtin_conversions():
    """Register all built-in conversions."""
    # String conversions
    registry.register(CtyString, CtyNumber, string_to_number, is_safe=False)
    registry.register(CtyString, CtyBool, string_to_bool, is_safe=False)
    
    # Number conversions
    registry.register(CtyNumber, CtyString, number_to_string, is_safe=True)
    registry.register(CtyNumber, CtyBool, number_to_bool, is_safe=False)
    
    # Bool conversions
    registry.register(CtyBool, CtyString, bool_to_string, is_safe=True)
    registry.register(CtyBool, CtyNumber, bool_to_number, is_safe=True)
    
    # Collection conversions
    # Note: Need to implement proper generic type handling
    
    # Dynamic conversions
    # These are special - we handle them in the converter itself
    
    logger.info("🧰📝✅ Registered built-in conversions")

# Initialize registry
register_builtin_conversions()
