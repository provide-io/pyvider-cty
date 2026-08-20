#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Generated values, compared against real go-cty rather than against ourselves.

The rest of `tests/compatibility/` is a hand-written table, and a hand-written
table only finds a divergence somebody already suspected. `tests/property_based/`
generates inputs but compares this package against itself, so it cannot see a
divergence at all -- an agreed-upon wrong answer round-trips perfectly.

This module is the two halves put together, and the three bugs it was written
out of are the argument for it. None was in the 2595-case table:

  * **Set element order.** go-cty ranks a composite element that has run out of
    members *last*; a Python tuple comparison ranks it first. Invisible in any
    single example -- it only shows when two elements happen to be prefix-related
    -- and it took 232 generated sets to characterise the rule.
  * **Vacuous refinements.** An empty string prefix and a zero length lower
    bound were written to the wire where go-cty writes a bare unknown.
  * **An unsatisfiable number range**, accepted and serialized.

What is compared is bytes, in both directions, because that is what Terraform
compares. Agreeing on the decoded value while disagreeing on the encoding is
exactly the class of bug above: every one of them round-tripped correctly
through this package and still put different bytes on the wire.

**What this cannot see.** Our value is spelled for the harness with
`rich`/`dynamic_arg`, so information this package drops *before* the comparison
is dropped from both sides and the two agree. `CtyDynamic.validate` discarding a
null's concrete type is the worked example, and `test_dynamic_carries_its_type`
constructs go's side by hand because of it. A differential property can only see
what survives into the value it compares.

Example counts are deliberately modest. Each one costs a subprocess, and the
generators are biased toward shapes that have actually broken rather than
sampling a space uniformly -- see `_strategies`. Raise `max_examples` locally
when hunting; the defaults keep `make compat` in the seconds it is today.
"""

from __future__ import annotations

import base64
import json
from typing import Any

from hypothesis import given, settings
import pytest

from pyvider.cty import CtyDynamic, CtyType, CtyValue
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack
from pyvider.cty.json_codec import CtyJsonError, cty_to_json
from tests.compatibility._oracle import canonical, dynamic_arg, examples, rich, run, type_spec
from tests.compatibility._strategies import cases, refined_unknowns, sets_of_sequences

pytestmark = pytest.mark.compat


# One subprocess per property per example. Enough to have caught all three of
# the 2026-08-19 bugs (the set ordering rule showed inside 60 sets once the
# generator was biased toward prefix-related elements) without turning a
# seconds-long suite into a minutes-long one.
EXAMPLES = examples(60)
# The narrow generators -- sets of sequences, refinements -- get their own
# budget. Both are shapes where a divergence needs a specific *combination*
# (two prefix-related elements; a bound that rules nothing out), which a
# general strategy reaches too rarely to be a guard. Verified by mutation:
# reverting each of the three 2026-08-19 fixes turns the matching property red.
NARROW_EXAMPLES = examples(120)


def _b64(payload: bytes) -> str:
    """The harness takes its msgpack argument as base64."""
    return base64.b64encode(payload).decode()


def _spec(cty_type: CtyType[Any], value: CtyValue[Any]) -> str:
    """The harness's spelling of `value`, carrying its type where it must.

    A `dynamic` position needs `dynamic_arg`: sent as a plain rich value, the
    harness infers the type from the JSON, and JSON infers a *tuple* from an
    array -- so a `list(string)` would arrive as `tuple(string, string)` and the
    comparison would be between two different values.
    """
    if isinstance(cty_type, CtyDynamic):
        return json.dumps(dynamic_arg(value))
    return json.dumps(rich(value))


def _encoded_by_go(cty_type: CtyType[Any], value: CtyValue[Any]) -> str | None:
    """go-cty's msgpack for the same value, as hex, or None if it refuses."""
    reported = run("cty", "msgpack", "encode", "--type", type_spec(cty_type), _spec(cty_type, value))
    return reported.get("hex") if reported.get("ok") else None


@settings(max_examples=EXAMPLES, deadline=None)
@given(cases())
def test_both_implementations_encode_the_same_msgpack(case: tuple[CtyType[Any], CtyValue[Any]]) -> None:
    """The bytes that reach Terraform, for a value neither side chose."""
    cty_type, value = case

    theirs = _encoded_by_go(cty_type, value)
    ours = cty_to_msgpack(value, cty_type).hex()

    assert theirs is not None, f"the harness refused {rich(value)!r} at {type_spec(cty_type)}"
    assert ours == theirs, f"{type_spec(cty_type)} {rich(value)!r}: go={theirs} ours={ours}"


