from decimal import Decimal
from typing import Any

import pytest

from pyvider.cty.exceptions import (
    CtyAttributeValidationError,
    CtyValidationError,
    InvalidTypeError,
)
from pyvider.cty.types.base import CtyType
from pyvider.cty.types.primitives import CtyBool, CtyNumber, CtyString
from pyvider.cty.types.structural.dynamic import CtyDynamic
from pyvider.cty.types.structural.object import CtyObject
from pyvider.cty.values import CtyValue


# --- Fixtures ---
@pytest.fixture
def string_type() -> CtyString:
    return CtyString()


@pytest.fixture
def number_type() -> CtyNumber:
    return CtyNumber()


@pytest.fixture
def bool_type() -> CtyBool:
    return CtyBool()


@pytest.fixture
def basic_object_type(string_type: CtyString, number_type: CtyNumber) -> CtyObject:
    return CtyObject(attribute_types={"name": string_type, "age": number_type})


@pytest.fixture
def object_with_optional_type(
    string_type: CtyString, number_type: CtyNumber
) -> CtyObject:
    return CtyObject(
        attribute_types={
            "id": number_type,
            "status": string_type,
            "description": string_type,
        },
        optional_attributes=frozenset({"status", "description"}),
    )


# --- Tests ---


class TestCtyObjectAttrsPostInit:
    def test_post_init_invalid_attribute_types_dict(
        self, string_type: CtyString
    ) -> None:
        """Test __attrs_post_init__ with attribute_types not being a dict."""
        with pytest.raises(
            InvalidTypeError, match="Expected dict for attribute_types, got list"
        ):
            CtyObject(attribute_types=[("name", string_type)])  # type: ignore

    def test_post_init_invalid_attribute_type_item(self) -> None:
        """Test __attrs_post_init__ with an item in attribute_types not being a CtyType."""
        with pytest.raises(
            CtyAttributeValidationError, match="Invalid types for attributes: age"
        ):
            CtyObject(attribute_types={"name": CtyString(), "age": 123})  # type: ignore

    def test_post_init_unknown_optional_attribute(self, string_type: CtyString) -> None:
        """Test __attrs_post_init__ with an optional attribute not in attribute_types."""
        with pytest.raises(
            CtyAttributeValidationError,
            match="Unknown optional attributes: unknown_opt",
        ):
            CtyObject(
                attribute_types={"name": string_type},
                optional_attributes=frozenset({"unknown_opt"}),
            )

    def test_post_init_success(
        self, string_type: CtyString, number_type: CtyNumber
    ) -> None:
        """Test successful __attrs_post_init__."""
        obj_type = CtyObject(
            attribute_types={
                "name": string_type,
                "age": number_type,
                "city": string_type,
            },
            optional_attributes=frozenset({"city"}),
        )
        assert len(obj_type.attribute_types) == 3
        assert "city" in obj_type.optional_attributes


