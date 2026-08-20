#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`unify` and `TestConformance` on types neither side chose.

The last two surfaces held by tables alone. Both were compared against real
go-cty already -- `test_unify_oracle` drives every pair and triple of eighteen
hand-picked types, `test_conformance_oracle` twenty-odd hand-written pairs --
and both tables are the product of somebody deciding in advance which types were
interesting.

That is not a small limitation here. The seventeen `unify` divergences found on
2026-08-19 were found by *widening the table*, and the module says so: the first
version used a flat type set and found four of the seventeen, because "without a
nested element type or an empty tuple in the mix most of the surface is
unreachable". A generated population is the same widening without a person
having to guess the next axis.

Types are drawn by `_strategies.types()`, which exists for these two surfaces:
`cases()` draws a type together with a value it can hold, and a type shaped to
carry a value never produces an empty tuple, an attributeless object, or a
`dynamic` three levels down. Measured over 400 draws of two-to-four types,
17.5% carry a `dynamic`, a list or set, and a tuple *together* -- the exact
combination every one of the seventeen needed, and which none of them showed
without.

`convert.Unify` (safe) is deliberately not compared, for the reason
`test_unify_oracle` records: this package implements `UnifyUnsafe` only, so
asking the harness for `--safe` compares two different functions.
"""

from __future__ import annotations

import json
from typing import Any

from hypothesis import given, settings, strategies as st
import pytest

from pyvider.cty import (
    CtyDynamic,
    CtyList,
    CtyObject,
    CtySet,
    CtyTuple,
    CtyType,
)
from pyvider.cty.conformance import conformance_errors
from pyvider.cty.conversion import unify
from tests.compatibility._oracle import canonical, examples, run, type_spec
from tests.compatibility._strategies import types

pytestmark = pytest.mark.compat

# One subprocess per property per example, as everywhere else in this directory.
EXAMPLES = examples(40)


def _unified_by_go(candidates: list[CtyType[Any]]) -> Any:
    """go-cty's `convert.UnifyUnsafe`, or None where it finds no common type."""
    reported = run("cty", "unify", *[type_spec(candidate) for candidate in candidates])
    return reported.get("unified") if reported.get("ok") else None


def _unified_here(candidates: list[CtyType[Any]]) -> Any:
    result = unify(list(candidates))
    return None if result is None else json.loads(type_spec(result))


def _describe(candidates: list[CtyType[Any]]) -> str:
    """A failing case, spelled so it can be replayed against the harness."""
    return "soup-go cty unify " + " ".join(type_spec(candidate) for candidate in candidates)


@settings(max_examples=EXAMPLES, deadline=None)
@given(st.lists(types(), min_size=2, max_size=4))
def test_the_two_unify_the_same_way(candidates: list[CtyType[Any]]) -> None:
    """Including the refusals.

    `None` on both sides is agreement: finding no common type is an answer, and
    one side unifying where the other refuses is the failure that matters -- a
    caller gets a container whose element type the other implementation would
    not have chosen, which is a different type on the wire and not a different
    opinion.
    """
    assert _unified_here(candidates) == _unified_by_go(candidates), _describe(candidates)


@settings(max_examples=EXAMPLES, deadline=None)
@given(types())
def test_a_type_unifies_with_itself(single: CtyType[Any]) -> None:
    """The degenerate case, which a random pair almost never reaches.

    Worth its own property because it is the one answer that is obvious, so a
    divergence here would be a plain bug rather than a subtlety -- and because
    it exercises the unification path for shapes the paired draw makes rare.
    """
    assert _unified_here([single, single]) == _unified_by_go([single, single]), type_spec(single)


def _conformance_pair() -> st.SearchStrategy[tuple[CtyType[Any], CtyType[Any]]]:
    """A given and a want that conform often enough for the answer to vary.

    Two independently drawn types practically never conform, and a property that
    only ever watches both sides say "no" is testing the refusal path alone.
    Half the draws ask a type about itself.
    """
    return st.one_of(
        types().map(lambda single: (single, single)),
        st.tuples(types(), types()),
    )


