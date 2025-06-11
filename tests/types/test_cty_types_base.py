from typing import Any

import pytest

from pyvider.cty.exceptions import CtyValidationError
from pyvider.cty.types.base import CtyType
from pyvider.cty.types.collections.list import CtyList
from pyvider.cty.types.collections.map import CtyMap
from pyvider.cty.types.collections.set import CtySet
from pyvider.cty.types.primitives.string import CtyString
from pyvider.cty.types.structural.object import CtyObject
from pyvider.cty.types.structural.tuple import CtyTuple

# CtyValue is forward referenced in type hints in ConcreteCtyType,
# but its actual import is only needed for type checking or if instantiated.
# For now, we only need `Any` from typing.
# from pyvider.cty.values.base import CtyValue


class ConcreteCtyType(CtyType[str]):
    ctype = "concrete"

    def validate(self, value: Any) -> "CtyValue[str]":  # type: ignore
        # This is a simplified CtyValue for testing, actual CtyValue is more complex
        if isinstance(value, str):
            # Actual CtyValue would be `from pyvider.cty.values import CtyValue`
            # For this test, we can mock it or use a simpler structure if CtyValue is not essential
            # For now, assuming CtyValue can be named for type hints and not instantiated.
            # If instantiation is needed, CtyValue must be imported.
            # Let's assume it's a forward reference for now, and tests might fail if it needs instantiation.
            # For the purpose of testing CtyType methods, we might not need full CtyValue objects.
            return {"type": self, "value": value}  # type: ignore
        raise CtyValidationError(f"Invalid value for ConcreteCtyType: {value}")

    def equal(self, other: CtyType[str]) -> bool:  # type: ignore
        return isinstance(other, ConcreteCtyType)

    def usable_as(self, other: CtyType[str]) -> bool:  # type: ignore
        return isinstance(other, ConcreteCtyType)


class TestCtyTypeBase:
    def test_from_raw_validation_error(self) -> None:
        """Test CtyType.from_raw raises CtyValidationError for non-CtyType instances."""
        with pytest.raises(CtyValidationError) as excinfo:
            ConcreteCtyType.from_raw(123)
        assert "Cannot convert int to ConcreteCtyType." in str(excinfo.value)

    def test_is_collection_type_false(self) -> None:
        """Test is_collection_type returns False for a non-collection type."""
        assert not ConcreteCtyType().is_collection_type()

    def test_is_set_type_false(self) -> None:
        """Test is_set_type returns False for a non-set type."""
        assert not ConcreteCtyType().is_set_type()
        assert not CtyList(
            element_type=CtyString()
        ).is_set_type()  # Test with another collection type

    def test_is_structured_type_false(self) -> None:
        """Test is_structured_type returns False for a non-structured type."""
        assert not ConcreteCtyType().is_structured_type()
        assert not CtyList(
            element_type=CtyString()
        ).is_structured_type()  # Test with a collection type

    def test_is_tuple_type_false(self) -> None:
        """Test is_tuple_type returns False for a non-tuple type."""
        assert not ConcreteCtyType().is_tuple_type()
        assert not CtyObject(
            {"attr": CtyString()}
        ).is_tuple_type()  # Test with another structured type

    def test_eq_not_implemented(self) -> None:
        """Test CtyType.__eq__ returns NotImplemented for non-CtyType comparison, leading to False."""
        # Check direct call if possible, or the resulting False from the operator
        assert ConcreteCtyType().__eq__(123) is NotImplemented
        assert (ConcreteCtyType() == 123) is False

    def test_str_representation(self) -> None:
        """Test the __str__ representation of a CtyType."""
        assert str(ConcreteCtyType()) == "ConcreteCtyType"

    def test_hash_representation(self) -> None:
        """Test the __hash__ representation of a CtyType."""
        # Basic check, hash depends on repr
        assert hash(ConcreteCtyType()) == hash(repr(ConcreteCtyType()))

    # Tests for already covered methods, ensuring they still work with a concrete subclass
    def test_is_primitive_type_false_for_concrete(self) -> None:
        assert not ConcreteCtyType().is_primitive_type()

    def test_is_list_type_false_for_concrete(self) -> None:
        assert not ConcreteCtyType().is_list_type()

    def test_is_map_type_false_for_concrete(self) -> None:
        assert not ConcreteCtyType().is_map_type()

    def test_is_object_type_false_for_concrete(self) -> None:
        assert not ConcreteCtyType().is_object_type()

    def test_from_raw_with_instance(self) -> None:
        instance = ConcreteCtyType()
        assert ConcreteCtyType.from_raw(instance) is instance

    def test_validate_concrete_type_valid(self) -> None:
        instance = ConcreteCtyType()
        val_dict = instance.validate("hello")
        assert isinstance(val_dict, dict)  # Changed from CtyValue
        assert val_dict["value"] == "hello"  # Changed from val.value
        assert val_dict["type"] == instance  # Changed from val.type

    def test_validate_concrete_type_invalid(self) -> None:
        instance = ConcreteCtyType()
        with pytest.raises(CtyValidationError):
            instance.validate(123)

    def test_equal_concrete_type(self) -> None:
        assert ConcreteCtyType().equal(ConcreteCtyType())
        assert not ConcreteCtyType().equal(CtyString())  # type: ignore

    def test_usable_as_concrete_type(self) -> None:
        assert ConcreteCtyType().usable_as(ConcreteCtyType())
        assert not ConcreteCtyType().usable_as(CtyString())  # type: ignore

    def test_repr_concrete_type(self) -> None:
        assert repr(ConcreteCtyType()) == "ConcreteCtyType()"


