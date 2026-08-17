#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""go-cty's `CapsuleOps`, and the two fields that are deliberately absent.

Capsules are the escape hatch: a cty value wrapping a native object cty knows
nothing about. `CapsuleOps` is how the wrapping type tells cty what it may do
with that object, so the interesting cases are the *defaults* -- what cty does
when it has not been told.
"""

from __future__ import annotations

from typing import Any

import pytest

from pyvider.cty import CtyCapsule, CtyCapsuleWithOps, CtyString
from pyvider.cty.conversion import can_convert_unsafe, convert
from pyvider.cty.exceptions import CtyConversionError


class Box:
    """A payload whose `__eq__` deliberately disagrees with identity."""

    def __init__(self, value: Any) -> None:
        self.value = value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Box) and self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


class Crate:
    def __init__(self, value: Any) -> None:
        self.value = value


class TestRawEquals:
    def test_the_default_is_identity(self) -> None:
        """go-cty compares by pointer identity when no operation is given.

        cty has not been told what equality means for the payload, so it will
        not guess -- two distinct objects are two distinct values.
        """
        capsule = CtyCapsuleWithOps("Box", Box)

        assert capsule.raw_equals(Box(1), Box(1)) is False

    def test_the_same_object_is_equal_to_itself(self) -> None:
        capsule = CtyCapsuleWithOps("Box", Box)
        box = Box(1)

        assert capsule.raw_equals(box, box) is True

    def test_an_explicit_raw_equals_is_used(self) -> None:
        capsule = CtyCapsuleWithOps("Box", Box, raw_equals_fn=lambda a, b: a.value == b.value)

        assert capsule.raw_equals(Box(1), Box(1)) is True

    def test_equal_fn_is_the_fallback(self) -> None:
        """A capsule declaring only `Equals` has still declared what equality means.

        go-cty falls back the other way -- `Equals` to `RawEquals` -- but
        ignoring a declared `equal_fn` in favour of identity would answer a
        question the type has already answered.
        """
        capsule = CtyCapsuleWithOps("Box", Box, equal_fn=lambda a, b: a.value == b.value)

        assert capsule.raw_equals(Box(1), Box(1)) is True


class TestConversionBothDirections:
    def test_out_of_a_capsule(self) -> None:
        """`convert_fn` is go-cty's `ConversionFrom`."""
        capsule = CtyCapsuleWithOps(
            "Box",
            Box,
            convert_fn=lambda raw, target: (
                CtyString().validate(raw.value) if isinstance(target, CtyString) else None
            ),
        )

        assert convert(capsule.validate(Box("x")), CtyString()).value == "x"

    def test_into_a_capsule(self) -> None:
        """`convert_to_fn` is `ConversionTo`, and was the missing half.

        Without it a capsule could be converted out of and never into, which is
        also what blocked capsule-to-capsule.
        """
        capsule = CtyCapsuleWithOps("Crate", Crate, convert_to_fn=lambda value, _: Crate(value.value))

        assert can_convert_unsafe(CtyString(), capsule) is True
        assert convert(CtyString().validate("y"), capsule).value.value == "y"

    def test_capsule_to_capsule(self) -> None:
        """Needs both halves, and the destination decides first.

        go-cty tries the target's `ConversionTo` before the source's
        `ConversionFrom` (`convert/conversion.go:172-184`).
        """
        source = CtyCapsuleWithOps("Box", Box, convert_fn=lambda raw, _: None)
        target = CtyCapsuleWithOps("Crate", Crate, convert_to_fn=lambda value, _: Crate(value.value.value))

        converted = convert(source.validate(Box("z")), target)

        assert isinstance(converted.value, Crate)
        assert converted.value.value == "z"

    def test_a_capsule_with_no_operations_converts_to_nothing(self) -> None:
        with pytest.raises(CtyConversionError):
            convert(CtyCapsule("Plain", Box).validate(Box(1)), CtyString())


class TestExtensionData:
    def test_an_unrecognised_key_yields_none(self) -> None:
        """Consumers must be able to ask without knowing who answers."""
        assert CtyCapsuleWithOps("Box", Box).extension_data("anything") is None

    def test_a_recognised_key_yields_its_value(self) -> None:
        capsule = CtyCapsuleWithOps("Box", Box, extension_data_fn=lambda key: {"k": 42}.get(key))

        assert capsule.extension_data("k") == 42
        assert capsule.extension_data("other") is None


class TestArity:
    @pytest.mark.parametrize(
        "operation",
        ["equal_fn", "raw_equals_fn", "hash_fn", "convert_fn", "convert_to_fn", "extension_data_fn"],
    )
    def test_a_wrong_arity_is_refused_at_construction(self, operation: str) -> None:
        """Caught here, not at the call site.

        A wrong arity discovered during a conversion or a set insert surfaces as
        a TypeError from deep inside cty, with nothing naming the capsule that
        supplied it.
        """
        with pytest.raises(TypeError, match=operation):
            CtyCapsuleWithOps("Box", Box, **{operation: lambda: None})


class TestTypeIdentity:
    def test_capsules_differing_only_in_an_operation_are_not_equal(self) -> None:
        """Every operation is part of the type's identity, new ones included."""
        plain = CtyCapsuleWithOps("Box", Box)
        with_raw = CtyCapsuleWithOps("Box", Box, raw_equals_fn=lambda a, b: True)

        assert not plain.equal(with_raw)
        assert hash(plain) != hash(with_raw)


def test_go_string_and_type_go_string_are_not_ported() -> None:
    """Recorded as a conclusion, not an omission.

    Two of go-cty's ten `CapsuleOps` fields implement Go's `%#v` verb. Python's
    equivalent is `__repr__`, which the capsule types already define, so there
    is nothing to port -- and a `go_string` attribute would be an invented API
    with no caller and no meaning here.
    """
    capsule = CtyCapsuleWithOps("Box", Box)

    assert not hasattr(capsule, "go_string")
    assert repr(capsule) == "CtyCapsuleWithOps(Box, Box)"


# 🌊🪢🔚
