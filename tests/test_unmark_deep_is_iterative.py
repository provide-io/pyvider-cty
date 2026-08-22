#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`unmark_deep` descends as far as `validate` accepts, and further.

The two halves of the deep-mark machinery disagreed about how deep they could
go. `collect_marks_deep` was made iterative when the recursion guard's abort
path was found to be quadratic; the *strip* beside it was left recursive, and
`_strip` and `_strip_uncached` call each other, so every level of nesting costs
two Python frames against CPython's 1000-frame ceiling.

Measured before this change:

    validate accepts                        450 levels
    collect_marks_deep survives             900+ (iterative, no Python frames)
    unmark_deep survives                    330

So a value this package had just accepted could not be unmarked. It reached
callers as a bare `RecursionError` -- not a `CtyError`, so outside the taxonomy
-- and from `length()`, `upper()` and every other stdlib function, since the
framework strips marks from every argument before the implementation runs.

A cycle was the same failure by a different route: `collect_marks_deep` has
cycle detection and answers, `unmark_deep` recursed until the interpreter
stopped it.
"""

from __future__ import annotations

import pytest

from pyvider.cty import CtyList, CtyMap, CtySet, CtyString, CtyValue
from pyvider.cty.config.defaults import MAX_VALIDATION_DEPTH
from pyvider.cty.exceptions import CtyError
from pyvider.cty.functions import length
from pyvider.cty.marks import _strip, collect_marks_deep, unmark_deep
from pyvider.cty.values.frozen import FrozenDict

SENSITIVE = "sensitive"


def nested(depth: int) -> CtyValue:
    """A `depth`-deep list nest around one marked string.

    Hand-built rather than validated: past `MAX_VALIDATION_DEPTH` the recursion
    guard deliberately degrades to an unknown, and what is under test here is
    how deep the *strip* goes, not how deep validation does.
    """
    value = CtyString().validate("x").with_marks({SENSITIVE})
    for _ in range(depth):
        value = CtyValue(CtyList(element_type=value.type), (value,))
    return value


def deepest(value: CtyValue) -> CtyValue:
    """The leaf at the bottom of a `nested()` chain."""
    while isinstance(value.value, tuple):
        value = value.value[0]
    return value


class TestDepth:
    def test_it_reaches_the_depth_validation_accepts(self) -> None:
        """The floor: anything `validate` returns must be unmarkable."""
        stripped, marks = unmark_deep(nested(MAX_VALIDATION_DEPTH))

        assert marks == frozenset({SENSITIVE})
        assert not deepest(stripped).marks

    def test_it_reaches_as_deep_as_the_collector_does(self) -> None:
        """The two halves of `unmark_deep` have to agree about what is walkable.

        `collect_marks_deep` reporting marks that `_strip` cannot remove is the
        exact shape of the bug this file exists for.
        """
        value = nested(900)

        assert collect_marks_deep(value) == frozenset({SENSITIVE})
        assert not deepest(unmark_deep(value)[0]).marks

    def test_a_stdlib_call_survives_a_deep_marked_argument(self) -> None:
        """How this reached callers: the framework strips every argument."""
        assert length(nested(400)).value == 1


class TestCycles:
    def test_a_cycle_is_refused_rather_than_recursed(self) -> None:
        """A `RecursionError` is not a `CtyError`, and a hang is worse than both.

        `validate` cannot build a cyclic value, and since the constructor
        freezes a raw payload neither can a hand-built one: the list it used to
        keep, and that this test appended to after construction, is a tuple
        now. The guard stays -- a `RecursionError` is not a `CtyError` -- so the
        cycle is forced in behind the frozen class, the one way left to make one.
        """
        marked = CtyString().validate("x").with_marks({SENSITIVE})
        cyclic = CtyValue(CtyList(element_type=CtyString()), [marked])
        object.__setattr__(cyclic, "value", (marked, cyclic))

        # The collector already answers here, which is what made the two differ.
        assert collect_marks_deep(cyclic) == frozenset({SENSITIVE})

        with pytest.raises(CtyError):
            unmark_deep(cyclic)


class TestTheShortcutsSurvive:
    """Each was load-bearing for performance and is easy to lose in a rewrite."""

    def test_an_unmarked_value_is_returned_untouched(self) -> None:
        """Not rebuilt: the wrapper strips every argument of every call."""
        value = CtyList(element_type=CtyString()).validate(["a", "b"])

        assert _strip(value) is value

    def test_the_stripped_copy_is_memoized(self) -> None:
        """Two calls hand back one object, not two equal ones."""
        value = CtyList(element_type=CtyString()).validate([CtyString().validate("a").with_marks({SENSITIVE})])

        assert _strip(value) is _strip(value)

    def test_an_unchanged_child_is_not_rebuilt(self) -> None:
        """Identity, never `==`: a capsule's `equal_fn` ignores marks entirely."""
        clean = CtyString().validate("keep")
        value = CtyValue(
            CtyList(element_type=CtyString()),
            (clean, CtyString().validate("a").with_marks({SENSITIVE})),
        )

        assert _strip(value).value[0] is clean


class TestPayloadShapes:
    def test_a_map_payload_stays_frozen(self) -> None:
        """`_strip` hands every caller the same object, so a plain dict here
        reintroduces the mutable shared payload `FrozenDict` exists to prevent."""
        value = CtyMap(element_type=CtyString()).validate(
            {"k": CtyString().validate("v").with_marks({SENSITIVE})}
        )

        assert isinstance(_strip(value).value, FrozenDict)

    def test_a_set_may_shrink(self) -> None:
        """Stripping can make two elements that differed only by a mark equal.

        A smaller set is what an unmarked view of it should be.
        """
        value = CtyValue(
            CtySet(element_type=CtyString()),
            frozenset(
                {
                    CtyString().validate("a").with_marks({SENSITIVE}),
                    CtyString().validate("a"),
                }
            ),
        )

        assert len(value.value) == 2
        assert len(_strip(value).value) == 1

    def test_a_dynamic_wrapper_is_descended(self) -> None:
        from pyvider.cty import CtyDynamic

        inner = CtyString().validate("x").with_marks({SENSITIVE})
        value = CtyValue(CtyDynamic(), inner)

        assert not _strip(value).value.marks


# 🐍🏗️🔚