class TestCtyObjectValidate:
    def test_validate_none_input_returns_null_value(
        self, basic_object_type: CtyObject
    ) -> None:
        """Test validate with None input returns a null CtyValue."""
        cty_val = basic_object_type.validate(None)
        assert isinstance(cty_val, CtyValue)
        assert cty_val.type == basic_object_type
        assert cty_val.is_null
        assert cty_val.value is None

    def test_validate_ctyvalue_matching_type(
        self,
        basic_object_type: CtyObject,
        string_type: CtyString,
        number_type: CtyNumber,
    ) -> None:
        """Test validate with a CtyValue of the exact same object type."""
        original_value_dict = {
            "name": string_type.validate("Alice"),
            "age": number_type.validate(30),
        }
        original_cty_value = CtyValue(
            vtype=basic_object_type, value=original_value_dict
        )

        validated_value = basic_object_type.validate(original_cty_value)
        assert validated_value is original_cty_value  # Should return the same instance

    def test_validate_ctyvalue_unknown_and_usable(
        self, basic_object_type: CtyObject
    ) -> None:
        """Test validate with an unknown CtyValue of a usable type."""
        # Assuming basic_object_type is usable as itself for unknown propagation
        unknown_object_val = CtyValue.unknown(basic_object_type)
        validated_val = basic_object_type.validate(unknown_object_val)
        assert validated_val.is_unknown
        assert validated_val.type == basic_object_type

    def test_validate_ctyvalue_unusable_type_unwraps_and_fails(
        self, basic_object_type: CtyObject, string_type: CtyString
    ) -> None:
        """Test CtyValue of a completely unrelated type that is not usable_as."""
        # e.g. CtyObject schema trying to validate CtyValue(CtyString, "foo")
        unrelated_cty_value = string_type.validate(
            "foo"
        )  # This is CtyValue(CtyString, "foo")
        with pytest.raises(CtyValidationError, match="Expected a dictionary, got str"):
            basic_object_type.validate(unrelated_cty_value)

    def test_validate_ctyvalue_known_different_compatible_type_unwraps(
        self, string_type: CtyString, number_type: CtyNumber
    ) -> None:
        """Test CtyValue of different but compatible object type unwraps and revalidates."""
        type1_schema = {"name": string_type, "age": number_type}
        type1 = CtyObject(type1_schema)

        # Type2 is compatible if it has a subset of type1's optional fields or same required fields
        # For this test, let's make type2 identical for simplicity of value,
        # but it's a different instance of CtyObject.
        type2_schema = {"name": string_type, "age": number_type}
        type2 = CtyObject(type2_schema)  # Different instance, but compatible

        # Ensure they are equal but not same instance
        assert type1.equal(type2)
        assert type1 is not type2
        assert type1.usable_as(type2)  # type1 is usable as type2 (same schema)

        original_value_dict = {
            "name": string_type.validate("Bob"),
            "age": number_type.validate(40),
        }
        cty_value_of_type2 = CtyValue(vtype=type2, value=original_value_dict)

        # Validate CtyValue(type2) against type1
        validated_against_type1 = type1.validate(cty_value_of_type2)
        assert isinstance(validated_against_type1, CtyValue)
        assert validated_against_type1.type == type1  # Should now be of type1
        assert validated_against_type1.value["name"].value == "Bob"
        assert validated_against_type1.value["age"].value == 40

    def test_validate_input_not_dict_or_none_or_ctyvalue(
        self, basic_object_type: CtyObject
    ) -> None:
        """Test validate raises error for input that is not dict, None, or CtyValue."""
        with pytest.raises(CtyValidationError, match="Expected a dictionary, got list"):
            basic_object_type.validate(["a", "b"])
        with pytest.raises(CtyValidationError, match="Expected a dictionary, got int"):
            basic_object_type.validate(123)

    def test_validate_missing_required_attribute(
        self, basic_object_type: CtyObject
    ) -> None:
        """Test validate raises error if a required attribute is missing."""
        with pytest.raises(CtyValidationError, match="Missing required attribute: age"):
            basic_object_type.validate({"name": "Alice"})

    def test_validate_unknown_attribute(self, basic_object_type: CtyObject) -> None:
        """Test validate raises error for an unknown attribute."""
        with pytest.raises(CtyValidationError, match="Unknown attributes: city"):
            basic_object_type.validate({"name": "Alice", "age": 30, "city": "London"})

    def test_validate_optional_attribute_missing(
        self, object_with_optional_type: CtyObject, number_type: CtyNumber
    ) -> None:
        """Test validate handles missing optional attributes (sets to null)."""
        # 'id' is required, 'status' and 'description' are optional
        input_data = {
            "id": number_type.validate(1)
        }  # 'status' and 'description' are missing
        cty_val = object_with_optional_type.validate(input_data)

        assert isinstance(cty_val, CtyValue)
        assert cty_val.value["id"].value == 1
        assert "status" in cty_val.value
        assert cty_val.value["status"].is_null
        assert "description" in cty_val.value
        assert cty_val.value["description"].is_null

    def test_validate_optional_attribute_present_and_none(
        self, object_with_optional_type: CtyObject, number_type: CtyNumber
    ) -> None:
        """Test validate handles optional attribute present as None (sets to null)."""
        input_data = {"id": number_type.validate(1), "status": None}
        cty_val = object_with_optional_type.validate(input_data)
        assert cty_val.value["status"].is_null

    def test_validate_required_attribute_is_none_raises(
        self, basic_object_type: CtyObject, string_type: CtyString
    ) -> None:
        """Test validate raises error if a required attribute is explicitly None."""
        with pytest.raises(
            CtyValidationError, match="Attribute 'age' is required and cannot be None"
        ):
            basic_object_type.validate(
                {"name": string_type.validate("Alice"), "age": None}
            )

    def test_validate_attribute_value_is_ctyvalue_compatible(
        self,
        basic_object_type: CtyObject,
        string_type: CtyString,
        number_type: CtyNumber,
    ) -> None:
        """Test attribute value is a CtyValue of a compatible type."""
        # basic_object_type expects age: CtyNumber
        # Pass a CtyValue of CtyDynamic holding a number for 'age'
        dynamic_age_val = CtyValue(vtype=CtyDynamic(), value=Decimal(25))

        input_data = {
            "name": string_type.validate("Compatible"),
            "age": dynamic_age_val,
        }
        # Expects error because CtyDynamic is not usable_as CtyNumber for attribute types
        with pytest.raises(CtyValidationError) as excinfo:
            basic_object_type.validate(input_data)
        assert "Invalid type for attribute 'age'" in str(excinfo.value)
        assert "expected number, got CtyDynamic" in str(excinfo.value)

    def test_validate_attribute_value_is_ctyvalue_incompatible(
        self, basic_object_type: CtyObject, string_type: CtyString
    ) -> None:
        """Test attribute value is a CtyValue of an incompatible type."""
        # basic_object_type expects age: CtyNumber. Pass CtyString for 'age'.
        string_age_val = string_type.validate("not-a-number")
        input_data = {
            "name": string_type.validate("Incompatible"),
            "age": string_age_val,
        }

        with pytest.raises(CtyValidationError) as excinfo:
            basic_object_type.validate(input_data)
        assert "Invalid type for attribute 'age'" in str(excinfo.value)
        assert "expected number, got string" in str(excinfo.value)

    def test_validate_attribute_value_validation_error(
        self, basic_object_type: CtyObject, string_type: CtyString
    ) -> None:
        """Test attribute value fails its own type validation."""
        input_data = {"name": string_type.validate("ErrorCase"), "age": "not-a-number"}
        with pytest.raises(CtyValidationError) as excinfo:
            basic_object_type.validate(input_data)
        assert "Invalid value for attribute 'age'" in str(excinfo.value)
        assert "Cannot convert string 'not-a-number' to number" in str(
            excinfo.value
        )  # From CtyNumber validation

    def test_validate_unexpected_error_during_attr_validation(
        self, basic_object_type: CtyObject, string_type: CtyString, mocker
    ) -> None:
        """Test handling of unexpected errors during an attribute's validate() call."""

        # Mock the 'validate' method of a custom type to raise an unexpected error
        class ExplodingType(CtyType):
            def validate(self, value: Any) -> "CtyValue":
                raise RuntimeError("Unexpected boom!")

            def equal(self, other: CtyType) -> bool:
                return False  # dummy

            def usable_as(self, other: CtyType) -> bool:
                return False  # dummy

        exploding_type_instance = ExplodingType()
        obj_type_with_exploding_attr = CtyObject(
            attribute_types={"name": string_type, "boom": exploding_type_instance}
        )

        input_data = {
            "name": string_type.validate("Panic"),
            "boom": "anything",
        }  # Value for boom will trigger RuntimeError

        with pytest.raises(CtyValidationError) as excinfo:
            obj_type_with_exploding_attr.validate(input_data)

        # Check for the specific format of the wrapped error.
        assert "Error validating attribute 'boom': Unexpected boom!" in str(
            excinfo.value
        )

    def test_validate_successful_object(
        self,
        object_with_optional_type: CtyObject,
        number_type: CtyNumber,
        string_type: CtyString,
    ) -> None:
        """Test successful validation of a complete object."""
        input_data = {
            "id": number_type.validate(101),
            "status": string_type.validate("active"),
            "description": string_type.validate("Full object"),
        }
        cty_val = object_with_optional_type.validate(input_data)
        assert isinstance(cty_val, CtyValue)
        assert cty_val.type == object_with_optional_type
        assert cty_val.value["id"].value == 101
        assert cty_val.value["status"].value == "active"
        assert cty_val.value["description"].value == "Full object"


