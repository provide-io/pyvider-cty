#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Test suite for collection query functions (contains, keys, values, hasindex, index, etc.)."""

import pytest

from pyvider.cty import (
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyValue,
)
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import contains, hasindex, index, keys, values


class TestContains:
    def test_contains_list(self) -> None:
        lst = CtyList(element_type=CtyString()).validate(["a", "b"])
        assert contains(lst, CtyString().validate("a")).raw_value is True
        assert contains(lst, CtyString().validate("c")).raw_value is False

    def test_contains_set(self) -> None:
        s = CtySet(element_type=CtyString()).validate({"a", "b"})
        assert contains(s, CtyString().validate("a")).raw_value is True
        assert contains(s, CtyString().validate("c")).raw_value is False

    def test_contains_tuple(self) -> None:
        t = CtyTuple(element_types=(CtyString(), CtyString())).validate(("a", "b"))
        assert contains(t, CtyString().validate("a")).raw_value is True
        assert contains(t, CtyString().validate("c")).raw_value is False

    def test_contains_null_unknown(self) -> None:
        CtyList(element_type=CtyString()).validate(["a", "b"])
        assert contains(CtyValue.null(CtyList(element_type=CtyString())), CtyString().validate("a")).is_unknown
        assert contains(
            CtyValue.unknown(CtyList(element_type=CtyString())),
            CtyString().validate("a"),
        ).is_unknown

    def test_contains_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            contains(CtyString().validate("a"), CtyString().validate("a"))


class TestKeysValues:
    def test_keys_map(self) -> None:
        m = CtyMap(element_type=CtyString()).validate({"a": "x", "b": "y"})
        assert keys(m).raw_value == ["a", "b"]

    def test_keys_object(self) -> None:
        o = CtyObject({"a": CtyString(), "b": CtyString()}).validate({"a": "x", "b": "y"})
        assert keys(o).raw_value == ["a", "b"]

    def test_keys_null_unknown(self) -> None:
        assert keys(CtyValue.null(CtyMap(element_type=CtyString()))).is_unknown
        assert keys(CtyValue.unknown(CtyMap(element_type=CtyString()))).is_unknown

    def test_keys_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            keys(CtyString().validate("hello"))

    def test_values_map(self) -> None:
        m = CtyMap(element_type=CtyString()).validate({"a": "x", "b": "y"})
        assert values(m).raw_value == ["x", "y"]

    def test_values_object(self) -> None:
        o = CtyObject({"a": CtyString(), "b": CtyString()}).validate({"a": "x", "b": "y"})
        assert values(o).raw_value == ["x", "y"]

    def test_values_null_unknown(self) -> None:
        assert values(CtyValue.null(CtyMap(element_type=CtyString()))).is_unknown
        assert values(CtyValue.unknown(CtyMap(element_type=CtyString()))).is_unknown

    def test_values_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            values(CtyString().validate("hello"))


class TestHasIndexIndex:
    def test_hasindex_list(self) -> None:
        lst = CtyList(element_type=CtyString()).validate(["a", "b"])
        assert hasindex(lst, CtyNumber().validate(0)).raw_value is True
        assert hasindex(lst, CtyNumber().validate(2)).raw_value is False
        assert hasindex(lst, CtyString().validate("a")).raw_value is False

    def test_hasindex_map(self) -> None:
        m = CtyMap(element_type=CtyString()).validate({"a": "x"})
        assert hasindex(m, CtyString().validate("a")).raw_value is True
        assert hasindex(m, CtyString().validate("b")).raw_value is False
        assert hasindex(m, CtyNumber().validate(0)).raw_value is False

    def test_hasindex_null_unknown(self) -> None:
        lst = CtyList(element_type=CtyString()).validate(["a"])
        assert (
            hasindex(
                CtyValue.null(CtyList(element_type=CtyString())),
                CtyNumber().validate(0),
            ).raw_value
            is False
        )
        assert hasindex(
            CtyValue.unknown(CtyList(element_type=CtyString())),
            CtyNumber().validate(0),
        ).is_unknown
        assert hasindex(lst, CtyValue.null(CtyNumber())).raw_value is False
        assert hasindex(lst, CtyValue.unknown(CtyNumber())).is_unknown

    def test_hasindex_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            hasindex(CtyString().validate("a"), CtyNumber().validate(0))

    def test_index_list(self) -> None:
        lst = CtyList(element_type=CtyString()).validate(["a", "b"])
        assert index(lst, CtyNumber().validate(1)).raw_value == "b"

    def test_index_map(self) -> None:
        m = CtyMap(element_type=CtyString()).validate({"a": "x"})
        assert index(m, CtyString().validate("a")).raw_value == "x"

    def test_index_not_found(self) -> None:
        lst = CtyList(element_type=CtyString()).validate(["a"])
        with pytest.raises(CtyFunctionError, match="key does not exist"):
            index(lst, CtyNumber().validate(1))


# 🌊🪢🔚
