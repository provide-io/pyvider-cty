#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`cty_to_json` / `cty_from_json` / `implied_json_type` — go-cty's `cty/json`.

The serialization codec, not the `jsonencode`/`jsondecode` stdlib functions. It
is byte-compared against real go-cty in `tests/compatibility/`; this covers the
decisions that a byte comparison of well-formed values would not reach — what it
*refuses*, and what it does with the two things JSON cannot express.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from pyvider.cty import (
    CtyBool,
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
from pyvider.cty.exceptions import CtyValidationError
from pyvider.cty.json_codec import (
    CtyJsonError,
    cty_from_json,
    cty_to_json,
    implied_json_type,
)
from pyvider.cty.marks import CtyMark

S, N, B = CtyString(), CtyNumber(), CtyBool()


class TestRoundTrip:
    @pytest.mark.parametrize(
        ("cty_type", "document"),
        [
            (S, b'"hi"'),
            (S, '"héllo"'.encode()),
            (N, b"42"),
            (N, b"1.5"),
            (N, b"9007199254740993"),
            (B, b"true"),
            (S, b"null"),
            (CtyList(element_type=S), b'["a","b"]'),
            (CtyList(element_type=S), b"[]"),
            (CtySet(element_type=S), b'["a","b"]'),
            (CtyMap(element_type=S), b'{"a":"1","b":"2"}'),
            (CtyObject({"a": S, "b": N}), b'{"a":"x","b":1}'),
            (CtyTuple(element_types=(S, N)), b'["a",1]'),
            (CtyList(element_type=S), b'["a",null]'),
        ],
        ids=lambda v: v.decode() if isinstance(v, bytes) else str(v),
    )
    def test_a_document_survives_a_round_trip_unchanged(self, cty_type: CtyType[Any], document: bytes) -> None:
        assert cty_to_json(cty_from_json(document, cty_type), cty_type) == document

    def test_an_escaped_string_canonicalises_to_literal_utf8(self) -> None:
        """Round-tripping is semantic, not byte-identity, for escaped input.

        go-cty writes the character rather than the escape, so `\\u00e9` on the
        way in comes back as `é`. Both are the same string; only one is what
        either implementation emits.
        """
        assert cty_to_json(cty_from_json(b'"h\\u00e9llo"', S), S) == '"héllo"'.encode()

    def test_a_number_is_written_the_way_go_cty_writes_it(self) -> None:
        """`big.Float.Text('f', -1)`: no exponent, no trailing zeros."""
        assert cty_to_json(N.validate(Decimal("1e2")), N) == b"100"
        assert cty_to_json(N.validate(Decimal("1.50")), N) == b"1.5"

    def test_a_big_integer_keeps_every_digit(self) -> None:
        """Past float64, which is where a naive encoder starts rounding."""
        assert cty_to_json(N.validate(Decimal("9007199254740993")), N) == b"9007199254740993"


class TestWhatJsonCannotCarry:
    def test_an_unknown_is_refused(self) -> None:
        """`null` would be a lie: not-yet-computed is not the same as no value."""
        with pytest.raises(CtyJsonError, match="not known"):
            cty_to_json(CtyValue.unknown(S), S)

    def test_a_marked_value_is_refused(self) -> None:
        """Same rule as the msgpack codec: serializing must not declassify."""
        with pytest.raises(CtyJsonError, match="marks"):
            cty_to_json(S.validate("secret").mark(CtyMark("sensitive")), S)

    def test_an_infinity_is_refused(self) -> None:
        """JSON has no infinity, and both alternatives change the value."""
        with pytest.raises(CtyJsonError, match="infinity"):
            cty_to_json(CtyValue(vtype=N, value=Decimal("Infinity")), N)


class TestDynamic:
    def test_a_dynamic_target_carries_its_real_type(self) -> None:
        """Without the type alongside, the far side has nothing to decode against."""
        encoded = cty_to_json(S.validate("x"), CtyDynamic())

        assert encoded == b'{"value":"x","type":"string"}'

    def test_a_dynamic_document_round_trips(self) -> None:
        decoded = cty_from_json(b'{"value":"x","type":"string"}', CtyDynamic())

        assert cty_to_json(decoded, CtyDynamic()) == b'{"value":"x","type":"string"}'

    def test_a_malformed_dynamic_document_is_refused(self) -> None:
        with pytest.raises(CtyJsonError, match="missing type"):
            cty_from_json(b'{"value":"x"}', CtyDynamic())

    def test_a_dynamic_envelope_that_is_not_an_object_is_refused(self) -> None:
        with pytest.raises(CtyJsonError, match="'value' and 'type'"):
            cty_from_json(b'"x"', CtyDynamic())

    def test_an_explicit_null_value_is_kept(self) -> None:
        """`value: null` is a null of the declared type, not a missing value."""
        decoded = cty_from_json(b'{"type":"string","value":null}', CtyDynamic())

        assert decoded.value.is_null


class TestRefusals:
    def test_an_array_is_required_for_a_collection(self) -> None:
        with pytest.raises(CtyJsonError, match="array is required"):
            cty_from_json(b'{"a":1}', CtyList(element_type=N))

    def test_an_object_is_required_for_a_map(self) -> None:
        with pytest.raises(CtyJsonError, match="object is required"):
            cty_from_json(b"[1]", CtyMap(element_type=N))

    def test_a_tuple_of_the_wrong_length_is_refused(self) -> None:
        with pytest.raises(CtyJsonError, match="2 elements are required"):
            cty_from_json(b'["a"]', CtyTuple(element_types=(S, N)))


class TestImpliedType:
    @pytest.mark.parametrize(
        ("document", "expected"),
        [
            (b'"s"', CtyString()),
            (b"1", CtyNumber()),
            (b"true", CtyBool()),
            (b"null", CtyDynamic()),
            (b'{"a":"x"}', CtyObject({"a": CtyString()})),
        ],
        ids=lambda v: v.decode() if isinstance(v, bytes) else str(v),
    )
    def test_the_type_a_document_implies(self, document: bytes, expected: CtyType[Any]) -> None:
        assert implied_json_type(document).equal(expected)

    def test_an_array_implies_a_tuple_and_not_a_list(self) -> None:
        """JSON does not promise an array's elements share a type.

        Choosing a list would have to invent one -- and for `[1, "a"]` there is
        no honest choice but `dynamic`, which loses both.
        """
        implied = implied_json_type(b'[1,"a"]')

        assert implied.equal(CtyTuple(element_types=(CtyNumber(), CtyString())))

    def test_an_implied_type_decodes_its_own_document(self) -> None:
        """The pair has to compose, or `ImpliedType` is only decorative."""
        document = b'{"a":"x","b":[1,2]}'

        decoded = cty_from_json(document, implied_json_type(document))

        assert decoded.value["a"].value == "x"


class TestDuplicateProperties:
    """go-cty 1.16.2: a repeated property name is an error, with one carve-out.

    `ImpliedType` refuses `{"a": 1, "a": "x"}` -- the two occurrences imply
    different types -- and accepts `{"a": 1, "a": 2}` as a compatibility
    concession, since the object type it implies decodes either one. `Unmarshal`
    decodes *every* occurrence against the declared type and keeps the last, so
    a wrong-typed earlier duplicate is still an error. This decoder took
    Python's last-wins reading for both and never saw the earlier value.
    """

    def test_implied_accepts_a_duplicate_of_the_same_type(self) -> None:
        assert implied_json_type(b'{"a": 1, "a": 2}').equal(CtyObject({"a": CtyNumber()}))

    def test_implied_refuses_a_duplicate_of_a_different_type(self) -> None:
        with pytest.raises(CtyJsonError, match='duplicate "a" property in JSON object'):
            implied_json_type(b'{"a": 1, "a": "x"}')

    def test_implied_refuses_a_nested_duplicate_of_a_different_type(self) -> None:
        with pytest.raises(CtyJsonError, match='duplicate "a" property in JSON object'):
            implied_json_type(b'{"o": {"a": 1, "a": "x"}}')

    def test_implied_a_same_typed_duplicate_decodes_with_the_last_value(self) -> None:
        document = b'{"a": 1, "a": 2}'
        assert cty_from_json(document, implied_json_type(document)).value["a"].value == 2

    @pytest.mark.parametrize(
        "cty_type",
        [CtyObject({"a": CtyNumber()}), CtyMap(element_type=CtyNumber())],
        ids=["object", "map"],
    )
    def test_unmarshal_decodes_every_duplicate_against_the_type(self, cty_type: CtyType[Any]) -> None:
        with pytest.raises(CtyJsonError, match="number is required"):
            cty_from_json(b'{"a": "x", "a": 1}', cty_type)

    @pytest.mark.parametrize(
        "cty_type",
        [CtyObject({"a": CtyNumber()}), CtyMap(element_type=CtyNumber())],
        ids=["object", "map"],
    )
    def test_unmarshal_keeps_the_last_duplicate(self, cty_type: CtyType[Any]) -> None:
        assert cty_from_json(b'{"a": 2, "a": 1}', cty_type).value["a"].value == 1


class TestDynamicEnvelopeDuplicateType:
    """The dynamic envelope's `type` key follows go-cty's own decode order, not a dict's.

    go-cty's `unmarshalDynamic` (`json/unmarshal.go:367`) reads key/value pairs
    one at a time and parses *every* `"type"` occurrence as it is encountered,
    failing immediately on the first one that is not a valid type description --
    even when a later occurrence would have been valid. A dict's last-wins
    reading only ever sees the final occurrence, so `{"type": ["bogus"],
    "type": "string", "value": "x"}` decoded to the string `"x"` here while
    go-cty refuses it on the first, invalid, occurrence. `value` has no such
    rule: go-cty overwrites it unconditionally with no validation at read
    time, so last-wins for `value` is already correct.
    """

    def test_an_invalid_type_before_a_valid_one_is_refused(self) -> None:
        # CtyValidationError, not CtyJsonError: the refusal comes straight out of
        # parse_tf_type_to_ctytype, unwrapped, exactly as a single bad type does.
        with pytest.raises(CtyValidationError):
            cty_from_json('{"type": ["bogus"], "type": "string", "value": "x"}', CtyDynamic())

    def test_an_invalid_type_after_a_valid_one_is_still_refused(self) -> None:
        with pytest.raises(CtyValidationError):
            cty_from_json('{"type": "string", "type": ["bogus"], "value": "x"}', CtyDynamic())

    def test_two_valid_types_keep_the_last(self) -> None:
        decoded = cty_from_json('{"type": "string", "type": "number", "value": 1}', CtyDynamic())

        assert decoded.value.type.equal(CtyNumber())
        assert decoded.value.value == 1

    def test_value_is_last_wins_regardless_of_order_relative_to_type(self) -> None:
        assert cty_from_json('{"value": "x", "type": "string"}', CtyDynamic()).value.value == "x"
        assert cty_from_json('{"value": "a", "value": "b", "type": "string"}', CtyDynamic()).value.value == "b"
        assert cty_from_json('{"type": "string", "value": "a", "value": "b"}', CtyDynamic()).value.value == "b"


class TestDynamicEnvelopeAcceptsOnlyTypeAndValue:
    """go-cty's `unmarshalDynamic` (`json/unmarshal.go:390`) has a `default:`
    branch: any key that is not `type` or `value` ends the decode with
    `invalid key %q in dynamically-typed value`. This decoder ignored them, so
    `{"type":"string","extra":1,"value":"x"}` decoded to `"x"` here and was
    refused there.

    The refusal happens *inside* the key loop, so it competes with the other
    two failures by document order -- an unknown key before a bad type
    descriptor wins, and after it loses. The missing-`type` and missing-`value`
    checks run only once the loop has finished, so they always lose to both.
    All four orderings are oracle-pinned in the compatibility suite.
    """

    def test_an_unknown_key_is_refused(self) -> None:
        with pytest.raises(CtyJsonError, match='invalid key "extra"'):
            cty_from_json('{"type": "string", "extra": 1, "value": "x"}', CtyDynamic())

    def test_an_unknown_key_is_refused_wherever_it_sits(self) -> None:
        with pytest.raises(CtyJsonError, match='invalid key "bogus"'):
            cty_from_json('{"value": "x", "type": "string", "bogus": [1, 2]}', CtyDynamic())

    def test_an_unknown_key_beats_a_later_invalid_type(self) -> None:
        with pytest.raises(CtyJsonError, match='invalid key "bogus"'):
            cty_from_json('{"bogus": 1, "type": ["nope"]}', CtyDynamic())

    def test_an_earlier_invalid_type_beats_an_unknown_key(self) -> None:
        # Not CtyJsonError's "invalid key" -- the type parse fails first, and
        # its refusal comes straight out of parse_tf_type_to_ctytype.
        with pytest.raises(CtyValidationError) as caught:
            cty_from_json('{"type": ["nope"], "bogus": 1}', CtyDynamic())
        assert "invalid key" not in str(caught.value)

    def test_an_unknown_key_beats_the_missing_type_check(self) -> None:
        with pytest.raises(CtyJsonError, match='invalid key "extra"'):
            cty_from_json('{"extra": 1}', CtyDynamic())

    def test_a_missing_type_is_reported_before_a_missing_value(self) -> None:
        with pytest.raises(CtyJsonError, match="missing type"):
            cty_from_json("{}", CtyDynamic())
        with pytest.raises(CtyJsonError, match="missing type"):
            cty_from_json('{"value": "x"}', CtyDynamic())

    def test_a_missing_value_is_reported_once_the_type_is_there(self) -> None:
        with pytest.raises(CtyJsonError, match="missing value"):
            cty_from_json('{"type": "string"}', CtyDynamic())


# 🌊🪢🔚
