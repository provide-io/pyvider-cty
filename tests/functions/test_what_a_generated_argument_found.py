#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Six rules the stdlib fuzz found on 2026-08-19, one class each.

`tests/compatibility/test_stdlib_fuzz.py` generates arguments for all 83 stdlib
functions and compares the answers against real go-cty. These are the rules it
turned up outside the numeric width (which has a file of its own,
`test_arithmetic_at_go_ctys_width.py`) and the set ordering (which has
`tests/set/test_a_composite_element_sorts_by_its_hash_bytes.py`).

Each one had a hand-written sweep row for the function already; none of the rows
used an argument shaped like these. They run without a Go toolchain, and every
expectation was read from the oracle rather than from go-cty's source.
"""

from __future__ import annotations

import pytest

from pyvider.cty import (
    CtyBool,
    CtyList,
    CtyNumber,
    CtySet,
    CtyString,
    CtyTuple,
    CtyValue,
)
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import STDLIB
from pyvider.cty.types import BytesCapsule

S, N, B = CtyString(), CtyNumber(), CtyBool()


class TestCsvDecodeIsAsStrictAsGosReader:
    """Python's `csv` has no strict mode; Go's reader refuses three things.

    A malformed document parsed here and refused by go-cty means a provider
    builds state out of something Terraform would have rejected outright.
    """

    @pytest.mark.parametrize(
        ("label", "document", "message"),
        [
            ("an unterminated quoted field", '"unterminated', "quoted-field"),
            ("a quoted field followed by junk", 'a,"b"x\n1,2', "quoted-field"),
            ("a bare quote in a plain field", 'a,b\n1,2"3', "non-quoted-field"),
            ("a ragged row", "a,b\n1,2,3", "wrong number of fields"),
        ],
    )
    def test_a_malformed_document_is_refused(self, label: str, document: str, message: str) -> None:
        with pytest.raises(CtyFunctionError, match=message):
            STDLIB["csvdecode"](S.validate(document))

    @pytest.mark.parametrize("document", ["", "\n", "\n\n"])
    def test_a_document_with_no_header_row_is_refused(self, document: str) -> None:
        """Go's reader skips a blank line; Python's yields an empty record, and
        that record became a header with no columns."""
        with pytest.raises(CtyFunctionError, match="missing header"):
            STDLIB["csvdecode"](S.validate(document))

    @pytest.mark.parametrize(
        ("label", "document"),
        [
            ("an escaped quote", 'a,b\n"1""x",2'),
            ("leading blank lines", "\n\na,b\n1,2"),
            ("a quoted comma", 'a,b\n"x,y",2'),
        ],
    )
    def test_a_well_formed_document_still_parses(self, label: str, document: str) -> None:
        assert len(STDLIB["csvdecode"](S.validate(document)).value) == 1, label


class TestRegexMatchesTheWayGoDoes:
    def test_an_empty_match_after_a_match_is_dropped(self) -> None:
        """Go's `FindAll` skips an empty match at the end of the previous one
        (`regexp.allMatches`); Python's `finditer` keeps it, so `regexall` had
        one extra element in a list a caller indexes into."""
        answer = STDLIB["regexall"](S.validate("a*a*"), S.validate("a"))

        assert [element.value for element in answer.value] == ["a"]

    def test_an_empty_match_anywhere_else_is_kept(self) -> None:
        """The rule has to stay narrow: two empty matches, on both sides."""
        answer = STDLIB["regexall"](S.validate("b*"), S.validate("a"))

        assert [element.value for element in answer.value] == ["", ""]

    def test_the_perl_classes_are_ascii_as_they_are_in_re2(self) -> None:
        """RE2 defines `\\w` as `[0-9A-Za-z_]`; Python's is Unicode-aware, so
        `regexall("\\w", "²")` was one match here and none in go-cty."""
        assert STDLIB["regexall"](S.validate(r"\w"), S.validate("²")).value == ()
        assert [e.value for e in STDLIB["regexall"](S.validate(r"\w"), S.validate("a")).value] == ["a"]

    def test_case_folding_stays_unicode(self) -> None:
        """`re.ASCII` would narrow folding too, which RE2 does not do, so it is
        withheld from a pattern that asks for case-insensitivity."""
        assert STDLIB["regex"](S.validate("(?i)Σ"), S.validate("σ")).value == "σ"  # noqa: RUF001


class TestTimeaddBelowAMicrosecond:
    def test_a_negative_nanosecond_moves_the_instant_backwards(self) -> None:
        """A `timedelta` resolves to microseconds and a `time.Duration` to
        nanoseconds, and taking the duration's magnitude before truncating put
        every negative sub-microsecond shift on the wrong side of the second."""
        answer = STDLIB["timeadd"](S.validate("0002-01-01T00:00:00Z"), S.validate("-1ns"))

        assert answer.value == "0001-12-31T23:59:59Z"

    @pytest.mark.parametrize(
        ("duration", "expected"),
        [
            ("1ns", "0002-01-01T00:00:00Z"),
            ("-1500ns", "0001-12-31T23:59:59Z"),
            ("1h", "0002-01-01T01:00:00Z"),
            ("-1h", "0001-12-31T23:00:00Z"),
        ],
    )
    def test_the_ordinary_durations_are_unchanged(self, duration: str, expected: str) -> None:
        answer = STDLIB["timeadd"](S.validate("0002-01-01T00:00:00Z"), S.validate(duration))

        assert answer.value == expected

    def test_a_duration_is_carried_as_whole_nanoseconds(self) -> None:
        """No longer rounded to a `timedelta` on the way in -- 1500ns is 1500ns,
        and `timeadd` rounds nothing at all now that the instant carries its own
        nanoseconds. See `test_timeadd_is_exact_to_the_nanosecond.py`."""
        from pyvider.cty.functions.datetime_functions import _parse_duration_nanoseconds

        assert _parse_duration_nanoseconds("1500ns") == 1500
        assert _parse_duration_nanoseconds("-1500ns") == -1500


class TestAnUnknownLeavesASetsLengthUndecided:
    """A set's length is a *bound* while any element is unknown, at any depth.

    An unknown element may still resolve to a value equal to another member and
    coalesce with it, so the count is not an answer. This asked whether any
    element `is_unknown`, one level deep, and a set of lists holding an unknown
    *inside* a list counted itself as known.
    """

    def test_a_nested_unknown_makes_the_length_unknown(self) -> None:
        holder = CtySet(element_type=CtyList(element_type=S)).validate([["a"], [CtyValue.unknown(S)]])

        assert STDLIB["length"](holder).is_unknown

    def test_a_single_element_set_still_knows_its_length(self) -> None:
        """go-cty's own exception: nothing else is there for it to coalesce with."""
        holder = CtySet(element_type=S).validate([CtyValue.unknown(S)])

        assert STDLIB["length"](holder).value == 1

    def test_flatten_defers_when_a_set_it_would_flatten_has_no_known_length(self) -> None:
        """go-cty's `flattener` opens with `Length().IsKnown()` and gives up on
        the whole result there, so the answer is an unknown of *dynamic* type
        rather than a tuple whose length it cannot claim to know."""
        inner = CtySet(element_type=B).validate([CtyValue.unknown(B), CtyValue.null(B)])
        outer = CtyTuple(element_types=(inner.type,)).validate([inner])

        answer = STDLIB["flatten"](outer)

        assert answer.is_unknown
        assert str(answer.type) == "dynamic"

    def test_flatten_of_a_list_holding_an_unknown_still_flattens(self) -> None:
        """A list always knows its length, so nothing is in doubt."""
        inner = CtyList(element_type=B).validate([CtyValue.unknown(B), CtyValue.null(B)])
        outer = CtyTuple(element_types=(inner.type,)).validate([inner])

        assert not STDLIB["flatten"](outer).is_unknown


