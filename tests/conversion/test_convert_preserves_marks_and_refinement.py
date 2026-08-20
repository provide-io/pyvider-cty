#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""convert() must not launder marks, and must not throw away refinements.

Both defects lived on the same early return. Marks are how sensitivity travels,
and the codec refuses to serialize a marked value -- so dropping them during a
conversion turns a value the wire rejects into one it accepts. Refinements are
what Terraform plans on, and `not_null` in particular is the bit equality reads
to decide `unknown == null`.
"""

from typing import Any

import pytest

from pyvider.cty import (
    CtyCapsuleWithOps,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyType,
    CtyValue,
)
from pyvider.cty.codec import cty_to_msgpack
from pyvider.cty.conversion.explicit import convert
from pyvider.cty.exceptions import CtyMarksSerializationError
from pyvider.cty.marks import collect_marks_deep
from pyvider.cty.refinement import refine


class Payload:
    """A capsule payload, so a capsule can be converted out of as well as into."""

    def __init__(self, text: str) -> None:
        self.text = text


def test_converting_a_marked_unknown_keeps_its_marks() -> None:
    marked = CtyValue.unknown(CtyNumber()).with_marks({"sensitive"})
    assert convert(marked, CtyString()).marks == frozenset({"sensitive"})


def test_converting_a_marked_null_keeps_its_marks() -> None:
    marked = CtyValue.null(CtyNumber()).with_marks({"sensitive"})
    assert convert(marked, CtyString()).marks == frozenset({"sensitive"})


def test_conversion_cannot_make_a_marked_value_serializable() -> None:
    """The regression in its own terms: refused before, refused after."""
    source = CtyList(element_type=CtyNumber()).validate(
        [CtyValue.unknown(CtyNumber()).with_marks({"sensitive"})]
    )
    target = CtyList(element_type=CtyString())

    with pytest.raises(CtyMarksSerializationError):
        cty_to_msgpack(source, source.type)

    converted = convert(source, target)
    assert collect_marks_deep(converted) == frozenset({"sensitive"})
    with pytest.raises(CtyMarksSerializationError):
        cty_to_msgpack(converted, target)


def test_unwrapping_a_dynamic_keeps_the_wrappers_marks() -> None:
    """The wrapper's marks are not the inner value's, and are just as sensitive."""
    wrapped = CtyDynamic().validate("hi").with_marks({"sensitive"})
    assert convert(wrapped, CtyString()).marks == frozenset({"sensitive"})


def test_converting_into_dynamic_is_a_no_op() -> None:
    """go-cty leaves the value alone: DynamicPseudoType constrains nothing."""
    refined = refine(CtyValue.unknown(CtyString())).string_prefix("https://").not_null().new_value()

    result = convert(refined, CtyDynamic())

    assert result.type.equal(CtyString())
    assert result.value.string_prefix == "https://"
    assert result.value.is_known_null is False


def test_not_null_survives_a_type_change_and_a_string_prefix_does_not() -> None:
    """Nullness is a fact about the value; a string prefix is a fact about a string."""
    refined = refine(CtyValue.unknown(CtyString())).string_prefix("https://").not_null().new_value()

    result = convert(refined, CtyNumber())

    assert result.type.equal(CtyNumber())
    assert result.value.is_known_null is False
    assert result.value.string_prefix is None


class TestNoReturnLaundersAMark:
    """The invariant stated once, over the whole branch space.

    `convert` is one long function with sixteen returns, and the rule that each
    of them re-applies the source's marks is enforced only by every author
    remembering it. One did not: the `convert_to_fn` branch handed back
    `target_type.validate(received)`, and because `received` is a raw Python
    object rather than a `CtyValue`, `@preserves_marks` had nothing to copy
    from. A marked value converted into such a capsule came out clean, which is
    the one thing the codec's refusal exists to prevent.

    The sweep below reaches every return, so a new branch that forgets has to
    also be a shape none of these cases takes.
    """

    SECRET = CtyCapsuleWithOps("Secret", bytes, convert_to_fn=lambda value, _: value.value.encode())
    OUTWARD = CtyCapsuleWithOps(
        "Outward",
        Payload,
        convert_fn=lambda raw, target: (
            CtyString().validate(raw.text) if isinstance(target, CtyString) else None
        ),
    )

    @pytest.mark.parametrize(
        ("label", "source", "target"),
        [
            ("identity", CtyString().validate("x"), CtyString()),
            ("into dynamic", CtyString().validate("x"), CtyDynamic()),
            ("out of dynamic", CtyDynamic().validate("x"), CtyString()),
            ("a null", CtyValue.null(CtyNumber()), CtyString()),
            ("an unknown", CtyValue.unknown(CtyNumber()), CtyString()),
            ("number to string", CtyNumber().validate(1), CtyString()),
            ("string to number", CtyString().validate("1"), CtyNumber()),
            (
                "list to set",
                CtyList(element_type=CtyString()).validate(["a"]),
                CtySet(element_type=CtyString()),
            ),
            (
                "set to list",
                CtySet(element_type=CtyString()).validate(["a"]),
                CtyList(element_type=CtyString()),
            ),
            (
                "tuple to list",
                CtyTuple(element_types=(CtyString(),)).validate(["a"]),
                CtyList(element_type=CtyString()),
            ),
            (
                "map to object",
                CtyMap(element_type=CtyString()).validate({"k": "v"}),
                CtyObject(attribute_types={"k": CtyString()}),
            ),
            (
                "object to map",
                CtyObject(attribute_types={"k": CtyString()}).validate({"k": "v"}),
                CtyMap(element_type=CtyString()),
            ),
            (
                "element retyped",
                CtyList(element_type=CtyNumber()).validate([1]),
                CtyList(element_type=CtyString()),
            ),
            ("into a capsule", CtyString().validate("x"), SECRET),
            ("out of a capsule", OUTWARD.validate(Payload("x")), CtyString()),
        ],
    )
    def test_the_source_marks_come_out_the_other_side(
        self, label: str, source: CtyValue[Any], target: CtyType[Any]
    ) -> None:
        marked = source.with_marks({"sensitive"})

        assert collect_marks_deep(convert(marked, target)) >= frozenset({"sensitive"}), label


class TestConvertingIntoACapsuleKeepsTheMark:
    """The regression in the terms that make it a security defect.

    `convert_to_fn` is provider-supplied, so this is what a provider coercing a
    sensitive config attribute into its own internal representation got: a value
    the wire had been refusing, now accepted.
    """

    SECRET = CtyCapsuleWithOps("Secret", bytes, convert_to_fn=lambda value, _: value.value.encode())

    def test_the_mark_survives_the_conversion(self) -> None:
        marked = CtyString().validate("hunter2").with_marks({"sensitive"})

        assert convert(marked, self.SECRET).marks == frozenset({"sensitive"})

    def test_and_the_codec_goes_on_refusing_it(self) -> None:
        """Unmarked, the payload is `b'\\xc4\\x07hunter2'` -- the secret in the
        clear. That is what the dropped mark was producing."""
        marked = CtyString().validate("hunter2").with_marks({"sensitive"})

        converted = convert(marked, self.SECRET)

        with pytest.raises(CtyMarksSerializationError):
            cty_to_msgpack(converted, self.SECRET)


# 🌊🪢🔚
