#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


import pytest

from pyvider.cty import (
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyObject,
    CtyString,
    CtyTuple,
    CtyValue,
)
from pyvider.cty.exceptions import AttributePathError
from pyvider.cty.path import (
    CtyPath,
    GetAttrStep,
    IndexStep,
    KeyStep,
    PathStep,
)


class TestPathStep:
    def test_path_step_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            PathStep()


class TestGetAttrStep:
    def test_get_attr_step_init(self) -> None:
        attr_step = GetAttrStep("property")
        assert attr_step.name == "property"

    def test_apply_to_object(self) -> None:
        obj_type = CtyObject({"name": CtyString()})
        obj_value = obj_type.validate({"name": "Alice"})
        step = GetAttrStep("name")
        result = step.apply(obj_value)
        assert result.value == "Alice"

    def test_apply_to_null(self) -> None:
        step = GetAttrStep("name")
        with pytest.raises(AttributePathError):
            step.apply(CtyValue.null(CtyObject({"name": CtyString()})))

    def test_apply_to_non_object(self) -> None:
        step = GetAttrStep("name")
        with pytest.raises(AttributePathError):
            step.apply(CtyString().validate("not an object"))

    def test_apply_type_to_object(self) -> None:
        obj_type = CtyObject({"name": CtyString()})
        step = GetAttrStep("name")
        result = step.apply_type(obj_type)
        assert result == CtyString()

    def test_apply_type_to_non_object(self) -> None:
        step = GetAttrStep("name")
        with pytest.raises(AttributePathError):
            step.apply_type(CtyString())

    def test_apply_type_to_missing_attr(self) -> None:
        obj_type = CtyObject({"age": CtyString()})
        step = GetAttrStep("name")
        with pytest.raises(AttributePathError):
            step.apply_type(obj_type)


class TestIndexStep:
    def test_apply_to_list(self) -> None:
        list_type = CtyList(element_type=CtyString())
        list_value = list_type.validate(["a", "b", "c"])
        step = IndexStep(1)
        result = step.apply(list_value)
        assert result.value == "b"

    def test_apply_to_tuple(self) -> None:
        tuple_type = CtyTuple((CtyString(), CtyString()))
        tuple_value = tuple_type.validate(("a", "b"))
        step = IndexStep(1)
        result = step.apply(tuple_value)
        assert result.value == "b"

    def test_apply_to_null(self) -> None:
        step = IndexStep(0)
        with pytest.raises(AttributePathError):
            step.apply(CtyValue.null(CtyList(element_type=CtyString())))

    def test_apply_to_unknown(self) -> None:
        step = IndexStep(0)
        result = step.apply(CtyValue.unknown(CtyList(element_type=CtyString())))
        assert result.is_unknown

    def test_apply_to_non_collection(self) -> None:
        step = IndexStep(0)
        with pytest.raises(AttributePathError):
            step.apply(CtyString().validate("not a collection"))

    def test_apply_type_to_list(self) -> None:
        list_type = CtyList(element_type=CtyString())
        step = IndexStep(0)
        result = step.apply_type(list_type)
        assert result == CtyString()

    def test_apply_type_to_tuple(self) -> None:
        tuple_type = CtyTuple((CtyString(), CtyString()))
        step = IndexStep(1)
        result = step.apply_type(tuple_type)
        assert result == CtyString()

    def test_apply_type_to_dynamic(self) -> None:
        step = IndexStep(0)
        result = step.apply_type(CtyDynamic())
        assert result == CtyDynamic()

    def test_apply_type_to_non_collection(self) -> None:
        step = IndexStep(0)
        with pytest.raises(AttributePathError):
            step.apply_type(CtyString())

    def test_apply_type_to_tuple_out_of_bounds(self) -> None:
        tuple_type = CtyTuple((CtyString(),))
        step = IndexStep(1)
        with pytest.raises(AttributePathError):
            step.apply_type(tuple_type)


