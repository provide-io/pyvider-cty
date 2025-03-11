
# pyvider/cty/values/operations.py

"""
Value operations for the CTY type system.

This module provides operations that can be performed on CTY values, similar to
the operations provided by Go-CTY. These include equality checking, type conversion,
arithmetic operations, and more complex operations like retrieval from collections.

Operations respect value state (known/unknown/null) and properly handle marks.
All operations maintain proper type checking and value immutability.
"""

import operator
from decimal import Decimal
from typing import Any, Dict, List, Optional, Set, Tuple, TypeVar, Union, cast

import attrs

from pyvider.cty.logger import logger
from pyvider.cty.types.base import CtyType
from pyvider.cty.types.primitives import CtyString, CtyNumber, CtyBool
from pyvider.cty.types.collections import CtyList, CtyMap, CtySet
from pyvider.cty.types.structural import CtyObject, CtyDynamic, CtyTuple
from pyvider.cty.values.base import Value
from pyvider.exceptions import CtyError, TypeMismatchError

# Type variables for generic operations
T = TypeVar('T')
R = TypeVar('R')


def equals(a: Value, b: Value) -> Value:
    """
    Check if two values are equal.
    
    Args:
        a: First value
        b: Second value
        
    Returns:
        A boolean Value representing the equality check result
        
    This operation checks both value equality and type equality.
    Unknown or null values result in unknown boolean values.
    """
    logger.debug(f"🧮🔄✅ Checking equality between {a} and {b}")
    
    # Handle unknown values
    if not a.is_known or not b.is_known:
        logger.debug("🧮🔄✅ One or both values are unknown, result is unknown")
        return Value.unknown(CtyBool())
    
    # Handle null values
    if a.is_null or b.is_null:
        # Two nulls of compatible types are equal
        if a.is_null and b.is_null and a.type.equal(b.type):
            logger.debug("🧮🔄✅ Both values are null with compatible types, result is true")
            return Value.bool(True)
        
        logger.debug("🧮🔄✅ One value is null, other is not, or types incompatible, result is false")
        return Value.bool(False)
    
    # Type mismatch
    if not a.type.equal(b.type):
        logger.debug(f"🧮🔄✅ Type mismatch: {a.type} != {b.type}, result is false")
        return Value.bool(False)
    
    # Check actual values
    try:
        # Special handling for different types
        if isinstance(a.type, CtyList) and isinstance(b.type, CtyList):
            return _equals_list(a, b)
        elif isinstance(a.type, CtyMap) and isinstance(b.type, CtyMap):
            return _equals_map(a, b)
        elif isinstance(a.type, CtySet) and isinstance(b.type, CtySet):
            return _equals_set(a, b)
        elif isinstance(a.type, CtyObject) and isinstance(b.type, CtyObject):
            return _equals_object(a, b)
        else:
            # Direct value comparison for basic types
            result = a.value == b.value
            logger.debug(f"🧮🔄✅ Direct value comparison result: {result}")
            return Value.bool(result)
            
    except Exception as e:
        logger.error(f"🧮🔄❌ Error comparing values: {e}", exc_info=True)
        # Return false on any error
        return Value.bool(False)


def _equals_list(a: Value, b: Value) -> Value:
    """Helper for list equality checking."""
    a_list = cast(List[Any], a.value)
    b_list = cast(List[Any], b.value)
    
    # Check length first
    if len(a_list) != len(b_list):
        return Value.bool(False)
    
    # Compare each element
    for i, (a_item, b_item) in enumerate(zip(a_list, b_list)):
        # Convert Python values to CTY values
        a_elem = Value(a.type.element_type, a_item)
        b_elem = Value(b.type.element_type, b_item)
        
        # Check element equality
        eq_result = equals(a_elem, b_elem)
        if not eq_result.is_known:
            return eq_result  # Propagate unknown
        if not eq_result.value:
            return Value.bool(False)  # Any non-equal element means not equal
    
    # All elements equal
    return Value.bool(True)


def _equals_map(a: Value, b: Value) -> Value:
    """Helper for map equality checking."""
    a_map = cast(Dict[str, Any], a.value)
    b_map = cast(Dict[str, Any], b.value)
    
    # Check keys first
    if set(a_map.keys()) != set(b_map.keys()):
        return Value.bool(False)
    
    # Compare each value
    for key in a_map:
        # Convert Python values to CTY values
        a_elem = Value(a.type.element_type, a_map[key])
        b_elem = Value(b.type.element_type, b_map[key])
        
        # Check value equality
        eq_result = equals(a_elem, b_elem)
        if not eq_result.is_known:
            return eq_result  # Propagate unknown
        if not eq_result.value:
            return Value.bool(False)  # Any non-equal value means not equal
    
    # All values equal
    return Value.bool(True)


def _equals_set(a: Value, b: Value) -> Value:
    """Helper for set equality checking."""
    a_set = cast(Set[Any], a.value)
    b_set = cast(Set[Any], b.value)
    
    # Simple length check first
    if len(a_set) != len(b_set):
        return Value.bool(False)
    
    # For sets, we need to check membership both ways
    # This is more complex than just comparing sets directly
    # because we need to use CTY equality semantics
    for a_item in a_set:
        # Check if a_item is in b_set
        found = False
        for b_item in b_set:
            # Convert to CTY values
            a_elem = Value(a.type.element_type, a_item)
            b_elem = Value(b.type.element_type, b_item)
            
            # Check equality
            eq_result = equals(a_elem, b_elem)
            if not eq_result.is_known:
                return eq_result  # Propagate unknown
            if eq_result.value:
                found = True
                break
        
        if not found:
            return Value.bool(False)  # Item in a not found in b
    
    # All elements found
    return Value.bool(True)


