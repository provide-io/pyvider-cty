#
# pyvider/cty/values/base.py
#

"""
CtyValue represents a value with its corresponding type in the Cty type system.

This module provides the core value representation that combines a value with its
type, along with additional metadata like whether the value is known or null.
"""
from decimal import Decimal
from typing import Any, FrozenSet, Generic, Iterator, Optional, Self, Tuple, TypeVar, Union, cast

from attrs import define, field, evolve

from pyvider.cty.logger import logger
from pyvider.cty.types import CtyType


T = TypeVar('T', covariant=True)


# @define(frozen=True, slots=True)
@define(slots=True)
class CtyValue(Generic[T]):
    """
    Immutable representation of a Cty value.

    A CtyValue combines a raw value with its type and metadata such as whether
    the value is known (vs unknown) or null. This follows the Go-CTY value model.

    CtyValue is the fundamental unit in the Cty type system. All operations preserve
    type information by returning new CtyValue instances rather than raw values.
    
    Attributes:
        _type: The Cty type of this value
        _value: The raw value (or None for null/unknown values)
        _is_unknown: Whether this value is unknown
        _is_null: Whether this value is null
        _marks: Set of marks applied to this value
    """
    # Core attributes
    _type: CtyType[T] = field(alias="type_")
    _value: Any = field(default=None)
    _is_unknown: bool = field(default=False)
    _is_null: bool = field(default=False)
    _marks: FrozenSet = field(factory=frozenset)
    _key_mapping: dict[str, "CtyValue"] = field(factory=dict)


    def __attrs_post_init__(self) -> None:
        """Log info about created CtyValue."""
        logger.debug(f"🔄🔧✅ Creating CtyValue of type {self._type.__class__.__name__}")

    # -------------------------------------------------------------------------
    # Backward compatibility factory - handles type_/_type naming differences
    # -------------------------------------------------------------------------
    @classmethod
    def __new__(cls, *args, **kwargs):
        """
        Create a new CtyValue instance, handling backward compatibility.
        
        This method ensures the class works with both old-style parameter names
        (type_) and new-style parameter names (_type).
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            A new CtyValue instance
        """
        # Handle type_ vs _type parameter
        if 'type_' in kwargs and '_type' not in kwargs:
            kwargs['_type'] = kwargs.pop('type_')
        
        # Handle value vs _value parameter  
        if 'value' in kwargs and '_value' not in kwargs:
            kwargs['_value'] = kwargs.pop('value')
            
        # Handle is_null vs _is_null parameter
        if 'is_null' in kwargs and '_is_null' not in kwargs:
            kwargs['_is_null'] = kwargs.pop('is_null')
            
        # Handle is_unknown vs _is_unknown parameter
        if 'is_unknown' in kwargs and '_is_unknown' not in kwargs:
            kwargs['_is_unknown'] = kwargs.pop('is_unknown')
            
        # Handle marks vs _marks parameter
        if 'marks' in kwargs and '_marks' not in kwargs:
            kwargs['_marks'] = kwargs.pop('marks')
        
        # Convert positional args to keyword args
        if args and len(args) >= 1 and '_type' not in kwargs:
            kwargs['_type'] = args[0]
            args = args[1:]
            if args and len(args) >= 1 and '_value' not in kwargs:
                kwargs['_value'] = args[0]
                args = args[1:]
        
        return super().__new__(cls)

    # -------------------------------------------------------------------------
    # Property accessors for backward compatibility
    # -------------------------------------------------------------------------
    @property
    def type(self) -> CtyType[T]:
        """Get the type of this value."""
        return self._type

    @property
    def value(self) -> Any:
        """
        Get the raw value of this CtyValue.

        Returns:
            The raw value

        Raises:
            ValueError: If this value is unknown
        """
        if self._is_unknown:
            logger.warning("🔄❗⚠️ Attempted to get raw value of unknown value")
            raise ValueError("Cannot get raw value of unknown value")
        if self._is_null:
            logger.warning("🔄❗⚠️ Attempted to get raw value of null value")
            return None
        return self._value

    @property
    def is_known(self) -> bool:
        """Check if this value is known (not unknown)."""
        return not self._is_unknown

    @property
    def is_unknown(self) -> bool:
        """Check if this value is unknown."""
        return self._is_unknown

    @property
    def is_null(self) -> bool:
        """Check if this value is null."""
        return self._is_null

    def has_mark(self, mark: Any) -> bool:
        """
        Check if this value has a specific mark.

        Args:
            mark: The mark to check for

        Returns:
            bool: True if the value has the mark
        """
        # Use string equality rather than identity for more flexible comparison
        mark_str = str(mark)
        for m in self._marks:
            if str(m) == mark_str:
                return True
        return False

    # -------------------------------------------------------------------------
    # Value modification methods
    # -------------------------------------------------------------------------
    def mark(self, mark: Any) -> Self:
        """
        Add a mark to this value.

        Args:
            mark: The mark to add

        Returns:
            A new CtyValue with the mark added
        """
        logger.debug(f"🔄🔧✅ Adding mark {mark} to value")
        return evolve(
            self,
            marks=frozenset(self._marks.union({mark}))
        )

    def unmark(self) -> Tuple[Self, FrozenSet]:
        """
        Remove all marks from this value and return them.

        Returns:
            tuple: (Unmarked value, Set of removed marks)
        """
        logger.debug(f"🔄🔧✅ Removing {len(self._marks)} marks from value")
        return evolve(self, marks=frozenset()), self._marks

    # -------------------------------------------------------------------------
    # Container operations
    # -------------------------------------------------------------------------
    def get(self, key: Any, default: Any = None) -> "CtyValue":
        """
        Get a value by key, with a default if not found.

        Args:
            key: The key to look up
            default: Value to return if key not found

        Returns:
            CtyValue: The retrieved value as a CtyValue, or the default

        Raises:
            TypeError: If the value doesn't support key lookup
        """
        logger.debug(f"🔄🔍🔄 Getting value for key: {key}")

        # Cannot get from unknown or null values
        if self._is_unknown or self._is_null:
            logger.debug(f"🔄🔍⚠️ Cannot get from unknown/null value, returning default")
            return default

        # Import locally to avoid circular imports
        from pyvider.cty.types.collections import CtyMap
        from pyvider.cty.types.structural import CtyObject

        # For maps, use the map's get method
        if isinstance(self._type, CtyMap):
            try:
                return self._type.get(self, key, default)
            except Exception as e:
                logger.debug(f"🔄🔍⚠️ Map get failed: {e}")
                return default

        # For objects, use the object's get_attribute method
        elif isinstance(self._type, CtyObject):
            try:
                if self._type.has_attribute(key):
                    return self._type.get_attribute(self, key)
                return default
            except Exception as e:
                logger.debug(f"🔄🔍⚠️ Object attribute access failed: {e}")
                return default

        # Value doesn't support key lookup
        logger.debug(f"🔄🔍⚠️ get() called on unsupported type: {self._type.__class__.__name__}")
        return default

    def set(self, key: Any, value: Any) -> Self:
        """
        Set a value in a container.

        This operation is immutable - it returns a new CtyValue with the updated container.

        Args:
            key: The key to set
            value: The value to set

        Returns:
            CtyValue: A new CtyValue with the updated container

        Raises:
            TypeError: If the value doesn't support key setting
        """
        logger.debug(f"🔄📝🔄 Setting key {key} to value {value}")

        # Cannot set on unknown or null values
        if self._is_unknown or self._is_null:
            error_msg = f"Cannot set key on unknown/null value"
            logger.error(f"🔄❗❌ {error_msg}")
            raise TypeError(error_msg)

        # Import locally to avoid circular imports
        from pyvider.cty.types.collections import CtyMap

        # For maps, use the map's set method
        if isinstance(self._type, CtyMap):
            new_value = self._type.set(self, key, value)
            return new_value

        # Value doesn't support key setting
        error_msg = f"set() method not supported for type {self._type.__class__.__name__}"
        logger.error(f"🔄❗❌ {error_msg}")
        raise TypeError(error_msg)

    def delete(self, key: Any) -> Self:
        """
        Delete a key from a container.

        This operation is immutable - it returns a new CtyValue with the updated container.

        Args:
            key: The key to delete

        Returns:
            CtyValue: A new CtyValue with the updated container

        Raises:
            TypeError: If the value doesn't support key deletion
        """
        logger.debug(f"🔄📝🔄 Deleting key {key}")

        # Cannot delete on unknown or null values
        if self._is_unknown or self._is_null:
            error_msg = f"Cannot delete key from unknown/null value"
            logger.error(f"🔄❗❌ {error_msg}")
            raise TypeError(error_msg)

        # Import locally to avoid circular imports
        from pyvider.cty.types.collections import CtyMap

        # For maps, use the map's delete method
        if isinstance(self._type, CtyMap):
            new_value = self._type.delete(self, key)
            return new_value

        # Value doesn't support key deletion
        error_msg = f"delete() method not supported for type {self._type.__class__.__name__}"
        logger.error(f"🔄❗❌ {error_msg}")
        raise TypeError(error_msg)

    def element_at(self, index: int) -> "CtyValue":
        """
        Get element at a specific index for list/tuple values.

        Args:
            index: The index to get the element at

        Returns:
            CtyValue: The element at that index as a CtyValue

        Raises:
            TypeError: If the value doesn't support indexing
            IndexError: If the index is out of bounds
        """
        logger.debug(f"🔄🔍🔄 Getting element at index {index}")

        # Cannot index into unknown or null values
        if self._is_unknown or self._is_null:
            error_msg = "Cannot get element from unknown or null value"
            logger.error(f"🔄❗❌ {error_msg}")
            raise TypeError(error_msg)

        # Import locally to avoid circular imports
        from pyvider.cty.types.collections import CtyList
        from pyvider.cty.types.structural import CtyTuple

        # Direct implementation to avoid recursion with __getitem__
        if isinstance(self._type, CtyList):
            # Handle negative indices
            if index < 0:
                index = len(self._value) + index

            # Check bounds
            if index < 0 or index >= len(self._value):
                error_msg = f"Index {index} out of bounds (0-{len(self._value)-1})"
                logger.error(f"🔄❗❌ {error_msg}")
                raise IndexError(error_msg)

            # Get the element at the specified index
            return self._value[index]
        elif isinstance(self._type, CtyTuple):
            return self._type.element_at(self._value, index)
        else:
            # Value doesn't support indexing
            error_msg = f"element_at method not supported for type {self._type.__class__.__name__}"
            logger.error(f"🔄❗❌ {error_msg}")
            raise TypeError(error_msg)

    # -------------------------------------------------------------------------
    # Factory methods
    # -------------------------------------------------------------------------
    @classmethod
    def bool(cls, value: bool) -> "CtyValue":
        """
        Create a boolean value.

        Args:
            value: The boolean value

        Returns:
            A new CtyValue with the boolean value
        """
        from pyvider.cty.types import CtyBool
        
        logger.debug(f"🔄🔧✅ Creating bool value: {value}")
        return cls(type_=CtyBool(), value=value)

    @classmethod
    def string(cls, value: str) -> "CtyValue":
        """
        Create a string value.

        Args:
            value: The string value

        Returns:
            A new CtyValue with the string value
        """
        from pyvider.cty.types import CtyString
        
        logger.debug(f"🔄🔧✅ Creating string value: {value}")
        return cls(type_=CtyString(), value=value)

    @classmethod
    def number(cls, value: Union[int, float, Decimal]) -> "CtyValue":
        """
        Create a number value.

        Args:
            value: The number value (int, float, or Decimal)

        Returns:
            A new CtyValue with the number value
        """
        from pyvider.cty.types import CtyNumber
        
        logger.debug(f"🔄🔧✅ Creating number value: {value}")
        return cls(type_=CtyNumber(), value=value)

    @classmethod
    def list(cls, element_type: CtyType, elements: list) -> "CtyValue":
        """
        Create a list value.

        Args:
            element_type: The type of the list elements
            elements: The list elements

        Returns:
            A new CtyValue with the list
        """
        from pyvider.cty.types import CtyList

        logger.debug(f"🔄🔧✅ Creating list value with {len(elements)} elements")
        # Create list type and validate the elements
        list_type = CtyList(element_type=element_type)
        return list_type.validate(elements)

    @classmethod
    def map(cls, key_type: CtyType, value_type: CtyType, items: dict) -> "CtyValue":
        """
        Create a map value.

        Args:
            key_type: The type of map keys
            value_type: The type of map values
            items: The map items

        Returns:
            A new CtyValue with the map
        """
        from pyvider.cty.types import CtyMap

        logger.debug(f"🔄🔧✅ Creating map value with {len(items)} items")
        # Create map type and validate the items
        map_type = CtyMap(key_type=key_type, value_type=value_type)
        return map_type.validate(items)

    @classmethod
    def set(cls, element_type: CtyType, elements: set) -> "CtyValue":
        """
        Create a set value.

        Args:
            element_type: The type of the set elements
            elements: The set elements

        Returns:
            A new CtyValue with the set
        """
        from pyvider.cty.types import CtySet

        logger.debug(f"🔄🔧✅ Creating set value with {len(elements)} elements")
        # Create set type and validate the elements
        set_type = CtySet(element_type=element_type)
        return set_type.validate(elements)

    @classmethod
    def tuple(cls, element_types: tuple, elements: tuple) -> "CtyValue":
        """
        Create a tuple value.

        Args:
            element_types: The types of the tuple elements
            elements: The tuple elements

        Returns:
            A new CtyValue with the tuple
        """
        from pyvider.cty.types import CtyTuple

        logger.debug(f"🔄🔧✅ Creating tuple value with {len(elements)} elements")
        # Create tuple type and validate the elements
        tuple_type = CtyTuple(element_types=element_types)
        return tuple_type.validate(elements)

    @classmethod
    def object(cls, attribute_types: dict, attributes: dict) -> "CtyValue":
        """
        Create an object value.
        
        Args:
            attribute_types: Dictionary mapping attribute names to their types
            attributes: Dictionary of attribute values
            
        Returns:
            A new CtyValue with the object
            
        Raises:
            CtyValidationError: If validation fails
        """
        from pyvider.cty.types import CtyObject
        from pyvider.cty.exceptions import CtyValidationError

        logger.debug(f"🔄🔧✅ Creating object value with {len(attributes)} attributes")
        # Validate attribute_types contains CtyType instances
        for attr_name, attr_type in attribute_types.items():
            if not isinstance(attr_type, CtyType):
                raise CtyValidationError(f"Expected CtyType for attribute '{attr_name}', got {type(attr_type).__name__}")

        # Create object type and validate
        object_type = CtyObject(attribute_types=attribute_types)
        return object_type.validate(attributes)

    @classmethod
    def unknown(cls, type_: CtyType) -> "CtyValue":
        """
        Create an unknown value of the given type.

        Args:
            type_: The type of the unknown value

        Returns:
            A new CtyValue marked as unknown
        """
        logger.debug(f"🔄🔧✅ Creating unknown value of type {type_.__class__.__name__}")
        return cls(type_=type_, is_unknown=True)

    @classmethod
    def null(cls, type_: CtyType) -> "CtyValue":
        """
        Create a null value of the given type.

        Args:
            type_: The type of the null value

        Returns:
            A new CtyValue marked as null
        """
        logger.debug(f"🔄🔧✅ Creating null value of type {type_.__class__.__name__}")
        return cls(type_=type_, is_null=True)

    # -------------------------------------------------------------------------
    # Serialization
    # -------------------------------------------------------------------------
    def to_dict(self) -> dict:
        """
        Convert to dictionary representation for serialization.

        Returns:
            A dictionary representation of this value
        """
        logger.debug(f"🔄🔧✅ Converting CtyValue to dictionary")
        result = {
            "type": self._type.__class__.__name__,
        }

        # Handle different value types for JSON serialization
        if self._is_unknown:
            result["is_unknown"] = True
        elif self._is_null:
            result["is_null"] = True
        else:
            # Handle collection types
            if isinstance(self._value, (set, frozenset)):
                result["value"] = list(self._value)
            elif isinstance(self._value, dict):
                # For dictionaries, convert keys and values
                serialized_dict = {}
                for k, v in self._value.items():
                    key = k.to_dict() if hasattr(k, 'to_dict') else str(k)
                    value = v.to_dict() if hasattr(v, 'to_dict') else v
                    serialized_dict[str(key)] = value
                result["value"] = serialized_dict
            elif isinstance(self._value, (list, tuple)):
                # For lists/tuples, convert each element
                result["value"] = [
                    v.to_dict() if hasattr(v, 'to_dict') else v
                    for v in self._value
                ]
            elif self._value is not None:
                result["value"] = self._value

        # Add marks if present
        if self._marks:
            result["marks"] = list(str(m) for m in self._marks)

        return result

    # -------------------------------------------------------------------------
    # Python special methods
    # -------------------------------------------------------------------------
    def __len__(self) -> int:
        """
        Get the length of this value, if it supports the operation.

        Returns:
            The length of the value

        Raises:
            TypeError: If the value doesn't support length
        """
        # Cannot get length of unknown values
        if self._is_unknown:
            error_msg = "Cannot get length of unknown value"
            logger.error(f"🔄❗❌ {error_msg}")
            raise TypeError(error_msg)

        # Cannot get length of null values
        if self._is_null:
            error_msg = "Cannot get length of null value"
            logger.error(f"🔄❗❌ {error_msg}")
            raise TypeError(error_msg)

        # For known values, delegate to the underlying value
        if hasattr(self._value, "__len__"):
            return len(self._value)

        # Value doesn't support length
        error_msg = f"Value of type {type(self._value).__name__} doesn't support length operation"
        logger.error(f"🔄❗❌ {error_msg}")
        raise TypeError(error_msg)

    def __iter__(self) -> Iterator:
        """
        Iterate over the elements in this value.

        Returns:
            An iterator over the elements

        Raises:
            TypeError: If the value doesn't support iteration
        """
        # Cannot iterate unknown or null values
        if self._is_unknown:
            error_msg = "Cannot iterate unknown value"
            logger.error(f"🔄❗❌ {error_msg}")
            raise TypeError(error_msg)

        if self._is_null:
            error_msg = "Cannot iterate null value"
            logger.error(f"🔄❗❌ {error_msg}")
            raise TypeError(error_msg)

        # For collections, iterate over the values
        if hasattr(self._value, "__iter__"):
            return iter(self._value)

        # Value doesn't support iteration
        error_msg = f"Value of type {type(self._value).__name__} doesn't support iteration"
        logger.error(f"🔄❗❌ {error_msg}")
        raise TypeError(error_msg)

    def __hash__(self) -> int:
        """
        Make CtyValue instances hashable for use in sets and as dict keys.
        Now incorporates the actual value for primitives.
        
        Returns:
            int: Hash value
        """
        # Hash based on type, value state, marks
        type_hash = hash(self._type.__class__)
        state_hash = hash((self._is_unknown, self._is_null))
        marks_hash = hash(self._marks) # Hash the frozenset of marks

        value_hash = 0
        if self._is_unknown or self._is_null:
            value_hash = hash(None) # Consistent hash for null/unknown
        else:
            # Use the actual value's hash for hashable primitives
            # This is essential for dictionary keys!
            if isinstance(self._value, (str, int, float, bool, Decimal, bytes)):
                try:
                    value_hash = hash(self._value)
                except TypeError: # Should not happen for these types, but safeguard
                    value_hash = hash(repr(self._value))
            # For collections/objects, hashing gets complex. If they are intended
            # as keys, they need a stable hash. Using repr is a fallback.
            # Using only type+state+marks might be safer if values aren't hashable.
            # Let's use repr as a moderately stable fallback for now.
            else:
                try:
                     # For tuples, hash elements recursively? Risky if elements unhashable
                     if isinstance(self._value, tuple):
                         # Simplified: hash tuple representation
                         value_hash = hash(tuple(repr(el) for el in self._value))
                     else: # Fallback for lists, dicts, sets, other objects
                         value_hash = hash(repr(self._value))
                except TypeError:
                     # If repr itself fails or value contains unhashable items
                     value_hash = hash(id(self._value)) # Less ideal, identity hash

        # Combine component hashes
        return hash((type_hash, state_hash, value_hash, marks_hash))

    def __eq__(self, other) -> bool:
        """
        Check if two CtyValue instances are equal.

        Args:
            other: The other value to compare with

        Returns:
            True if the values are equal
        """
        # Direct comparison with native types for primitive values
        if not isinstance(other, CtyValue):
            if self.is_known and not self.is_null and isinstance(self._value, (str, int, float, bool, Decimal)):
                try:
                    return self._value == other
                except Exception:
                    return False
            return False

        # Check type compatibility
        if not isinstance(self._type, type(other._type)):
            return False

        # Check state
        if self._is_unknown != other._is_unknown:
            return False
        if self._is_null != other._is_null:
            return False
        if self._marks != other._marks:
            return False

        # For known, non-null values, compare values
        if self.is_known and not self.is_null and other.is_known and not other.is_null:
            # For primitive values, compare directly
            if isinstance(self._value, (str, int, float, bool, Decimal)):
                return self._value == other._value

            # For collections, compare elements
            if isinstance(self._value, (list, tuple)) and isinstance(other._value, (list, tuple)):
                if len(self._value) != len(other._value):
                    return False
                return all(a == b for a, b in zip(self._value, other._value))

            if isinstance(self._value, (set, frozenset)) and isinstance(other._value, (set, frozenset)):
                if len(self._value) != len(other._value):
                    return False
                # For sets, all elements from self must be in other
                return all(a in other._value for a in self._value)

            if isinstance(self._value, dict) and isinstance(other._value, dict):
                if len(self._value) != len(other._value):
                    return False
                # For dictionaries, compare each key-value pair
                for k1, v1 in self._value.items():
                    found = False
                    for k2, v2 in other._value.items():
                        if k1 == k2:
                            if v1 != v2:
                                return False
                            found = True
                            break
                    if not found:
                        return False
                return True

        # Unknown/null values of the same type are equal
        return True

    def __getitem__(self, key) -> "CtyValue":
        """
        Support for container indexing operations.

        Args:
            key: The key or index

        Returns:
            The value at the key/index

        Raises:
            TypeError: If the value doesn't support indexing
            KeyError: If the key doesn't exist
            IndexError: If the index is out of bounds
        """
        logger.debug(f"🔄🔍🔄 Getting item with key/index: {key}")

        # Cannot index into unknown or null values
        if self._is_unknown or self._is_null:
            error_msg = "Cannot index into unknown or null value"
            logger.error(f"🔄❗❌ {error_msg}")
            raise TypeError(error_msg)

        # Import locally to avoid circular imports
        from pyvider.cty.types.collections import CtyMap, CtyList
        from pyvider.cty.types.structural import CtyObject, CtyTuple
        from pyvider.cty.exceptions import CtyAttributeValidationError

        try:
           # Check for CtyObject type first for specific attribute handling
            if isinstance(self._type, CtyObject):
                if not isinstance(key, str):
                     raise TypeError(f"Object attribute name must be a string, got {type(key).__name__}")
                if not self._type.has_attribute(key):
                    # Raise specific error if attribute doesn't exist in schema
                    raise CtyAttributeValidationError(f"Object has no attribute '{key}'")
                # If attribute exists in schema, proceed to dictionary lookup
                # (KeyError might still occur if internal state is inconsistent)
                return self._value[key]

            # For maps, check key in values
            if isinstance(self._type, CtyMap):
                for k, v in self._value.items():
                    if hasattr(k, 'value') and k.value == key:
                        return v
                    if k == key:
                        return v
                raise KeyError(f"Key not found: {key}")

            # For lists/tuples, handle both direct indexing and slices
            elif isinstance(self._type, (CtyList, CtyTuple)):
                if isinstance(key, slice):
                    # Handle slice operations
                    start = key.start if key.start is not None else 0
                    stop = key.stop if key.stop is not None else len(self._value)
                    step = key.step or 1

                    # Create sliced list of values
                    sliced_values = self._value[start:stop:step]

                    # For tuples, maintain tuple types
                    if isinstance(self._type, CtyTuple):
                        element_types = self._type.element_types[start:stop:step]
                        from pyvider.cty.types import CtyTuple
                        tuple_type = CtyTuple(element_types=element_types)
                        return CtyValue(type_=tuple_type, value=sliced_values)
                    # For lists, maintain element type
                    else:
                        return CtyValue(type_=self._type, value=sliced_values)
                else:
                    # Handle direct indexing
                    return self.element_at(key)

            # Value doesn't support indexing
            error_msg = f"Value of type {self._type.__class__.__name__} doesn't support indexing"
            logger.error(f"🔄❗❌ {error_msg}")
            raise TypeError(error_msg)

        except CtyAttributeValidationError as e:
             logger.error(f"🔄❗❌ {e}")
             raise

        except IndexError as e:
            # Re-raise IndexError
            logger.error(f"🔄❗❌ Index error: {e}")
            raise
        except KeyError as e:
            # Re-raise KeyError
            logger.error(f"🔄❗❌ Key error: {e}")
            raise
        except Exception as e:
            # Wrap other exceptions
            error_msg = f"Error during indexing: {e}"
            logger.error(f"🔄❗❌ {error_msg}")
            raise TypeError(error_msg) from e

    def __contains__(self, item) -> bool:
        """
        Support for 'in' operator with proper value comparison.

        Args:
            item: The item to check for

        Returns:
            True if the item is in the container, False otherwise

        Raises:
            TypeError: If the value doesn't support membership testing
        """
        logger.debug(f"🔄🔍🔄 Checking if {item} is in container")

        # Cannot check membership in unknown or null values
        if self._is_unknown or self._is_null:
            error_msg = "Cannot check membership in unknown or null value"
            logger.error(f"🔄❗❌ {error_msg}")
            raise TypeError(error_msg)

        # Import locally to avoid circular imports
        from pyvider.cty.types.collections import CtyMap, CtyList, CtySet
        from pyvider.cty.types.structural import CtyObject

        try:
            # For maps, check keys
            if isinstance(self._type, CtyMap):
                for k in self._value.keys():
                    if hasattr(k, 'value') and k.value == item:
                        return True
                    if k == item:
                        return True
                return False

            # For lists, check elements
            elif isinstance(self._type, CtyList):
                for element in self._value:
                    if hasattr(element, 'value') and element.value == item:
                        return True
                    if element == item:
                        return True
                return False

            # For sets, check elements
            elif isinstance(self._type, CtySet):
                for element in self._value:
                    if hasattr(element, 'value') and element.value == item:
                        return True
                    if element == item:
                        return True
                return False

            # For objects, check attributes
            elif isinstance(self._type, CtyObject):
                return self._type.has_attribute(item)

            # For other types, fall back to Python's native containment check
            if hasattr(self._value, '__contains__'):
                return item in self._value

            # Value doesn't support membership testing
            error_msg = f"Value of type {self._type.__class__.__name__} doesn't support membership testing"
            logger.error(f"🔄❗❌ {error_msg}")
            raise TypeError(error_msg)

        except Exception as e:
            logger.debug(f"🔄❗⚠️ Error during membership test: {e}")
            return False

    def __bool__(self) -> bool:
        """
        Boolean evaluation of this value.

        Returns:
            True if the value is truthy, False otherwise

        Notes:
            - Unknown values are always falsy
            - Null values are always falsy
            - For known, non-null values, use Python's truthiness rules
        """
        # Unknown and null values are always falsy
        if self._is_unknown or self._is_null:
            return False

        # For known, non-null values, use Python's truthiness rules
        return bool(self._value)

    def __str__(self) -> str:
        """
        String representation for display.

        Returns:
            A string representation
        """
        if self._is_unknown:
            return f"<unknown {self._type.__class__.__name__}>"
        if self._is_null:
            return f"<null {self._type.__class__.__name__}>"

        # For known, non-null values, convert to string
        return str(self._value)

    def __repr__(self) -> str:
        """
        Detailed string representation.

        Returns:
            A detailed string representation
        """
        parts = [
            f"type_={self._type.__class__.__name__}",
        ]

        if not self._is_unknown and not self._is_null:
            parts.append(f"value={self._value!r}")
        if self._is_unknown:
            parts.append("is_unknown=True")
        if self._is_null:
            parts.append("is_null=True")
        if self._marks:
            parts.append(f"marks={self._marks}")

        return f"CtyValue({', '.join(parts)})"

# 🐍🏗️🐣
