#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`deep_values`, `walk` and `transform` -- go-cty's `cty/walk.go`.

The load-bearing property, tested throughout: **an emitted path re-applies to
the value it was emitted from**. A traversal that reports a location it cannot
then reach is worse than one that reports nothing, because the caller only
finds out at the point of use.
"""

from __future__ import annotations

from typing import Any

import pytest

from pyvider.cty import (
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyValue,
)
from pyvider.cty.exceptions import CtyListValidationError
from pyvider.cty.path import CtyPath
from pyvider.cty.walk import deep_values, transform, walk

STRS = CtyList(element_type=CtyString())


def paths(value: CtyValue[Any]) -> list[str]:
    return [str(path) for path, _ in deep_values(value)]


def assert_paths_reapply(value: CtyValue[Any]) -> None:
    """Every emitted path must reach the value that was emitted with it."""
    for path, expected in deep_values(value):
        reached = path.apply_path(value)
        assert reached.type.equal(expected.type), f"{path}: type changed on re-apply"
        assert reached.value == expected.value, f"{path}: value changed on re-apply"


class TestDeepValues:
    def test_a_primitive_yields_only_itself(self) -> None:
        assert paths(CtyString().validate("a")) == ["(root)"]

    def test_a_list_yields_itself_then_its_elements_in_order(self) -> None:
        assert paths(STRS.validate(["a", "b"])) == ["(root)", "[0]", "[1]"]

    def test_an_object_yields_its_attributes_in_sorted_order(self) -> None:
        """Sorted, not declared -- and the difference is stability.

        This asserted declaration order on the grounds that being driven by the
        type rather than the payload made it stable. It is stable only for a
        given spelling of the type: the same logical object declared the other
        way round walks the other way round. go-cty sorts, and says why -- "so
        that results will always be stable given the same input".
        """
        obj = CtyObject(attribute_types={"b": CtyString(), "a": CtyString()})

        assert paths(obj.validate({"a": "1", "b": "2"})) == ["(root)", "a", "b"]

    def test_a_map_yields_a_key_step_per_entry(self) -> None:
        m = CtyMap(element_type=CtyString()).validate({"k": "v"})

        assert paths(m) == ["(root)", "['k']"]

    def test_a_map_yields_its_keys_in_sorted_order(self) -> None:
        """Insertion order is a property of how the dict was built, not of the value."""
        m = CtyMap(element_type=CtyString()).validate({"z": "1", "a": "2"})

        assert paths(m) == ["(root)", "['a']", "['z']"]

    def test_a_set_element_is_addressed_by_itself(self) -> None:
        """go-cty's rule: "a set element effectively acts as its own key"."""
        st = CtySet(element_type=CtyString()).validate(["b", "a"])

        assert paths(st) == ["(root)", "['a']", "['b']"]

    def test_set_order_is_stable_rather_than_the_frozenset_order(self) -> None:
        """A traversal whose output moves between runs cannot be tested or
        diffed, and a frozenset has no order of its own to report."""
        first = CtySet(element_type=CtyString()).validate(["c", "a", "b"])
        second = CtySet(element_type=CtyString()).validate(["b", "c", "a"])

        assert paths(first) == paths(second) == ["(root)", "['a']", "['b']", "['c']"]

    def test_nesting_is_reported_depth_first(self) -> None:
        nested = CtyObject(attribute_types={"a": STRS, "b": CtyString()})

        assert paths(nested.validate({"a": ["x", "y"], "b": "z"})) == ["(root)", "a", "a[0]", "a[1]", "b"]

    def test_deeply_nested_values_do_not_exhaust_the_stack(self) -> None:
        """The reason this is iterative. A recursive version of exactly this
        shape in pyvider's marshaler did raise RecursionError at a depth this
        package advertises as supported.
        """
        value: CtyValue[Any] = CtyString().validate("bottom")
        for _ in range(400):
            value = CtyTuple(element_types=(value.type,)).validate((value,))

        assert len(list(deep_values(value))) == 401

    @pytest.mark.parametrize(
        "value",
        [
            CtyValue.null(STRS),
            CtyValue.unknown(STRS),
            CtyValue.null(CtyObject(attribute_types={"a": CtyString()})),
            CtyValue.unknown(CtyMap(element_type=CtyString())),
        ],
        ids=["null list", "unknown list", "null object", "unknown map"],
    )
    def test_a_null_or_unknown_container_is_a_leaf(self, value: CtyValue[Any]) -> None:
        """There is nothing inside either one to visit -- go-cty's rule too."""
        assert paths(value) == ["(root)"]

    def test_an_empty_container_yields_only_itself(self) -> None:
        assert paths(STRS.validate([])) == ["(root)"]

    def test_a_dynamic_wrapper_is_transparent(self) -> None:
        """The wrapper says how the value was typed, not that there is another
        level of nesting. Emitting a step for it would produce paths that no
        longer describe the underlying structure."""
        assert paths(CtyDynamic().validate(["a", "b"])) == ["(root)", "[0]", "[1]"]

    def test_a_parent_mark_does_not_reach_its_children(self) -> None:
        """The bug go-cty fixed in 1.15.0. Marks live on the value here, and a
        child is a separate value, so the leak has no route -- pinned so that
        a future change to how containers carry marks cannot reopen it.
        """
        marked = STRS.validate(["a"]).with_marks({"sensitive"})

        collected = {str(path): value.marks for path, value in deep_values(marked)}

        assert collected["(root)"] == frozenset({"sensitive"})
        assert collected["[0]"] == frozenset()

    def test_a_child_keeps_its_own_marks(self) -> None:
        element = CtyString().validate("a").with_marks({"sensitive"})
        holder = CtyTuple(element_types=(CtyString(),)).validate((element,))

        assert dict(deep_values(holder))[CtyPath.index(0)].marks == frozenset({"sensitive"})

    @pytest.mark.parametrize(
        "value",
        [
            STRS.validate(["a", "b"]),
            CtyMap(element_type=CtyString()).validate({"k": "v"}),
            CtySet(element_type=CtyString()).validate(["a", "b"]),
            CtyObject(attribute_types={"a": STRS}).validate({"a": ["x"]}),
            CtyTuple(element_types=(CtyString(), CtyNumber())).validate(("a", 1)),
            CtyDynamic().validate(["a"]),
        ],
        ids=["list", "map", "set", "object", "tuple", "dynamic"],
    )
    def test_every_emitted_path_re_applies(self, value: CtyValue[Any]) -> None:
        assert_paths_reapply(value)