def _equals_object(a: Value, b: Value) -> Value:
    """Helper for object equality checking."""
    a_obj = cast(Dict[str, Any], a.value)
    b_obj = cast(Dict[str, Any], b.value)
    
    # Get object type info
    a_type = cast(CtyObject, a.type)
    b_type = cast(CtyObject, b.type)
    
    # Check attributes
    for attr_name, attr_type in a_type.attribute_types.items():
        # Get attribute values
        a_attr = a_obj.get(attr_name)
        b_attr = b_obj.get(attr_name)
        
        # Convert to CTY values
        a_elem = Value(attr_type, a_attr)
        b_elem = Value(attr_type, b_attr)
        
        # Check equality
        eq_result = equals(a_elem, b_elem)
        if not eq_result.is_known:
            return eq_result  # Propagate unknown
        if not eq_result.value:
            return Value.bool(False)  # Any non-equal attribute means not equal
    
    # All attributes equal
    return Value.bool(True)


def add(a: Value, b: Value) -> Value:
    """
    Add two values together.
    
    Args:
        a: First value
        b: Second value
        
    Returns:
        Result of the addition
        
    Supported combinations:
    - Number + Number = Number (arithmetic addition)
    - String + String = String (concatenation)
    - List + List = List (concatenation)
    
    Raises:
        TypeError: If the operation is not supported for the given types
    """
    logger.debug(f"🧮➕✅ Adding {a} and {b}")
    
    # Handle unknown values
    if not a.is_known or not b.is_known:
        # For unknown values, return unknown of the expected result type
        if isinstance(a.type, CtyNumber) and isinstance(b.type, CtyNumber):
            return Value.unknown(CtyNumber())
        elif isinstance(a.type, CtyString) and isinstance(b.type, CtyString):
            return Value.unknown(CtyString())
        elif isinstance(a.type, CtyList) and isinstance(b.type, CtyList):
            # For lists, ensure element types are compatible
            if a.type.element_type.equal(b.type.element_type):
                return Value.unknown(CtyList(element_type=a.type.element_type))
            else:
                raise TypeMismatchError("Cannot add lists with incompatible element types")
        else:
            raise TypeError(f"Cannot add values of types {a.type} and {b.type}")
    
    # Handle null values
    if a.is_null or b.is_null:
        # For null values, return null of the expected result type
        if isinstance(a.type, CtyNumber) and isinstance(b.type, CtyNumber):
            return Value.null(CtyNumber())
        elif isinstance(a.type, CtyString) and isinstance(b.type, CtyString):
            return Value.null(CtyString())
        elif isinstance(a.type, CtyList) and isinstance(b.type, CtyList):
            # For lists, ensure element types are compatible
            if a.type.element_type.equal(b.type.element_type):
                return Value.null(CtyList(element_type=a.type.element_type))
            else:
                raise TypeMismatchError("Cannot add lists with incompatible element types")
        else:
            raise TypeError(f"Cannot add values of types {a.type} and {b.type}")
    
    # Handle actual addition
    try:
        # Number addition
        if isinstance(a.type, CtyNumber) and isinstance(b.type, CtyNumber):
            num_a = Decimal(str(a.value))
            num_b = Decimal(str(b.value))
            result = num_a + num_b
            logger.debug(f"🧮➕✅ Number addition result: {result}")
            return Value(CtyNumber(), result)
        
        # String concatenation
        elif isinstance(a.type, CtyString) and isinstance(b.type, CtyString):
            result = str(a.value) + str(b.value)
            logger.debug(f"🧮➕✅ String concatenation result: {result}")
            return Value(CtyString(), result)
        
        # List concatenation
        elif isinstance(a.type, CtyList) and isinstance(b.type, CtyList):
            # Ensure element types are compatible
            if not a.type.element_type.equal(b.type.element_type):
                raise TypeMismatchError("Cannot add lists with incompatible element types")
            
            a_list = cast(List[Any], a.value)
            b_list = cast(List[Any], b.value)
            result = a_list + b_list
            logger.debug(f"🧮➕✅ List concatenation result: {result}")
            return Value(CtyList(element_type=a.type.element_type), result)
        
        # Unsupported combination
        else:
            raise TypeError(f"Cannot add values of types {a.type} and {b.type}")
            
    except Exception as e:
        if isinstance(e, TypeError) and "Cannot add values" in str(e):
            # Re-raise type errors from this function
            raise
        
        logger.error(f"🧮➕❌ Error adding values: {e}", exc_info=True)
        raise CtyError(f"Error adding values: {e}") from e