class TestJsonencodeOfAByteBuffer:
    def test_a_capsule_is_encoded_rather_than_refused(self) -> None:
        """go-cty hands the encapsulated value to `encoding/json`
        (`cty/json/marshal.go:165`), and a `[]byte` there is base64."""
        assert STDLIB["jsonencode"](BytesCapsule.validate(b"hi")).value == '"aGk="'

    def test_an_empty_buffer_too(self) -> None:
        assert STDLIB["jsonencode"](BytesCapsule.validate(b"")).value == '""'


class TestARangeWithAZeroStep:
    def test_an_empty_range_is_an_empty_list(self) -> None:
        """go-cty's zero-step guard never fires -- it compares two structs
        holding different `*big.Float` pointers -- so the loop decides, and this
        one stops on its first iteration."""
        assert STDLIB["range"](N.validate(0), N.validate(0), N.validate(0)).value == ()

    def test_a_non_empty_range_hits_the_value_cap_instead(self) -> None:
        with pytest.raises(CtyFunctionError, match="more than 1024 values"):
            STDLIB["range"](N.validate(0), N.validate(10), N.validate(0))


def test_an_object_may_have_an_empty_attribute_name() -> None:
    """`merge` produces one from a map with an empty key, which HCL can write.

    `CtyObject.validate` builds a `GetAttrStep` per attribute and the step
    refused an empty name, so no value of such an object type could be validated
    at all -- and it escaped as a `ValueError`, which the function framework
    reports as a panic.
    """
    from pyvider.cty import CtyMap, CtyObject

    merged = STDLIB["merge"](
        CtyMap(element_type=S).validate({"": "x"}),
        CtyObject(attribute_types={}).validate({}),
    )

    assert merged.value[""].value == "x"


# 🌊🪢🔚
