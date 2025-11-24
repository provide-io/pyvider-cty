#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Test suite for collection functions (reverse, hasindex, index, element, etc.) from stdlib_parity."""

import pytest

from pyvider.cty import CtyList, CtyMap, CtyNumber, CtySet, CtyString, CtyTuple
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import (
    chunklist,
    coalescelist,
    compact,
    element,
    hasindex,
    index,
    lookup,
    merge,
    reverse,
    setproduct,
    zipmap,
)


# Helper functions for creating CtyValues to improve test readability
def S(v):
    return CtyString().validate(v)


def N(v):
    return CtyNumber().validate(v)


def L(t, v):
    return CtyList(element_type=t).validate(v)


def M(t, v):
    return CtyMap(element_type=t).validate(v)


def Set(t, v):
    return CtySet(element_type=t).validate(v)


class TestCollectionFunctions:
    def test_reverse(self) -> None:
        assert reverse(L(CtyString(), ["a", "b", "c"])).raw_value == ["c", "b", "a"]

    def test_hasindex(self) -> None:
        assert hasindex(L(CtyString(), ["a"]), N(0)).is_true()
        assert hasindex(M(CtyString(), {"k": "v"}), S("k")).is_true()
        assert hasindex(M(CtyString(), {"k": "v"}), S("z")).is_false()

    def test_index(self) -> None:
        assert index(L(CtyString(), ["a", "b"]), N(1)).value == "b"
        with pytest.raises(CtyFunctionError):
            index(L(CtyString(), []), N(0))

    def test_element(self) -> None:
        assert element(L(CtyString(), ["a", "b"]), N(3)).value == "b"  # wraps

    def test_coalescelist(self) -> None:
        l1, l2 = L(CtyString(), []), L(CtyString(), ["a"])
        assert coalescelist(l1, l2).raw_value == ["a"]

    def test_compact(self) -> None:
        assert compact(L(CtyString(), ["a", "", "b"])).raw_value == ["a", "b"]

    def test_chunklist(self) -> None:
        lst = L(CtyString(), ["a", "b", "c", "d", "e"])
        assert chunklist(lst, N(2)).raw_value == [["a", "b"], ["c", "d"], ["e"]]

    def test_lookup(self) -> None:
        m = M(CtyString(), {"a": "b"})
        assert lookup(m, S("a"), S("z")).value == "b"
        assert lookup(m, S("x"), S("z")).value == "z"

    def test_merge(self) -> None:
        m1 = M(CtyString(), {"a": "1", "b": "2"})
        m2 = M(CtyString(), {"b": "3", "c": "4"})
        assert merge(m1, m2).raw_value == {"a": "1", "b": "3", "c": "4"}

    def test_setproduct(self) -> None:
        s1 = Set(CtyString(), ["a", "b"])
        s2 = Set(CtyNumber(), [1, 2])
        prod = setproduct(s1, s2)
        assert isinstance(prod.type, CtySet)
        assert isinstance(prod.type.element_type, CtyTuple)
        result_set = {item.raw_value for item in prod.value}
        expected_set = {("a", 1), ("a", 2), ("b", 1), ("b", 2)}
        assert result_set == expected_set

    def test_zipmap(self) -> None:
        keys = L(CtyString(), ["a", "b"])
        vals = L(CtyNumber(), [1, 2])
        assert zipmap(keys, vals).raw_value == {"a": 1, "b": 2}


# 🌊🪢🔚