def subtract(a: Value, b: Value) -> Value:
    """
    Subtract one value from another.
    
    Args:
        a: First value
        b: Second value
        
    Returns:
        Result of the subtraction
        
    Supported combinations:
    - Number - Number = Number (arithmetic subtraction)
    
    Raises:
        TypeError: If the operation is not supported for the given types
    """
    logger.debug(f"🧮➖✅ Subtracting {b} from {a}")
    
    # Handle unknown values
    if not a.is_known or not b.is_known:
        if isinstance(a.type, CtyNumber) and isinstance(b.type, CtyNumber):
            return Value.unknown(CtyNumber())
        else:
            raise TypeError(f"Cannot subtract values of types {a.type} and {b.type}")
    
    # Handle null values
    if a.is_null or b.is_null:
        if isinstance(a.type, CtyNumber) and isinstance(b.type, CtyNumber):
            return Value.null(CtyNumber())
        else:
            raise TypeError(f"Cannot subtract values of types {a.type} and {b.type}")
    
    # Only number subtraction is supported
    if isinstance(a.type, CtyNumber) and isinstance(b.type, CtyNumber):
        try:
            num_a = Decimal(str(a.value))
            num_b = Decimal(str(b.value))
            result = num_a - num_b
            logger.debug(f"🧮➖✅ Number subtraction result: {result}")
            return Value(CtyNumber(), result)
        except Exception as e:
            logger.error(f"🧮➖❌ Error subtracting values: {e}", exc_info=True)
            raise CtyError(f"Error subtracting values: {e}") from e
    else:
        raise TypeError(f"Cannot subtract values of types {a.type} and {b.type}")


def multiply(a: Value, b: Value) -> Value:
    """
    Multiply two values.
    
    Args:
        a: First value
        b: Second value
        
    Returns:
        Result of the multiplication
        
    Supported combinations:
    - Number * Number = Number (arithmetic multiplication)
    - String * Number = String (repetition)
    - List * Number = List (repetition)
    
    Raises:
        TypeError: If the operation is not supported for the given types
    """
    logger.debug(f"🧮✖️✅ Multiplying {a} and {b}")
    
    # Handle unknown values
    if not a.is_known or not b.is_known:
        if isinstance(a.type, CtyNumber) and isinstance(b.type, CtyNumber):
            return Value.unknown(CtyNumber())
        elif isinstance(a.type, CtyString) and isinstance(b.type, CtyNumber):
            return Value.unknown(CtyString())
        elif isinstance(a.type, CtyList) and isinstance(b.type, CtyNumber):
            return Value.unknown(CtyList(element_type=a.type.element_type))
        else:
            raise TypeError(f"Cannot multiply values of types {a.type} and {b.type}")
    
    # Handle null values
    if a.is_null or b.is_null:
        if isinstance(a.type, CtyNumber) and isinstance(b.type, CtyNumber):
            return Value.null(CtyNumber())
        elif isinstance(a.type, CtyString) and isinstance(b.type, CtyNumber):
            return Value.null(CtyString())
        elif isinstance(a.type, CtyList) and isinstance(b.type, CtyNumber):
            return Value.null(CtyList(element_type=a.type.element_type))
        else:
            raise TypeError(f"Cannot multiply values of types {a.type} and {b.type}")
    
    # Handle actual multiplication
    try:
        # Number multiplication
        if isinstance(a.type, CtyNumber) and isinstance(b.type, CtyNumber):
            num_a = Decimal(str(a.value))
            num_b = Decimal(str(b.value))
            result = num_a * num_b
            logger.debug(f"🧮✖️✅ Number multiplication result: {result}")
            return Value(CtyNumber(), result)
        
        # String repetition
        elif isinstance(a.type, CtyString) and isinstance(b.type, CtyNumber):
            # Ensure the number is an integer
            count = int(b.value)
            if count < 0:
                raise ValueError("Cannot repeat string a negative number of times")
            
            result = str(a.value) * count
            logger.debug(f"🧮✖️✅ String repetition result: {result}")
            return Value(CtyString(), result)
        
        # List repetition
        elif isinstance(a.type, CtyList) and isinstance(b.type, CtyNumber):
            # Ensure the number is an integer
            count = int(b.value)
            if count < 0:
                raise ValueError("Cannot repeat list a negative number of times")
            
            a_list = cast(List[Any], a.value)
            result = a_list * count
            logger.debug(f"🧮✖️✅ List repetition result: {result}")
            return Value(CtyList(element_type=a.type.element_type), result)
        
        # Unsupported combination
        else:
            raise TypeError(f"Cannot multiply values of types {a.type} and {b.type}")
            
    except Exception as e:
        if isinstance(e, (TypeError, ValueError)) and "Cannot" in str(e):
            # Re-raise validation errors
            raise
        
        logger.error(f"🧮✖️❌ Error multiplying values: {e}", exc_info=True)
        raise CtyError(f"Error multiplying values: {e}") from e


def divide(a: Value, b: Value) -> Value:
    """
    Divide one value by another.
    
    Args:
        a: Dividend
        b: Divisor
        
    Returns:
        Result of the division
        
    Supported combinations:
    - Number / Number = Number (arithmetic division)
    
    Raises:
        TypeError: If the operation is not supported for the given types
        ValueError: If dividing by zero
    """
    logger.debug(f"🧮➗✅ Dividing {a} by {b}")
    
    # Handle unknown values
    if not a.is_known or not b.is_known:
        if isinstance(a.type, CtyNumber) and isinstance(b.type, CtyNumber):
            return Value.unknown(CtyNumber())
        else:
            raise TypeError(f"Cannot divide values of types {a.type} and {b.type}")
    
    # Handle null values
    if a.is_null or b.is_null:
        if isinstance(a.type, CtyNumber) and isinstance(b.type, CtyNumber):
            return Value.null(CtyNumber())
        else:
            raise TypeError(f"Cannot divide values of types {a.type} and {b.type}")
    
    # Only number division is supported
    if isinstance(a.type, CtyNumber) and isinstance(b.type, CtyNumber):
        try:
            num_a = Decimal(str(a.value))
            num_b = Decimal(str(b.value))
            
            # Check for division by zero
            if num_b == 0:
                raise ValueError("Division by zero")
            
            result = num_a / num_b
            logger.debug(f"🧮➗✅ Number division result: {result}")
            return Value(CtyNumber(), result)
        except Exception as e:
            logger.error(f"🧮➗❌ Error dividing values: {e}", exc_info=True)
            raise CtyError(f"Error dividing values: {e}") from e
    else:
        raise TypeError(f"Cannot divide values of types {a.type} and {b.type}")


