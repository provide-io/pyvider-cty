#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`convert.Convert`, against real go-cty.

Conversion had only ever been checked *through* the three stdlib functions that
use it -- `tostring`, `tonumber`, `tobool` -- and that is how two earlier bugs
came to be filed against the functions when they were in `convert` underneath.
The harness's `cty convert` converts between serialization formats, not types,
so the conversion table itself had no oracle at all.

Four divergences came out of the first run, and the shape of them is worth
naming: **two were this library converting things go-cty refuses, and two were
its result carrying a type constraint where go-cty produces a concrete type.**

  - list-to-tuple and set-to-tuple were performed here and do not exist in
    go-cty's table. `can_convert_unsafe` already said they were impossible, so
    `convert` was also contradicting its own predicate -- unification asks that
    predicate, so it could refuse a type `convert` would have reached.
  - map-to-object was *missing*, so a provider decoding `map(string)` config
    into a schema object was simply refused.
  - converting to an object type with optional attributes produced a value
    whose type still said "optional", which is a constraint describing a value
    that already exists.
  - converting to `list(any)` produced `list(dynamic)` rather than resolving the
    element type from the source, so a provider returning one told Terraform
    nothing about its elements.

A fifth was in the harness. `GetConversionUnsafe(string, string)` returns nil --
identical types need no conversion function -- and reading that as "not
convertible" made the most ordinary case in the table look like a divergence.

The `CASES` table below is the agreement half. The last section of this module
is the one conversion in the table's neighbourhood that is deliberately *not*
matched -- a set whose length is unknown, converted to a list. Since 2026-08-17
it is not matched by *either* of the two answers that were on the table: this
library now returns a third one, because go-cty's answer and this library's
previous answer are each wrong in a different half of the same question.
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
from pyvider.cty.conversion import can_convert_unsafe, convert
from pyvider.cty.exceptions import CtyConversionError
from pyvider.cty.functions import length
from tests.compatibility._oracle import canonical, refinements, rich, run, type_spec

pytestmark = pytest.mark.compat

S = CtyString()
N = CtyNumber()
B = CtyBool()
D = CtyDynamic()
LS = CtyList(element_type=S)
LN = CtyList(element_type=N)
SS = CtySet(element_type=S)
SN = CtySet(element_type=N)
MS = CtyMap(element_type=S)
MN = CtyMap(element_type=N)
TSS = CtyTuple(element_types=(S, S))
TSN = CtyTuple(element_types=(S, N))
OBJ = CtyObject(attribute_types={"a": S})
OBJ_N = CtyObject(attribute_types={"a": N})
OBJ_TWO = CtyObject(attribute_types={"a": S, "b": N})
OBJ_OPT = CtyObject(attribute_types={"a": S, "b": N}, optional_attributes=frozenset({"b"}))

