import pytest
from decimal import Decimal
from pyvider.cty import CtyBool, CtyList, CtyMap, CtyNumber, CtyObject, CtyString, CtyTuple, CtyValue, CtyDynamic
from pyvider.cty.exceptions import CtyMapValidationError

class TestCtyMapCreation:
    def test_map_type_initialization(self):
        string_map = CtyMap(key_type=CtyString(), value_type=CtyString())
        assert isinstance(string_map.key_type, CtyString)
        assert isinstance(string_map.value_type, CtyString)

    def test_map_type_with_invalid_types(self):
        with pytest.raises(CtyMapValidationError, match="key_type must be a CtyType instance"):
            CtyMap(key_type="string", value_type=CtyString())
        with pytest.raises(CtyMapValidationError, match="value_type must be a CtyType instance"):
            CtyMap(key_type=CtyString(), value_type="string")
        with pytest.raises(CtyMapValidationError, match="Map key_type must be a primitive type"):
            CtyMap(key_type=CtyList(element_type=CtyString()), value_type=CtyString())

    def test_map_string_representation(self):
        string_map = CtyMap(key_type=CtyString(), value_type=CtyString())
        assert str(string_map) == "map(string)"

class TestCtyMapValidation:
    def test_simple_map_validation(self):
        number_map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        number_data = {"count": 10, "total": 123.45}
        result = number_map_type.validate(number_data)
        assert isinstance(result, CtyValue)
        assert result.value["count"].value == Decimal("10")
        assert result.value["total"].value == pytest.approx(Decimal("123.45"))

    def test_map_with_invalid_inputs(self):
        string_map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
        with pytest.raises(CtyMapValidationError):
            string_map_type.validate([1, 2, 3])
        # FIX: The validator now correctly coerces the number to a string.
        validated = string_map_type.validate({"key": 123})
        assert validated.value["key"].value == "123"

class TestCtyMapOperations:
    @pytest.fixture
    def sample_map_val(self):
        map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
        return map_type.validate({"key1": "value1", "key2": "value2"})

    def test_map_get_operation(self, sample_map_val):
        result = sample_map_val["key1"]
        assert result.value == "value1"
        
        default_val = CtyString().validate("default")
        get_result = sample_map_val.type.get(sample_map_val, "missing", default_val)
        assert get_result is default_val

class TestCtyMapComparison:
    def test_map_equality(self):
        map1 = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        map2 = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        map3 = CtyMap(key_type=CtyString(), value_type=CtyString())
        assert map1.equal(map2)
        assert not map1.equal(map3)