def modulo(a: Value, b: Value) -> Value:
    """
    Calculate the modulo of one value by another.
    
    Args:
        a: Dividend
        b: Divisor
        
    Returns:
        Remainder of the division
        
    Supported combinations:
    - Number % Number = Number (arithmetic modulo)
    
    Raises:
        TypeError: If the operation is not supported for the given types
        ValueError: If divisor is zero
    """
    logger.debug(f"🧮📊✅ Calculating modulo of {a} by {b}")
    
    # Handle unknown values
    if not a.is_known or not b.is_known:
        if isinstance(a.type, CtyNumber) and isinstance(b.type, CtyNumber):
            return Value.unknown(CtyNumber())
        else:
            raise TypeError(f"Cannot calculate modulo of values of types {a.type} and {b.type}")
    
    # Handle null values
    if a.is_null or b.is_null:
        if isinstance(a.type, CtyNumber) and isinstance(b.type, CtyNumber):
            return Value.null(CtyNumber())
        else:
            raise TypeError(f"Cannot calculate modulo of values of types {a.type} and {b.type}")
    
    # Only number modulo is supported
    if isinstance(a.type, CtyNumber) and isinstance(b.type, CtyNumber):
        try:
            num_a = Decimal(str(a.value))
            num_b = Decimal(str(b.value))
            
            # Check for modulo by zero
            if num_b == 0:
                raise ValueError("Modulo by zero")
            
            result = num_a % num_b
            logger.debug(f"🧮📊✅ Number modulo result: {result}")
            return Value(CtyNumber(), result)
        except Exception as e:
            logger.error(f"🧮📊❌ Error calculating modulo: {e}", exc_info=True)
            raise CtyError(f"Error calculating modulo: {e}") from e
    else:
        raise TypeError(f"Cannot calculate modulo of values of types {a.type} and {b.type}")


def negate(a: Value) -> Value:
    """
    Negate a value.
    
    Args:
        a: Value to negate
        
    Returns:
        Negated value
        
    Supported types:
    - Number -> -Number (arithmetic negation)
    - Bool -> !Bool (logical negation)
    
    Raises:
        TypeError: If the operation is not supported for the given type
    """
    logger.debug(f"🧮❓✅ Negating {a}")
    
    # Handle unknown values
    if not a.is_known:
        if isinstance(a.type, CtyNumber):
            return Value.unknown(CtyNumber())
        elif isinstance(a.type, CtyBool):
            return Value.unknown(CtyBool())
        else:
            raise TypeError(f"Cannot negate value of type {a.type}")
    
    # Handle null values
    if a.is_null:
        if isinstance(a.type, CtyNumber):
            return Value.null(CtyNumber())
        elif isinstance(a.type, CtyBool):
            return Value.null(CtyBool())
        else:
            raise TypeError(f"Cannot negate value of type {a.type}")
    
    # Handle actual negation
    try:
        # Number negation
        if isinstance(a.type, CtyNumber):
            num_a = Decimal(str(a.value))
            result = -num_a
            logger.debug(f"🧮❓✅ Number negation result: {result}")
            return Value(CtyNumber(), result)
        
        # Boolean negation
        elif isinstance(a.type, CtyBool):
            result = not a.value
            logger.debug(f"🧮❓✅ Boolean negation result: {result}")
            return Value(CtyBool(), result)
        
        # Unsupported type
        else:
            raise TypeError(f"Cannot negate value of type {a.type}")
            
    except Exception as e:
        if isinstance(e, TypeError) and "Cannot negate" in str(e):
            # Re-raise validation errors
            raise
        
        logger.error(f"🧮❓❌ Error negating value: {e}", exc_info=True)
        raise CtyError(f"Error negating value: {e}") from e


