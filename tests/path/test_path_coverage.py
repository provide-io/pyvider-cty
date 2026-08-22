#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


import pytest

from pyvider.cty.exceptions import AttributePathError
from pyvider.cty.marks import CtyMark
from pyvider.cty.path import CtyPath, GetAttrStep, IndexStep, KeyStep, PathStep
from pyvider.cty.types import (
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyObject,
    CtyString,
)
from pyvider.cty.values import CtyValue


class DummyPathStep(PathStep):
    """A step that implements only `_apply`, to show what the base class adds."""

    def _apply(self, value):
        return value

    def apply_type(self, vtype):
        return vtype

    def __str__(self) -> str:
        return "dummy"


def test_path_step_is_abstract() -> None:
    with pytest.raises(TypeError):
        PathStep()


def test_a_step_that_implements_only_apply_still_carries_marks() -> None:
    """`PathStep.apply` unmarks, delegates and remarks, so no step can forget."""
    sensitive = CtyMark("sensitive")
    marked = CtyString().validate("x").mark(sensitive)

    assert DummyPathStep().apply(marked).marks == frozenset({sensitive})


def test_a_step_never_sees_a_marked_receiver() -> None:
    seen: list[frozenset[object]] = []

    class Recording(DummyPathStep):
        def _apply(self, value):
            seen.append(value.marks)
            return value

    Recording().apply(CtyString().validate("x").mark(CtyMark("sensitive")))

    assert seen == [frozenset()]


class TestASubclassWrittenAgainstTheOlderApply:
    """`PathStep` is exported, so a step outside this package implements `apply`.

    That was the abstract method until `apply` became a template that carries the
    receiver's marks. Such a subclass is bridged rather than broken: its `apply`
    becomes its `_apply`, the base class supplies `apply` again, and it gains the
    mark handling it was written too early to have.
    """

    @staticmethod
    def _legacy() -> type[PathStep]:
        with pytest.warns(DeprecationWarning, match="Implement `_apply` instead"):

            class LegacyStep(PathStep):
                def apply(self, value):
                    return value

                def apply_type(self, vtype):
                    return vtype

                def __str__(self) -> str:
                    return "legacy"

        return LegacyStep

    def test_it_is_not_abstract(self) -> None:
        assert self._legacy().__abstractmethods__ == frozenset()

    def test_it_can_still_be_instantiated(self) -> None:
        assert self._legacy()() is not None

    def test_its_old_method_still_runs(self) -> None:
        value = CtyString().validate("x")
        assert self._legacy()().apply(value).value == "x"

    def test_it_gains_the_mark_handling_it_never_had(self) -> None:
        sensitive = CtyMark("sensitive")
        marked = CtyString().validate("x").mark(sensitive)
        assert self._legacy()().apply(marked).marks == frozenset({sensitive})

    def test_a_subclass_defining_both_is_left_alone(self) -> None:
        class Both(PathStep):
            def apply(self, value):
                return CtyString().validate("from apply")

            def _apply(self, value):
                return CtyString().validate("from _apply")

            def apply_type(self, vtype):
                return vtype

            def __str__(self) -> str:
                return "both"

        assert Both().apply(CtyString().validate("x")).value == "from apply"

    def test_a_subclass_implementing_neither_is_still_abstract(self) -> None:
        class Neither(PathStep):
            def apply_type(self, vtype):
                return vtype

            def __str__(self) -> str:
                return "neither"

        with pytest.raises(TypeError, match="_apply"):
            Neither()


def test_getattrstep_empty_name() -> None:
    """An empty attribute name is a name. go-cty puts no constraint on one, and
    refusing it here meant no value of `object({"": string})` could be
    validated at all -- `CtyObject.validate` builds a step per attribute -- so
    `merge({"" = "x"}, {})` raised where go-cty answers."""
    step = GetAttrStep("")

    assert step.name == ""


def test_getattr_on_non_object() -> None:
    step = GetAttrStep("name")
    with pytest.raises(AttributePathError):
        step.apply(CtyValue(CtyString(), "hello"))


def test_index_on_dynamic_value() -> None:
    step = IndexStep(0)
    list_val = CtyValue(CtyList(element_type=CtyString()), ("a", "b"))
    dynamic_val = CtyValue(CtyDynamic(), list_val)
    result = step.apply(dynamic_val)
    assert result.value == "a"


def test_key_on_dynamic_value() -> None:
    step = KeyStep("name")
    map_val = CtyValue(CtyMap(element_type=CtyString()), {"name": "Alice"})
    dynamic_val = CtyValue(CtyDynamic(), map_val)
    result = step.apply(dynamic_val)
    assert result.value == "Alice"


def test_apply_path_to_non_cty_value() -> None:
    path = CtyPath.get_attr("name")
    with pytest.raises(AttributePathError):
        path.apply_path("not a cty value")


def test_apply_path_with_error() -> None:
    path = CtyPath.get_attr("name")
    value = CtyValue(CtyList(element_type=CtyString()), ("a", "b"))
    with pytest.raises(AttributePathError):
        path.apply_path(value)


def test_apply_path_type_with_error() -> None:
    path = CtyPath.get_attr("name")
    vtype = CtyList(element_type=CtyString())
    with pytest.raises(AttributePathError):
        path.apply_path_type(vtype)


def test_string_representation_of_empty_path() -> None:
    path = CtyPath.empty()
    assert path.string() == "(root)"


def test_empty_path_applied_to_a_value_is_that_value() -> None:
    value = CtyString().validate("x")
    assert CtyPath.empty().apply_path(value) is value


def test_empty_path_applied_to_a_non_cty_value() -> None:
    with pytest.raises(AttributePathError):
        CtyPath.empty().apply_path("not a cty value")


def test_empty_path_applied_to_a_type_is_that_type() -> None:
    assert CtyPath.empty().apply_path_type(CtyString()).equal(CtyString())


def test_getattr_on_a_known_dynamic_that_does_not_wrap_a_value() -> None:
    """The fall-through of `GetAttrStep`'s dynamic branch.

    A `dynamic` is stepped through when it wraps a `CtyValue`, and answered with
    an unknown when it is wholly unknown. A hand-built one that is neither has
    nothing to step into and no unknown to report, so it raises like any other
    non-object.
    """
    step = GetAttrStep("a")
    with pytest.raises(AttributePathError):
        step.apply(CtyValue(CtyDynamic(), "not a CtyValue"))


def test_key_step_with_invalid_key_type() -> None:
    step = KeyStep(123)
    with pytest.raises(AttributePathError):
        step.apply_type(CtyMap(element_type=CtyString()))


def test_path_edge_cases_from_z_file() -> None:
    """Integrates and fixes tests from the old z_high_coverage_final file."""
    obj_type = CtyObject(attribute_types={"name": CtyString()})
    path = CtyPath.get_attr("name")
    assert path.apply_path_type(obj_type) == CtyString()
    with pytest.raises(AttributePathError):
        path.apply_path_type(CtyString())
    with pytest.raises(AttributePathError):
        # FIX: Corrected typo from apply_type to apply_path_type
        CtyPath.key("k").apply_path_type(CtyString())
    with pytest.raises(AttributePathError):
        CtyPath.key(1).apply_path_type(CtyMap(element_type=CtyString()))


# 🌊🪢🔚