class TestActualTypesReturnValues:
    """Test the is_X_type methods for actual Cty types."""

    def test_is_primitive_types(self) -> None:
        assert CtyString().is_primitive_type()
        assert not CtyList(element_type=CtyString()).is_primitive_type()

    def test_is_collection_types(self) -> None:
        assert CtyList(element_type=CtyString()).is_collection_type()
        assert CtyMap(key_type=CtyString(), value_type=CtyString()).is_collection_type()
        assert CtySet(element_type=CtyString()).is_collection_type()
        assert not CtyString().is_collection_type()
        assert not CtyObject({}).is_collection_type()
        assert not CtyTuple(()).is_collection_type()

    def test_is_list_type(self) -> None:
        assert CtyList(element_type=CtyString()).is_list_type()
        assert not CtyString().is_list_type()
        assert not CtyMap(key_type=CtyString(), value_type=CtyString()).is_list_type()
        assert not CtySet(element_type=CtyString()).is_list_type()
        assert not CtyObject({}).is_list_type()
        assert not CtyTuple(()).is_list_type()

    def test_is_map_type(self) -> None:
        assert CtyMap(key_type=CtyString(), value_type=CtyString()).is_map_type()
        assert not CtyString().is_map_type()
        assert not CtyList(element_type=CtyString()).is_map_type()
        assert not CtySet(element_type=CtyString()).is_map_type()
        assert not CtyObject({}).is_map_type()
        assert not CtyTuple(()).is_map_type()

    def test_is_set_type(self) -> None:
        assert CtySet(element_type=CtyString()).is_set_type()
        assert not CtyString().is_set_type()
        assert not CtyList(element_type=CtyString()).is_set_type()
        assert not CtyMap(key_type=CtyString(), value_type=CtyString()).is_set_type()
        assert not CtyObject({}).is_set_type()
        assert not CtyTuple(()).is_set_type()

    def test_is_structured_types(self) -> None:
        assert CtyObject({}).is_structured_type()
        assert CtyTuple(()).is_structured_type()
        assert not CtyString().is_structured_type()
        assert not CtyList(element_type=CtyString()).is_structured_type()
        assert not CtyMap(
            key_type=CtyString(), value_type=CtyString()
        ).is_structured_type()
        assert not CtySet(element_type=CtyString()).is_structured_type()

    def test_is_object_type(self) -> None:
        assert CtyObject({}).is_object_type()
        assert not CtyString().is_object_type()
        assert not CtyList(element_type=CtyString()).is_object_type()
        assert not CtyMap(key_type=CtyString(), value_type=CtyString()).is_object_type()
        assert not CtySet(element_type=CtyString()).is_object_type()
        assert not CtyTuple(()).is_object_type()

    def test_is_tuple_type(self) -> None:
        assert CtyTuple(()).is_tuple_type()
        assert not CtyString().is_tuple_type()
        assert not CtyList(element_type=CtyString()).is_tuple_type()
        assert not CtyMap(key_type=CtyString(), value_type=CtyString()).is_tuple_type()
        assert not CtySet(element_type=CtyString()).is_tuple_type()
        assert not CtyObject({}).is_tuple_type()