class TestKeyStep:
    def test_apply_to_map(self) -> None:
        map_type = CtyMap(element_type=CtyString())
        map_value = map_type.validate({"name": "Alice"})
        step = KeyStep("name")
        result = step.apply(map_value)
        assert result.value == "Alice"

    def test_apply_to_null(self) -> None:
        step = KeyStep("name")
        with pytest.raises(AttributePathError):
            step.apply(CtyValue.null(CtyMap(element_type=CtyString())))

    def test_apply_to_unknown(self) -> None:
        step = KeyStep("name")
        result = step.apply(CtyValue.unknown(CtyMap(element_type=CtyString())))
        assert result.is_unknown

    def test_apply_to_non_map(self) -> None:
        step = KeyStep("name")
        with pytest.raises(AttributePathError):
            step.apply(CtyString().validate("not a map"))

    def test_apply_type_to_map(self) -> None:
        map_type = CtyMap(element_type=CtyString())
        step = KeyStep("name")
        result = step.apply_type(map_type)
        assert result == CtyString()

    def test_apply_type_to_dynamic(self) -> None:
        step = KeyStep("name")
        result = step.apply_type(CtyDynamic())
        assert result == CtyDynamic()

    def test_apply_type_to_non_map(self) -> None:
        step = KeyStep("name")
        with pytest.raises(AttributePathError):
            step.apply_type(CtyString())

    def test_apply_type_with_invalid_key(self) -> None:
        map_type = CtyMap(element_type=CtyString())
        step = KeyStep(123)
        with pytest.raises(AttributePathError):
            step.apply_type(map_type)


class TestPath:
    def test_path_init_empty(self) -> None:
        path = CtyPath.empty()
        assert path.steps == []

    def test_path_init_with_steps(self) -> None:
        path = CtyPath([GetAttrStep("user"), IndexStep(0)])
        assert len(path.steps) == 2

    def test_path_child_methods(self) -> None:
        path = CtyPath.get_attr("user").index_step(0).key_step("name")
        assert len(path.steps) == 3
        assert isinstance(path.steps[0], GetAttrStep)
        assert isinstance(path.steps[1], IndexStep)
        assert isinstance(path.steps[2], KeyStep)

    def test_apply_path(self) -> None:
        obj_type = CtyObject({"users": CtyList(element_type=CtyObject({"name": CtyString()}))})
        obj_value = obj_type.validate({"users": [{"name": "Alice"}, {"name": "Bob"}]})
        path = CtyPath.get_attr("users").index_step(1).child("name")
        result = path.apply_path(obj_value)
        assert result.value == "Bob"

    def test_apply_path_to_non_value(self) -> None:
        path = CtyPath.get_attr("a")
        with pytest.raises(AttributePathError):
            path.apply_path("not a cty value")

    def test_apply_path_type(self) -> None:
        obj_type = CtyObject({"users": CtyList(element_type=CtyObject({"name": CtyString()}))})
        path = CtyPath.get_attr("users").index_step(1).child("name")
        result = path.apply_path_type(obj_type)
        assert result == CtyString()

    def test_string_representation(self) -> None:
        path = CtyPath.get_attr("users").index_step(1).key_step("name")
        assert str(path) == "users[1]['name']"


class TestCtyPathStringRepresentation:
    """
    Tests for the human-readable string representation of CtyPath objects,
    which is crucial for clear diagnostic messages.
    """

    def test_empty_path_representation(self) -> None:
        path = CtyPath.empty()
        assert str(path) == "(root)"

    def test_simple_attribute_path(self) -> None:
        path = CtyPath.get_attr("user")
        assert str(path) == "user"

    def test_complex_mixed_path(self) -> None:
        path = CtyPath.get_attr("users").index_step(0).child("addresses").key_step("home").child("zip")
        assert str(path) == "users[0].addresses['home'].zip"

    def test_path_starting_with_index(self) -> None:
        path = CtyPath.index(0).child("name")
        assert str(path) == "[0].name"

    def test_path_with_only_key(self) -> None:
        path = CtyPath.key("config-key")
        assert str(path) == "['config-key']"


# 🌊🪢🔚