def get_attribute(obj: Value, name: str) -> Value:
    """
    Get an attribute from an object.
    
    Args:
        obj: Object value
        name: Attribute name
        
    Returns:
        Attribute value
        
    Raises:
        TypeError: If obj is not an object type
        AttributeError: If the attribute does not exist
    """
    logger.debug(f"🧮🔍✅ Getting attribute '{name}' from {obj}")
    
    # Handle unknown values
    if not obj.is_known:
        # For unknown objects, return an unknown of the attribute type
        # (if we can determine it)
        if isinstance(obj.type, CtyObject):
            if name in obj.type.attribute_types:
                attr_type = obj.type.attribute_types[name]
                return Value.unknown(attr_type)
            else:
                raise AttributeError(f"Unknown object has no attribute '{name}'")
        else:
            raise TypeError(f"Cannot get attribute from non-object type {obj.type}")
    
    # Handle null values
    if obj.is_null:
        if isinstance(obj.type, CtyObject):
            if name in obj.type.attribute_types:
                attr_type = obj.type.attribute_types[name]
                return Value.null(attr_type)
            else:
                raise AttributeError(f"Object has no attribute '{name}'")
        else:
            raise TypeError(f"Cannot get attribute from non-object type {obj.type}")
    
    # Only attributes of objects are supported
    if isinstance(obj.type, CtyObject):
        try:
            # Get object attributes
            obj_value = cast(Dict[str, Any], obj.value)
            
            # Check if the attribute exists in the type definition
            if name not in obj.type.attribute_types:
                raise AttributeError(f"Object has no attribute '{name}'")
            
            # Get the attribute type
            attr_type = obj.type.attribute_types[name]
            
            # Get the attribute value
            if name in obj_value:
                attr_value = obj_value[name]
                logger.debug(f"🧮🔍✅ Got attribute value: {attr_value}")
                return Value(attr_type, attr_value)
            else:
                # If the attribute is in the type but not in the value,
                # it might be optional - return null
                logger.debug(f"🧮🔍✅ Attribute not found in value, returning null")
                return Value.null(attr_type)
                
        except Exception as e:
            if isinstance(e, AttributeError):
                # Re-raise attribute errors
                raise
            
            logger.error(f"🧮🔍❌ Error getting attribute: {e}", exc_info=True)
            raise CtyError(f"Error getting attribute: {e}") from e
    else:
        raise TypeError(f"Cannot get attribute from non-object type {obj.type}")


def get_element(collection: Value, index: Union[Value, int, str]) -> Value:
    """
    Get an element from a collection.
    
    Args:
        collection: Collection value (list, map, tuple)
        index: Element index or key
        
    Returns:
        Element value
        
    Raises:
        TypeError: If collection is not a suitable type
        KeyError: If the key does not exist in a map
        IndexError: If the index is out of range for a list/tuple
    """
    logger.debug(f"🧮🔢✅ Getting element at {index} from {collection}")
    
    # Convert index to Value if it's not already
    if not isinstance(index, Value):
        if isinstance(index, int) and (
            isinstance(collection.type, CtyList) or 
            isinstance(collection.type, CtyTuple)
        ):
            index = Value(CtyNumber(), index)
        elif isinstance(index, str) and isinstance(collection.type, CtyMap):
            index = Value(CtyString(), index)
        else:
            raise TypeError(f"Invalid index type: {type(index).__name__}")
    
    # Handle unknown collection
    if not collection.is_known:
        # For unknown collections, return an unknown of the element type
        # (if we can determine it)
        if isinstance(collection.type, CtyList):
            return Value.unknown(collection.type.element_type)
        elif isinstance(collection.type, CtyMap):
            return Value.unknown(collection.type.element_type)
        elif isinstance(collection.type, CtyTuple):
            # For tuples, we need to check if the index is a known number
            if isinstance(index.type, CtyNumber) and index.is_known:
                try:
                    idx = int(index.value)
                    if 0 <= idx < len(collection.type.element_types):
                        return Value.unknown(collection.type.element_types[idx])
                except (ValueError, TypeError):
                    pass
            # If we can't determine the element type, return unknown dynamic
            return Value.unknown(CtyDynamic())
        else:
            raise TypeError(f"Cannot get element from type {collection.type}")
    
    # Handle null collection
    if collection.is_null:
        # Accessing elements of null always results in null
        if isinstance(collection.type, CtyList):
            return Value.null(collection.type.element_type)
        elif isinstance(collection.type, CtyMap):
            return Value.null(collection.type.element_type)
        elif isinstance(collection.type, CtyTuple):
            # For tuples, we need to determine the element type
            if isinstance(index.type, CtyNumber) and index.is_known:
                try:
                    idx = int(index.value)
                    if 0 <= idx < len(collection.type.element_types):
                        return Value.null(collection.type.element_types[idx])
                except (ValueError, TypeError):
                    pass
            # If we can't determine the element type, return null dynamic
            return Value.null(CtyDynamic())
        else:
            raise TypeError(f"Cannot get element from type {collection.type}")
    
    # Handle unknown index for known collection
    if not index.is_known:
        # For unknown indices, return an unknown of the element type
        if isinstance(collection.type, CtyList):
            return Value.unknown(collection.type.element_type)
        elif isinstance(collection.type, CtyMap):
            return Value.unknown(collection.type.element_type)
        elif isinstance(collection.type, CtyTuple):
            # For tuples, we need a known index to determine element type
            return Value.unknown(CtyDynamic())
        else:
            raise TypeError(f"Cannot get element from type {collection.type}")
    
    # Handle null index
    if index.is_null:
        raise ValueError("Cannot use null as an index")
    
    # Handle actual element access
    try:
        # List element access
        if isinstance(collection.type, CtyList):
            # Ensure index is a number
            if not isinstance(index.type, CtyNumber):
                raise TypeError(f"List index must be a number, got {index.type}")
            
            # Convert index to integer
            try:
                idx = int(index.value)
            except (ValueError, TypeError):
                raise TypeError(f"List index must be an integer, got {index.value}")
            
            # Get the list value
            list_value = cast(List[Any], collection.value)
            
            # Check bounds
            if idx < 0 or idx >= len(list_value):
                raise IndexError(f"List index {idx} out of range (0-{len(list_value)-1})")
            
            # Get the element
            element = list_value[idx]
            logger.debug(f"🧮🔢✅ Got list element: {element}")
            return Value(collection.type.element_type, element)
        
        # Map element access
        elif isinstance(collection.type, CtyMap):
            # Ensure index is a string
            if not isinstance(index.type, CtyString):
                raise TypeError(f"Map key must be a string, got {index.type}")
            
            # Get the key
            key = str(index.value)
            
            # Get the map value
            map_value = cast(Dict[str, Any], collection.value)
            
            # Check if key exists
            if key not in map_value:
                raise KeyError(f"Map does not contain key '{key}'")
            
            # Get the element
            element = map_value[key]
            logger.debug(f"🧮🔢✅ Got map element: {element}")
            return Value(collection.type.element_type, element)
        
        # Tuple element access
        elif isinstance(collection.type, CtyTuple):
            # Ensure index is a number
            if not isinstance(index.type, CtyNumber):
                raise TypeError(f"Tuple index must be a number, got {index.type}")
            
            # Convert index to integer
            try:
                idx = int(index.value)
            except (ValueError, TypeError):
                raise TypeError(f"Tuple index must be an integer, got {index.value}")
            
            # Get the tuple value
            tuple_value = collection.value
            
            # Check bounds
            if idx < 0 or idx >= len(tuple_value):
                raise IndexError(f"Tuple index {idx} out of range (0-{len(tuple_value)-1})")
            
            # Get the element type and value
            element_type = collection.type.element_types[idx]
            element = tuple_value[idx]
            logger.debug(f"🧮🔢✅ Got tuple element: {element}")
            return Value(element_type, element)
        
        # Unsupported type
        else:
            raise TypeError(f"Cannot get element from type {collection.type}")
            
    except Exception as e:
        if isinstance(e, (TypeError, ValueError, KeyError, IndexError)):
            # Re-raise validation errors
            raise
        
        logger.error(f"🧮🔢❌ Error getting element: {e}", exc_info=True)
        raise CtyError(f"Error getting element: {e}") from e