class TestWalk:
    def test_it_visits_what_deep_values_yields(self) -> None:
        value = CtyObject(attribute_types={"a": STRS}).validate({"a": ["x"]})
        seen: list[str] = []

        walk(value, lambda path, _value: bool(seen.append(str(path))) or True)

        assert seen == paths(value)

    def test_returning_false_skips_the_contents_but_not_the_siblings(self) -> None:
        """The one thing a plain generator cannot express, and the only reason
        this exists alongside `deep_values`."""
        value = CtyObject(attribute_types={"a": STRS, "b": CtyString()}).validate({"a": ["x"], "b": "y"})
        seen: list[str] = []

        def visit(path: CtyPath, _value: CtyValue[Any]) -> bool:
            seen.append(str(path))
            return str(path) != "a"

        walk(value, visit)

        assert seen == ["(root)", "a", "b"]


class TestTransform:
    def test_a_leaf_is_replaced(self) -> None:
        result = transform(CtyString().validate("a"), lambda _p, v: CtyString().validate(f"{v.value}!"))

        assert result.value == "a!"

    def test_children_are_transformed_before_their_container(self) -> None:
        """Postorder is the whole point: the callback sees a container already
        built from its transformed contents."""
        order: list[str] = []

        def note(path: CtyPath, value: CtyValue[Any]) -> CtyValue[Any]:
            order.append(str(path))
            return value

        transform(CtyObject(attribute_types={"a": STRS}).validate({"a": ["x"]}), note)

        assert order == ["a[0]", "a", "(root)"]

    def test_a_nested_value_is_rebuilt_around_the_change(self) -> None:
        value = CtyObject(attribute_types={"a": STRS, "b": CtyString()}).validate({"a": ["x", "y"], "b": "z"})

        result = transform(
            value,
            lambda _p, v: (
                CtyString().validate(v.value.upper()) if isinstance(v.type, CtyString) and not v.is_null else v
            ),
        )

        assert [e.value for e in result.value["a"].value] == ["X", "Y"]
        assert result.value["b"].value == "Z"

    def test_the_identity_transform_preserves_the_type(self) -> None:
        value = CtyObject(attribute_types={"a": STRS}).validate({"a": ["x"]})

        assert transform(value, lambda _p, v: v).type.equal(value.type)

    def test_an_untouched_container_is_returned_rather_than_rebuilt(self) -> None:
        """Not just an optimisation to leave untested: most transforms touch a
        few leaves, and rebuilding everything above them meant re-validating the
        whole structure -- 166 ms for an identity pass over a 10k-object list,
        against 53 ms now.
        """
        value = CtyObject(attribute_types={"a": STRS}).validate({"a": ["x"]})

        assert transform(value, lambda _p, v: v) is value

    def test_only_the_branch_that_changed_is_rebuilt(self) -> None:
        """The sibling that nothing touched keeps its identity."""
        value = CtyObject(attribute_types={"a": STRS, "b": STRS}).validate({"a": ["x"], "b": ["y"]})

        result = transform(value, lambda p, v: CtyString().validate("X") if str(p) == "a[0]" else v)

        assert result is not value
        assert result.value["b"] is value.value["b"]
        assert result.value["a"] is not value.value["a"]

    def test_a_changed_leaf_still_reaches_the_result(self) -> None:
        """The shortcut must not swallow a real edit -- identity is the test,
        so a replacement value always counts as a change."""
        value = STRS.validate(["a", "b"])

        result = transform(
            value, lambda _p, v: CtyString().validate(v.value.upper()) if isinstance(v.type, CtyString) else v
        )

        assert [e.value for e in result.value] == ["A", "B"]

    def test_an_equal_but_distinct_replacement_still_counts_as_a_change(self) -> None:
        """Identity rather than equality, for the reason `marks._strip` gives:
        `==` can report "unchanged" for a value whose marks in fact changed."""
        value = STRS.validate(["a"])

        result = transform(
            value,
            lambda _p, v: v.with_marks({"sensitive"}) if isinstance(v.type, CtyString) else v,
        )

        assert result is not value
        assert result.value[0].marks == frozenset({"sensitive"})

    def test_a_container_keeps_its_own_marks(self) -> None:
        """A rebuild constructs a fresh value, so the marks have to be put back
        or a sensitive collection is silently declassified by being walked."""
        marked = STRS.validate(["a"]).with_marks({"sensitive"})

        assert transform(marked, lambda _p, v: v).marks == frozenset({"sensitive"})

    def test_an_element_keeps_its_own_marks(self) -> None:
        element = CtyString().validate("a").with_marks({"sensitive"})
        holder = CtyTuple(element_types=(CtyString(),)).validate((element,))

        assert transform(holder, lambda _p, v: v).value[0].marks == frozenset({"sensitive"})

    def test_a_set_hoists_its_element_marks_onto_itself(self) -> None:
        """`validate` does this, matching go-cty's `SetVal`. Recorded here
        because it makes the rebuilt set differ from the input in where the
        mark sits, which is easy to mistake for a leak."""
        element = CtyString().validate("a").with_marks({"sensitive"})
        st = CtySet(element_type=CtyString()).validate([element])

        assert transform(st, lambda _p, v: v).marks == frozenset({"sensitive"})

    @pytest.mark.parametrize(
        "value",
        [CtyValue.null(STRS), CtyValue.unknown(STRS)],
        ids=["null", "unknown"],
    )
    def test_a_null_or_unknown_value_is_handed_over_whole(self, value: CtyValue[Any]) -> None:
        seen: list[str] = []

        result = transform(value, lambda p, v: (seen.append(str(p)), v)[1])

        assert seen == ["(root)"]
        assert result is value

    def test_a_tuple_takes_the_type_of_its_transformed_elements(self) -> None:
        """A tuple's type is a statement about each element, so changing an
        element's type changes the tuple's -- which is what go-cty's `TupleVal`
        does when it derives the type from what it was handed."""
        value = CtyTuple(element_types=(CtyString(),)).validate(("1",))

        result = transform(
            value, lambda _p, v: CtyNumber().validate(1) if isinstance(v.type, CtyString) else v
        )

        assert result.type.equal(CtyTuple(element_types=(CtyNumber(),)))

    def test_changing_a_list_element_type_is_refused(self) -> None:
        """A list names its element type once, so this invariant cannot hold.
        go-cty reaches the same outcome by panicking, and says so: "this
        function can panic if such invariants are violated"."""
        value = STRS.validate(["a"])

        with pytest.raises(CtyListValidationError):
            transform(value, lambda _p, v: CtyNumber().validate(1) if isinstance(v.type, CtyString) else v)

    def test_a_dynamic_wrapper_survives_the_rebuild(self) -> None:
        """A transform should not retype what it did not touch."""
        value = CtyDynamic().validate(["a"])

        result = transform(value, lambda _p, v: v)

        assert isinstance(result.type, CtyDynamic)
        assert [e.value for e in result.value.value] == ["a"]

    def test_deeply_nested_values_do_not_exhaust_the_stack(self) -> None:
        value: CtyValue[Any] = CtyString().validate("bottom")
        for _ in range(400):
            value = CtyTuple(element_types=(value.type,)).validate((value,))

        assert transform(value, lambda _p, v: v).type.equal(value.type)


# 🌊🪢🔚
