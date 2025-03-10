import pytest

from pyvider.cty.exceptions import AttributeValidationError, SchemaValidationError, ValidationError
from pyvider.cty import CtyBool, CtyNumber, CtyString, CtyObject

# --------------------------------
# Test: CtyObject Basic Validation
# --------------------------------

def test_ctyobject_validate_success():
    obj = CtyObject({
        "name": CtyString(),
        "age": CtyNumber(),
        "active": CtyBool()
    })

    validated = obj.validate({
        "name": "John Doe",
        "age": 30,
        "active": True
    })
    assert validated == {"name": "John Doe", "age": 30, "active": True}


def test_ctyobject_validate_missing_required():
    obj = CtyObject({
        "name": CtyString(),
        "age": CtyNumber(),
    })

    with pytest.raises(ValidationError, match="Missing required attribute: age"):
        obj.validate({"name": "Jane Doe"})


# --------------------------------
# Test: CtyObject Nested Validation
# --------------------------------

def test_ctyobject_nested_validation():
    address_type = CtyObject({
        "street": CtyString(),
        "city": CtyString(),
        "postal_code": CtyString()
    })

    user_type = CtyObject({
        "name": CtyString(),
        "address": address_type,
    })

    validated = user_type.validate({
        "name": "John",
        "address": {
            "street": "123 Main St",
            "city": "Springfield",
            "postal_code": "12345"
        }
    })

    assert validated["address"]["city"] == "Springfield"


def test_ctyobject_nested_invalid_type():
    address_type = CtyObject({
        "street": CtyString(),
        "city": CtyString()
    })

    user_type = CtyObject({
        "name": CtyString(),
        "address": address_type,
    })

    with pytest.raises(ValidationError, match="Invalid value for attribute 'address'"):
        user_type.validate({
            "name": "John",
            "address": "Not an object"
        })


# --------------------------------
# Test: CtyObject with Immutability
# --------------------------------

def test_ctyobject_validate_immutable():
    obj = CtyObject(
        {"title": CtyString()},
        mutable=False
    )

    validated = obj.validate({"title": "Immutable Object"})

    assert validated == {"title": "Immutable Object"}

    with pytest.raises(TypeError):
        validated["title"] = "Changed"


# --------------------------------
# Test: CtyObject Schema Errors
# --------------------------------

def test_ctyobject_with_invalid_block_attributes():
    with pytest.raises(AttributeValidationError, match="Unknown attributes: invalid_block"):
        CtyObject(
            {"age": CtyNumber()},
            block_attributes={"invalid_block"}
        )


# --------------------------------
# Test: CtyObject Attribute Access
# --------------------------------

def test_ctyobject_get_valid_attribute():
    obj = CtyObject({
        "title": CtyString(),
        "level": CtyNumber()
    })

    data = obj.validate({"title": "Game Title", "level": 5})
    assert obj.get_attribute(data, "title") == "Game Title"


def test_ctyobject_get_invalid_attribute():
    obj = CtyObject({
        "username": CtyString()
    })

    data = obj.validate({"username": "user1"})

    with pytest.raises(AttributeValidationError, match="Unknown attribute: password"):
        obj.get_attribute(data, "password")


# --------------------------------
# Test: CtyObject with Blocks
# --------------------------------

def test_ctyobject_with_blocks():
    block_type = CtyObject({
        "id": CtyString(),
        "enabled": CtyBool()
    })

    parent = CtyObject({
        "config": block_type,
        "metadata": CtyString(),
    })

    validated = parent.validate({
        "config": {
            "id": "123",
            "enabled": True
        },
        "metadata": "meta"
    })

    assert validated["config"]["enabled"] is True


def test_ctyobject_invalid_block():
    block_type = CtyObject({
        "id": CtyString()
    })

    parent = CtyObject({
        "config": block_type
    })

    with pytest.raises(ValidationError, match="Invalid value for attribute 'config'"):
        parent.validate({
            "config": "invalid_block"
        })


# --------------------------------
# Test: CtyObject Equality
# --------------------------------

def test_ctyobject_equality():
    obj1 = CtyObject({
        "name": CtyString(),
        "age": CtyNumber()
    })

    obj2 = CtyObject({
        "name": CtyString(),
        "age": CtyNumber()
    })

    assert obj1.equal(obj2)


def test_ctyobject_inequality():
    obj1 = CtyObject({"name": CtyString()})
    obj2 = CtyObject({"email": CtyString()})

    assert not obj1.equal(obj2)


# --------------------------------
# Test: CtyObject with Mixed Attribute Types
# --------------------------------

def test_ctyobject_mixed_types():
    obj = CtyObject({
        "string_attr": CtyString(),
        "number_attr": CtyNumber(),
        "bool_attr": CtyBool()
    })

    validated = obj.validate({
        "string_attr": "sample",
        "number_attr": 42,
        "bool_attr": False
    })

    assert validated == {
        "string_attr": "sample",
        "number_attr": 42,
        "bool_attr": False
    }

    with pytest.raises(ValidationError, match="Invalid value for attribute 'number_attr'"):
        obj.validate({
            "string_attr": "sample",
            "number_attr": "not_a_number",
            "bool_attr": True
        })


# --------------------------------
# Test: Missing All Required Attributes
# --------------------------------

def test_ctyobject_all_required_missing():
    obj = CtyObject({
        "first_name": CtyString(),
        "last_name": CtyString(),
    })

    with pytest.raises(ValidationError, match="Missing required attribute: first_name"):
        obj.validate({})


