#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Test suite for comparison functions (equal, not_equal, less_than, greater_than, etc.)."""

import pytest

from pyvider.cty import CtyNumber, CtyString, CtyValue
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import (
    equal,
    greater_than,
    greater_than_or_equal_to,
    less_than,
    less_than_or_equal_to,
    max_fn,
    min_fn,
    not_equal,
)


# Helper functions for creating CtyValues to improve test readability
def S(v):
    return CtyString().validate(v)


def N(v):
    return CtyNumber().validate(v)


class TestComparisonFunctions:
    def test_equal(self) -> None:
        assert equal(N(5), N(5)).is_true()
        assert equal(S("a"), S("b")).is_false()
        assert equal(CtyValue.unknown(CtyNumber()), N(5)).is_unknown

    def test_not_equal(self) -> None:
        assert not_equal(N(5), N(5)).is_false()
        assert not_equal(S("a"), S("b")).is_true()
        assert not_equal(CtyValue.unknown(CtyNumber()), N(5)).is_unknown

    def test_less_than(self) -> None:
        assert less_than(N(5), N(10)).is_true()
        with pytest.raises(CtyFunctionError):
            less_than(N(1), S("a"))

    def test_the_orderings_are_defined_on_numbers_only(self) -> None:
        """Until 2026-08-17 this asserted `less_than("a", "b")` is true.

        go-cty's four ordering comparisons declare both parameters as
        `cty.Number` (`stdlib/number.go:210`) and their implementations are
        `Value.LessThan` and friends, which panic on anything else
        (`value_ops.go:1374`). There is no string ordering in the stdlib at all,
        so comparing two strings was an extra function this package offered
        under a go-cty name -- and one whose answer Terraform would never
        produce.
        """
        with pytest.raises(CtyFunctionError):
            less_than(S("a"), S("b"))

    def test_max_min(self) -> None:
        assert max_fn(N(1), N(10), N(5)).value == 10
        assert min_fn(N(1), N(10), N(5)).value == 1
        with pytest.raises(CtyFunctionError):
            min_fn(N(1), S("a"))

    def test_max_and_min_are_defined_on_numbers_only(self) -> None:
        """Until 2026-08-17 this asserted `min("z", "a", "m")` is `"a"`.

        go-cty's `MinFunc` and `MaxFunc` declare one variadic parameter of type
        `cty.Number` (`stdlib/number.go:328`), and their bodies seed with
        `cty.PositiveInfinity`/`cty.NegativeInfinity` and compare with
        `Value.LessThan` -- numbers throughout. This package sorted strings too,
        by admitting any argument list that was homogeneous.
        """
        with pytest.raises(CtyFunctionError):
            min_fn(S("z"), S("a"), S("m"))

    def test_compare_with_refuses_a_null(self) -> None:
        with pytest.raises(CtyFunctionError):
            greater_than(CtyValue.null(CtyNumber()), N(1))
        with pytest.raises(CtyFunctionError):
            greater_than(N(1), CtyValue.null(CtyNumber()))

    def test_multi_compare_no_args(self) -> None:
        with pytest.raises(CtyFunctionError):
            max_fn()
        with pytest.raises(CtyFunctionError):
            min_fn()

    def test_multi_compare_all_refuses_a_null(self) -> None:
        with pytest.raises(CtyFunctionError):
            max_fn(CtyValue.null(CtyNumber()), CtyValue.null(CtyNumber()))

    def test_multi_compare_mixed_types(self) -> None:
        with pytest.raises(CtyFunctionError):
            max_fn(N(1), S("a"))

    def test_greater_than_or_equal_to(self) -> None:
        assert greater_than_or_equal_to(N(2), N(1)).is_true()
        assert greater_than_or_equal_to(N(1), N(1)).is_true()
        assert greater_than_or_equal_to(N(1), N(2)).is_false()

    def test_less_than_or_equal_to(self) -> None:
        assert less_than_or_equal_to(N(1), N(2)).is_true()
        assert less_than_or_equal_to(N(1), N(1)).is_true()
        assert less_than_or_equal_to(N(2), N(1)).is_false()


# 🌊🪢🔚


class TestEqualityWithNestedUnknowns:
    """`equal` and `not_equal` must not decide a comparison they cannot see.

    `is_unknown` answers only for the top level. An object whose attribute is
    unknown is itself known, so testing it alone let a partially-unknown value
    reach `==`, which answers with a plain bool. That unknown attribute could
    still resolve to the value that makes the two equal, so a definite answer
    asserts more than the data supports.

    The containers are inconsistent about this by nature, which is why the bug
    showed up for objects and not lists: a list built from an unknown element
    reports itself unknown, an object with an unknown attribute does not.

    The break these tests catch: deciding equality from `is_unknown` rather than
    from whether the values are wholly known.
    """

    def _obj(self, attr_value):
        from pyvider.cty import CtyObject

        return CtyObject(attribute_types={"a": CtyString()}).validate({"a": attr_value})

    def test_equal_is_undecided_when_an_attribute_is_unknown(self) -> None:
        lhs = self._obj(CtyValue.unknown(CtyString()))
        rhs = self._obj(CtyString().validate("z"))

        assert equal(lhs, rhs).is_unknown

    def test_not_equal_is_undecided_when_an_attribute_is_unknown(self) -> None:
        lhs = self._obj(CtyValue.unknown(CtyString()))
        rhs = self._obj(CtyString().validate("z"))

        assert not_equal(lhs, rhs).is_unknown

    def test_wholly_known_values_still_answer_definitely(self) -> None:
        assert equal(CtyString().validate("a"), CtyString().validate("a")).value is True
        assert equal(CtyString().validate("a"), CtyString().validate("b")).value is False
        assert not_equal(CtyString().validate("a"), CtyString().validate("b")).value is True

    def test_nulls_are_still_equal(self) -> None:
        """A null is a known absence, not an open question."""
        assert equal(CtyValue.null(CtyString()), CtyValue.null(CtyString())).value is True

    def test_equal_objects_with_all_attributes_known_answer_definitely(self) -> None:
        lhs = self._obj(CtyString().validate("z"))
        rhs = self._obj(CtyString().validate("z"))

        assert equal(lhs, rhs).value is True
