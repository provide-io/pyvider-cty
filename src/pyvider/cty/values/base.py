
# pyvider/cty/values/base.py

from decimal import Decimal
from typing import Any, Optional, FrozenSet, Generic, TypeVar

from pyvider.cty.types import CtyType

T = TypeVar('T', covariant=True)

class CtyValue(Generic[T]):
    """Immutable representation of a Cty value."""

    def __init__(self,
                 type_: CtyType[T],
                 value: Any = None,
                 is_unknown: bool = False,
                 is_null: bool = False,
                 marks: Optional[FrozenSet] = None):
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
    def is_known(self) -> bool:
        """Check if this value is known (not unknown)."""
        return not self._is_unknown

    @property
    def is_unknown(self) -> bool:
        """Check if this value is known (not unknown)."""
        return self._is_unknown

    @property
    def is_null(self) -> bool:
        """Check if this value is null."""
        return self._is_null

    def has_mark(self, mark: Any) -> bool:
        """Check if this value has a specific mark."""
        return mark in self._marks

    def mark(self, mark: Any) -> "CtyValue[T]":
        """Add a mark to this value."""
        return CtyValue(
            type_=self._type,
            value=self._value,
            is_unknown=self._is_unknown,
            is_null=self._is_null,
            marks=frozenset(self._marks.union({mark}))
        )

    def unmark(self) -> tuple["CtyValue[T]", FrozenSet]:
        """Remove all marks from this value and return them."""
        return CtyValue(
            type_=self._type,
            value=self._value,
            is_unknown=self._is_unknown,
            is_null=self._is_null,
            marks=frozenset()
        ), self._marks

    @property
    def value(self) -> Any:
        """Get the raw value of this CtyValue."""
        return self._value

    @classmethod
    def bool(cls, value: bool) -> "CtyValue":
        """Create a boolean value."""
        from pyvider.cty.types import CtyBool
        return cls(type_=CtyBool(), value=value)

    @classmethod
    def unknown(cls, type_: "CtyType") -> "CtyValue":
        """Create an unknown value of the given type."""
        return cls(type_=type_, is_unknown=True)

    @classmethod
    def null(cls, type_: "CtyType") -> "CtyValue":
        """Create a null value of the given type."""
        return cls(type_=type_, is_null=True)

    def to_dict(self) -> dict:
        """Convert to dictionary representation for serialization."""
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
            result["marks"] = list(self._marks)
        
        return result

    def __len__(self) -> int:
        """Get the length of this value, similar to go-cty's behavior."""
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
        """Make CtyValue instances hashable for use in sets and as dict keys."""
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
        marks_hash = hash(frozenset(self._marks)) if self._marks else 0
        
        return hash((type_hash, state_hash, value_hash, marks_hash))

    def __eq__(self, other) -> bool:
        """Check if two CtyValue instances are equal."""
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

# 🐍🏗️