# --------------------------------
# Test: CtyObject Immutability with Nested Structures
# --------------------------------

def test_ctyobject_immutable_nested():
    inner = CtyObject({"key": CtyString()}, mutable=False)
    outer = CtyObject({"nested": inner}, mutable=False)

    validated = outer.validate({
        "nested": {
            "key": "value"
        }
    })

    assert validated["nested"]["key"] == "value"

    # Attempt to mutate nested object
    with pytest.raises(TypeError):
        validated["nested"]["key"] = "new_value"


# --------------------------------
# Test: Equality with Different Attribute Sets
# --------------------------------

def test_ctyobject_equality_with_different_attributes():
    obj1 = CtyObject({
        "name": CtyString(),
        "age": CtyNumber()
    })

    obj2 = CtyObject({
        "name": CtyString(),
        "gender": CtyString()
    })

    assert not obj1.equal(obj2)


# --------------------------------
# Test: CtyObject Usable As Another Object
# --------------------------------

def test_ctyobject_usable_as():
    parent = CtyObject({
        "name": CtyString(),
        "email": CtyString(),
    })

    child = CtyObject({
        "name": CtyString(),
    })

    assert child.usable_as(parent)
    assert not parent.usable_as(child)  # Missing email


# --------------------------------
# Test: Schema Validation Errors (Blocks and Optional Attributes)
# --------------------------------

def test_ctyobject_schema_validation_error():
    with pytest.raises(SchemaValidationError, match="Unknown attributes: invalid"):
        CtyObject(
            {"name": CtyString()},
            block_attributes={"invalid"}
        )


# --------------------------------
# Test: Immutability Enforcement During Validation
# --------------------------------

def test_ctyobject_immutable_list():
    obj = CtyObject({
        "tags": CtyList(element_type=CtyString())
    }, mutable=False)

    validated = obj.validate({"tags": ["one", "two"]})

    with pytest.raises(TypeError):
        validated["tags"].append("three")



# --------------------------------
# Test: CtyObject with Block Attribute Not Passed
# --------------------------------

def test_ctyobject_block_not_passed():
    obj = CtyObject({
        "config": CtyObject({
            "enabled": CtyBool()
        }, block_attributes={"enabled"})
    })

    validated = obj.validate({
        "config": {}
    })
    assert "enabled" not in validated["config"]


# --------------------------------
# Test: CtyObject Validate with Extra Attributes (Fail)
# --------------------------------

def test_ctyobject_extra_attributes_fail():
    obj = CtyObject({
        "username": CtyString(),
    })

    with pytest.raises(ValidationError, match="Unknown attribute: role"):
        obj.validate({
            "username": "admin",
            "role": "manager"
        })


# --------------------------------
# Test: CtyObject with Block Attribute Not in Schema
# --------------------------------

def test_ctyobject_invalid_block_attribute():
    with pytest.raises(AttributeValidationError, match="Unknown attributes: invalid_block"):
        CtyObject({
            "title": CtyString()
        }, block_attributes={"invalid_block"})


# --------------------------------
# Test: CtyObject Immutability on Nested Structures
# --------------------------------

def test_ctyobject_nested_immutability():
    nested_obj = CtyObject({
        "key": CtyString()
    }, mutable=False)

    outer_obj = CtyObject({
        "nested": nested_obj
    }, mutable=False)

    validated = outer_obj.validate({
        "nested": {"key": "value"}
    })

    with pytest.raises(TypeError):
        validated["nested"]["key"] = "new_value"


# --------------------------------
# Test: CtyObject Partial Equality (Extra Attributes)
# --------------------------------

def test_ctyobject_partial_equality_extra_attributes():
    obj1 = CtyObject({
        "name": CtyString(),
        "email": CtyString()
    })

    obj2 = CtyObject({
        "name": CtyString()
    })

    assert not obj1.equal(obj2)  # obj1 has more attributes


# --------------------------------
# Test: CtyObject Partial Usability (Extra Attributes)
# --------------------------------

def test_ctyobject_usable_as_partial():
    parent = CtyObject({
        "name": CtyString(),
        "email": CtyString(),
    })

    child = CtyObject({
        "name": CtyString(),
    })

    assert child.usable_as(parent)
    assert not parent.usable_as(child)  # Parent cannot be used as a less complete child



# --------------------------------
# Test: CtyObject Immutable with Nested Lists
# --------------------------------

def test_ctyobject_nested_list_immutable():
    obj = CtyObject({
        "tags": CtyObject({
            "labels": CtyObject({
                "key": CtyString()
            }, mutable=False)
        }, mutable=False)
    }, mutable=False)

    validated = obj.validate({
        "tags": {
            "labels": {"key": "value"}
        }
    })

    with pytest.raises(TypeError):
        validated["tags"]["labels"]["key"] = "new_value"


# --------------------------------
# Test: CtyObject With No Attributes (Empty Object)
# --------------------------------

def test_ctyobject_no_attributes():
    obj = CtyObject({})

    validated = obj.validate({})
    assert validated == {}


# --------------------------------
# Test: CtyObject Validation Error Cascading
# --------------------------------

def test_ctyobject_cascading_validation_error():
    inner = CtyObject({
        "age": CtyNumber()
    })

    outer = CtyObject({
        "user": inner
    })

    with pytest.raises(ValidationError, match="Invalid value for attribute 'user'"):
        outer.validate({
            "user": {"age": "not_a_number"}
        })
