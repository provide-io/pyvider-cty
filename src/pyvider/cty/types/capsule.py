#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

from collections.abc import Callable
import inspect
from typing import Any, ClassVar

from pyvider.cty.exceptions import CtyValidationError
from pyvider.cty.types.base import CtyType
from pyvider.cty.types.structural import CtyDynamic
from pyvider.cty.validation.marks import preserves_marks
from pyvider.cty.values import CtyValue

# pyvider/cty/types/capsule.py
"""
Defines the CtyCapsule type for encapsulating opaque Python objects
within the CTY type system.
"""


class CtyCapsule(CtyType[Any]):
    """
    Represents a capsule type in the Cty type system.
    Capsule types are opaque types that can be used to wrap arbitrary Python objects.
    """

    _type_order: ClassVar[int] = 8

    def __init__(self, capsule_name: str, py_type: type) -> None:
        super().__init__()
        self.name = capsule_name
        self._py_type = py_type

    @property
    def py_type(self) -> type:
        return self._py_type

    @preserves_marks
    def validate(self, value: object) -> CtyValue[Any]:
        val_to_check: object | None
        original_marks: frozenset[Any] = frozenset()

        if isinstance(value, CtyValue):
            if value.is_null:
                return CtyValue.null(self)
            if value.is_unknown:
                return CtyValue.unknown(self)
            val_to_check = value.value
            original_marks = value.marks
        else:
            val_to_check = value

        if val_to_check is None:
            return CtyValue.null(self)

        if not isinstance(val_to_check, self._py_type):
            raise CtyValidationError(
                f"Value is not an instance of {self._py_type.__name__}. Got {type(val_to_check).__name__}."
            )
        return CtyValue(self, val_to_check, marks=original_marks)

    def equal(self, other: CtyType[Any]) -> bool:
        if not isinstance(other, CtyCapsule) or isinstance(other, CtyCapsuleWithOps):
            return False
        return self.name == other.name and self._py_type == other._py_type

    def usable_as(self, other: CtyType[Any]) -> bool:
        if isinstance(other, CtyDynamic):
            return True
        return self.equal(other)

    def _to_wire_json(self) -> Any:
        return None

    def __str__(self) -> str:
        return f"CtyCapsule({self.name})"

    def __repr__(self) -> str:
        return f"CtyCapsule({self.name}, {self._py_type.__name__})"

    def __hash__(self) -> int:
        return hash((self.name, self._py_type))


class CtyCapsuleWithOps(CtyCapsule):
    """A capsule carrying go-cty's `CapsuleOps`.

    Two of go-cty's ten fields are deliberately absent, and their absence is a
    conclusion rather than an omission. `GoString` and `TypeGoString` exist to
    implement Go's `%#v` verb; Python's equivalent is `__repr__`, which
    `CtyCapsule` already defines. There is nothing to port.

    `equal_fn` is go-cty's `Equals` and `raw_equals_fn` is its `RawEquals`. The
    distinction matters for a capsule wrapping something that itself contains
    cty values: `Equals` may answer *unknown*, `RawEquals` is always a bool and
    compares structurally. go-cty falls back from a missing `Equals` to
    `RawEquals`, and so does this.
    """

    def __init__(
        self,
        capsule_name: str,
        py_type: type,
        *,
        equal_fn: Callable[[Any, Any], bool] | None = None,
        raw_equals_fn: Callable[[Any, Any], bool] | None = None,
        hash_fn: Callable[[Any], int] | None = None,
        convert_fn: Callable[[Any, CtyType[Any]], CtyValue[Any] | None] | None = None,
        convert_to_fn: Callable[[CtyValue[Any], CtyType[Any]], Any | None] | None = None,
        extension_data_fn: Callable[[Any], Any | None] | None = None,
    ) -> None:
        """Initialize a capsule with custom operational functions."""
        super().__init__(capsule_name, py_type)
        self.equal_fn = equal_fn
        self.raw_equals_fn = raw_equals_fn
        self.hash_fn = hash_fn
        # `convert_fn` is go-cty's `ConversionFrom`: this capsule to some other
        # type. `convert_to_fn` is `ConversionTo`: some other value into this
        # capsule. Both directions are needed for the capsule-to-capsule
        # fallback go-cty added in 1.16.0 -- with only one, a capsule can be
        # converted out of and never into.
        self.convert_fn = convert_fn
        self.convert_to_fn = convert_to_fn
        self.extension_data_fn = extension_data_fn
        self._validate_ops_arity()

    def _validate_ops_arity(self) -> None:
        """Reject an operation whose signature cannot be called as documented.

        Caught here rather than at the call site, because a wrong arity there
        surfaces as a TypeError from deep inside a conversion or a set insert,
        with nothing naming the capsule that supplied it.
        """
        for name, expected in (
            ("equal_fn", 2),
            ("raw_equals_fn", 2),
            ("hash_fn", 1),
            ("convert_fn", 2),
            ("convert_to_fn", 2),
            ("extension_data_fn", 1),
        ):
            function = getattr(self, name)
            if function and len(inspect.signature(function).parameters) != expected:
                plural = "argument" if expected == 1 else "arguments"
                raise TypeError(f"`{name}` must be a callable that accepts {expected} {plural}")

    def raw_equals(self, a: Any, b: Any) -> bool:
        """Structural equality, never unknown. go-cty's `RawEquals`."""
        if self.raw_equals_fn is not None:
            return bool(self.raw_equals_fn(a, b))
        if self.equal_fn is not None:
            # go-cty's fallback runs the other way -- Equals falls back to
            # RawEquals -- but a capsule that declares only Equals has still
            # declared what equality means for it, and identity would ignore it.
            return bool(self.equal_fn(a, b))
        return a is b

    def extension_data(self, key: Any) -> Any | None:
        """Application-defined data for `key`, or None if unrecognised.

        go-cty's extension point for building features on capsule types. The key
        is whatever the defining application chose; an unfamiliar one must yield
        None rather than raise, so consumers can ask without knowing who answers.
        """
        if self.extension_data_fn is None:
            return None
        return self.extension_data_fn(key)

    def _ops(self) -> tuple[Any, ...]:
        return (
            self.equal_fn,
            self.raw_equals_fn,
            self.hash_fn,
            self.convert_fn,
            self.convert_to_fn,
            self.extension_data_fn,
        )

    def equal(self, other: CtyType[Any]) -> bool:
        if not isinstance(other, CtyCapsuleWithOps):
            return False
        return self.name == other.name and self._py_type == other._py_type and self._ops() == other._ops()

    def __repr__(self) -> str:
        return f"CtyCapsuleWithOps({self.name}, {self._py_type.__name__})"

    def __hash__(self) -> int:
        return hash((self.name, self._py_type, *self._ops()))


# 🌊🪢🔚
