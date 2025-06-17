#
# tests/structural/test_object_with_capsule.py
#

import pytest

from pyvider.cty.types.structural import CtyObject
from pyvider.cty.types.capsule import CtyCapsule
from pyvider.cty.types.primitives import CtyString
from pyvider.cty.values import CtyValue
from pyvider.cty.exceptions import CtyValidationError

# A simple custom class for testing encapsulation
class MyService:
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"MyService(name='{self.name}')"

    # For CtyValue comparison if it wraps raw objects directly in some cases.
    # And for direct assertion if needed.
    def __eq__(self, other):
        if isinstance(other, MyService):
            return self.name == other.name
        return False

@pytest.fixture
def my_service_capsule_type() -> CtyCapsule:
    """Fixture for a CtyCapsule type wrapping MyService."""
    return CtyCapsule("MyServiceType", MyService)

@pytest.fixture
def object_with_capsule_type(my_service_capsule_type: CtyCapsule) -> CtyObject:
    """Fixture for a CtyObject type that includes a CtyCapsule attribute."""
    return CtyObject({
        "id": CtyString(),
        "service": my_service_capsule_type
    })

@pytest.fixture
def object_with_optional_capsule_type(my_service_capsule_type: CtyCapsule) -> CtyObject:
    """Fixture for a CtyObject type with an optional CtyCapsule attribute."""
    return CtyObject(
        {"name": CtyString(), "service_instance": my_service_capsule_type},
        optional_attributes={"service_instance"}
    )


def test_create_object_with_capsule_type(object_with_capsule_type: CtyObject, my_service_capsule_type: CtyCapsule):
    """Test that CtyObject can be defined with a CtyCapsule attribute."""
    assert "service" in object_with_capsule_type.attribute_types
    assert object_with_capsule_type.attribute_types["service"] == my_service_capsule_type

def test_validate_object_with_capsule_attribute(object_with_capsule_type: CtyObject):
    """Test validating a dictionary with a correct capsule instance."""
    service_instance = MyService("test_service")
    data = {"id": "obj1", "service": service_instance}

    cty_val = object_with_capsule_type.validate(data)
    assert isinstance(cty_val, CtyValue)
    assert cty_val.type == object_with_capsule_type
    assert cty_val.value["id"].value == "obj1"
    # The capsule value should be the raw MyService instance
    assert cty_val.value["service"].value == service_instance
    assert isinstance(cty_val.value["service"].value, MyService)

def test_validate_object_with_incorrect_capsule_type(object_with_capsule_type: CtyObject):
    """Test validation failure when capsule attribute has an incorrect type."""
    data = {"id": "obj2", "service": "not_a_service_instance"}

    with pytest.raises(CtyValidationError) as excinfo:
        object_with_capsule_type.validate(data)

    assert "Value is not an instance of MyService" in str(excinfo.value)
    assert "attribute 'service'" in str(excinfo.value)


def test_validate_object_with_missing_required_capsule(object_with_capsule_type: CtyObject):
    """Test validation failure when a required capsule attribute is missing."""
    data = {"id": "obj3"}
    with pytest.raises(CtyValidationError, match="Missing required attribute: service"):
        object_with_capsule_type.validate(data)

def test_get_capsule_attribute(object_with_capsule_type: CtyObject):
    """Test retrieving a capsule attribute from a validated CtyObject value."""
    service_instance = MyService("retrieval_test")
    data = {"id": "obj4", "service": service_instance}

    cty_obj_val = object_with_capsule_type.validate(data)

    # Using CtyObject.get_attribute
    service_attr_val = object_with_capsule_type.get_attribute(cty_obj_val, "service")
    assert isinstance(service_attr_val, CtyValue)
    assert service_attr_val.value == service_instance
    assert isinstance(service_attr_val.value, MyService)

    # Direct access from the validated dictionary of CtyValues
    raw_service_val = cty_obj_val.value["service"]
    assert isinstance(raw_service_val, CtyValue)
    assert raw_service_val.value == service_instance
    assert isinstance(raw_service_val.value, MyService)

def test_object_with_optional_capsule_present(object_with_optional_capsule_type: CtyObject):
    """Test validation when an optional capsule attribute is present."""
    service_instance = MyService("optional_svc")
    data = {"name": "optional_test_present", "service_instance": service_instance}

    cty_val = object_with_optional_capsule_type.validate(data)
    assert cty_val.value["service_instance"].value == service_instance

def test_object_with_optional_capsule_missing(object_with_optional_capsule_type: CtyObject):
    """Test validation when an optional capsule attribute is missing (should be null)."""
    data = {"name": "optional_test_missing"}

    cty_val = object_with_optional_capsule_type.validate(data)
    service_val = cty_val.value["service_instance"]
    assert service_val.is_null  # Changed from is_null() to is_null
    assert service_val.value is None # The underlying value of a null CtyValue is None

def test_object_with_optional_capsule_explicitly_null(object_with_optional_capsule_type: CtyObject):
    """Test validation when an optional capsule attribute is explicitly set to None."""
    data = {"name": "optional_test_explicit_null", "service_instance": None}

    cty_val = object_with_optional_capsule_type.validate(data)
    service_val = cty_val.value["service_instance"]
    assert service_val.is_null  # Changed from is_null() to is_null
    assert service_val.value is None

# 🐍🏗️🐣