# Initial focus on __attrs_post_init__ and validate.


class TestCtyObjectGetAttribute:
    def test_get_attribute_existing(
        self,
        basic_object_type: CtyObject,
        string_type: CtyString,
        number_type: CtyNumber,
    ) -> None:
        obj_value_dict = {
            "name": string_type.validate("Alice"),
            "age": number_type.validate(30),
        }
        cty_obj_value = CtyValue(vtype=basic_object_type, value=obj_value_dict)

        name_attr = basic_object_type.get_attribute(cty_obj_value, "name")
        assert name_attr.value == "Alice"
        age_attr = basic_object_type.get_attribute(cty_obj_value, "age")
        assert age_attr.value == 30

    def test_get_attribute_optional_missing_returns_null(
        self, object_with_optional_type: CtyObject, number_type: CtyNumber
    ) -> None:
        # 'status' is optional
        obj_value_dict = {"id": number_type.validate(1)}  # status is missing
        cty_obj_value = CtyValue(vtype=object_with_optional_type, value=obj_value_dict)

        status_attr = object_with_optional_type.get_attribute(cty_obj_value, "status")
        assert status_attr.is_null
        assert status_attr.type == object_with_optional_type.attribute_types["status"]

    def test_get_attribute_unknown_attribute_raises(
        self, basic_object_type: CtyObject
    ) -> None:
        cty_obj_value = basic_object_type.validate({"name": "Test", "age": 1})
        with pytest.raises(
            CtyAttributeValidationError, match="Unknown attribute: city"
        ):
            basic_object_type.get_attribute(cty_obj_value, "city")

    def test_get_attribute_from_null_value_raises(
        self, basic_object_type: CtyObject
    ) -> None:
        null_obj_value = CtyValue.null(basic_object_type)
        with pytest.raises(
            CtyAttributeValidationError, match="Cannot get attribute from null value"
        ):
            basic_object_type.get_attribute(null_obj_value, "name")

    def test_get_attribute_from_unknown_value_returns_unknown_attr(
        self, basic_object_type: CtyObject
    ) -> None:
        unknown_obj_value = CtyValue.unknown(basic_object_type)
        name_attr = basic_object_type.get_attribute(unknown_obj_value, "name")
        assert name_attr.is_unknown
        assert name_attr.type == basic_object_type.attribute_types["name"]

    def test_get_attribute_from_non_dict_value_raises(
        self, basic_object_type: CtyObject
    ) -> None:
        # Pass a raw non-dict value directly to get_attribute (if CtyValue unwrapping is bypassed)
        with pytest.raises(CtyValidationError, match="Expected a dictionary, got str"):
            basic_object_type.get_attribute("not-a-dict", "name")  # type: ignore

    def test_get_attribute_value_not_ctyvalue_is_wrapped(
        self, string_type: CtyString
    ) -> None:
        # Test case where the dict contains raw Python values instead of CtyValues
        obj_type = CtyObject(attribute_types={"raw_name": string_type})
        raw_dict_val = {"raw_name": "RawName"}  # not CtyValue(string_type, "RawName")

        # get_attribute should wrap it
        attr_val = obj_type.get_attribute(raw_dict_val, "raw_name")
        assert isinstance(attr_val, CtyValue)
        assert attr_val.type == string_type
        assert attr_val.value == "RawName"


