import pytest

from pyvider.cty.exceptions import CtyAttributeValidationError, InvalidTypeError
from pyvider.cty.types import CtyNumber, CtyString
from pyvider.cty.types.structural.object import CtyObject, _attrs_to_dict_safe


def test_attrs_to_dict_safe_no_attrs() -> None:
    class NoAttrs:
        pass

    assert _attrs_to_dict_safe(NoAttrs()) == {}


def test_attrs_post_init_invalid_attribute_type() -> None:
    with pytest.raises(InvalidTypeError):
        CtyObject(attribute_types={"name": "not_a_type"})


def test_validate_unknown_optionals() -> None:
    with pytest.raises(
        CtyAttributeValidationError, match="Unknown optional attributes"
    ):
        CtyObject(
            attribute_types={"name": CtyString()}, optional_attributes={"age"}
        ).validate({"name": "test"})


def test_validate_with_cty_value_different_type() -> None:
    obj_type = CtyObject(attribute_types={"name": CtyString()})
    other_obj_type = CtyObject(attribute_types={"name": CtyNumber()})
    value = other_obj_type.validate({"name": 1})
    with pytest.raises(CtyAttributeValidationError):
        obj_type.validate(value)


def test_validate_null_attribute_in_required_field() -> None:
    obj_type = CtyObject(attribute_types={"name": CtyString()})
    with pytest.raises(CtyAttributeValidationError, match="Attribute cannot be null"):
        obj_type.validate({"name": None})


from pyvider.cty.exceptions import CtyTypeMismatchError


def test_get_attribute_on_non_cty_value() -> None:
    obj_type = CtyObject(attribute_types={"name": CtyString()})
    with pytest.raises(CtyTypeMismatchError):
        obj_type.get_attribute("not a cty value", "name")


def test_equal_different_keys() -> None:
    type1 = CtyObject(attribute_types={"name": CtyString()})
    type2 = CtyObject(attribute_types={"age": CtyNumber()})
    assert type1.equal(type2) is False


def test_usable_as_not_subset() -> None:
    type1 = CtyObject(attribute_types={"name": CtyString()})
    type2 = CtyObject(attribute_types={"name": CtyString(), "age": CtyNumber()})
    assert type1.usable_as(type2) is False


def test_usable_as_not_subset_required() -> None:
    type1 = CtyObject(
        attribute_types={"name": CtyString(), "age": CtyNumber()},
        optional_attributes={"age"},
    )
    type2 = CtyObject(attribute_types={"name": CtyString(), "age": CtyNumber()})
    assert type1.usable_as(type2) is False
