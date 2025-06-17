#
# pyvider/cty/types/capsule.py
#

from typing import Any
from pyvider.cty.types.base import CtyType
from pyvider.cty.values import CtyValue
from pyvider.cty.exceptions import CtyValidationError
from pyvider.cty.types.structural import CtyDynamic


class CtyCapsule(CtyType):
    """
    Represents a capsule type in the Cty type system.
    Capsule types are opaque types that can be used to wrap arbitrary Python objects.
    """

    def __init__(self, capsule_name: str, py_type: type):
        # Note: CtyType's __init__ doesn't take arguments.
        # The 'name' for a type is usually its ctype class variable or derived.
        # For Capsule, the instance specific 'name' is the capsule_name.
        super().__init__()
        self.name = capsule_name # Storing capsule_name as an instance attribute
        self._py_type = py_type

    @property
    def py_type(self) -> type:
        return self._py_type

    @property
    def ctype(self) -> str:
        # Override ctype to return the specific capsule name for this instance
        return self.name

    def validate(self, value: Any) -> 'CtyValue':
        if isinstance(value, CtyValue):
            if value.is_null():
                return CtyValue.null(self)
            if value.is_unknown():
                return CtyValue.unknown(self)
            # If it's already a CtyValue, check if its type is a compatible CtyCapsule
            if isinstance(value.type, CtyCapsule) and value.type.name == self.name and value.type.py_type == self.py_type:
                return value
            # Otherwise, validate its underlying value
            val_to_check = value.value
        else:
            val_to_check = value

        if not isinstance(val_to_check, self._py_type):
            raise CtyValidationError(
                f"Value is not an instance of {self._py_type.__name__}. Got {type(val_to_check).__name__}."
            )
        return CtyValue(self, val_to_check)

    def equal(self, other: 'CtyType') -> bool:
        if not isinstance(other, CtyCapsule):
            return False
        # Compare based on the instance-specific name and py_type
        return self.name == other.name and self._py_type == other._py_type

    def usable_as(self, other: 'CtyType') -> bool:
        if isinstance(other, CtyDynamic):
            return True
        return self.equal(other)

    def __repr__(self) -> str:
        return f"CtyCapsule({self.name}, {self._py_type.__name__})"

    # __eq__ is handled by CtyType's base __eq__ which calls self.equal()
    # def __eq__(self, other) -> bool:
    #     if not isinstance(other, CtyCapsule):
    #         return False
    #     return self.name == other.name and self._py_type == other._py_type

    def __hash__(self) -> int:
        # Hash based on the instance-specific name and py_type
        return hash((self.name, self._py_type))

__all__ = ["CtyCapsule"]

# 🐍🏗️🐣