from typing import Any

# Import CtyValue properly for type hints and potential instantiation
from pyvider.cty.values import CtyValue


# Define dummy types at module level to resolve NameError
class _TypeA(CtyType[Any]):
    def validate(self, value: Any) -> CtyValue[Any]:
        return CtyValue(self, value)  # type: ignore

    def equal(self, other: CtyType[Any]) -> bool:
        return isinstance(other, _TypeA)

    def usable_as(self, other: CtyType[Any]) -> bool:
        return isinstance(other, _TypeA | _TypeB)


class _TypeB(CtyType[Any]):
    def validate(self, value: Any) -> CtyValue[Any]:
        return CtyValue(self, value)  # type: ignore

    def equal(self, other: CtyType[Any]) -> bool:
        return isinstance(other, _TypeB)

    def usable_as(self, other: CtyType[Any]) -> bool:
        return isinstance(other, _TypeB)


class _TypeC(CtyType[Any]):
    def validate(self, value: Any) -> CtyValue[Any]:
        return CtyValue(self, value)  # type: ignore

    def equal(self, other: CtyType[Any]) -> bool:
        return isinstance(other, _TypeC)

    def usable_as(self, other: CtyType[Any]) -> bool:
        return isinstance(other, _TypeC)


@pytest.fixture
def type_a():
    return _TypeA()


@pytest.fixture
def type_b():
    return _TypeB()


@pytest.fixture
def type_c():
    return _TypeC()


def test_ctytype_equality_and_usability(type_a, type_b, type_c) -> None:
    # Test equality: __eq__ delegates to equal method
    assert type_a == type_a  # Equal to itself
    assert type_a != type_b  # Not equal to a different type

    # Test usability: usable_as method
    assert type_a.usable_as(type_a)  # Usable as itself
    assert type_a.usable_as(type_b)  # TypeA is designed to be usable as TypeB
    assert not type_b.usable_as(type_a)  # TypeB is not designed to be usable as TypeA
    assert not type_a.usable_as(type_c)  # Not usable as an unrelated type TypeC

    # Test __eq__ with non-CtyType returns NotImplemented
    assert type_a.__eq__("not a cty type") is NotImplemented
    assert (type_a == "not a cty type") is False

    # Test __repr__
    assert "TypeA" in repr(type_a)

    # Test __str__
    assert "TypeA" in str(type_a)

    # Test __hash__
    assert isinstance(hash(type_a), int)

    # Test is_primitive_type default
    assert not type_a.is_primitive_type()
    assert not type_b.is_primitive_type()
    assert not type_c.is_primitive_type()

    # Test is_collection_type default
    assert not type_a.is_collection_type()

    # Test is_list_type default
    assert not type_a.is_list_type()

    # Test is_map_type default
    assert not type_a.is_map_type()

    # Test is_set_type default
    assert not type_a.is_set_type()

    # Test is_structured_type default
    assert not type_a.is_structured_type()

    # Test is_object_type default
    assert not type_a.is_object_type()

    # Test is_tuple_type default
    assert not type_a.is_tuple_type()

    # Test from_raw
    with pytest.raises(CtyValidationError, match="Cannot convert str to _TypeA."):
        type_a.__class__.from_raw("test")  # type: ignore

    assert type_a.__class__.from_raw(type_a) is type_a  # type: ignore

    # Test validate (dummy implementation)
    assert type_a.validate("any").value == "any"


