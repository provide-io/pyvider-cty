from __future__ import annotations

from collections.abc import Iterator
from typing import (
    TYPE_CHECKING,
    Any,
    Self,
    TypeVar,
)

from attrs import define, evolve, field

from ..exceptions import CtyValidationError
from .markers import UNREFINED_UNKNOWN

T = TypeVar("T", covariant=True)

if TYPE_CHECKING:
    from pyvider.cty.types import CtyType


@define(frozen=True, slots=True)
class CtyValue[T]:
    vtype: CtyType[T] = field()
    value: object | None = field(default=None)
    is_unknown: bool = field(default=False)
    is_null: bool = field(default=False)
    marks: frozenset[Any] = field(factory=frozenset)
    key_mapping: dict[str, CtyValue[Any]] = field(factory=dict)

    def __attrs_post_init__(self) -> None:
        if self.is_unknown and self.is_null:
            object.__setattr__(self, "is_null", False)
        elif self.is_null and self.value is not None:
            object.__setattr__(self, "value", None)

    @property
    def type(self) -> CtyType[T]:
        return self.vtype

    @property
    def raw_value(self) -> object | None:
        if self.is_unknown:
            raise ValueError("Cannot get raw value of unknown value")
        if self.is_null:
            return None
        from ..conversion.adapter import cty_to_native

        return cty_to_native(self)  # type: ignore

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CtyValue):
            return NotImplemented
        from ..types import CtyCapsuleWithOps

        if isinstance(self.type, CtyCapsuleWithOps) and self.type.equal(other.type):
            if self.type.equal_fn:
                return self.type.equal_fn(self.value, other.value)

        return (
            self.type.equal(other.type)
            and self.is_unknown == other.is_unknown
            and self.is_null == other.is_null
            and self.marks == other.marks
            and self.value == other.value
        )

    def _check_comparable(self, other: object) -> CtyValue[Any]:
        from ..types import CtyNumber, CtyString
        if not isinstance(other, CtyValue):
            raise TypeError(f"Cannot compare CtyValue with {type(other).__name__}")
        if self.is_unknown or self.is_null or other.is_unknown or other.is_null:
            raise TypeError("Cannot compare null or unknown values")
        if not self.type.equal(other.type):
            raise TypeError(f"Cannot compare CtyValues of different types: {self.type} and {other.type}")
        if not isinstance(self.type, (CtyNumber, CtyString)):
             raise TypeError(f"Value of type {self.type} is not comparable")
        return other

    def __lt__(self, other: object) -> bool:
        other_val = self._check_comparable(other)
        return self.value < other_val.value

    def __le__(self, other: object) -> bool:
        other_val = self._check_comparable(other)
        return self.value <= other_val.value

    def __gt__(self, other: object) -> bool:
        other_val = self._check_comparable(other)
        return self.value > other_val.value

    def __ge__(self, other: object) -> bool:
        other_val = self._check_comparable(other)
        return self.value >= other_val.value

    def __contains__(self, item: Any) -> bool:
        if self.is_unknown or self.is_null:
            return False
        if hasattr(self.value, "__contains__"):
            return item in self.value
        return self.value == item  # type: ignore

    def __bool__(self) -> bool:
        from pyvider.cty.types import CtyDynamic

        if self.is_unknown or self.is_null:
            return False
        if isinstance(self.vtype, CtyDynamic) and isinstance(self.value, CtyValue):
            return bool(self.value)
        return True

    def __len__(self) -> int:
        from pyvider.cty.types import CtyDynamic, CtyList, CtyMap, CtySet, CtyTuple

        if self.is_unknown:
            raise TypeError("Cannot get length of unknown value")
        if isinstance(self.vtype, CtyDynamic) and isinstance(self.value, CtyValue):
            return len(self.value)
        if self.is_null:
            return 0
        if isinstance(self.vtype, (CtyList, CtyMap, CtySet, CtyTuple)):
            if hasattr(self.value, "__len__"):
                return len(self.value)
        raise TypeError(f"Value of type {self.vtype.__class__.__name__} has no len()")

    def __iter__(self) -> Iterator[Any]:
        from pyvider.cty.types import CtyList, CtyMap, CtySet, CtyTuple

        if self.is_unknown:
            raise TypeError("Cannot iterate unknown value")
        if self.is_null:
            return iter([])
        if isinstance(self.vtype, (CtyList, CtySet, CtyTuple)):
            if hasattr(self.value, "__iter__"):
                return iter(self.value)
        if isinstance(self.vtype, CtyMap):
            if hasattr(self.value, "__iter__"):
                return iter(self.value.values())

        raise TypeError(
            f"Value of type {self.vtype.__class__.__name__} is not iterable"
        )

    def __getitem__(self, key: Any) -> CtyValue[Any]:
        from pyvider.cty.types import CtyList, CtyMap, CtyObject, CtyTuple

        if self.is_unknown or self.is_null:
            raise TypeError("Cannot index into unknown or null value")
        if isinstance(self.vtype, CtyObject):
            if not isinstance(key, str):
                raise TypeError(
                    f"Object attribute name must be a string, got {type(key).__name__}"
                )
            return self.vtype.get_attribute(self, key)
        if isinstance(self.vtype, CtyList):
            if not isinstance(self.value, list | tuple):
                raise TypeError(
                    f"CtyList value is not a list/tuple, but {type(self.value).__name__}"
                )
            if isinstance(key, slice):
                return CtyValue(vtype=self.vtype, value=self.value[key])
            return self.vtype.element_at(self, key)
        if isinstance(self.vtype, CtyTuple):
            return self.vtype.element_at(self, key)
        if isinstance(self.vtype, CtyMap):
            return self.vtype.get(self, key)  # type: ignore
        raise TypeError(
            f"Value of type {self.vtype.__class__.__name__} is not subscriptable"
        )

    def __hash__(self) -> int:
        from pyvider.cty.types import (
            CtyCapsuleWithOps,
            CtyList,
            CtyMap,
            CtyObject,
            CtySet,
            CtyTuple,
        )

        if isinstance(self.type, CtyCapsuleWithOps):
            if self.type.hash_fn:
                return self.type.hash_fn(self.value)

        if isinstance(self.vtype, CtyTuple):
            pass
        elif isinstance(self.vtype, CtyList | CtySet | CtyMap | CtyObject):
            raise TypeError(f"unhashable type: 'CtyValue[{self.vtype.ctype}]'")

        if self.is_unknown or self.is_null:
            return hash((self.vtype, self.is_unknown, self.is_null, self.marks))
        return hash((self.vtype, self.is_unknown, self.is_null, self.marks, self.value))

    def has_mark(self, mark: object) -> bool:
        return mark in self.marks

    def mark(self, mark: object) -> Self:
        return evolve(self, marks=self.marks.union({mark}))

    def with_marks(self, marks_to_add: set[Any]) -> Self:
        return evolve(self, marks=self.marks.union(marks_to_add))

    def unmark(self) -> tuple[Self, frozenset[Any]]:
        unmarked_value = evolve(self, marks=frozenset())
        return unmarked_value, self.marks

    def is_true(self) -> bool:
        from pyvider.cty.types import CtyDynamic
        if isinstance(self.vtype, CtyDynamic) and isinstance(self.value, CtyValue):
            return self.value.is_true()
        return self.value is True

    def is_false(self) -> bool:
        from pyvider.cty.types import CtyDynamic
        if isinstance(self.vtype, CtyDynamic) and isinstance(self.value, CtyValue):
            return self.value.is_false()
        return self.value is False

    def is_empty(self) -> bool:
        return not self.value if hasattr(self.value, "__len__") else False

    def with_key(self, key: str, value: Any) -> Self:
        from ..types import CtyMap
        if not isinstance(self.vtype, CtyMap): raise TypeError("'.with_key()' can only be used on CtyMap values.")
        new_dict = dict(self.value)
        new_dict[key] = value
        return self.vtype.validate(new_dict)

    def without_key(self, key: str) -> Self:
        from ..types import CtyMap
        if not isinstance(self.vtype, CtyMap): raise TypeError("'.without_key()' can only be used on CtyMap values.")
        if key not in self.value: return self
        new_dict = dict(self.value)
        del new_dict[key]
        return self.vtype.validate(new_dict)

    def append(self, value: Any) -> Self:
        from ..types import CtyList
        if not isinstance(self.vtype, CtyList): raise TypeError("'.append()' can only be used on CtyList values.")
        new_list = list(self.value)
        new_list.append(value)
        return self.vtype.validate(new_list)

    def with_element_at(self, index: int, value: Any) -> Self:
        from ..types import CtyList
        if not isinstance(self.vtype, CtyList): raise TypeError("'.with_element_at()' can only be used on CtyList values.")
        new_list = list(self.value)
        if not (-len(new_list) <= index < len(new_list)): raise IndexError("list index out of range")
        new_list[index] = value
        return self.vtype.validate(new_list)

    @classmethod
    def unknown(cls, vtype: CtyType[Any], value: Any = UNREFINED_UNKNOWN) -> CtyValue[Any]:
        return cls(vtype=vtype, is_unknown=True, value=value)

    @classmethod
    def null(cls, vtype: CtyType[Any]) -> CtyValue[Any]:
        return cls(vtype=vtype, is_null=True)
