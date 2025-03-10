import pytest

from pyvider.exceptions import AttributeValidationError, SchemaValidationError, ValidationError
from pyvider.cty.primitives import TFBool, TFNumber, TFString
from pyvider.cty.structural import TFObject

# --------------------------------
# Test: TFObject Basic Validation
# --------------------------------

def test_tfobject_validate_success():
    obj = TFObject({
        "name": TFString(),
        "age": TFNumber(),
        "active": TFBool()
    })

    validated = obj.validate({
        "name": "John Doe",
        "age": 30,
        "active": True
    })
    assert validated == {"name": "John Doe", "age": 30, "active": True}


def test_tfobject_validate_missing_required():
    obj = TFObject({
        "name": TFString(),
        "age": TFNumber(),
    })

    with pytest.raises(ValidationError, match="Missing required attribute: age"):
        obj.validate({"name": "Jane Doe"})


# --------------------------------
# Test: TFObject Nested Validation
# --------------------------------

def test_tfobject_nested_validation():
    address_type = TFObject({
        "street": TFString(),
        "city": TFString(),
        "postal_code": TFString()
    })

    user_type = TFObject({
        "name": TFString(),
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


def test_tfobject_nested_invalid_type():
    address_type = TFObject({
        "street": TFString(),
        "city": TFString()
    })

    user_type = TFObject({
        "name": TFString(),
        "address": address_type,
    })

    with pytest.raises(ValidationError, match="Invalid value for attribute 'address'"):
        user_type.validate({
            "name": "John",
            "address": "Not an object"
        })


# --------------------------------
# Test: TFObject with Immutability
# --------------------------------

def test_tfobject_validate_immutable():
    obj = TFObject(
        {"title": TFString()},
        mutable=False
    )

    validated = obj.validate({"title": "Immutable Object"})

    assert validated == {"title": "Immutable Object"}

    with pytest.raises(TypeError):
        validated["title"] = "Changed"


# --------------------------------
# Test: TFObject Schema Errors
# --------------------------------

def test_tfobject_with_invalid_block_attributes():
    with pytest.raises(AttributeValidationError, match="Unknown attributes: invalid_block"):
        TFObject(
            {"age": TFNumber()},
            block_attributes={"invalid_block"}
        )


# --------------------------------
# Test: TFObject Attribute Access
# --------------------------------

def test_tfobject_get_valid_attribute():
    obj = TFObject({
        "title": TFString(),
        "level": TFNumber()
    })

    data = obj.validate({"title": "Game Title", "level": 5})
    assert obj.get_attribute(data, "title") == "Game Title"


def test_tfobject_get_invalid_attribute():
    obj = TFObject({
        "username": TFString()
    })

    data = obj.validate({"username": "user1"})

    with pytest.raises(AttributeValidationError, match="Unknown attribute: password"):
        obj.get_attribute(data, "password")


# --------------------------------
# Test: TFObject with Blocks
# --------------------------------

def test_tfobject_with_blocks():
    block_type = TFObject({
        "id": TFString(),
        "enabled": TFBool()
    })

    parent = TFObject({
        "config": block_type,
        "metadata": TFString(),
    })

    validated = parent.validate({
        "config": {
            "id": "123",
            "enabled": True
        },
        "metadata": "meta"
    })

    assert validated["config"]["enabled"] is True


def test_tfobject_invalid_block():
    block_type = TFObject({
        "id": TFString()
    })

    parent = TFObject({
        "config": block_type
    })

    with pytest.raises(ValidationError, match="Invalid value for attribute 'config'"):
        parent.validate({
            "config": "invalid_block"
        })


# --------------------------------
# Test: TFObject Equality
# --------------------------------

def test_tfobject_equality():
    obj1 = TFObject({
        "name": TFString(),
        "age": TFNumber()
    })

    obj2 = TFObject({
        "name": TFString(),
        "age": TFNumber()
    })

    assert obj1.equal(obj2)


def test_tfobject_inequality():
    obj1 = TFObject({"name": TFString()})
    obj2 = TFObject({"email": TFString()})

    assert not obj1.equal(obj2)


# --------------------------------
# Test: TFObject with Mixed Attribute Types
# --------------------------------

def test_tfobject_mixed_types():
    obj = TFObject({
        "string_attr": TFString(),
        "number_attr": TFNumber(),
        "bool_attr": TFBool()
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

def test_tfobject_all_required_missing():
    obj = TFObject({
        "first_name": TFString(),
        "last_name": TFString(),
    })

    with pytest.raises(ValidationError, match="Missing required attribute: first_name"):
        obj.validate({})


# --------------------------------
# Test: TFObject Immutability with Nested Structures
# --------------------------------

def test_tfobject_immutable_nested():
    inner = TFObject({"key": TFString()}, mutable=False)
    outer = TFObject({"nested": inner}, mutable=False)

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

def test_tfobject_equality_with_different_attributes():
    obj1 = TFObject({
        "name": TFString(),
        "age": TFNumber()
    })

    obj2 = TFObject({
        "name": TFString(),
        "gender": TFString()
    })

    assert not obj1.equal(obj2)


# --------------------------------
# Test: TFObject Usable As Another Object
# --------------------------------

def test_tfobject_usable_as():
    parent = TFObject({
        "name": TFString(),
        "email": TFString(),
    })

    child = TFObject({
        "name": TFString(),
    })

    assert child.usable_as(parent)
    assert not parent.usable_as(child)  # Missing email


# --------------------------------
# Test: Schema Validation Errors (Blocks and Optional Attributes)
# --------------------------------

def test_tfobject_schema_validation_error():
    with pytest.raises(SchemaValidationError, match="Unknown attributes: invalid"):
        TFObject(
            {"name": TFString()},
            block_attributes={"invalid"}
        )


# --------------------------------
# Test: Immutability Enforcement During Validation
# --------------------------------

def test_tfobject_immutable_list():
    obj = TFObject({
        "tags": TFList(element_type=TFString())
    }, mutable=False)

    validated = obj.validate({"tags": ["one", "two"]})

    with pytest.raises(TypeError):
        validated["tags"].append("three")



# --------------------------------
# Test: TFObject with Block Attribute Not Passed
# --------------------------------

def test_tfobject_block_not_passed():
    obj = TFObject({
        "config": TFObject({
            "enabled": TFBool()
        }, block_attributes={"enabled"})
    })

    validated = obj.validate({
        "config": {}
    })
    assert "enabled" not in validated["config"]


# --------------------------------
# Test: TFObject Validate with Extra Attributes (Fail)
# --------------------------------

def test_tfobject_extra_attributes_fail():
    obj = TFObject({
        "username": TFString(),
    })

    with pytest.raises(ValidationError, match="Unknown attribute: role"):
        obj.validate({
            "username": "admin",
            "role": "manager"
        })


# --------------------------------
# Test: TFObject with Block Attribute Not in Schema
# --------------------------------

def test_tfobject_invalid_block_attribute():
    with pytest.raises(AttributeValidationError, match="Unknown attributes: invalid_block"):
        TFObject({
            "title": TFString()
        }, block_attributes={"invalid_block"})


# --------------------------------
# Test: TFObject Immutability on Nested Structures
# --------------------------------

def test_tfobject_nested_immutability():
    nested_obj = TFObject({
        "key": TFString()
    }, mutable=False)

    outer_obj = TFObject({
        "nested": nested_obj
    }, mutable=False)

    validated = outer_obj.validate({
        "nested": {"key": "value"}
    })

    with pytest.raises(TypeError):
        validated["nested"]["key"] = "new_value"


# --------------------------------
# Test: TFObject Partial Equality (Extra Attributes)
# --------------------------------

def test_tfobject_partial_equality_extra_attributes():
    obj1 = TFObject({
        "name": TFString(),
        "email": TFString()
    })

    obj2 = TFObject({
        "name": TFString()
    })

    assert not obj1.equal(obj2)  # obj1 has more attributes


# --------------------------------
# Test: TFObject Partial Usability (Extra Attributes)
# --------------------------------

def test_tfobject_usable_as_partial():
    parent = TFObject({
        "name": TFString(),
        "email": TFString(),
    })

    child = TFObject({
        "name": TFString(),
    })

    assert child.usable_as(parent)
    assert not parent.usable_as(child)  # Parent cannot be used as a less complete child



# --------------------------------
# Test: TFObject Immutable with Nested Lists
# --------------------------------

def test_tfobject_nested_list_immutable():
    obj = TFObject({
        "tags": TFObject({
            "labels": TFObject({
                "key": TFString()
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
# Test: TFObject With No Attributes (Empty Object)
# --------------------------------

def test_tfobject_no_attributes():
    obj = TFObject({})

    validated = obj.validate({})
    assert validated == {}


# --------------------------------
# Test: TFObject Validation Error Cascading
# --------------------------------

def test_tfobject_cascading_validation_error():
    inner = TFObject({
        "age": TFNumber()
    })

    outer = TFObject({
        "user": inner
    })

    with pytest.raises(ValidationError, match="Invalid value for attribute 'user'"):
        outer.validate({
            "user": {"age": "not_a_number"}
        })
