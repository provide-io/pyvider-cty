
# pyvider/cty/values/base.py

from typing import Any, Optional, FrozenSet, Generic, TypeVar
from pyvider.cty import CtyType

T = TypeVar('T', covariant=True)

class Value(Generic[T]):
    """Immutable representation of a CTY value."""
    
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
        from pyvider_cty.values.refinement import ValueRefinementBuilder
        return ValueRefinementBuilder(self)
