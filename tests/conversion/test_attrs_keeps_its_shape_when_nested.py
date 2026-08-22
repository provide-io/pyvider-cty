#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""An attrs instance infers as an object wherever it sits, not only at the root.

`infer_cty_type_from_raw` walks a work stack keyed by `id()`. An attrs instance
is replaced along the way by a plain dict, and a new dict is a new id -- but the
*parent* container is still holding the instance, so it looked the child's
schema up under the instance's id and found nothing. The child degraded to
`dynamic`, so `[Child(value=1)]` came back as `list(dynamic)` instead of a list
of objects, and any schema derived from it lost the attribute.

At the root it worked, and that is what hid it: the conversion there happens
before the stack is built, so there is no parent to disagree with.
"""

from __future__ import annotations

import attrs
import pytest

from pyvider.cty import CtyList, CtyMap, CtyObject, CtySet, CtyTuple
from pyvider.cty.conversion import infer_cty_type_from_raw


@attrs.define
class Child:
    value: int


@attrs.define
class Parent:
    name: str
    child: Child


@attrs.frozen
class FrozenChild:
    """Hashable, so it can be a set member."""

    value: int


def child_object() -> CtyObject:
    """What a `Child` should infer as, wherever it appears."""
    inferred = infer_cty_type_from_raw(Child(value=1))
    assert isinstance(inferred, CtyObject)
    return inferred


class TestAtTheRoot:
    """Already worked. Held so the fix cannot regress it."""

    def test_an_attrs_instance_is_an_object(self) -> None:
        assert isinstance(infer_cty_type_from_raw(Child(value=1)), CtyObject)

    def test_with_its_attribute(self) -> None:
        assert "value" in child_object().attribute_types


class TestInEveryContainerPosition:
    def test_in_a_list(self) -> None:
        inferred = infer_cty_type_from_raw([Child(value=1)])

        assert isinstance(inferred, CtyList)
        assert inferred.element_type.equal(child_object())

    def test_in_a_list_of_several(self) -> None:
        inferred = infer_cty_type_from_raw([Child(value=1), Child(value=2)])

        assert isinstance(inferred, CtyList)
        assert inferred.element_type.equal(child_object())

    def test_in_a_tuple(self) -> None:
        inferred = infer_cty_type_from_raw((Child(value=1),))

        assert isinstance(inferred, CtyTuple)
        assert inferred.element_types[0].equal(child_object())

    def test_in_a_dict(self) -> None:
        inferred = infer_cty_type_from_raw({"c": Child(value=1)})

        assert isinstance(inferred, CtyObject)
        assert inferred.attribute_types["c"].equal(child_object())

    def test_in_a_set(self) -> None:
        """Frozen, because `@attrs.define` sets `__hash__` to None and an
        ordinary attrs instance cannot be a set member at all."""
        inferred = infer_cty_type_from_raw({FrozenChild(value=1)})

        assert isinstance(inferred, CtySet)
        assert isinstance(inferred.element_type, CtyObject)
        assert "value" in inferred.element_type.attribute_types

    def test_as_an_attribute_of_another_attrs_class(self) -> None:
        inferred = infer_cty_type_from_raw(Parent(name="p", child=Child(value=1)))

        assert isinstance(inferred, CtyObject)
        assert inferred.attribute_types["child"].equal(child_object())

    def test_two_levels_down(self) -> None:
        inferred = infer_cty_type_from_raw({"outer": [Child(value=1)]})

        assert isinstance(inferred, CtyObject)
        outer = inferred.attribute_types["outer"]
        assert isinstance(outer, CtyList)
        assert outer.element_type.equal(child_object())

    def test_in_a_map_keyed_by_something_other_than_a_string(self) -> None:
        inferred = infer_cty_type_from_raw({1: Child(value=1)})

        assert isinstance(inferred, CtyMap)
        assert inferred.element_type.equal(child_object())


class TestTheSameInstanceTwice:
    """Aliasing by `id()` has to survive the same object appearing twice."""

    def test_one_instance_in_two_positions(self) -> None:
        shared = Child(value=1)
        inferred = infer_cty_type_from_raw({"a": shared, "b": shared})

        assert isinstance(inferred, CtyObject)
        assert inferred.attribute_types["a"].equal(child_object())
        assert inferred.attribute_types["b"].equal(child_object())


@pytest.mark.parametrize("build", [list, tuple], ids=["list", "tuple"])
def test_many_instances_do_not_collide(build: type) -> None:
    """Enough instances that a recycled `id()` would show up as a wrong answer."""
    inferred = infer_cty_type_from_raw(build(Child(value=n) for n in range(200)))

    expected = child_object()
    members = inferred.element_types if isinstance(inferred, CtyTuple) else (inferred.element_type,)
    assert all(member.equal(expected) for member in members)


# 🌊🪢🔚
