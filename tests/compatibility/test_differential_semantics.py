#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Generated values through the *semantic* surfaces, against real go-cty.

`test_differential_properties` covers the codecs -- what bytes each side writes
and reads. This covers what each side *answers*: `Value.Equals`, `convert`,
`Value.Range`, and the mark-path round trip. Those four have 148, 94, 44 and 40
hand-written oracle cases between them and, until this module, not one generated
input.

The distinction matters because the two find different things. A codec property
compares an encoding, so it catches a value that is spelled differently; a
semantic property compares an answer, so it catches a value that is *decided*
differently. The set-ordering bug was the first kind. `Value.Equals` returning
unknown where go-cty returns false would be the second, and nothing here was
looking for it.

Kept deliberately narrow in one respect: equality and conversion are driven from
*pairs* of generated values of the same type, because a pair of unrelated types
mostly exercises the type-mismatch path, which the hand-written tables already
cover exhaustively and which generated inputs re-find over and over.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
import json
import os
from typing import Any

from hypothesis import given, settings
import pytest

from pyvider.cty import CtyBool, CtyNumber, CtyString, CtyType, CtyValue
from pyvider.cty.conversion import convert
from pyvider.cty.exceptions import CtyConversionError
from pyvider.cty.mark_paths import unmark_deep_with_paths
from pyvider.cty.path import GetAttrStep, IndexStep, KeyStep
from pyvider.cty.value_range import value_range
from pyvider.cty.values.equality import equals
from tests.compatibility._oracle import canonical, rich, run, type_spec
from tests.compatibility._strategies import cases, scalars

pytestmark = pytest.mark.compat


def _examples(default: int) -> int:
    """The per-property example count, raisable for a hunt.

    `PYVIDER_COMPAT_EXAMPLES=600 make compat` widens every property at once. The
    committed defaults are sized to keep the differential suite in the seconds it
    is today; finding a *new* divergence generally means running wider than a
    regression guard needs to.
    """
    override = os.environ.get("PYVIDER_COMPAT_EXAMPLES")
    return max(1, int(override)) if override else default


EXAMPLES = _examples(60)


def _step_form(step: Any) -> dict[str, Any]:
    """One pyvider path step in the harness's structural form."""
    match step:
        case GetAttrStep(name=name):
            return {"attr": name}
        case IndexStep(index=index):
            return {"index": Decimal(index)}
        case KeyStep(key=key):
            return {"index": rich(key) if isinstance(key, CtyValue) else key}
    raise AssertionError(f"no structural form for {step!r}")


def _ordered(entries: Any) -> list[str]:
    """Entries as sorted, key-order-independent strings.

    Sorting by `repr` would compare each side's key insertion order, which is a
    property of how the dict was built and not of where the marks were found.
    """
    return sorted(json.dumps(entry, sort_keys=True, default=str) for entry in entries)


def _ordered_paths(found: Any) -> list[str]:
    return _ordered(
        {
            "path": [canonical(_step_form(step)) for step in path.steps],
            "marks": sorted(str(mark) for mark in marks),
        }
        for path, marks in found.items()
    )


def _described(answer: CtyValue[Any]) -> dict[str, Any]:
    """`Value.Equals`' answer in the harness's shape."""
    described: dict[str, Any] = {"known": not answer.is_unknown}
    if not answer.is_unknown:
        described["value"] = bool(answer.value)
    if answer.marks:
        described["marks"] = sorted(str(mark) for mark in answer.marks)
    return described


@settings(max_examples=EXAMPLES, deadline=None)
@given(scalars(), scalars())
def test_equality_answers_the_same(
    left_case: tuple[CtyType[Any], CtyValue[Any]],
    right_case: tuple[CtyType[Any], CtyValue[Any]],
) -> None:
    """`Value.Equals`, three-valued, across known/null/unknown combinations.

    Scalars rather than the full generator: a pair of unrelated container types
    spends its budget on the type-mismatch path, which the hand-written table
    already covers case by case.
    """
    left_type, left = left_case
    right_type, right = right_case

    theirs = run(
        "cty",
        "equals",
        "--left-type",
        type_spec(left_type),
        "--right-type",
        type_spec(right_type),
        json.dumps(rich(left)),
        json.dumps(rich(right)),
    )

    assert theirs["ok"], theirs
    assert _described(equals(left, right)) == theirs["equals"], (
        f"{type_spec(left_type)} {rich(left)!r} == {type_spec(right_type)} {rich(right)!r}"
    )


