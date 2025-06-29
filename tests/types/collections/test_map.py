import pytest
from pyvider.cty.exceptions import CtyMapValidationError
from pyvider.cty.types import CtyDynamic, CtyList, CtyMap, CtyNumber, CtyString

class TestCtyMapInstantiation:
    def test_instantiation_valid(self) -> None:
        m = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        assert isinstance(m.key_type, CtyString)
        assert isinstance(m.value_type, CtyNumber)

    def test_instantiation_invalid_key_or_value_type(self) -> None:
        with pytest.raises(CtyMapValidationError, match="key_type must be a CtyType instance"):
            CtyMap(key_type="not-a-type", value_type=CtyNumber())
        with pytest.raises(CtyMapValidationError, match="value_type must be a CtyType instance"):
            CtyMap(key_type=CtyString(), value_type=123)

class TestCtyMapValidate:
    def test_validate_non_dict_input(self) -> None:
        map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
        with pytest.raises(CtyMapValidationError, match="Input must be a dictionary"):
            map_type.validate(["a", "b"])