def length(collection: Value) -> Value:
    """
    Get the length of a collection.
    
    Args:
        collection: Collection value (string, list, map, set, tuple)
        
    Returns:
        Length as a number value
        
    Raises:
        TypeError: If collection is not a suitable type
    """
    logger.debug(f"🧮📏✅ Getting length of {collection}")
    
    # Handle unknown values
    if not collection.is_known:
        return Value.unknown(CtyNumber())
    
    # Handle null values
    if collection.is_null:
        return Value.null(CtyNumber())
    
    # Handle actual length calculation
    try:
        # String length
        if isinstance(collection.type, CtyString):
            result = len(str(collection.value))
            logger.debug(f"🧮📏✅ String length: {result}")
            return Value(CtyNumber(), result)
        
        # List length
        elif isinstance(collection.type, CtyList):
            list_value = cast(List[Any], collection.value)
            result = len(list_value)
            logger.debug(f"🧮📏✅ List length: {result}")
            return Value(CtyNumber(), result)
        
        # Map length
        elif isinstance(collection.type, CtyMap):
            map_value = cast(Dict[str, Any], collection.value)
            result = len(map_value)
            logger.debug(f"🧮📏✅ Map length: {result}")
            return Value(CtyNumber(), result)
        
        # Set length
        elif isinstance(collection.type, CtySet):
            set_value = cast(Set[Any], collection.value)
            result = len(set_value)
            logger.debug(f"🧮📏✅ Set length: {result}")
            return Value(CtyNumber(), result)
        
        # Tuple length
        elif isinstance(collection.type, CtyTuple):
            tuple_value = collection.value
            result = len(tuple_value)
            logger.debug(f"🧮📏✅ Tuple length: {result}")
            return Value(CtyNumber(), result)
        
        # Unsupported type
        else:
            raise TypeError(f"Cannot get length of type {collection.type}")
            
    except Exception as e:
        if isinstance(e, TypeError) and "Cannot get length" in str(e):
            # Re-raise validation errors
            raise
        
        logger.error(f"🧮📏❌ Error getting length: {e}", exc_info=True)
        raise CtyError(f"Error getting length: {e}") from e


def contains(collection: Value, item: Value) -> Value:
    """
    Check if a collection contains an item.
    
    Args:
        collection: Collection value (string, list, map, set)
        item: Item to check for
        
    Returns:
        Boolean value indicating if the item is in the collection
        
    Raises:
        TypeError: If collection is not a suitable type
    """
    logger.debug(f"🧮🔎✅ Checking if {collection} contains {item}")
    
    # Handle unknown values
    if not collection.is_known or not item.is_known:
        return Value.unknown(CtyBool())
    
    # Handle null values
    if collection.is_null or item.is_null:
        return Value.null(CtyBool())
    
    # Handle actual containment check
    try:
        # String containment
        if isinstance(collection.type, CtyString):
            # Ensure item is a string
            if not isinstance(item.type, CtyString):
                raise TypeError(f"String can only contain strings, got {item.type}")
            
            collection_str = str(collection.value)
            item_str = str(item.value)
            result = item_str in collection_str
            logger.debug(f"🧮🔎✅ String containment result: {result}")
            return Value(CtyBool(), result)
        
        # List containment
        elif isinstance(collection.type, CtyList):
            # Check if item type is compatible with list element type
            if not item.type.equal(collection.type.element_type):
                # If types don't match, it cannot be in the list
                return Value(CtyBool(), False)
            
            list_value = cast(List[Any], collection.value)
            
            # We need to perform a deep equals check for each element
            for elem in list_value:
                elem_value = Value(collection.type.element_type, elem)
                eq_result = equals(elem_value, item)
                
                if eq_result.is_known and eq_result.value:
                    # Found a match
                    return Value(CtyBool(), True)
            
            # No match found
            return Value(CtyBool(), False)
        
        # Map containment (key check)
        elif isinstance(collection.type, CtyMap):
            # Ensure item is a string (map keys are always strings)
            if not isinstance(item.type, CtyString):
                raise TypeError(f"Map keys can only be strings, got {item.type}")
            
            map_value = cast(Dict[str, Any], collection.value)
            result = str(item.value) in map_value
            logger.debug(f"🧮🔎✅ Map key containment result: {result}")
            return Value(CtyBool(), result)
        
        # Set containment
        elif isinstance(collection.type, CtySet):
            # Check if item type is compatible with set element type
            if not item.type.equal(collection.type.element_type):
                # If types don't match, it cannot be in the set
                return Value(CtyBool(), False)
            
            set_value = cast(Set[Any], collection.value)
            
            # We need to perform a deep equals check for each element
            for elem in set_value:
                elem_value = Value(collection.type.element_type, elem)
                eq_result = equals(elem_value, item)
                
                if eq_result.is_known and eq_result.value:
                    # Found a match
                    return Value(CtyBool(), True)
            
            # No match found
            return Value(CtyBool(), False)
        
        # Unsupported type
        else:
            raise TypeError(f"Cannot check containment in type {collection.type}")
            
    except Exception as e:
        if isinstance(e, TypeError) and "Cannot check containment" in str(e):
            # Re-raise validation errors
            raise
        
        logger.error(f"🧮🔎❌ Error checking containment: {e}", exc_info=True)
        raise CtyError(f"Error checking containment: {e}") from e


