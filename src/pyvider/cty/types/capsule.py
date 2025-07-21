# pyvider/cty/types/capsule.py
"""
Defines the CtyCapsule type for encapsulating opaque Python objects
within the CTY type system.
"""

from collections.abc import Callable
from typing import Any

from pyvider.cty.exceptions import CtyValidationError
from pyvider.cty.types.base import CtyType
from pyvider.cty.types.structural import CtyDynamic
from pyvider.cty.values import CtyValue


class CtyCapsule(CtyType[Any]):
    """
    Represents a capsule type in the Cty type system.
    Capsule types are opaque types that can be used to wrap arbitrary Python objects.
    """

    def __init__(self, capsule_name: str, py_type: type) -> None:
        super().__init__()
        self.name = capsule_name
        self._py_type = py_type

    @property
    def py_type(self) -> type:
        return self._py_type

    def validate(self, value: object) -> "CtyValue[Any]":
        if isinstance(value, CtyValue):
            if value.is_null:
                return CtyValue.null(self)
            if value.is_unknown:
                return CtyValue.unknown(self)
            if (
                isinstance(value.type, CtyCapsule)
                and value.type.name == self.name
                and value.type.py_type == self.py_type
            ):
                return value
            val_to_check = value.value
        else:
            val_to_check = value

        if val_to_check is None:
            return CtyValue.null(self)

        if not isinstance(val_to_check, self._py_type):
            raise CtyValidationError(
                f"Value is not an instance of {self._py_type.__name__}. Got {type(val_to_check).__name__}."
            )
        return CtyValue(self, val_to_check)

    def equal(self, other: "CtyType[Any]") -> bool:
        # FIX: Use strict type checking to differentiate CtyCapsule from CtyCapsuleWithOps
        if type(self) is not type(other):
            return False

        # Now we know they are the same class (both base or both WithOps)
        if isinstance(self, CtyCapsuleWithOps):
            # This check is now safe because we know 'other' is also WithOps
            return (
                self.name == other.name
                and self._py_type == other._py_type
                and self.equal_fn == other.equal_fn
                and self.hash_fn == other.hash_fn
            )
        
        # Base CtyCapsule logic
        return self.name == other.name and self._py_type == other._py_type

    def usable_as(self, other: "CtyType[Any]") -> bool:
        if isinstance(other, CtyDynamic):
            return True
        return self.equal(other)

    def _to_wire_json(self) -> Any:
        # Capsule types have no standard wire representation and are encoded as null.
        return None

    def __repr__(self) -> str:
        return f"CtyCapsule({self.name}, {self._py_type.__name__})"

    def __hash__(self) -> int:
        return hash((self.name, self._py_type))


class CtyCapsuleWithOps(CtyCapsule):
    """
    A CtyCapsule that supports custom operations like equality and hashing.
    """

    def __init__(
        self,
        capsule_name: str,
        py_type: type,
        *,
        equal_fn: Callable[[Any, Any], bool] | None = None,
        hash_fn: Callable[[Any], int] | None = None,
    ) -> None:
        """
        Initializes a CtyCapsule with custom operational functions.
        """
        super().__init__(capsule_name, py_type)
        self.equal_fn = equal_fn
        self.hash_fn = hash_fn

    def __repr__(self) -> str:
        return f"CtyCapsuleWithOps({self.name}, {self._py_type.__name__})"

    def __hash__(self) -> int:
        return hash((self.name, self._py_type, self.equal_fn, self.hash_fn))
