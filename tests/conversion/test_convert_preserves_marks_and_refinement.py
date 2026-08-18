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

import pytest

from pyvider.cty import (
    CtyDynamic,
    CtyList,
    CtyNumber,
    CtyString,
    CtyValue,
)
from pyvider.cty.codec import cty_to_msgpack
from pyvider.cty.conversion.explicit import convert
from pyvider.cty.exceptions import CtyMarksSerializationError
from pyvider.cty.marks import collect_marks_deep
from pyvider.cty.refinement import refine


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