# Add a simple test for a type that overrides is_primitive_type
class MyPrimitiveType(CtyType[str]):
    def validate(self, value: Any) -> CtyValue[str]:
        return CtyValue(self, str(value))  # type: ignore

    def equal(self, other: CtyType[str]) -> bool:
        return isinstance(other, MyPrimitiveType)

    def usable_as(self, other: CtyType[str]) -> bool:
        return isinstance(other, MyPrimitiveType)

    def is_primitive_type(self) -> bool:
        return True


def test_my_primitive_type() -> None:
    primitive = MyPrimitiveType()
    assert primitive.is_primitive_type()
    assert not primitive.is_collection_type()
    assert not primitive.is_structured_type()


# Add a simple test for a type that overrides is_collection_type and is_list_type
class MyListType(CtyType[list]):
    def __init__(self, element_type: CtyType[Any]) -> None:
        self.element_type = element_type
        super().__init__()

    def validate(self, value: Any) -> CtyValue[list]:
        return CtyValue(self, list(value))  # type: ignore

    def equal(self, other: CtyType[list]) -> bool:
        return isinstance(other, MyListType) and self.element_type.equal(
            other.element_type
        )  # type: ignore

    def usable_as(self, other: CtyType[list]) -> bool:
        return isinstance(other, MyListType) and self.element_type.usable_as(
            other.element_type
        )  # type: ignore

    def is_collection_type(self) -> bool:
        return True

    def is_list_type(self) -> bool:
        return True


def test_my_list_type() -> None:
    list_type = MyListType(CtyString())
    assert list_type.is_collection_type()
    assert list_type.is_list_type()
    assert not list_type.is_primitive_type()
    assert not list_type.is_map_type()
    assert not list_type.is_set_type()
    assert not list_type.is_structured_type()
    assert not list_type.is_object_type()
    assert not list_type.is_tuple_type()


# Add a simple test for a type that overrides is_map_type
class MyMapType(CtyType[dict]):
    def __init__(self, value_type: CtyType[Any]) -> None:
        self.value_type = value_type
        super().__init__()

    def validate(self, value: Any) -> CtyValue[dict]:
        return CtyValue(self, dict(value))  # type: ignore

    def equal(self, other: CtyType[dict]) -> bool:
        return isinstance(other, MyMapType) and self.value_type.equal(other.value_type)  # type: ignore

    def usable_as(self, other: CtyType[dict]) -> bool:
        return isinstance(other, MyMapType) and self.value_type.usable_as(
            other.value_type
        )  # type: ignore

    def is_collection_type(self) -> bool:
        return True

    def is_map_type(self) -> bool:
        return True


def test_my_map_type() -> None:
    map_type = MyMapType(CtyString())
    assert map_type.is_collection_type()
    assert map_type.is_map_type()
    assert not map_type.is_primitive_type()
    assert not map_type.is_list_type()
    assert not map_type.is_set_type()
    assert not map_type.is_structured_type()
    assert not map_type.is_object_type()
    assert not map_type.is_tuple_type()


# Add a simple test for a type that overrides is_set_type
class MySetType(CtyType[set]):
    def __init__(self, element_type: CtyType[Any]) -> None:
        self.element_type = element_type
        super().__init__()

    def validate(self, value: Any) -> CtyValue[set]:
        return CtyValue(self, set(value))  # type: ignore

    def equal(self, other: CtyType[set]) -> bool:
        return isinstance(other, MySetType) and self.element_type.equal(
            other.element_type
        )  # type: ignore

    def usable_as(self, other: CtyType[set]) -> bool:
        return isinstance(other, MySetType) and self.element_type.usable_as(
            other.element_type
        )  # type: ignore

    def is_collection_type(self) -> bool:
        return True

    def is_set_type(self) -> bool:
        return True


def test_my_set_type() -> None:
    set_type = MySetType(CtyString())
    assert set_type.is_collection_type()
    assert set_type.is_set_type()
    assert not set_type.is_primitive_type()
    assert not set_type.is_list_type()
    assert not set_type.is_map_type()
    assert not set_type.is_structured_type()
    assert not set_type.is_object_type()
    assert not set_type.is_tuple_type()


