import pytest
from pyvider.cty import CtyBool, CtyNumber, CtyObject, CtyString, CtyValue
from pyvider.cty.exceptions import CtyAttributeValidationError, CtyTypeMismatchError

class TestCtyObjectAttributes:
    @pytest.fixture
    def person_type(self):
        return CtyObject(
            attribute_types={"name": CtyString(), "age": CtyNumber()},
            optional_attributes=frozenset(["age"])
        )

    @pytest.fixture
    def person_value(self, person_type):
        return person_type.validate({"name": "Alice", "age": 30})

    def test_get_valid_attribute(self, person_type, person_value):
        name_val = person_value["name"]
        assert name_val.value == "Alice"
        
        age_val = person_type.get_attribute(person_value, "age")
        assert age_val.value == 30

    def test_get_invalid_attribute(self, person_type, person_value):
        with pytest.raises(CtyAttributeValidationError, match="Object has no attribute 'unknown'"):
            person_type.get_attribute(person_value, "unknown")

    def test_has_attribute(self, person_type):
        assert person_type.has_attribute("name")
        assert not person_type.has_attribute("unknown")

    def test_get_attribute_from_null_object(self, person_type):
        null_person = CtyValue.null(person_type)
        name_from_null = person_type.get_attribute(null_person, "name")
        assert name_from_null.is_null
        assert isinstance(name_from_null.type, CtyString)
