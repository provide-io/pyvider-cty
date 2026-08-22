#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""A type description is a peer's bytes, so its nesting is not ours to trust.

`parse_tf_type_to_ctytype` decodes what arrived over the wire. Its depth is
therefore an input, and an input that decides how much stack and CPU to spend is
a denial of service. Three separate defects met here:

* the recursive function was wrapped in an `error_boundary` whose context
  stringified the whole remaining subtree, once per level -- quadratic in the
  input and paid on the way *in*, before anything had been validated. A
  1600-level description cost seventeen seconds;
* nothing bounded the descent, so it ran the interpreter out of stack and raised
  a bare `RecursionError`, which is not a `CtyError` -- a caller catching
  `CtyError` around its decoding did not catch it;
* and once a budget was added, the boundary undid it: it logs with
  `exc_info=True`, and rendering that traceback walks the frame locals, which
  hold the description itself. The render overflowed and replaced the
  `CtyValidationError` the budget had correctly raised.
"""

from __future__ import annotations

import time

import pytest

from pyvider.cty.config.defaults import MAX_TYPE_NESTING_DEPTH
from pyvider.cty.exceptions import CtyError, CtyValidationError
from pyvider.cty.parser import parse_tf_type_to_ctytype
from pyvider.cty.types import CtyList, CtyString

# Far past the budget, and past the interpreter's own stack: the point is that
# neither of those is what decides the outcome any more.
HOSTILE_DEPTHS = (2_000, 5_000, 20_000)

# Generous. The refusal happens without descending, so it is bounded by building
# the description rather than by parsing it.
REFUSAL_BUDGET_SECONDS = 2.0


def nest(depth: int) -> object:
    """A list-of-list-of-...-of-string description, `depth` levels deep."""
    spec: object = "string"
    for _ in range(depth):
        spec = ["list", spec]
    return spec


class TestADescriptionWithinTheBudgetStillParses:
    def test_a_shallow_description_is_unaffected(self) -> None:
        assert parse_tf_type_to_ctytype(["list", "string"]) == CtyList(element_type=CtyString())

    def test_the_budget_is_far_beyond_any_real_schema(self) -> None:
        """Real schemas nest in the tens. This lands in the hundreds."""
        assert MAX_TYPE_NESTING_DEPTH > 100

    def test_a_description_just_inside_the_budget_parses(self) -> None:
        parsed = parse_tf_type_to_ctytype(nest(MAX_TYPE_NESTING_DEPTH - 1))

        assert isinstance(parsed, CtyList)


@pytest.mark.parametrize("depth", HOSTILE_DEPTHS)
class TestADescriptionPastTheBudgetIsRefused:
    def test_it_raises_inside_the_error_taxonomy(self, depth: int) -> None:
        """A bare `RecursionError` before; a caller catching `CtyError` missed it."""
        with pytest.raises(CtyValidationError):
            parse_tf_type_to_ctytype(nest(depth))

    def test_that_refusal_is_catchable_as_ctyerror(self, depth: int) -> None:
        with pytest.raises(CtyError):
            parse_tf_type_to_ctytype(nest(depth))

    def test_it_refuses_promptly(self, depth: int) -> None:
        """The quadratic diagnostic, and the seventeen seconds it cost."""
        spec = nest(depth)

        started = time.perf_counter()
        with pytest.raises(CtyValidationError):
            parse_tf_type_to_ctytype(spec)

        assert time.perf_counter() - started < REFUSAL_BUDGET_SECONDS

    def test_the_message_says_what_the_limit_was(self, depth: int) -> None:
        with pytest.raises(CtyValidationError, match="nests deeper than"):
            parse_tf_type_to_ctytype(nest(depth))


class TestTheDiagnosticIsBounded:
    """A message built from a peer's description must not embed all of it."""

    def test_the_depth_refusal_does_not_render_the_whole_tree(self) -> None:
        with pytest.raises(CtyValidationError) as caught:
            parse_tf_type_to_ctytype(nest(5_000))

        # 5000 levels rendered in full would be tens of thousands of characters.
        assert len(str(caught.value)) < 1_000

    def test_an_invalid_description_is_reported_briefly_too(self) -> None:
        with pytest.raises(CtyValidationError) as caught:
            parse_tf_type_to_ctytype([nest(5_000)])

        assert len(str(caught.value)) < 1_000

    def test_an_over_long_primitive_name_is_trimmed(self) -> None:
        with pytest.raises(CtyValidationError) as caught:
            parse_tf_type_to_ctytype("z" * 10_000)

        assert len(str(caught.value)) < 1_000

    def test_over_long_optional_names_are_trimmed(self) -> None:
        """The parser's own complaint about the third element.

        Reached by making the names *not* a list of strings, which is what this
        check is for. A list that really is all strings is the object type's
        business, and it reports unknown optional names itself.
        """
        with pytest.raises(CtyValidationError) as caught:
            parse_tf_type_to_ctytype(["object", {}, ["x" * 10_000, 123]])

        assert len(str(caught.value)) < 1_000


# 🌊🪢🔚