def concat_lists(*lists: Value) -> Value:
    """
    Concatenate multiple lists into a single list.
    
    Args:
        *lists: List values to concatenate
        
    Returns:
        Concatenated list value
        
    Raises:
        TypeError: If any argument is not a list type
        ValueError: If lists have incompatible element types
    """
    logger.debug(f"🧮🔗✅ Concatenating {len(lists)} lists")
    
    if not lists:
        # No lists provided - return an empty list with dynamic element type
        logger.debug("🧮🔗✅ No lists provided, returning empty list")
        return Value(CtyList(element_type=CtyDynamic()), [])
    
    # Determine the element type from the first non-null, known list
    element_type = None
    for lst in lists:
        if not isinstance(lst.type, CtyList):
            raise TypeError(f"Expected list type, got {lst.type}")
        
        if lst.is_known and not lst.is_null:
            element_type = lst.type.element_type
            break
    
    # If all lists are null or unknown, use the first list's element type
    if element_type is None:
        element_type = lists[0].type.element_type
    
    # Check for unknowns and nulls
    has_unknown = False
    all_null = True
    
    for lst in lists:
        if not isinstance(lst.type, CtyList):
            raise TypeError(f"Expected list type, got {lst.type}")
        
        # Check element type compatibility
        if not lst.type.element_type.equal(element_type):
            raise ValueError(f"List element types don't match: {lst.type.element_type} vs {element_type}")
        
        if not lst.is_known:
            has_unknown = True
        
        if not lst.is_null:
            all_null = False
    
    # Handle special cases
    if has_unknown:
        return Value.unknown(CtyList(element_type=element_type))
    
    if all_null:
        return Value.null(CtyList(element_type=element_type))
    
    # Concatenate the lists
    try:
        result = []
        for lst in lists:
            if not lst.is_null:
                list_value = cast(List[Any], lst.value)
                result.extend(list_value)
        
        logger.debug(f"🧮🔗✅ Concatenated list result length: {len(result)}")
        return Value(CtyList(element_type=element_type), result)
        
    except Exception as e:
        logger.error(f"🧮🔗❌ Error concatenating lists: {e}", exc_info=True)
        raise CtyError(f"Error concatenating lists: {e}") from e


def merge_maps(*maps: Value) -> Value:
    """
    Merge multiple maps into a single map.
    
    Args:
        *maps: Map values to merge
        
    Returns:
        Merged map value
        
    Raises:
        TypeError: If any argument is not a map type
        ValueError: If maps have incompatible element types
    """
    logger.debug(f"🧮🔀✅ Merging {len(maps)} maps")
    
    if not maps:
        # No maps provided - return an empty map with dynamic element type
        logger.debug("🧮🔀✅ No maps provided, returning empty map")
        return Value(CtyMap(element_type=CtyDynamic()), {})
    
    # Determine the element type from the first non-null, known map
    element_type = None
    for map_val in maps:
        if not isinstance(map_val.type, CtyMap):
            raise TypeError(f"Expected map type, got {map_val.type}")
        
        if map_val.is_known and not map_val.is_null:
            element_type = map_val.type.element_type
            break
    
    # If all maps are null or unknown, use the first map's element type
    if element_type is None:
        element_type = maps[0].type.element_type
    
    # Check for unknowns and nulls
    has_unknown = False
    all_null = True
    
    for map_val in maps:
        if not isinstance(map_val.type, CtyMap):
            raise TypeError(f"Expected map type, got {map_val.type}")
        
        # Check element type compatibility
        if not map_val.type.element_type.equal(element_type):
            raise ValueError(f"Map element types don't match: {map_val.type.element_type} vs {element_type}")
        
        if not map_val.is_known:
            has_unknown = True
        
        if not map_val.is_null:
            all_null = False
    
    # Handle special cases
    if has_unknown:
        return Value.unknown(CtyMap(element_type=element_type))
    
    if all_null:
        return Value.null(CtyMap(element_type=element_type))
    
    # Merge the maps
    try:
        result = {}
        for map_val in maps:
            if not map_val.is_null:
                map_value = cast(Dict[str, Any], map_val.value)
                # Later maps override earlier ones for duplicate keys
                result.update(map_value)
        
        logger.debug(f"🧮🔀✅ Merged map result size: {len(result)}")
        return Value(CtyMap(element_type=element_type), result)
        
    except Exception as e:
        logger.error(f"🧮🔀❌ Error merging maps: {e}", exc_info=True)
        raise CtyError(f"Error merging maps: {e}") from e


