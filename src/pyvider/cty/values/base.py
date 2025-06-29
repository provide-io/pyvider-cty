# pyvider/cty/values/base.py
from __future__ import annotations
from collections.abc import Iterator
from decimal import Decimal
from typing import (
    Any,
    Generic,
    Self,
    TypeVar,
    TYPE_CHECKING,
)

from attrs import define, evolve, field

# Import the lightweight protocol, NOT the concrete ABC
from pyvider.cty.types.types_base import CtyTypeProtocol
from pyvider.telemetry import logger

# Define UnknownValue classes here, as they are value concepts.
class UnknownValue: ...

@define(frozen=True, slots=True, auto_attribs=True, match_args=True)
class RefinedUnknownValue(UnknownValue):
    is_known_null: bool | None = None
    string_prefix: str | None = None
    number_lower_bound: tuple[Decimal | int | float, bool] | None = None
    number_upper_bound: tuple[Decimal | int | float, bool] | None = None
    collection_length_lower_bound: int | None = None
    collection_length_upper_bound: int | None = None

@define(frozen=True, slots=True, auto_attribs=True, match_args=True)
class UnrefinedUnknownValue(UnknownValue): ...

UNREFINED_UNKNOWN = UnrefinedUnknownValue()

T = TypeVar("T", covariant=True)

# Use a forward reference for CtyType in type hints inside the class
if TYPE_CHECKING:
    from pyvider.cty.types import CtyType
    from pyvider.cty.marks import CtyMark