# (label, source type, value, target type)
CASES: list[tuple[str, CtyType[Any], CtyValue[Any], CtyType[Any]]] = [
    ("a number to a string", N, N.validate(5), S),
    ("a fraction to a string", N, N.validate("1.50"), S),
    ("an exponent to a string", N, N.validate("1e2"), S),
    ("a string to a number", S, S.validate("5"), N),
    ("a string that is not a number", S, S.validate("abc"), N),
    ("a bool to a string", B, B.validate(True), S),
    ("a string to a bool", S, S.validate("true"), B),
    ("a string to a bool, wrong case", S, S.validate("TRUE"), B),
    ("a one to a bool", S, S.validate("1"), B),
    ("a number to a bool", N, N.validate(1), B),
    ("a bool to a number", B, B.validate(True), N),
    ("a string to itself", S, S.validate("x"), S),
    ("a null through a conversion", N, CtyValue.null(N), S),
    ("an unknown through a conversion", N, CtyValue.unknown(N), S),
    ("a null with no conversion available", LS, CtyValue.null(LS), N),
    ("a list to a set", LS, LS.validate(["a", "a", "b"]), SS),
    ("a set to a list", SS, SS.validate(["b", "a"]), LS),
    ("a tuple to a list", TSS, TSS.validate(["a", "b"]), LS),
    ("a mixed tuple to a list", TSN, TSN.validate(["a", 1]), LS),
    ("a tuple to a set", TSS, TSS.validate(["a", "a"]), SS),
    ("a list of numbers to a list of strings", LN, LN.validate([1, 2]), LS),
    ("an empty list to a set", LS, LS.validate([]), SS),
    ("a list holding a null to a set", LS, LS.validate(["a", CtyValue.null(S)]), SS),
    ("a null list to a set", LS, CtyValue.null(LS), SS),
    # The two go-cty does not have. A collection's length is a property of the
    # value and a tuple's is part of its type.
    ("a list to a tuple", LS, LS.validate(["a", "b"]), TSS),
    ("a set to a tuple", SS, SS.validate(["a", "b"]), TSS),
    ("a map to an object", MS, MS.validate({"a": "x"}), OBJ),
    ("a map with a spare key to an object", MS, MS.validate({"a": "x", "z": "y"}), OBJ),
    ("a map missing a required attribute", MS, MS.validate({"z": "y"}), OBJ),
    ("a map missing an optional attribute", MS, MS.validate({"a": "x"}), OBJ_OPT),
    ("a map whose elements need converting", MN, MN.validate({"a": 5}), OBJ),
    ("an object to a map", OBJ, OBJ.validate({"a": "x"}), MS),
    ("an object attribute needing conversion", OBJ, OBJ.validate({"a": "5"}), OBJ_N),
    ("an object missing an optional attribute", OBJ, OBJ.validate({"a": "x"}), OBJ_OPT),
    ("an object missing a required attribute", OBJ, OBJ.validate({"a": "x"}), OBJ_TWO),
    (
        "an object with a spare attribute",
        CtyObject(attribute_types={"a": S, "z": S}),
        CtyObject(attribute_types={"a": S, "z": S}).validate({"a": "x", "z": "y"}),
        OBJ,
    ),
    ("anything to dynamic", LS, LS.validate(["a"]), D),
    ("a dynamic to a string", D, D.validate("x"), S),
    # `list(any)` is the absence of a constraint, not a request for dynamics.
    ("a list to a list of any", LS, LS.validate(["a"]), CtyList(element_type=D)),
    ("a set to a list of any", SS, SS.validate(["a"]), CtyList(element_type=D)),
    ("a uniform tuple to a list of any", TSS, TSS.validate(["a", "b"]), CtyList(element_type=D)),
    ("an empty list to a list of any", LS, LS.validate([]), CtyList(element_type=D)),
    ("a string to a list", S, S.validate("x"), LS),
    ("a list to a number", LS, LS.validate(["a"]), N),
    ("an object to an unrelated object", OBJ, OBJ.validate({"a": "x"}), CtyObject(attribute_types={"q": S})),
    (
        "a list of objects to a list of objects",
        CtyList(element_type=OBJ),
        CtyList(element_type=OBJ).validate([{"a": "5"}]),
        CtyList(element_type=OBJ_N),
    ),
    (
        "a nested optional attribute",
        CtyObject(attribute_types={"inner": OBJ}),
        CtyObject(attribute_types={"inner": OBJ}).validate({"inner": {"a": "x"}}),
        CtyObject(attribute_types={"inner": OBJ_OPT}),
    ),
]

IDS = [case[0] for case in CASES]


def _theirs(source: CtyType[Any], value: CtyValue[Any], target: CtyType[Any]) -> dict[str, Any]:
    return run(
        "cty",
        "convert-value",
        "--from",
        type_spec(source),
        "--to",
        type_spec(target),
        json.dumps(rich(value)),
    )


@pytest.mark.parametrize(("label", "source", "value", "target"), CASES, ids=IDS)
def test_the_two_convert_the_same_way(
    label: str, source: CtyType[Any], value: CtyValue[Any], target: CtyType[Any]
) -> None:
    theirs = _theirs(source, value, target)

    if not theirs["ok"]:
        with pytest.raises(CtyConversionError):
            convert(value, target)
        return

    here = convert(value, target)
    assert canonical(rich(here)) == canonical(theirs["value"]), label
    assert json.loads(type_spec(here.type)) == theirs["type"], f"{label}: result type"


@pytest.mark.parametrize(("label", "source", "value", "target"), CASES, ids=IDS)
def test_the_predicate_agrees_with_go_cty(
    label: str, source: CtyType[Any], value: CtyValue[Any], target: CtyType[Any]
) -> None:
    """`can_convert_unsafe` is `GetConversionUnsafe` as a question about types.

    Unification asks it, so a divergence here means unification proposes a type
    nothing can reach, or refuses one that is reachable.
    """
    theirs = _theirs(source, value, target)

    assert can_convert_unsafe(source, target) == theirs["unsafe"], label


