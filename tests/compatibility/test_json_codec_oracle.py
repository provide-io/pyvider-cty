#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The `cty/json` value codec, against real go-cty.

This codec writes state files, `terraform show -json` and plan output, so the
comparison is on **bytes**, not on parsed JSON. Parsing hides the differences
that matter: `1E-7` and `0.0000001` are the same number and not the same state
file, and a `<` written raw or as `\\u003c` is a diff on every plan.

Four divergences were found here, all of them in the direction that looks safe:

  - `<`, `>` and `&` were written raw. Go's encoder escapes them by default, so
    every string containing one differed byte for byte.
  - an unexpected attribute in the document was *dropped*, where go-cty errors.
    A typo in a state file read back as "that attribute is not set".
  - a *missing* attribute was refused, where go-cty fills it with null. That is
    how every unset optional attribute is written, so this rejected ordinary
    documents.
  - a JSON number for a `string` attribute was refused, where go-cty takes the
    literal digits. Being stricter than the reference in a *decoder* means
    refusing input the reference accepts.

The number cases carry the literal token through deliberately: go-cty hands over
the digits as they were written, so `1.50` decodes to `"1.50"` and not `"1.5"`.
"""

from __future__ import annotations

import json
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
from pyvider.cty.conversion import encode_cty_type_to_wire_json
from pyvider.cty.exceptions import CtyValidationError
from pyvider.cty.json_codec import CtyJsonError, cty_from_json, cty_to_json, implied_json_type
from pyvider.cty.parser import parse_tf_type_to_ctytype
from tests.compatibility._oracle import canonical, dynamic_arg, rich, run, type_spec

pytestmark = pytest.mark.compat

S = CtyString()
N = CtyNumber()
B = CtyBool()
STRINGS = CtyList(element_type=S)
NUMBERS = CtySet(element_type=N)
STRING_SET = CtySet(element_type=S)
STRING_MAP = CtyMap(element_type=S)
PAIR = CtyObject(attribute_types={"a": S, "b": N})
TUPLE = CtyTuple(element_types=(S, N))
DYNAMIC = CtyDynamic()

MARSHAL: list[tuple[str, CtyType[Any], CtyValue[Any], Any]] = [
    ("a string", S, S.validate("x"), None),
    ("a string with quotes", S, S.validate('he said "hi"'), None),
    # The escaping cases. Go escapes these three so its output is safe to embed
    # in HTML; Python's json does not.
    ("a string with angle brackets", S, S.validate("a<b>c"), None),
    ("a string with an ampersand", S, S.validate("a&b"), None),
    ("a string with a newline and a tab", S, S.validate("a\nb\tc"), None),
    ("a non-ascii string", S, S.validate("héllo"), None),
    ("an emoji string", S, S.validate("👨‍👩‍👧‍👦"), None),
    ("an integer", N, N.validate(1), None),
    ("a fraction", N, N.validate("1.5"), None),
    ("a trailing zero", N, N.validate("1.50"), None),
    ("a number past 2**53", N, N.validate("9007199254740993"), None),
    # Past `decimal`'s default 28-digit context, where the renderer used to
    # round. The msgpack codec carried every digit of the same value, so the
    # two codecs in this package disagreed and the lossy one was this.
    ("a number past the decimal context", N, N.validate(2**100), None),
    ("a decimal past the context", N, N.validate("1.2345678901234567890123456789"), None),
    ("a negative zero", N, N.validate("-0.0"), None),
    ("an exponent", N, N.validate("1e2"), None),
    ("a tiny number", N, N.validate("1e-7"), None),
    ("a negative fraction", N, N.validate("-0.5"), None),
    ("a bool", B, B.validate(True), None),
    ("a false bool", B, B.validate(False), None),
    ("a null", S, CtyValue.null(S), None),
    ("a list", STRINGS, STRINGS.validate(["a", "b"]), None),
    ("an empty list", STRINGS, STRINGS.validate([]), None),
    ("a list holding a null", STRINGS, STRINGS.validate(["a", CtyValue.null(S)]), None),
    ("a set of strings", STRING_SET, STRING_SET.validate(["b", "a"]), None),
    # See the msgpack oracle: a prefix sorts last in go-cty and used to sort
    # first here, so a set of composites re-encoded in a different order.
    (
        "a set of lists where one is a prefix of another",
        CtySet(element_type=STRINGS),
        CtySet(element_type=STRINGS).validate([["a"], ["a", "c"], []]),
        None,
    ),
    ("a set of numbers", NUMBERS, NUMBERS.validate([3, 1, 2]), None),
    ("a map", STRING_MAP, STRING_MAP.validate({"b": "2", "a": "1"}), None),
    ("an empty map", STRING_MAP, STRING_MAP.validate({}), None),
    ("a map key needing an escape", STRING_MAP, STRING_MAP.validate({"a<b": "1"}), None),
    ("an object", PAIR, PAIR.validate({"a": "x", "b": 1}), None),
    ("an object holding a null", PAIR, PAIR.validate({"a": CtyValue.null(S), "b": 1}), None),
    ("a tuple", TUPLE, TUPLE.validate(["x", 1]), None),
    (
        "a nested structure",
        CtyList(element_type=PAIR),
        CtyList(element_type=PAIR).validate([{"a": "x", "b": 1}]),
        None,
    ),
]

DYNAMIC_MARSHAL: list[tuple[str, CtyValue[Any]]] = [
    ("a dynamic string", S.validate("x")),
    ("a dynamic number", N.validate(1)),
    ("a dynamic bool", B.validate(True)),
    ("a dynamic list", STRINGS.validate(["a"])),
    ("a dynamic object", PAIR.validate({"a": "x", "b": 1})),
]


@pytest.mark.parametrize(("label", "cty_type", "value", "_unused"), MARSHAL, ids=[case[0] for case in MARSHAL])
def test_marshal_produces_the_same_bytes(
    label: str, cty_type: CtyType[Any], value: CtyValue[Any], _unused: Any
) -> None:
    theirs = run("cty", "json", "marshal", "--type", type_spec(cty_type), json.dumps(rich(value)))
    assert theirs["ok"], theirs

    assert cty_to_json(value, cty_type).decode() == theirs["text"], label


@pytest.mark.parametrize(("label", "value"), DYNAMIC_MARSHAL, ids=[case[0] for case in DYNAMIC_MARSHAL])
def test_marshal_of_a_dynamic_position_produces_the_same_bytes(label: str, value: CtyValue[Any]) -> None:
    """The envelope: a dynamic position carries the concrete type alongside."""
    theirs = run("cty", "json", "marshal", "--type", type_spec(DYNAMIC), json.dumps(dynamic_arg(value)))
    assert theirs["ok"], theirs

    assert cty_to_json(value, DYNAMIC).decode() == theirs["text"], label


def test_marshal_refuses_infinity_the_same_way() -> None:
    theirs = run("cty", "json", "marshal", "--type", type_spec(N), json.dumps({"$number": "Infinity"}))

    assert theirs["ok"] is False
    assert "infinity" in (theirs.get("error") or theirs.get("panic", "")).lower()

    with pytest.raises(CtyJsonError, match="infinity"):
        cty_to_json(N.validate("Infinity"), N)


UNMARSHAL: list[tuple[str, CtyType[Any], str]] = [
    ("a string", S, '"x"'),
    ("an escaped string", S, '"a\\u003cb"'),
    ("a number", N, "1.5"),
    ("a number past 2**53", N, "9007199254740993"),
    ("a number written as a string", N, '"1.5"'),
    ("a bool", B, "true"),
    ("a bool written as a string", B, '"true"'),
    ("a null", S, "null"),
    # The coercions. go-cty takes the literal digits for a string.
    ("a number for a string", S, "1.5"),
    ("a trailing zero for a string", S, "1.50"),
    ("an exponent for a string", S, "1e2"),
    ("a bool for a string", S, "true"),
    ("a bool for a number", N, "true"),
    ("a string for a bool", B, '"nonsense"'),
    ("a list", STRINGS, '["a","b"]'),
    ("an empty list", STRINGS, "[]"),
    ("a list holding a null", STRINGS, '["a",null]'),
    ("a set with a duplicate", STRING_SET, '["a","a","b"]'),
    ("a map", STRING_MAP, '{"a":"1","b":"2"}'),
    ("an empty map", STRING_MAP, "{}"),
    ("an object", PAIR, '{"a":"x","b":1}'),
    ("an object missing an attribute", PAIR, '{"a":"x"}'),
    ("an object with an unexpected attribute", PAIR, '{"a":"x","b":1,"c":2}'),
    ("an empty object", PAIR, "{}"),
    ("a tuple", TUPLE, '["x",1]'),
    ("a dynamic envelope", DYNAMIC, '{"value":"x","type":"string"}'),
    ("a dynamic envelope holding a list", DYNAMIC, '{"value":["a"],"type":["list","string"]}'),
    ("an object for a list", STRINGS, '{"a":"b"}'),
    ("a list for an object", PAIR, '["a"]'),
]


@pytest.mark.parametrize(("label", "cty_type", "payload"), UNMARSHAL, ids=[case[0] for case in UNMARSHAL])
def test_unmarshal_reads_the_same_value(label: str, cty_type: CtyType[Any], payload: str) -> None:
    theirs = run("cty", "json", "unmarshal", "--type", type_spec(cty_type), payload)

    if not theirs["ok"]:
        # go-cty refused it, so this must refuse it too. Which exception carries
        # the refusal is this library's business; that there is one is not.
        with pytest.raises(CtyJsonError):
            cty_from_json(payload, cty_type)
        return

    here = cty_from_json(payload, cty_type)
    assert canonical(rich(here)) == canonical(theirs["value"]), label


IMPLIED = [
    '"x"',
    "1",
    "1.5",
    "true",
    "null",
    "[]",
    '["a"]',
    '["a",1]',
    "{}",
    '{"a":"x"}',
    '{"a":{"b":1}}',
    '{"a":[1,"b"]}',
    "[[1],[2]]",
    '{"value":"x","type":"string"}',
    '{"a":null}',
    '{"a": 1, "a": 2}',
    "[null]",
]


@pytest.mark.parametrize("payload", IMPLIED)
def test_implied_type_agrees(payload: str) -> None:
    theirs = run("cty", "json", "implied-type", payload)
    assert theirs["ok"], theirs

    assert canonical(encode_cty_type_to_wire_json(implied_json_type(payload))) == canonical(theirs["type"])


@pytest.mark.parametrize(
    "payload",
    ['{"a": 1, "a": "x"}', '{"o": {"a": 1, "a": "x"}}'],
)
def test_a_duplicate_property_of_a_different_type_is_refused_by_both(payload: str) -> None:
    """go-cty 1.16.2; the same-typed carve-out is in IMPLIED above via the agree test."""
    theirs = run("cty", "json", "implied-type", payload)

    assert theirs["ok"] is False, theirs
    assert 'duplicate "a" property' in theirs["error"]
    with pytest.raises(CtyJsonError, match='duplicate "a" property in JSON object'):
        implied_json_type(payload)


@pytest.mark.parametrize("type_json", ['["object",{"a":"number"}]', '["map","number"]'])
def test_unmarshal_decodes_every_duplicate_property_as_go_does(type_json: str) -> None:
    """go-cty decodes each occurrence against the type and keeps the last."""
    cty_type = parse_tf_type_to_ctytype(json.loads(type_json))

    refused = run("cty", "json", "unmarshal", '{"a": "x", "a": 1}', "--type", type_json)
    assert refused["ok"] is False, refused
    with pytest.raises(CtyJsonError):
        cty_from_json('{"a": "x", "a": 1}', cty_type)

    kept = run("cty", "json", "unmarshal", '{"a": 2, "a": 1}', "--type", type_json)
    assert kept["ok"], kept
    assert canonical(kept["value"]) == canonical({"a": 1})
    assert cty_from_json('{"a": 2, "a": 1}', cty_type).value["a"].value == 1


@pytest.mark.parametrize(
    "payload",
    [
        '{"type": ["bogus"], "type": "string", "value": "x"}',
        '{"type": "string", "type": ["bogus"], "value": "x"}',
    ],
)
def test_an_invalid_duplicate_type_in_the_dynamic_envelope_is_refused_by_both(payload: str) -> None:
    """go-cty fails on the first invalid `type` occurrence regardless of order."""
    theirs = run("cty", "json", "unmarshal", payload, "--type", '"dynamic"')

    assert theirs["ok"] is False, theirs
    with pytest.raises(CtyValidationError):
        cty_from_json(payload, CtyDynamic())


def test_two_valid_duplicate_types_in_the_dynamic_envelope_keep_the_last() -> None:
    payload = '{"type": "string", "type": "number", "value": 1}'
    theirs = run("cty", "json", "unmarshal", payload, "--type", '"dynamic"')

    assert theirs["ok"], theirs
    decoded = cty_from_json(payload, CtyDynamic())
    assert canonical(rich(decoded)) == canonical(theirs["value"])


def test_a_document_that_is_not_json_is_refused_by_both() -> None:
    theirs = run("cty", "json", "implied-type", "not json")

    assert theirs["ok"] is False
    with pytest.raises(json.JSONDecodeError):
        implied_json_type("not json")


def test_a_round_trip_through_go_returns_the_same_value() -> None:
    """The two halves composed across the language boundary.

    Marshalled here, decoded there, and the value that comes back is compared
    against the one that went in. A pair of encoders that agree with each other
    but not with go-cty would pass every test above that compares like with
    like; this one cannot be satisfied that way.
    """
    value = PAIR.validate({"a": "a<b", "b": "1.50"})

    encoded = cty_to_json(value, PAIR).decode()
    theirs = run("cty", "json", "unmarshal", "--type", type_spec(PAIR), encoded)

    assert theirs["ok"], theirs
    assert canonical(theirs["value"]) == canonical(rich(value))


# 🌊🪢🔚