@define(frozen=True, slots=True)
class CtyValue(Generic[T]):
    """Immutable representation of a Cty value with type information."""
    _vtype: "CtyType[T]" = field()
    _value: object | None = field(default=None)
    _is_unknown: bool = field(default=False)
    _is_null: bool = field(default=False)
    _marks: frozenset = field(factory=frozenset)
    _key_mapping: dict[str, "CtyValue"] = field(factory=dict)

    def __attrs_post_init__(self) -> None:
        if self._is_unknown:
            if self._is_null: object.__setattr__(self, "_is_null", False)
            if self._value is not None: object.__setattr__(self, "_value", None)
        elif self._is_null and self._value is not None:
            object.__setattr__(self, "_value", None)

    @property
    def type(self) -> "CtyType[T]":
        return self._vtype

    @property
    def value(self) -> object | None:
        if self._is_unknown:
            raise ValueError("Cannot get raw value of unknown value")
        return self._value

    @property
    def is_unknown(self) -> bool:
        return self._is_unknown

    @property
    def is_null(self) -> bool:
        return self._is_null

    def has_mark(self, mark: object) -> bool:
        mark_str = str(mark)
        return any(str(m) == mark_str for m in self._marks)

    def mark(self, mark: object) -> Self:
        return evolve(self, _marks=frozenset(self._marks.union({mark})))

    def unmark(self) -> tuple[Self, frozenset]:
        unmarked_value = evolve(self, _marks=frozenset())
        return unmarked_value, self._marks

    # --- Dunder Methods for Container-like Behavior ---
    def __len__(self) -> int:
        if self.is_unknown: raise TypeError("Cannot get length of unknown value")
        if self.is_null: return 0
        if hasattr(self._value, "__len__"): return len(self._value)
        raise TypeError(f"Value of type {self._vtype.__class__.__name__} has no len()")

    def __iter__(self) -> Iterator:
        if self.is_unknown: raise TypeError("Cannot iterate unknown value")
        if self.is_null: return iter([])
        if hasattr(self._value, "__iter__"):
            if isinstance(self._value, dict): return iter(self._value.keys())
            return iter(self._value)
        raise TypeError(f"Value of type {self._vtype.__class__.__name__} is not iterable")

    def __getitem__(self, key: Any) -> "CtyValue":
        from pyvider.cty.types import CtyList, CtyMap, CtyObject, CtyTuple
        if self.is_unknown or self.is_null: raise TypeError("Cannot index into unknown or null value")

        if isinstance(self._vtype, CtyObject):
            if not isinstance(key, str): raise TypeError(f"Object attribute name must be a string, got {type(key).__name__}")
            return self._vtype.get_attribute(self, key)

        if isinstance(self._vtype, CtyList):
            if not isinstance(self.value, (list, tuple)):
                raise TypeError(f"CtyList value is not a list, but {type(self.value).__name__}")
            if isinstance(key, slice):
                sliced_list = self.value[key]
                return CtyValue(vtype=self._vtype, value=sliced_list)
            # It's an integer index, delegate to element_at
            return self._vtype.element_at(self, key)

        if isinstance(self._vtype, CtyTuple):
            # CtyTuple.element_at correctly handles both int and slice
            return self._vtype.element_at(self, key)

        if isinstance(self._vtype, CtyMap):
            return self._vtype.get(self, key)
            
        raise TypeError(f"Value of type {self._vtype.__class__.__name__} is not subscriptable")

    def __contains__(self, item: Any) -> bool:
        from pyvider.cty.types import CtyMap, CtyObject, CtyList, CtySet, CtyTuple, CtyDynamic
        from pyvider.cty.exceptions import CtyValidationError

        if self.is_unknown or self.is_null: return False

        if isinstance(self._vtype, CtyMap):
            if not isinstance(self._value, dict): return False
            try:
                key_to_validate = item.value if isinstance(item, CtyValue) and not isinstance(self._vtype.key_type, CtyDynamic) else item
                validated_key = self._vtype.key_type.validate(key_to_validate)
                if validated_key.is_null or validated_key.is_unknown: return False
                return str(validated_key.value) in self._value
            except CtyValidationError: return False
        
        if isinstance(self._vtype, CtyObject):
            return isinstance(item, str) and self._vtype.has_attribute(item)

        if isinstance(self._vtype, (CtyList, CtySet, CtyTuple)):
            if not hasattr(self._value, "__iter__"): return False
            for element in self._value:
                try:
                    # Compare CtyValue to CtyValue
                    if isinstance(item, CtyValue):
                        if element == item: return True
                    # Compare CtyValue to raw Python value
                    else:
                        if not element.is_unknown and not element.is_null:
                            if element.type.validate(item) == element:
                                return True
                except CtyValidationError:
                    continue
            return False

        if hasattr(self._value, "__contains__"):
            try: return item in self._value
            except TypeError: return False
        
        return self._value == item

    def __hash__(self) -> int:
        value_hash = 0
        if not self.is_unknown and not self.is_null:
            try:
                value_hash = hash(self._value)
            except TypeError:
                value_hash = hash(repr(self._value))
        return hash((self._vtype, self.is_unknown, self.is_null, self._marks, value_hash))
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CtyValue): return False
        if not self.type.equal(other.type): return False
        if self._is_unknown != other._is_unknown: return False
        if self._is_null != other._is_null: return False
        if self._marks != other._marks: return False
        if self._is_unknown or self._is_null: return True
        return self._value == other._value

    def __str__(self) -> str:
        if self.is_unknown: return f"<unknown {self.type}>"
        if self.is_null: return f"<null {self.type}>"
        return str(self.value)

    # --- Boolean/Empty Checks ---
    def is_true(self) -> bool:
        if self.is_unknown or self.is_null: return False
        if isinstance(self.value, CtyValue): return self.value.is_true()
        return self.value is True

    def is_false(self) -> bool:
        if self.is_unknown or self.is_null: return False
        if isinstance(self.value, CtyValue): return self.value.is_false()
        return self.value is False

    def is_empty(self) -> bool:
        if self.is_unknown or self.is_null: return True
        if isinstance(self.value, CtyValue): return self.value.is_empty()
        if isinstance(self.value, (str, list, tuple, dict, set, frozenset)): return not self.value
        return False
        
    # --- Factory Methods ---
    @classmethod
    def unknown(cls, vtype: "CtyType") -> "CtyValue":
        return cls(vtype=vtype, is_unknown=True)

    @classmethod
    def null(cls, vtype: "CtyType") -> "CtyValue":
        return cls(vtype=vtype, is_null=True)