@pytest.mark.parametrize(("label", "source", "value", "target"), CASES, ids=IDS)
def test_the_predicate_agrees_with_this_librarys_own_convert(
    label: str, source: CtyType[Any], value: CtyValue[Any], target: CtyType[Any]
) -> None:
    """The internal half, which is how the list-to-tuple divergence was visible.

    `convert` performed a conversion `can_convert_unsafe` denied. A predicate
    that disagrees with the function it describes is wrong however go-cty
    behaves, so this holds without consulting the harness at all.

    The converse does not hold and is not asserted: "unsafe" means the
    conversion depends on the value, so a permitted conversion may still fail on
    a particular one -- `"abc"` to a number is the standing example.
    """
    try:
        convert(value, target)
    except CtyConversionError:
        return

    assert can_convert_unsafe(source, target), label


def test_a_conversion_result_never_carries_optional_attributes() -> None:
    """Optionality describes a constraint, and a converted value is not one.

    go-cty strips it in both directions -- deciding a conversion is unnecessary,
    and building the result -- and the difference reaches the wire, where a
    schema and a value would otherwise be told apart by it.
    """
    converted = convert(OBJ.validate({"a": "x"}), OBJ_OPT)

    assert isinstance(converted.type, CtyObject)
    assert converted.type.optional_attributes == frozenset()
    assert converted.value["b"].is_null


# --------------------------------------------------------------------------- #
# A set whose length is unknown, converted to a list. Deliberately not matched.
# --------------------------------------------------------------------------- #
#
# Three answers are possible, and until 2026-08-17 the two implementations held
# the two wrong ones:
#
#   - **go-cty's**: a wholly-unknown value typed from the *source* element type.
#     Right to defer, wrong about the type -- `Convert(v, T)` returning a value
#     that is not of type `T` is a contract violation, not a behaviour.
#   - **this library's, until 2026-08-17**: elementwise conversion. Right about
#     the type, wrong to invent a length -- it hardened the source's `[1, n]`
#     bound into an exact `n`, and `length` said so about the source and then
#     contradicted itself about the result.
#   - **this library's now**: an *unknown* list of the **target** element type,
#     refined `collection_length in [1, stored]`, and not null. go-cty's
#     deferral with the caller's type: the only one of the three that no caller
#     can catch out.
#
# Being deliberately more correct than go-cty is an established posture here
# rather than a liberty taken in this one place -- `Value.Equals` is
# deterministic where go-cty's answer depends on Go's randomised map iteration,
# and `regex` and `indent` refuse where go-cty guesses. This case is the least
# arguable of them, because the third answer is not a preference: it is what
# both implementations' own `Length` already says.
#
# The trigger is narrower than "a set holding an unknown", and the boundary
# tests below pin each edge of it, because an attempt to match go-cty here, or
# to widen the deferral, would most likely start by moving one of them:
#
#   - the source must be a **set**, since a known list, map, tuple or object has
#     a known length whatever its elements are;
#   - the set's store must hold **more than one** element, at least one of them
#     not wholly known, because that is when coalescing becomes possible and
#     `Value.Length` stops being exact (`cty/value_ops.go:1127-1145`);
#   - the source must not be **wholly** unknown, which is handled earlier and
#     correctly, against the target type (`cty/convert/conversion.go:36-47`);
#   - the target must be a **list**, because only `conversionCollectionToList`
#     carries the short-circuit, and a set's stored element count was never a
#     claim about its length in the first place.

SET_WITH_UNKNOWN_LENGTH = SN.validate([N.validate(1), CtyValue.unknown(N)])
"""A `set(number)` whose store holds `1` and an unknown: length 1 or 2, not both."""


