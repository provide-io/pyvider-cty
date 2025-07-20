# pyvider/cty/types/capsule.py
"""
Defines the CtyCapsule type for encapsulating opaque Python objects
within the CTY type system.
"""

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
        if not isinstance(other, CtyCapsule):
            return False
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
