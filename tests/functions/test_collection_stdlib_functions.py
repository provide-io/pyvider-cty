#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Test suite for collection functions (reverse, hasindex, index, element, etc.) from stdlib_parity."""

import pytest

from pyvider.cty import CtyDynamic, CtyList, CtyMap, CtyNumber, CtySet, CtyString, CtyTuple, CtyValue
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

    def test_setproduct_of_ordered_arguments_preserves_order(self) -> None:
        """A list in, a list out.

        go-cty returns `cty.List(cty.Tuple(...))` when every argument is a list
        or a tuple (`collection.go:975`) and a set only when one argument is a
        set -- its own parameter documentation says lists and tuples "preserve
        the input ordering". This always built a set, so the ordering a caller
        asked for by passing lists was discarded on the way out.
        """
        prod = setproduct(L(CtyString(), ["a", "b"]), L(CtyString(), ["x", "y"]))

        assert isinstance(prod.type, CtyList)
        assert [item.raw_value for item in prod.value] == [
            ("a", "x"),
            ("a", "y"),
            ("b", "x"),
            ("b", "y"),
        ]

    def test_setproduct_of_a_set_and_a_list_is_a_set(self) -> None:
        """One unordered argument is enough to make the result unordered."""
        prod = setproduct(Set(CtyString(), ["a"]), L(CtyString(), ["x"]))

        assert isinstance(prod.type, CtySet)

    def test_setproduct_requires_two_arguments(self) -> None:
        """A cartesian product of one collection is not a thing go-cty makes.

        This accepted a single argument and returned a set of one-tuples.
        """
        with pytest.raises(CtyFunctionError):
            setproduct(Set(CtyString(), ["a"]))
        with pytest.raises(CtyFunctionError):
            setproduct()

    def test_setproduct_refuses_a_product_over_the_safety_limit(self) -> None:
        """The one place this package refuses on size rather than on meaning.

        go-cty allocates whatever the arguments multiply out to; two 1024-element
        lists are 1,048,576 tuples from a payload that fits in a plan request.
        An accepted divergence -- see `.provide/GO-CTY-PARITY.md`.
        """
        big = L(CtyString(), [str(i) for i in range(1024)])

        with pytest.raises(CtyFunctionError, match="safety limit"):
            setproduct(big, big)

    def test_setproduct_caps_only_a_product_it_would_materialize(self) -> None:
        """An unknown-length argument allocates nothing, so the cap must not fire.

        The cap was checked before the unknown branch, so this raised where
        go-cty answers an unknown -- refusing the one shape that cannot be a DoS,
        and the shape Terraform sends at plan time.
        """
        big = L(CtyString(), [str(i) for i in range(1024)])
        unknown = CtyValue.unknown(CtyList(element_type=CtyString()))

        result = setproduct(big, big, unknown)

        assert result.is_unknown

    def test_setproduct_refuses_a_null_argument(self) -> None:
        """A dropped null changed the arity of the result tuple.

        Nulls used to be filtered out of the arguments, so the element type of
        the result depended on which arguments happened to be null rather than
        on the argument types. go-cty refuses a null here outright.
        """
        with pytest.raises(CtyFunctionError):
            setproduct(CtyValue.null(CtySet(element_type=CtyString())), Set(CtyString(), ["x"]))

    def test_setproduct_keeps_its_type_when_an_argument_is_unknown(self) -> None:
        """The result type comes from the argument types, which are known.

        An unknown argument used to make the result `set(dynamic)`, discarding
        a type that was fully determined.
        """
        result = setproduct(CtyValue.unknown(CtySet(element_type=CtyString())), Set(CtyString(), ["x"]))

        assert result.is_unknown
        assert result.type.equal(CtySet(element_type=CtyTuple(element_types=(CtyString(), CtyString()))))

    def test_setproduct_unifies_a_tuple_argument(self) -> None:
        """A tuple contributes one element type, not one per position.

        go-cty runs `UnifyUnsafe` over a tuple's element types
        (`collection.go:958`); an empty tuple has nothing to unify and
        contributes dynamic. A tuple counts as ordered, so a product of two of
        them is a list.
        """
        homogeneous = CtyTuple(element_types=(CtyString(), CtyString())).validate(("a", "b"))
        empty = CtyTuple(element_types=()).validate(())

        prod = setproduct(homogeneous, L(CtyString(), ["x"]))
        assert isinstance(prod.type, CtyList)
        assert prod.type.element_type.equal(CtyTuple(element_types=(CtyString(), CtyString())))

        with_empty = setproduct(empty, L(CtyString(), ["x"]))
        assert with_empty.type.element_type.equal(  # type: ignore[union-attr]
            CtyTuple(element_types=(CtyDynamic(), CtyString()))
        )
        assert list(with_empty.value) == []

    def test_setproduct_refuses_a_non_collection(self) -> None:
        with pytest.raises(CtyFunctionError):
            setproduct(CtyString().validate("a"), Set(CtyString(), ["x"]))

    def test_zipmap(self) -> None:
        keys = L(CtyString(), ["a", "b"])
        vals = L(CtyNumber(), [1, 2])
        assert zipmap(keys, vals).raw_value == {"a": 1, "b": 2}


# 🌊🪢🔚