def test_a_set_with_an_unknown_converts_to_an_unknown_list_of_the_target_element_type() -> None:
    """Deliberately not matched. Implemented 2026-08-17; do not "fix" it back.

    **go-cty** returns a wholly-unknown value typed `list(number)` -- the
    *source* element type -- from `Convert(v, cty.List(cty.String))`.
    `cty/convert/conversion_collection.go:16-22` short-circuits on an unknown
    input length and builds its answer from `val.Type().ElementType()`, while the
    target element type sits unused in the enclosing `ety` parameter::

        if !val.Length().IsKnown() {
            return cty.UnknownVal(cty.List(val.Type().ElementType())), nil
        }

    **This library, until 2026-08-17,** converted elementwise and returned a
    known two-element `list(string)`.

    **This library now** returns an *unknown* `list(string)`, refined
    `collection_length in [1, 2]` and not null -- which is neither of the above,
    and is the answer both implementations' own `Length` already implies.

    **Why.** Each of the first two answers is right about one half and wrong
    about the other. go-cty is right to defer: its own comment says "we can't
    predict how many elements the resulting list should have", and a store of
    `{1, unknown}` really does become a one-element list if the unknown resolves
    to `1`. It is wrong about the type, and `Convert(v, T)` returning a value
    that is not of type `T` is a contract violation rather than a behaviour --
    every caller, unification and msgpack-against-a-schema and a provider handing
    state back to Terraform, reads the result's type as the answer to the
    question it asked. Elementwise conversion is the opposite trade: the type is
    honoured and the length is invented. The third answer gives up neither. The
    element types have to *differ* for the type half to be observable at all,
    which is why this case is `set(number)` to `list(string)` and not the
    `set(string)` to `list(string)` the agreement table already covers.

    Not-null is asserted here rather than left loose: the source is a known,
    non-null set, so whatever its length turns out to be there is definitely a
    list, and that is information a plan can use.
    """
    theirs = _theirs(SN, SET_WITH_UNKNOWN_LENGTH, LS)

    assert theirs["ok"] is True, theirs
    assert theirs["type"] == ["list", "number"], "go-cty stopped returning the source element type"
    assert theirs["value"] == {"$unknown": True}, "go-cty stopped collapsing the whole value"

    here = convert(SET_WITH_UNKNOWN_LENGTH, LS)

    assert json.loads(type_spec(here.type)) == ["list", "string"]
    assert here.is_unknown is True
    assert refinements(here) == {
        "is_known_null": False,
        "collection_length_lower_bound": 1,
        "collection_length_upper_bound": 2,
    }


def test_the_divergent_result_type_reaches_an_enclosing_conversion() -> None:
    """Deliberately not matched. The same fault, one level up.

    **go-cty** converts `object({s = set(number)})` to
    `object({s = list(string)})` and hands back a value typed
    `object({s = list(number)})`. The inner short-circuit at
    `cty/convert/conversion_collection.go:16-22` decides the attribute's type,
    and `conversionObjectToObject` assembles whatever its element conversions
    returned, so the requested target type is not merely decorated -- it is
    absent from the answer.

    **This library, until 2026-08-17,** returned `object({s = list(string)})`
    with a known two-element attribute; **now** it returns the same object type
    with the attribute deferred and refined. The type half of the fix is what
    this test exists for, and it is unchanged by the length half: the object is
    still *known*, and its declared type is still the one the caller asked for.

    **Why not matched.** This is the case that makes go-cty's answer a contract
    violation rather than a debatable choice about unknowns: a provider decoding
    config into its schema object gets back an object that does not conform to
    that schema, and the wire encoder is then asked to write a `number` where the
    schema says `string`. Pinned separately from the flat case because the flat
    one could be waved away as "the result is unknown, so its type hardly
    matters" -- here the result is a *known* object, and only one attribute
    inside it is undecided.
    """
    source_type = CtyObject(attribute_types={"s": SN})
    target_type = CtyObject(attribute_types={"s": LS})
    value = source_type.validate({"s": SET_WITH_UNKNOWN_LENGTH})

    theirs = _theirs(source_type, value, target_type)

    assert theirs["ok"] is True, theirs
    assert theirs["type"] == ["object", {"s": ["list", "number"]}]
    assert theirs["type"] != json.loads(type_spec(target_type)), "go-cty now honours the target type"

    here = convert(value, target_type)

    assert json.loads(type_spec(here.type)) == json.loads(type_spec(target_type))
    assert here.is_unknown is False, "only the attribute defers; the object around it is known"
    assert here.value["s"].is_unknown is True
    assert refinements(here.value["s"])["collection_length_upper_bound"] == 2