class TestCtyObjectHelpersAndFlags:
    def test_required_attributes(
        self, basic_object_type: CtyObject, object_with_optional_type: CtyObject
    ) -> None:
        assert basic_object_type.required_attributes() == frozenset({"name", "age"})
        assert object_with_optional_type.required_attributes() == frozenset({"id"})

    def test_has_attribute(self, basic_object_type: CtyObject) -> None:
        assert basic_object_type.has_attribute("name")
        assert not basic_object_type.has_attribute("city")

    def test_type_flags(self, basic_object_type: CtyObject) -> None:
        assert basic_object_type.is_structured_type()
        assert basic_object_type.is_object_type()
        assert not basic_object_type.is_primitive_type()
        assert not basic_object_type.is_collection_type()


class TestCtyObjectEqualAndUsableAs:
    def test_equal_true_same_schema(self, string_type, number_type) -> None:
        obj1 = CtyObject(
            {"name": string_type, "age": number_type},
            optional_attributes=frozenset({"age"}),
        )
        obj2 = CtyObject(
            {"name": string_type, "age": number_type},
            optional_attributes=frozenset({"age"}),
        )
        assert obj1.equal(obj2)
        assert obj1 == obj2  # Tests __eq__ via CtyType base

    def test_equal_false_different_attr_names(self, string_type, number_type) -> None:
        obj1 = CtyObject({"name": string_type, "age": number_type})
        obj2 = CtyObject({"nombre": string_type, "edad": number_type})
        assert not obj1.equal(obj2)

    def test_equal_false_different_attr_types(self, string_type, number_type) -> None:
        obj1 = CtyObject({"name": string_type, "age": number_type})
        obj2 = CtyObject(
            {"name": string_type, "age": string_type}
        )  # age is string here
        assert not obj1.equal(obj2)

    def test_equal_false_different_optional_attrs(
        self, string_type, number_type
    ) -> None:
        obj1 = CtyObject(
            {"name": string_type, "age": number_type},
            optional_attributes=frozenset({"age"}),
        )
        obj2 = CtyObject(
            {"name": string_type, "age": number_type}
        )  # age is required here
        assert not obj1.equal(obj2)

    def test_equal_false_not_object_type(self, basic_object_type, string_type) -> None:
        assert not basic_object_type.equal(string_type)  # type: ignore

    def test_usable_as_true_identical(self, basic_object_type: CtyObject) -> None:
        assert basic_object_type.usable_as(basic_object_type)

    def test_usable_as_true_subset_attributes(self, string_type, number_type) -> None:
        # self_type has more attributes or same, all of other's attrs are present in self
        # and compatible type-wise and optionality-wise.
        self_type = CtyObject(
            {"name": string_type, "age": number_type, "city": string_type},
            optional_attributes=frozenset({"city"}),
        )
        other_type = CtyObject(
            {"name": string_type, "age": number_type}  # other has less attrs
        )
        assert self_type.usable_as(other_type)

    def test_usable_as_false_other_has_more_attributes(
        self, basic_object_type: CtyObject, string_type
    ) -> None:
        other_type = CtyObject(
            attribute_types={**basic_object_type.attribute_types, "extra": string_type}
        )
        assert not basic_object_type.usable_as(other_type)

    def test_usable_as_false_attr_type_incompatible(
        self, string_type, number_type
    ) -> None:
        self_type = CtyObject({"data": number_type})
        other_type = CtyObject(
            {"data": string_type}
        )  # Expects string, self provides number
        assert not self_type.usable_as(other_type)

    def test_usable_as_false_other_requires_attr_self_has_optional(
        self, string_type
    ) -> None:
        self_type = CtyObject(
            {"config": string_type}, optional_attributes=frozenset({"config"})
        )
        other_type = CtyObject({"config": string_type})  # config is required here
        assert not self_type.usable_as(other_type)

    def test_usable_as_true_self_requires_attr_other_has_optional(
        self, string_type
    ) -> None:
        self_type = CtyObject({"config": string_type})  # config is required here
        other_type = CtyObject(
            {"config": string_type}, optional_attributes=frozenset({"config"})
        )
        assert self_type.usable_as(other_type)

    def test_usable_as_false_not_object_type(
        self, basic_object_type: CtyObject, string_type
    ) -> None:
        assert not basic_object_type.usable_as(string_type)