@settings(max_examples=EXAMPLES, deadline=None)
@given(cases())
def test_both_implementations_read_the_same_bytes_the_same_way(
    case: tuple[CtyType[Any], CtyValue[Any]],
) -> None:
    """The decode direction, asked as a *differential* question.

    Deliberately not "does a round trip return the original". That is a
    different property and it is not true of either implementation: both encode
    `-0.0` as the msgpack integer `00`, discarding the sign, so decoding gives
    `0` on both sides. Asserting round-trip identity here would have reported
    that as a divergence when the two agree exactly -- which is what it did on
    this suite's first run.

    So both are handed the same bytes and their readings are compared. Whether
    an encoding is lossy is go-cty's business; whether this package reads it the
    way go-cty does is ours.
    """
    cty_type, value = case
    encoded = _encoded_by_go(cty_type, value)
    if encoded is None:
        pytest.skip("go-cty declined to encode this value")

    ours = cty_from_msgpack(bytes.fromhex(encoded), cty_type)
    theirs = run("cty", "msgpack", "decode", "--type", type_spec(cty_type), _b64(bytes.fromhex(encoded)))

    assert theirs.get("ok"), f"go-cty could not read its own bytes for {rich(value)!r}: {theirs}"
    assert canonical(rich(ours)) == canonical(theirs.get("value")), (
        f"{type_spec(cty_type)}: go read {theirs.get('value')!r}, this package read {rich(ours)!r}"
    )


@settings(max_examples=EXAMPLES, deadline=None)
@given(cases())
def test_go_cty_can_read_what_this_package_writes(
    case: tuple[CtyType[Any], CtyValue[Any]],
) -> None:
    """The direction a provider writes, compared against our own reading.

    Same reasoning as above: the comparison is go's reading of our bytes against
    our reading of our bytes, not against the value we started from.
    """
    cty_type, value = case
    ours_bytes = cty_to_msgpack(value, cty_type)
    ours = cty_from_msgpack(ours_bytes, cty_type)

    theirs = run("cty", "msgpack", "decode", "--type", type_spec(cty_type), _b64(ours_bytes))

    assert theirs.get("ok"), f"go-cty could not read our bytes for {rich(value)!r}: {theirs}"
    assert canonical(theirs.get("value")) == canonical(rich(ours)), (
        f"{type_spec(cty_type)}: go read {theirs.get('value')!r}, this package read {rich(ours)!r}"
    )


@settings(max_examples=EXAMPLES, deadline=None)
@given(cases())
def test_both_implementations_write_the_same_json(case: tuple[CtyType[Any], CtyValue[Any]]) -> None:
    """The other codec. Neither side can spell an unknown, and both must refuse."""
    cty_type, value = case
    reported = run("cty", "json", "marshal", _spec(cty_type, value), "--type", type_spec(cty_type))

    try:
        ours = cty_to_json(value, cty_type).decode()
    except CtyJsonError:
        assert not reported.get("ok"), (
            f"{type_spec(cty_type)} {rich(value)!r}: this package refused, go-cty answered "
            f"{reported.get('text')!r}"
        )
        return

    assert reported.get("ok"), (
        f"{type_spec(cty_type)} {rich(value)!r}: go-cty refused ({reported.get('error')!r}), "
        f"this package answered {ours!r}"
    )
    assert ours == reported.get("text"), f"{type_spec(cty_type)}: go={reported.get('text')!r} ours={ours!r}"


@settings(max_examples=NARROW_EXAMPLES, deadline=None)
@given(refined_unknowns())
def test_a_refinement_encodes_the_same_way(case: tuple[CtyType[Any], CtyValue[Any]]) -> None:
    """Refinements, given their own budget for the same reason sets have one.

    Drawn from `cases()` alone, a degenerate refinement is roughly one example
    in a hundred and twenty -- six shapes, four kinds, five prefixes -- so the
    general property missed the vacuous-refinement regression under mutation
    while catching the other two. A narrow generator with its own count is what
    makes it a guard rather than a coin flip.
    """
    cty_type, value = case

    theirs = _encoded_by_go(cty_type, value)
    ours = cty_to_msgpack(value, cty_type).hex()

    assert theirs is not None, f"the harness refused {rich(value)!r} at {type_spec(cty_type)}"
    assert ours == theirs, f"refinement: go={theirs} ours={ours} for {rich(value)!r}"


@settings(max_examples=NARROW_EXAMPLES, deadline=None)
@given(sets_of_sequences())
def test_a_set_of_sequences_orders_its_elements_the_same_way(
    case: tuple[CtyType[Any], CtyValue[Any]],
) -> None:
    """The regression this suite exists for, given its own example budget.

    Ordering is only observable in the encoding -- both spellings decode to the
    same set -- so this compares bytes rather than values, and draws from a
    three-letter alphabet so that elements are prefixes of one another often
    rather than by luck.
    """
    cty_type, value = case

    theirs = _encoded_by_go(cty_type, value)
    ours = cty_to_msgpack(value, cty_type).hex()

    assert ours == theirs, f"set order: go={theirs} ours={ours} for {rich(value)!r}"


# 🌊🪢🔚
