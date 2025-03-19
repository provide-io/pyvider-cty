
# pyvider/cty/values/base.py

from typing import Any, Optional, FrozenSet, Generic, TypeVar

from pyvider.cty.ctypes import CtyType

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
    def is_null(self) -> bool:
        """Check if this value is null."""
        return self._is_null

    def has_mark(self, mark: Any) -> bool:
        """Check if this value has a specific mark."""
        return mark in self._marks

    def mark(self, mark: Any) -> "Value[T]":
        """Add a mark to this value."""
        return Value(
            type_=self._type,
            value=self._value,
            is_unknown=self._is_unknown,
            is_null=self._is_null,
            marks=frozenset(self._marks.union({mark}))
        )

    def unmark(self) -> tuple["Value[T]", FrozenSet]:
        """Remove all marks from this value and return them."""
        return Value(
            type_=self._type,
            value=self._value,
            is_unknown=self._is_unknown,
            is_null=self._is_null,
            marks=frozenset()
        ), self._marks

    def refine(self) -> "ValueRefinementBuilder":
        """Create a refinement builder for this value."""
        from pyvider.cty.values.refinement import ValueRefinementBuilder
        return ValueRefinementBuilder(self)

    @property
    def value(self) -> Any:
        """Get the raw value of this CtyValue."""
        return self._value

    @classmethod
    def bool(cls, value: bool) -> "CtyValue":
        """Create a boolean value."""
        from pyvider.cty.ctypes import CtyBool
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
        """Get the length of this value, similar to Go-CTY's behavior."""
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

# 🐍🏗️
