#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


import pytest

from pyvider.cty import (
    CtyBool,
    CtyNumber,
    CtyObject,
    CtyString,
)
from pyvider.cty.exceptions import (
    CtyAttributeValidationError,
    CtyValidationError,
    InvalidTypeError,
)


@pytest.mark.asyncio
async def test_object_init_empty() -> None:
    obj = CtyObject()
    assert obj.attribute_types == {}
    assert obj.optional_attributes == frozenset()


@pytest.mark.asyncio
async def test_object_init_with_attributes() -> None:
    obj = CtyObject(attribute_types={"name": CtyString(), "age": CtyNumber(), "active": CtyBool()})
    assert set(obj.attribute_types.keys()) == {"name", "age", "active"}
    assert isinstance(obj.attribute_types["name"], CtyString)
    assert obj.optional_attributes == frozenset()


@pytest.mark.asyncio
async def test_object_init_with_optional_attributes() -> None:
    obj = CtyObject(
        attribute_types={"name": CtyString(), "age": CtyNumber()},
        optional_attributes=frozenset(["age"]),
    )
    assert set(obj.attribute_types.keys()) == {"name", "age"}
    assert obj.optional_attributes == frozenset(["age"])


@pytest.mark.asyncio
async def test_object_init_invalid_attribute_type() -> None:
    with pytest.raises(InvalidTypeError):
        CtyObject(attribute_types={"name": CtyString(), "age": "not a type"})


@pytest.mark.asyncio
async def test_object_init_invalid_optional_attribute() -> None:
    obj = CtyObject(
        attribute_types={"name": CtyString(), "age": CtyNumber()},
        optional_attributes=frozenset(["unknown"]),
    )
    with pytest.raises(CtyValidationError, match="Unknown optional attributes: unknown"):
        obj.validate({"name": "test", "age": 1})


class TestCtyObjectValidation:
    def test_validate_success(self) -> None:
        obj_type = CtyObject({"name": CtyString(), "age": CtyNumber()})
        value = obj_type.validate({"name": "Alice", "age": 30})
        assert value.value["name"].value == "Alice"
        assert value.value["age"].value == 30

    def test_validate_missing_required_attribute(self) -> None:
        obj_type = CtyObject({"name": CtyString(), "age": CtyNumber()})
        with pytest.raises(CtyAttributeValidationError, match="Missing required attribute"):
            obj_type.validate({"name": "Alice"})

    def test_validate_optional_attribute(self) -> None:
        obj_type = CtyObject({"name": CtyString(), "age": CtyNumber()}, optional_attributes={"age"})
        value = obj_type.validate({"name": "Alice"})
        assert value.value["name"].value == "Alice"
        assert value.value["age"].is_null

    def test_validate_unknown_attribute(self) -> None:
        obj_type = CtyObject({"name": CtyString()})
        with pytest.raises(CtyAttributeValidationError, match="Unknown attributes: age"):
            obj_type.validate({"name": "Alice", "age": 30})

    def test_validate_null_attribute(self) -> None:
        obj_type = CtyObject({"name": CtyString()})
        with pytest.raises(CtyAttributeValidationError, match="Attribute cannot be null"):
            obj_type.validate({"name": None})

    def test_validate_attrs_object(self) -> None:
        import attr

        from pyvider.cty import CtyNumber, CtyObject, CtyString

        @attr.s(auto_attribs=True)
        class MyAttrsClass:
            name: str
            age: int

        attrs_instance = MyAttrsClass("Bob", 42)

        obj_type = CtyObject({"name": CtyString(), "age": CtyNumber()})
        value = obj_type.validate(attrs_instance)
        assert value.value["name"].value == "Bob"
        assert value.value["age"].value == 42


class TestCtyObjectMethods:
    def setup_method(self) -> None:
        self.obj_type = CtyObject({"name": CtyString(), "age": CtyNumber()})
        self.obj_value = self.obj_type.validate({"name": "Alice", "age": 30})

    def test_get_attribute(self) -> None:
        assert self.obj_type.get_attribute(self.obj_value, "name").value == "Alice"

    def test_get_missing_attribute(self) -> None:
        with pytest.raises(CtyAttributeValidationError):
            self.obj_type.get_attribute(self.obj_value, "address")

    def test_has_attribute(self) -> None:
        assert self.obj_type.has_attribute("name")
        assert not self.obj_type.has_attribute("address")

    def test_equal(self) -> None:
        obj_type2 = CtyObject({"name": CtyString(), "age": CtyNumber()})
        obj_type3 = CtyObject({"name": CtyString()})
        assert self.obj_type.equal(obj_type2)
        assert not self.obj_type.equal(obj_type3)

    def test_usable_as(self) -> None:
        obj_type2 = CtyObject({"name": CtyString()})
        obj_type3 = CtyObject({"name": CtyString(), "age": CtyString()})
        assert self.obj_type.usable_as(obj_type2)
        assert not self.obj_type.usable_as(obj_type3)


# 🌊🪢🔚
