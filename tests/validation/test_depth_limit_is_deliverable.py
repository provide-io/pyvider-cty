#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The advertised validation depth must be a depth that actually validates.

`MAX_VALIDATION_DEPTH` was a flat 500 and could not be honoured. Each level of
nesting costs two Python frames -- the `with_recursion_detection` wrapper, then
the `validate` it wraps -- against CPython's 1000-frame limit, so 500 levels
needed the entire stack with nothing left for the caller. The real ceiling was
496, and input nested 497-500 deep came back as a silent unknown while sitting
inside the documented limit.

The limit is now derived from the recursion limit in force, so the number is
true by construction rather than by hope.

The break these tests catch: an advertised depth the interpreter cannot carry.
"""

from __future__ import annotations

import sys
from typing import Any

from pyvider.cty import CtyDynamic, CtyList, CtyString, CtyType
from pyvider.cty.config.defaults import (
    FRAMES_PER_VALIDATION_LEVEL,
    MAX_VALIDATION_DEPTH,
    VALIDATION_STACK_MARGIN,
    default_max_validation_depth,
)
from pyvider.cty.validation import clear_recursion_context, get_recursion_context


def nested(depth: int, base: CtyType[Any] | None = None) -> tuple[CtyType[Any], Any]:
    """A list nested `depth` deep around a single leaf value."""
    cty_type: CtyType[Any] = base or CtyString()
    raw: Any = "x"
    for _ in range(depth):
        cty_type, raw = CtyList(element_type=cty_type), [raw]
    return cty_type, raw


class TestTheAdvertisedDepthIsReal:
    def teardown_method(self) -> None:
        clear_recursion_context()

    def test_validation_succeeds_at_exactly_the_advertised_depth(self) -> None:
        """The whole point. Previously false for the four levels 497-500."""
        clear_recursion_context()
        limit = get_recursion_context().max_depth_allowed
        cty_type, raw = nested(limit)

        result = cty_type.validate(raw)

        assert not result.is_unknown, f"depth {limit} is advertised but does not validate"

    def test_the_guard_stops_before_python_does(self) -> None:
        """One past the limit must be a controlled unknown, not a RecursionError.

        The margin exists so the failure is the guard's, with its logging and
        its mark handling, rather than an exception thrown from the caller's
        stack -- and it has to hold for a *realistic* caller. Running under
        pytest already sits deeper than the original 40-frame margin, which is
        how a too-small margin was found: this test crashed instead of stopping.
        """
        clear_recursion_context()
        limit = get_recursion_context().max_depth_allowed
        cty_type, raw = nested(limit + 1)

        result = cty_type.validate(raw)

        assert result.is_unknown

    def test_the_limit_leaves_the_configured_margin(self) -> None:
        derived = default_max_validation_depth()

        assert derived * FRAMES_PER_VALIDATION_LEVEL <= sys.getrecursionlimit() - VALIDATION_STACK_MARGIN

    def test_the_limit_tracks_a_raised_recursion_limit(self) -> None:
        """A host that raises the recursion limit gets the depth it paid for.

        This is what the derivation buys over simply lowering the constant.
        """
        original = sys.getrecursionlimit()
        try:
            sys.setrecursionlimit(3000)
            raised = default_max_validation_depth()
        finally:
            sys.setrecursionlimit(original)

        assert raised > default_max_validation_depth()

    def test_the_import_time_constant_agrees_with_the_live_value(self) -> None:
        """`pyvider.cty.context` used to export a second, unrelated 500.

        The guard permits one level more than the advertised depth. That extra
        entry is spent by CtyDynamic, whose guarded `validate` delegates to the
        concrete type's guarded `validate`; without it, dynamic values stopped
        one level short of the number every other type reached.
        """
        from pyvider.cty.config.defaults import DYNAMIC_DELEGATION_RESERVE
        from pyvider.cty.context import MAX_VALIDATION_DEPTH as CONTEXT_CONSTANT

        clear_recursion_context()

        assert CONTEXT_CONSTANT == MAX_VALIDATION_DEPTH
        assert get_recursion_context().max_depth_allowed == MAX_VALIDATION_DEPTH + DYNAMIC_DELEGATION_RESERVE

    def test_a_dynamic_value_reaches_the_advertised_depth_too(self) -> None:
        """The reserve exists for exactly this case."""
        clear_recursion_context()
        cty_type, raw = nested(MAX_VALIDATION_DEPTH, CtyDynamic())

        assert not cty_type.validate(raw).is_unknown