@settings(max_examples=EXAMPLES, deadline=None)
@given(scalars(), scalars())
def test_equality_is_symmetric_on_both_sides(
    left_case: tuple[CtyType[Any], CtyValue[Any]],
    right_case: tuple[CtyType[Any], CtyValue[Any]],
) -> None:
    """Swapping the operands cannot change either implementation's answer.

    `Equals` is a cascade of one-sided cases -- "known on the left, unknown on
    the right", then the mirror -- so a rule added to one arm and not the other
    is how this breaks. Generated pairs reach combinations a table does not.
    """
    _, left = left_case
    _, right = right_case

    assert _described(equals(left, right)) == _described(equals(right, left))


CONVERSION_TARGETS = [CtyString(), CtyNumber(), CtyBool()]

# The spellings go-cty's `big.ParseFloat` accepts. Anything else that `Decimal`
# reads as non-finite is a known input-acceptance divergence.
_GO_NON_FINITE = {"inf", "+inf", "-inf"}


def _parses_non_finite(text: str) -> bool:
    """Whether `Decimal` reads `text` as an infinity or a NaN go-cty would not."""
    if text.strip().lower() in _GO_NON_FINITE:
        return False
    try:
        return not Decimal(text).is_finite()
    except InvalidOperation:
        return False


@settings(max_examples=EXAMPLES, deadline=None)
@given(scalars())
def test_conversion_agrees_including_about_refusing(
    case: tuple[CtyType[Any], CtyValue[Any]],
) -> None:
    """`convert` to each primitive, comparing refusals as well as results.

    Both refusing counts as agreement -- the messages differ between a Go and a
    Python implementation -- but one refusing where the other answers does not,
    and that asymmetry is what this is for.
    """
    source_type, value = case
    if isinstance(value.value, str) and _parses_non_finite(value.value):
        # `Decimal` takes more non-finite spellings than Go's `big.ParseFloat`
        # -- `Infinity`, `infinity`, `INF`, and NaN in any casing -- so this
        # package converts strings go-cty refuses. Recorded and reasoned about
        # in `test_non_finite_numbers.py`; excluded here so the property stays
        # about conversions the two are supposed to agree on.
        return

    for target in CONVERSION_TARGETS:
        theirs = run(
            "cty",
            "convert-value",
            "--from",
            type_spec(source_type),
            "--to",
            type_spec(target),
            json.dumps(rich(value)),
        )
        label = f"{type_spec(source_type)} {rich(value)!r} -> {type_spec(target)}"

        try:
            ours = convert(value, target)
        except CtyConversionError:
            assert not theirs["ok"], f"{label}: this package refused, go-cty answered {theirs}"
            continue

        assert theirs["ok"], f"{label}: go-cty refused ({theirs.get('error')!r}), this answered {ours!r}"
        assert canonical(rich(ours)) == canonical(theirs["value"]), (
            f"{label}: go={theirs['value']!r} ours={rich(ours)!r}"
        )


@settings(max_examples=EXAMPLES, deadline=None)
@given(cases())
def test_the_nullness_range_agrees(case: tuple[CtyType[Any], CtyValue[Any]]) -> None:
    """`Value.Range`'s null-ness verdict, which refinements feed.

    Every value shape, not just scalars: a container's range is derived from its
    own refinements, and an unknown collection with length bounds is the shape a
    plan actually carries.
    """
    cty_type, value = case
    theirs = run("cty", "range", "--type", type_spec(cty_type), json.dumps(rich(value)))
    assert theirs["ok"], theirs

    here = value_range(value)

    assert here.could_be_null() == theirs["could_be_null"], f"{type_spec(cty_type)} {rich(value)!r}"
    assert here.definitely_not_null() == theirs["definitely_not_null"], (
        f"{type_spec(cty_type)} {rich(value)!r}"
    )


@settings(max_examples=EXAMPLES, deadline=None)
@given(cases())
def test_stripping_marks_finds_the_same_paths(case: tuple[CtyType[Any], CtyValue[Any]]) -> None:
    """`UnmarkDeepWithPaths` over a value marked at its root.

    The paths are what the two have to agree about: a mark's *location* is what
    lets a caller put it back, and a path reported against the wrong step puts a
    `sensitive` mark somewhere it does not belong.
    """
    cty_type, value = case
    marked = value.mark("sensitive")

    theirs = run("cty", "marks", "--type", type_spec(cty_type), json.dumps(rich(marked)))
    assert theirs["ok"], theirs

    stripped, found = unmark_deep_with_paths(marked)

    assert theirs["round_trip_equal"], f"go-cty could not re-apply its own marks: {theirs}"
    assert _ordered_paths(found) == _ordered(theirs["paths"]), f"{type_spec(cty_type)} {rich(marked)!r}"
    assert canonical(rich(stripped)) == canonical(theirs["unmarked"]), (
        f"{type_spec(cty_type)}: stripped to {rich(stripped)!r}, go-cty to {theirs['unmarked']!r}"
    )


# 🌊🪢🔚
