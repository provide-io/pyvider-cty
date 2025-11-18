#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

import pytest

from pyvider.cty.exceptions import AttributePathError
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
    def apply(self, value):
        return value

    def apply_type(self, vtype):
        return vtype

    def __str__(self) -> str:
        return "dummy"


def test_path_step_is_abstract() -> None:
    with pytest.raises(TypeError):
        PathStep()


def test_getattrstep_empty_name() -> None:
    with pytest.raises(ValueError):
        GetAttrStep("")


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
