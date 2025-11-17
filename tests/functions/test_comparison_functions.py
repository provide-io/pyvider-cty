#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
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
        assert less_than(S("a"), S("b")).is_true()
        with pytest.raises(CtyFunctionError):
            less_than(N(1), S("a"))

    def test_max_min(self) -> None:
        assert max_fn(N(1), N(10), N(5)).value == 10
        assert min_fn(S("z"), S("a"), S("m")).value == "a"
        with pytest.raises(CtyFunctionError):
            min_fn(N(1), S("a"))

    def test_compare_with_null(self) -> None:
        assert greater_than(CtyValue.null(CtyNumber()), N(1)).is_unknown
        assert greater_than(N(1), CtyValue.null(CtyNumber())).is_unknown

    def test_multi_compare_no_args(self) -> None:
        with pytest.raises(CtyFunctionError):
            max_fn()
        with pytest.raises(CtyFunctionError):
            min_fn()

    def test_multi_compare_all_null(self) -> None:
        assert max_fn(CtyValue.null(CtyNumber()), CtyValue.null(CtyNumber())).is_null

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