def test_the_converted_list_reports_the_same_length_as_the_set_it_came_from() -> None:
    """The half of go-cty's answer that is *right*, and is now reproduced.

    go-cty's short-circuit exists for a real reason, stated in its own comment:
    "we can't predict how many elements the resulting list should have". A set
    store holding `1` and an unknown becomes a one-element set if the unknown
    resolves to `1`, so no list of a definite length is a correct answer.

    **go-cty** therefore defers the whole value, and is not wrong about length --
    only about type. **This library, until 2026-08-17,** converted elementwise
    and returned a two-element list, hardening a `[1, 2]` bound into an exact
    `2`: its own `length` said one thing about the source and the opposite about
    the result. **Now** the two agree, which is what this test asserts, and it
    asserts it by comparing the two answers rather than by naming the numbers --
    the claim being defended is the agreement, not the arithmetic.

    This test used to pin the hardening, with a docstring saying that changing it
    would be a deliberate improvement and should turn it red. That is what
    happened; this is the same test, re-pointed at the fix. **Do not re-point it
    at go-cty**: matching go-cty here means reintroducing the wrong result type,
    which the two tests above exist to prevent.
    """
    source_length = length(SET_WITH_UNKNOWN_LENGTH)

    assert source_length.is_unknown, "a set holding an unknown has a bounded, not exact, length"
    assert refinements(source_length)["number_lower_bound"] == ["1", True]
    assert refinements(source_length)["number_upper_bound"] == ["2", True]

    here = convert(SET_WITH_UNKNOWN_LENGTH, LS)
    result_length = length(here)

    assert result_length.is_unknown, "the converted list must not claim a length the set does not have"
    assert refinements(result_length) == refinements(source_length)


def test_a_wholly_unknown_set_converts_to_the_target_type_on_both_sides() -> None:
    """The boundary below the divergence: go-cty is right here, and is matched.

    A wholly unknown source never reaches `conversionCollectionToList` at all.
    `cty/convert/conversion.go:36-47` intercepts it and builds the result from
    `out` -- the target -- via `prepareUnknownResult`, which is exactly the
    behaviour the case above is missing. Pinned so that "go-cty types the result
    from the source" is not read as a general claim about unknowns and used to
    justify breaking this.

    Untouched by the 2026-08-17 fix, and this is the edge that says so: there is
    no store to bound a length against, so the result is a bare unknown of the
    target type on both sides rather than a refined one.
    """
    value = CtyValue.unknown(SN)

    theirs = _theirs(SN, value, LS)

    assert theirs["ok"] is True, theirs
    assert theirs["type"] == ["list", "string"]

    here = convert(value, LS)

    assert json.loads(type_spec(here.type)) == ["list", "string"]
    assert here.is_unknown is True


def test_a_one_element_set_holding_an_unknown_converts_the_same_way_on_both_sides() -> None:
    """The boundary at the other edge: one stored element, so the length is exact.

    `Value.Length` in `cty/value_ops.go:1133-1140` returns the store count for a
    set whose store holds a single element even when that element is unknown,
    because there is nothing for it to coalesce with. So `set(number)` holding
    one unknown has a *known* length of 1, the short-circuit does not fire, and
    both implementations convert elementwise to `list(string)`.

    This is the case that makes the two-element case above necessary: written
    with one element, the divergence is invisible and the test passes for the
    wrong reason.

    Untouched by the 2026-08-17 fix. Deferring here would be as wrong as go-cty's
    typing is: a length that is known must not be thrown away, and the result is
    a known one-element list on both sides.
    """
    value = SN.validate([CtyValue.unknown(N)])

    theirs = _theirs(SN, value, LS)

    assert theirs["ok"] is True, theirs
    assert theirs["type"] == ["list", "string"]
    assert theirs["value"] == [{"$unknown": True}]

    here = convert(value, LS)

    assert json.loads(type_spec(here.type)) == ["list", "string"]
    assert canonical(rich(here)) == canonical(theirs["value"])


def test_a_set_target_is_unaffected_and_agrees() -> None:
    """Only the list target carries the short-circuit.

    `conversionCollectionToSet` (`cty/convert/conversion_collection.go:76-121`)
    has no `val.Length().IsKnown()` check -- a set's stored element count is not
    a claim about its length, so there is nothing to be unable to predict -- and
    it converts elementwise. Both implementations return
    `set(string)` holding `"1"` and an unknown.

    Pinned because it is the reason the tracker entry names *lists*: a fix that
    took the short-circuit as a general rule about unknown-holding sets would
    break a conversion the two already agree on.

    Untouched by the 2026-08-17 fix, and the reason it is worth re-reading now
    that this library defers a set-to-list conversion of its own accord: the
    deferral is not a rule about unknowns, it is a rule about *lists*, whose
    length is a promise the value has to keep.
    """
    theirs = _theirs(SN, SET_WITH_UNKNOWN_LENGTH, SS)

    assert theirs["ok"] is True, theirs
    assert theirs["type"] == ["set", "string"]

    here = convert(SET_WITH_UNKNOWN_LENGTH, SS)

    assert json.loads(type_spec(here.type)) == ["set", "string"]
    assert canonical(rich(here)) == canonical(theirs["value"])


# 🌊🪢🔚