class TestCtyObjectWithAttributeMethods:
    def test_with_attribute_new(
        self, basic_object_type: CtyObject, bool_type: CtyBool
    ) -> None:
        new_obj_type = basic_object_type.with_attribute("is_active", bool_type)
        assert "is_active" in new_obj_type.attribute_types
        assert new_obj_type.attribute_types["is_active"] == bool_type
        assert (
            "is_active" not in new_obj_type.optional_attributes
        )  # default not optional

    def test_with_attribute_new_optional(
        self, basic_object_type: CtyObject, bool_type: CtyBool
    ) -> None:
        new_obj_type = basic_object_type.with_attribute(
            "is_verified", bool_type, optional=True
        )
        assert "is_verified" in new_obj_type.attribute_types
        assert "is_verified" in new_obj_type.optional_attributes

    def test_with_attribute_existing_raises(
        self, basic_object_type: CtyObject, string_type: CtyString
    ) -> None:
        with pytest.raises(
            CtyAttributeValidationError, match="Attribute already exists: name"
        ):
            basic_object_type.with_attribute("name", string_type)

    def test_with_optional_attributes_new(self, basic_object_type: CtyObject) -> None:
        new_obj_type = basic_object_type.with_optional_attributes(
            "age"
        )  # age was required
        assert "age" in new_obj_type.optional_attributes
        assert "name" not in new_obj_type.optional_attributes  # name remains required

    def test_with_optional_attributes_unknown_raises(
        self, basic_object_type: CtyObject
    ) -> None:
        with pytest.raises(
            CtyAttributeValidationError, match="Unknown attributes: city"
        ):
            basic_object_type.with_optional_attributes("city")

    def test_with_optional_attributes_already_optional(
        self, object_with_optional_type: CtyObject
    ) -> None:
        # status is already optional
        new_obj_type = object_with_optional_type.with_optional_attributes("status")
        assert "status" in new_obj_type.optional_attributes  # Stays optional

    def test_with_required_attributes_make_optional_required(
        self, object_with_optional_type: CtyObject
    ) -> None:
        # status was optional
        new_obj_type = object_with_optional_type.with_required_attributes("status")
        assert "status" not in new_obj_type.optional_attributes
        assert "id" not in new_obj_type.optional_attributes  # id remains required
        assert (
            "description" in new_obj_type.optional_attributes
        )  # description stays optional

    def test_with_required_attributes_unknown_raises(
        self, basic_object_type: CtyObject
    ) -> None:
        with pytest.raises(
            CtyAttributeValidationError, match="Unknown attributes: city"
        ):
            basic_object_type.with_required_attributes("city")

    def test_with_required_attributes_already_required_raises(
        self, basic_object_type: CtyObject
    ) -> None:
        # name is already required
        with pytest.raises(
            CtyAttributeValidationError, match="Attributes already required: name"
        ):
            basic_object_type.with_required_attributes("name")


class TestCtyObjectDunderMethods:
    def test_str_representation(
        self, basic_object_type: CtyObject, object_with_optional_type: CtyObject
    ) -> None:
        assert str(basic_object_type) == "object({age: CtyNumber, name: CtyString})"
        # Sorted order, flags for optional
        expected_str = "object({description: CtyString (optional), id: CtyNumber, status: CtyString (optional)})"
        assert str(object_with_optional_type) == expected_str

        empty_obj = CtyObject()
        assert str(empty_obj) == "object({})"

    def test_iter_and_len(self, basic_object_type: CtyObject) -> None:
        assert len(basic_object_type) == 2
        attr_names = set()
        for name in basic_object_type:
            attr_names.add(name)
        assert attr_names == {"name", "age"}

        empty_obj = CtyObject()
        assert len(empty_obj) == 0
        assert list(iter(empty_obj)) == []