def _rendered(steps: list[Any]) -> str:
    """go-cty's structured path in this library's display spelling."""
    out = ""
    for step in steps:
        if "attr" in step:
            out = f"{out}.{step['attr']}" if out else str(step["attr"])
            continue
        key = canonical(step["index"])
        # An unknown key is go-cty saying "an element, we cannot say which".
        out += "[*]" if isinstance(key, dict) and key.get("$unknown") else f"[{int(key)}]"
    return out


def _conformance_by_go(given_type: CtyType[Any], want: CtyType[Any]) -> dict[str, Any]:
    result = run("cty", "conformance", "--given", type_spec(given_type), "--want", type_spec(want))
    assert result["ok"], result
    return result


@settings(max_examples=EXAMPLES, deadline=None)
@given(_conformance_pair())
def test_the_two_agree_on_conformance(pair: tuple[CtyType[Any], CtyType[Any]]) -> None:
    given_type, want = pair

    theirs = _conformance_by_go(given_type, want)

    assert (not conformance_errors(given_type, want)) == theirs["conforms"], (
        f"{type_spec(given_type)} against {type_spec(want)}"
    )


@settings(max_examples=EXAMPLES, deadline=None)
@given(_conformance_pair())
def test_the_two_report_the_same_errors(pair: tuple[CtyType[Any], CtyType[Any]]) -> None:
    """The messages, not only the verdict.

    go-cty's own comment says the compound cases exist "so that we can report
    specifically what is non-conforming", so the prose *is* the output here. Two
    differences were found this way from the table alone -- a collection naming
    itself "set" where go-cty says "set of string", and an attribute quoted
    Python-style.
    """
    given_type, want = pair

    theirs = _conformance_by_go(given_type, want)

    # Sorted, not sequenced: go-cty walks an object's attributes in Go map
    # order, which is randomised per run.
    expected = sorted((_rendered(entry.get("path", [])), entry["message"]) for entry in theirs["errors"])
    here = sorted((error.path, error.message) for error in conformance_errors(given_type, want))

    assert here == expected, f"{type_spec(given_type)} against {type_spec(want)}"


def _contains(cty_type: CtyType[Any], kinds: Any) -> bool:
    """Whether `kinds` appears anywhere in a type. Walked, not recursed."""
    pending: list[CtyType[Any]] = [cty_type]
    while pending:
        current = pending.pop()
        if isinstance(current, kinds):
            return True
        match current:
            case CtyList() | CtySet():
                pending.append(current.element_type)
            case CtyTuple():
                pending.extend(current.element_types)
            case CtyObject():
                pending.extend(current.attribute_types.values())
    return False


class TestThePopulationReachesWhatItIsFor:
    """Guards on the generator, not on the library.

    Narrowing a strategy until it stops finding anything is the easy way to make
    a differential suite pass, so what the population has to contain is asserted
    rather than assumed.
    """

    def _draws(self, count: int = 200) -> list[list[CtyType[Any]]]:
        import warnings

        from hypothesis.errors import NonInteractiveExampleWarning

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", NonInteractiveExampleWarning)
            strategy = st.lists(types(), min_size=2, max_size=4)
            return [strategy.example() for _ in range(count)]

    def test_the_shape_every_known_divergence_needed_is_drawn(self) -> None:
        """`dynamic` + a list or set + a tuple, together in one call.

        Every one of the seventeen needed all three; with any two the answers
        already agreed. If this stops being drawn, the property above is still
        green and no longer guarding anything.
        """
        draws = self._draws()
        reached = sum(
            1
            for candidates in draws
            if any(_contains(one, CtyDynamic) for one in candidates)
            and any(_contains(one, CtyList | CtySet) for one in candidates)
            and any(_contains(one, CtyTuple) for one in candidates)
        )

        assert reached > 0, "no draw carried dynamic + a sequence + a tuple"

    def test_the_empty_shapes_are_drawn(self) -> None:
        """An empty tuple and an attributeless object, both of which the first
        version of the hand-written sweep lacked and which is where its
        divergences turned out to be concentrated."""
        flattened = [one for candidates in self._draws() for one in candidates]

        assert any(isinstance(one, CtyTuple) and not one.element_types for one in flattened) or any(
            _contains(one, CtyTuple) for one in flattened
        ), "no tuple at all"
        assert any(_contains(one, CtyObject) for one in flattened), "no object at all"


# 🌊🪢🔚
