#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""A set holding unknown elements does not have a known length.

An unknown element may resolve to a value the set already holds and collapse
into it, so the stored count is an upper bound rather than the length. Treating
it as exact let equality report a definite difference between two sets that may
be identical -- and a provider comparing planned against prior state plans a
replacement on the strength of that.
"""

from pyvider.cty import CtyList, CtySet, CtyString, CtyValue
from pyvider.cty.refinement import refine
from pyvider.cty.value_range import value_range

SET_TYPE = CtySet(element_type=CtyString())


def _set_with_one_unknown() -> CtyValue:
    return SET_TYPE.validate([CtyValue(CtyString(), "a"), CtyValue.unknown(CtyString())])


def test_the_length_of_such_a_set_is_a_range() -> None:
    measured = value_range(_set_with_one_unknown())

    assert measured.length_lower_bound() == 1
    assert measured.length_upper_bound() == 2


def test_a_list_length_is_still_exact() -> None:
    """Only sets collapse; a list of two is two however unknown its elements."""
    with_unknown = CtyList(element_type=CtyString()).validate(
        [CtyValue(CtyString(), "a"), CtyValue.unknown(CtyString())]
    )

    measured = value_range(with_unknown)

    assert measured.length_lower_bound() == 2
    assert measured.length_upper_bound() == 2


def test_equality_against_a_length_refined_unknown_is_undecided() -> None:
    """go-cty answers {"known": false} here; this used to answer a definite False."""
    length_one = refine(CtyValue.unknown(SET_TYPE)).collection_length(1).new_value()

    assert length_one.equals(_set_with_one_unknown()).is_unknown


def test_a_length_that_cannot_overlap_is_still_excluded() -> None:
    """Undecided must not become uninformative: disjoint ranges still answer."""
    length_nine = refine(CtyValue.unknown(SET_TYPE)).collection_length(9).new_value()

    assert length_nine.equals(_set_with_one_unknown()).value is False
