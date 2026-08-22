#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Objects unify *among themselves* into a map before meeting the real maps.

go-cty's `unifyObjectsAsMaps` (`convert/unify.go:192`) unifies the objects'
attribute types into one map type first, then unifies that map with the map
types given. This module pooled every attribute type and every map element
type into a single unify, and a `dynamic` anywhere in the pool won it: for
`map(list(string))` + `object({a: string, b: dynamic})` the pool
`[list(string), string, dynamic]` unified to `dynamic`, giving `map(dynamic)`
where go-cty unifies the object to `map(string)` first, then finds that
`list(string)` and `string` share nothing, and refuses. Found 2026-08-22 by the
generated unify sweep against the oracle.
"""

from typing import Any

import pytest

from pyvider.cty import CtyDynamic, CtyList, CtyMap, CtyNumber, CtyObject, CtySet, CtyString, CtyType
from pyvider.cty.conversion.unify import unify

S, N, D = CtyString(), CtyNumber(), CtyDynamic()


def _map(element: CtyType[Any]) -> CtyMap[Any]:
    return CtyMap(element_type=element)


def _list(element: CtyType[Any]) -> CtyList[Any]:
    return CtyList(element_type=element)


def test_the_falsifying_example_is_refused() -> None:
    assert unify([_map(_list(S)), CtyObject({"a": S, "b": D})]) is None


def test_the_falsifying_example_inside_a_set_is_refused() -> None:
    inner = [CtySet(element_type=_map(_list(S))), CtySet(element_type=CtyObject({"a": S, "b": D}))]
    assert unify(inner) is None


@pytest.mark.parametrize(
    ("types", "expected"),
    [
        ([_map(S), CtyObject({"a": S, "b": D})], _map(S)),
        ([_map(S), CtyObject({"a": N})], _map(S)),
        ([_map(S), CtyObject({"a": S}), D], _map(S)),
        ([_map(_list(S)), CtyObject({"a": _list(S), "b": _list(N)})], _map(_list(S))),
        ([_map(D), CtyObject({"a": S})], _map(S)),
        ([CtyObject({"a": S}), CtyObject({"b": N})], _map(S)),
    ],
    ids=[
        "string map + dynamic attr",
        "string map + number attr",
        "with a dynamic",
        "list maps",
        "dynamic map",
        "two objects",
    ],
)
def test_what_go_cty_unifies_still_unifies(types: list[CtyType[Any]], expected: CtyType[Any]) -> None:
    """Each answer here was taken from real go-cty through the oracle."""
    result = unify(types)
    assert result is not None and result.equal(expected), result


@pytest.mark.parametrize(
    "types",
    [
        [_map(S), CtyObject({"a": _list(S)})],
        [CtyObject({"a": S}), CtyObject({"b": _list(S)})],
    ],
    ids=["string map + list attr", "two objects, string vs list"],
)
def test_what_go_cty_refuses_is_refused(types: list[CtyType[Any]]) -> None:
    assert unify(types) is None
