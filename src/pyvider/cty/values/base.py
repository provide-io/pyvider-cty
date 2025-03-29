#
# pyvider/cty/values/base.py
#

"""
CtyValue represents a value with its corresponding type in the Cty type system.

This module provides the core value representation that combines a value with its
type, along with additional metadata like whether the value is known or null.
"""

from decimal import Decimal
from typing import Any, FrozenSet, Generic, Optional, TypeVar, cast

from pyvider.cty.logger import logger
from pyvider.cty.types.base import CtyType

T = TypeVar('T', covariant=True)

class CtyValue(Generic[T]):
    """
    Immutable representation of a Cty value.

    A CtyValue combines a raw value with its type and metadata such as whether
    the value is known (vs unknown) or null. This follows the Go-CTY value model.
    """

    def __init__(
        self,
        type_: CtyType[T],
        value: Any = None,
        is_unknown: bool = False,
        is_null: bool = False,
        marks: Optional[FrozenSet] = None
    ):
        """
        Initialize a new CtyValue.

        Args:
            type_: The Cty type of this value
            value: The raw value (or None for null/unknown values)
            is_unknown: Whether this value is unknown
            is_null: Whether this value is null
            marks: Optional set of marks to apply to this value
        """
        logger.debug(f"🔄🔧✅ Creating CtyValue of type {type_.__class__.__name__}")
        self._type = type_
        self._value = value
        self._is_unknown = is_unknown
        self._is_null = is_null
        self._marks = marks or frozenset()

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
            ValueError: If this value is unknown or null
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
        # Use equality comparison rather than identity
        for m in self._marks:
            if str(m) == str(mark):
                return True
        return False

    def mark(self, mark: Any) -> "CtyValue[T]":
        """
        Add a mark to this value.

        Args:
            mark: The mark to add

        Returns:
            A new CtyValue with the mark added
        """
        logger.debug(f"🔄🔧✅ Adding mark {mark} to value")
        return CtyValue(
            type_=self._type,
            value=self._value,
            is_unknown=self._is_unknown,
            is_null=self._is_null,
            marks=frozenset(self._marks.union({mark}))
        )

    def unmark(self) -> tuple["CtyValue[T]", FrozenSet]:
        """
        Remove all marks from this value and return them.

        Returns:
            tuple: (Unmarked value, Set of removed marks)
        """
        logger.debug(f"🔄🔧✅ Removing {len(self._marks)} marks from value")
        return CtyValue(
            type_=self._type,
            value=self._value,
            is_unknown=self._is_unknown,
            is_null=self._is_null,
            marks=frozenset()
        ), self._marks

    def get(self, key, default=None):
        """
        Get a value by key, with a default if not found.

        Args:
            key: The key to look up
            default: Value to return if key not found
        """
        logger.debug(f"🔄🔍🔄 Getting value for key: {key}")
        
        if self._is_unknown or self._is_null:
            logger.debug(f"🔄🔍⚠️ Cannot get from unknown/null value, returning default")
            return default

        # Import locally to avoid circular imports
        from pyvider.cty.types.collections import CtyMap

        # Handle maps
        if isinstance(self._type, CtyMap):
            try:
                return self._type.get(self, key, default)
            except Exception as e:
                logger.debug(f"🔄🔍⚠️ Map get failed: {e}")
                return default
        else:
            logger.debug(f"🔄🔍⚠️ get() called on non-map value")
            return default

    def set(self, key, value):
        """
        Set a value in a map.
        
        This delegates to the type's set method.
        """
        logger.debug(f"🔄📝🔄 Setting key {key} to value {value}")
        
        from pyvider.cty.types.collections import CtyMap
        
        if not isinstance(self._type, CtyMap):
            error_msg = f"set() method only valid for map types, not {self._type.__class__.__name__}"
            logger.error(f"🔄❗❌ {error_msg}")
            raise TypeError(error_msg)
        
        return self._type.set(self, key, value)

    def delete(self, key):
        """
        Delete a key from a map.
        
        This delegates to the type's delete method.
        """
        logger.debug(f"🔄📝🔄 Deleting key {key}")
        
        from pyvider.cty.types.collections import CtyMap
        
        if not isinstance(self._type, CtyMap):
            error_msg = f"delete() method only valid for map types, not {self._type.__class__.__name__}"
            logger.error(f"🔄❗❌ {error_msg}")
            raise TypeError(error_msg)
        
        return self._type.delete(self, key)

    def element_at(self, index: int) -> "CtyValue":
        """Get list element at index."""
        logger.debug(f"🔄🔍🔄 Getting element at index {index}")
        
        if self._is_unknown or self._is_null:
            error_msg = "Cannot get element from unknown or null value"
            logger.error(f"🔄❗❌ {error_msg}")
            raise ValueError(error_msg)

        from pyvider.cty.types.collections import CtyList
        from pyvider.cty.types.structural import CtyTuple
        
        if isinstance(self._type, CtyList):
            return self._type.element_at(self, index)
        elif isinstance(self._type, CtyTuple):
            return self._type.element_at(self, index)
        else:
            error_msg = f"element_at method only available on list/tuple types, not {type(self._type).__name__}"
            logger.error(f"🔄❗❌ {error_msg}")
            raise TypeError(error_msg)

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
        return cls(type_=CtyString(), value=value)

    @classmethod
    def number(cls, value: Any) -> "CtyValue":
        """
        Create a number value.

        Args:
            value: The number value (int, float, or Decimal)

        Returns:
            A new CtyValue with the number value
        """
        from pyvider.cty.types import CtyNumber
        return cls(type_=CtyNumber(), value=value)

    @classmethod
    def unknown(cls, type_: "CtyType") -> "CtyValue":
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
    def null(cls, type_: "CtyType") -> "CtyValue":
        """
        Create a null value of the given type.

        Args:
            type_: The type of the null value

        Returns:
            A new CtyValue marked as null
        """
        logger.debug(f"🔄🔧✅ Creating null value of type {type_.__class__.__name__}")
        return cls(type_=type_, is_null=True)

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
        if isinstance(self._value, (set, frozenset)):
            result["value"] = list(self._value)
        elif self._value is not None:
            result["value"] = self._value

        # Add metadata
        result["is_unknown"] = self._is_unknown
        result["is_null"] = self._is_null

        # Add marks if present
        if self._marks:
            result["marks"] = list(str(m) for m in self._marks)

        return result

    def __len__(self) -> int:
        """
        Get the length of this value, similar to go-cty's behavior.

        Returns:
            The length of the value

        Raises:
            TypeError: If the value doesn't support length
        """
        # Cannot get length of unknown values
        if self._is_unknown:
            raise TypeError("Cannot get length of unknown value")

        # Cannot get length of null values
        if self._is_null:
            raise TypeError("Cannot get length of null value")

        # For known values, delegate to the underlying value
        if hasattr(self._value, "__len__"):
            return len(self._value)

        # Value doesn't support length
        raise TypeError(f"Value of type {type(self._value).__name__} doesn't support length operation")

    def __hash__(self) -> int:
        """
        Make CtyValue instances hashable for use in sets and as dict keys.

        Returns:
            A hash value
        """
        # Hash based on type, value state, and value (if simple)
        type_hash = hash(self._type.__class__)
        state_hash = hash((self._is_unknown, self._is_null))

        # Only include the value in the hash if it's hashable
        value_hash = 0
        if self._value is None:
            value_hash = hash(None)
        elif isinstance(self._value, (str, int, float, bool, Decimal)):
            value_hash = hash(self._value)
        # For complex values, we only use their type in the hash

        # Include marks in hash if present
        marks_hash = hash(frozenset(str(m) for m in self._marks)) if self._marks else 0

        return hash((type_hash, state_hash, value_hash, marks_hash))

    def __eq__(self, other) -> bool:
        """
        Check if two CtyValue instances are equal.

        Args:
            other: The other value to compare with

        Returns:
            True if the values are equal
        """
        if not isinstance(other, CtyValue):
            # For primitive type comparison support
            if isinstance(self._value, (str, int, float, bool, Decimal)) and self.is_known and not self.is_null:
                try:
                    return self._value == other
                except:
                    return False
            return False

        # Check type, state, and marks
        if self._type.__class__ != other._type.__class__:
            return False
        if self._is_unknown != other._is_unknown:
            return False
        if self._is_null != other._is_null:
            return False
        if self._marks != other._marks:
            return False

        # For known, non-null values, compare the actual values
        if self.is_known and not self.is_null:
            return self._value == other._value

        return True

    def __getitem__(self, key):
        """Support for indexing into container values."""
        logger.debug(f"🔄🔍🔄 Getting item with key: {key}")
        
        if self._is_unknown or self._is_null:
            error_msg = "Cannot index into unknown or null value"
            logger.error(f"🔄❗❌ {error_msg}")
            raise TypeError(error_msg)
            
        # Import locally to avoid circular imports
        from pyvider.cty.types.collections import CtyMap, CtyList
        from pyvider.cty.types.structural import CtyObject, CtyTuple
        
        # Delegate to appropriate type implementation
        if isinstance(self._type, CtyMap):
            return self._type.element(self, key)
        elif isinstance(self._type, (CtyList, CtyTuple)):
            if isinstance(key, slice):
                # Handle slice operations
                start = key.start or 0
                stop = key.stop or len(self._value)
                if isinstance(self._type, CtyList):
                    return self._type.slice(start, stop)
                # Not currently supporting slice for tuple
                raise TypeError(f"Slice operations not supported for {self._type.__class__.__name__}")
            else:
                # Handle direct indexing
                return self._type.element_at(self, key)
        elif isinstance(self._type, CtyObject):
            return self._type.get_attribute(self._value, key)
            
        # Value doesn't support indexing
        error_msg = f"Value of type {self._type.__class__.__name__} doesn't support indexing"
        logger.error(f"🔄❗❌ {error_msg}")
        raise TypeError(error_msg)

    def __contains__(self, item):
        """Support for 'in' operator."""
        logger.debug(f"🔄🔍🔄 Checking if {item} is in container")
        
        if self._is_unknown or self._is_null:
            error_msg = "Cannot check membership in unknown or null value"
            logger.error(f"🔄❗❌ {error_msg}")
            raise TypeError(error_msg)
            
        # Import locally to avoid circular imports
        from pyvider.cty.types.collections import CtyMap, CtyList, CtySet
        
        # Delegate to appropriate type implementation
        if isinstance(self._type, CtyMap):
            # Maps check keys - validate the key first
            try:
                key = self._type.key_type.validate(item)
                for k in self._value:
                    if k.value == key.value:
                        return True
                return False
            except:
                return False
        elif isinstance(self._type, CtyList):
            return self._type.contains(self, item)
        elif isinstance(self._type, CtySet):
            return self._type.contains(self, item)
            
        # Fallback to standard Python behavior
        try:
            return item in self._value
        except TypeError:
            error_msg = f"Value of type {self._type.__class__.__name__} doesn't support membership test"
            logger.error(f"🔄❗❌ {error_msg}")
            raise TypeError(error_msg)

    def __str__(self) -> str:
        """
        Get a string representation of this value.
        Returns:
            A string representation
        """
        if self._is_unknown:
            return f"<unknown {self._type.__class__.__name__}>"
        if self._is_null:
            return f"<null {self._type.__class__.__name__}>"
        return str(self._value)

    def __repr__(self) -> str:
        """
        Get a detailed string representation of this value.

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