def slice_string(str_val: Value, start_idx: Value, end_idx: Optional[Value] = None) -> Value:
    """
    Extract a substring from a string.
    
    Args:
        str_val: String value
        start_idx: Start index (inclusive)
        end_idx: End index (exclusive, optional)
        
    Returns:
        Sliced string value
        
    Raises:
        TypeError: If str_val is not a string or indices are not numbers
        IndexError: If indices are out of range
    """
    logger.debug(f"🧮✂️✅ Slicing string {str_val} from {start_idx} to {end_idx}")
    
    # Check types
    if not isinstance(str_val.type, CtyString):
        raise TypeError(f"Expected string type, got {str_val.type}")
    
    if not isinstance(start_idx.type, CtyNumber):
        raise TypeError(f"Expected number type for start index, got {start_idx.type}")
    
    if end_idx is not None and not isinstance(end_idx.type, CtyNumber):
        raise TypeError(f"Expected number type for end index, got {end_idx.type}")
    
    # Handle unknown values
    if not str_val.is_known or not start_idx.is_known or (end_idx is not None and not end_idx.is_known):
        return Value.unknown(CtyString())
    
    # Handle null values
    if str_val.is_null or start_idx.is_null or (end_idx is not None and end_idx.is_null):
        return Value.null(CtyString())
    
    # Get the string value
    string = str(str_val.value)
    
    # Get the start index
    try:
        start = int(start_idx.value)
    except (ValueError, TypeError):
        raise TypeError(f"Start index must be an integer, got {start_idx.value}")
    
    # Get the end index
    if end_idx is not None:
        try:
            end = int(end_idx.value)
        except (ValueError, TypeError):
            raise TypeError(f"End index must be an integer, got {end_idx.value}")
    else:
        end = len(string)
    
    # Check bounds
    if start < 0 or start > len(string):
        raise IndexError(f"Start index {start} out of range (0-{len(string)})")
    
    if end < start or end > len(string):
        raise IndexError(f"End index {end} out of range ({start}-{len(string)})")
    
    # Slice the string
    try:
        result = string[start:end]
        logger.debug(f"🧮✂️✅ String slice result: {result}")
        return Value(CtyString(), result)
    except Exception as e:
        logger.error(f"🧮✂️❌ Error slicing string: {e}", exc_info=True)
        raise CtyError(f"Error slicing string: {e}") from e


def slice_list(list_val: Value, start_idx: Value, end_idx: Optional[Value] = None) -> Value:
    """
    Extract a slice from a list.
    
    Args:
        list_val: List value
        start_idx: Start index (inclusive)
        end_idx: End index (exclusive, optional)
        
    Returns:
        Sliced list value
        
    Raises:
        TypeError: If list_val is not a list or indices are not numbers
        IndexError: If indices are out of range
    """
    logger.debug(f"🧮✂️✅ Slicing list {list_val} from {start_idx} to {end_idx}")
    
    # Check types
    if not isinstance(list_val.type, CtyList):
        raise TypeError(f"Expected list type, got {list_val.type}")
    
    if not isinstance(start_idx.type, CtyNumber):
        raise TypeError(f"Expected number type for start index, got {start_idx.type}")
    
    if end_idx is not None and not isinstance(end_idx.type, CtyNumber):
        raise TypeError(f"Expected number type for end index, got {end_idx.type}")
    
    # Handle unknown values
    if not list_val.is_known or not start_idx.is_known or (end_idx is not None and not end_idx.is_known):
        return Value.unknown(CtyList(element_type=list_val.type.element_type))
    
    # Handle null values
    if list_val.is_null or start_idx.is_null or (end_idx is not None and end_idx.is_null):
        return Value.null(CtyList(element_type=list_val.type.element_type))
    
    # Get the list value
    list_value = cast(List[Any], list_val.value)
    
    # Get the start index
    try:
        start = int(start_idx.value)
    except (ValueError, TypeError):
        raise TypeError(f"Start index must be an integer, got {start_idx.value}")
    
    # Get the end index
    if end_idx is not None:
        try:
            end = int(end_idx.value)
        except (ValueError, TypeError):
            raise TypeError(f"End index must be an integer, got {end_idx.value}")
    else:
        end = len(list_value)
    
    # Check bounds
    if start < 0 or start > len(list_value):
        raise IndexError(f"Start index {start} out of range (0-{len(list_value)})")
    
    if end < start or end > len(list_value):
        raise IndexError(f"End index {end} out of range ({start}-{len(list_value)})")
    
    # Slice the list
    try:
        result = list_value[start:end]
        logger.debug(f"🧮✂️✅ List slice result length: {len(result)}")
        return Value(CtyList(element_type=list_val.type.element_type), result)
    except Exception as e:
        logger.error(f"🧮✂️❌ Error slicing list: {e}", exc_info=True)
        raise CtyError(f"Error slicing list: {e}") from e