# Add a simple test for a type that overrides is_structured_type and is_object_type
class MyObjectType(CtyType[object]):
    def __init__(self, attr_types: dict[str, CtyType[Any]]) -> None:
        self.attr_types = attr_types
        super().__init__()

    def validate(self, value: Any) -> CtyValue[object]:
        return CtyValue(self, value)  # type: ignore

    def equal(self, other: CtyType[object]) -> bool:
        return isinstance(other, MyObjectType)  # type: ignore

    def usable_as(self, other: CtyType[object]) -> bool:
        return isinstance(other, MyObjectType)  # type: ignore

    def is_structured_type(self) -> bool:
        return True

    def is_object_type(self) -> bool:
        return True


def test_my_object_type() -> None:
    obj_type = MyObjectType({"name": CtyString()})
    assert obj_type.is_structured_type()
    assert obj_type.is_object_type()
    assert not obj_type.is_primitive_type()
    assert not obj_type.is_collection_type()
    assert not obj_type.is_list_type()
    assert not obj_type.is_map_type()
    assert not obj_type.is_set_type()
    assert not obj_type.is_tuple_type()


# Add a simple test for a type that overrides is_tuple_type
class MyTupleType(CtyType[tuple]):
    def __init__(self, element_types: list[CtyType[Any]]) -> None:
        self.element_types = element_types
        super().__init__()

    def validate(self, value: Any) -> CtyValue[tuple]:
        return CtyValue(self, tuple(value))  # type: ignore

    def equal(self, other: CtyType[tuple]) -> bool:
        return isinstance(other, MyTupleType)  # type: ignore

    def usable_as(self, other: CtyType[tuple]) -> bool:
        return isinstance(other, MyTupleType)  # type: ignore

    def is_structured_type(self) -> bool:
        return True

    def is_tuple_type(self) -> bool:
        return True


def test_my_tuple_type() -> None:
    tuple_type = MyTupleType([CtyString(), CtyString()])
    assert tuple_type.is_structured_type()
    assert tuple_type.is_tuple_type()
    assert not tuple_type.is_primitive_type()
    assert not tuple_type.is_collection_type()
    assert not tuple_type.is_list_type()
    assert not tuple_type.is_map_type()
    assert not tuple_type.is_set_type()
    assert not tuple_type.is_object_type()


# Test default __repr__ and __str__ if not overridden by concrete types for some reason
class MinimalCtyType(CtyType[Any]):
    def validate(self, value: Any) -> CtyValue[Any]:
        raise NotImplementedError

    def equal(self, other: CtyType[Any]) -> bool:
        raise NotImplementedError

    def usable_as(self, other: CtyType[Any]) -> bool:
        raise NotImplementedError


def test_minimal_cty_type_representations() -> None:
    minimal_type = MinimalCtyType()
    assert repr(minimal_type) == "MinimalCtyType()"
    assert str(minimal_type) == "MinimalCtyType"
    # Also test hash, which depends on repr
    assert hash(minimal_type) == hash("MinimalCtyType()")


ConcreteCtyType.ctype = "concrete"  # Assign after class definition for linters


def test_ctype_classvar() -> None:
    assert ConcreteCtyType.ctype == "concrete"
    # Ensure base CtyType still has None
    assert CtyType.ctype is None


# Ensure that CtyValue can be imported and used (it's in the return type hint)
def test_cty_value_importable() -> None:
    from pyvider.cty.values import CtyValue  # noqa F401 - unused but checks import

    pass


# Test CtyType.from_raw with a CtyType subclass instance
def test_from_raw_with_subclass_instance() -> None:
    instance = ConcreteCtyType()
    assert ConcreteCtyType.from_raw(instance) is instance

    with pytest.raises(CtyValidationError) as excinfo:
        CtyString.from_raw(ConcreteCtyType())  # type: ignore
    assert "Cannot convert ConcreteCtyType to CtyString." in str(excinfo.value)
