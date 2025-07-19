import pytest
from pyvider.cty import CtyString, CtyNumber, CtyBool
from pyvider.cty.exceptions import CtyStringValidationError, CtyNumberValidationError, CtyBoolValidationError

class TestCtyStringType:
    def setup_method(self):
        self.string_type = CtyString()

    def test_validate_invalid_string(self):
        with pytest.raises(CtyStringValidationError):
            self.string_type.validate(123)

    def test_validate_none_string(self) -> None:
        with pytest.raises(CtyStringValidationError, match="Cannot convert null to string"):
            self.string_type.validate(None)

    def test_validate_valid_string(self) -> None:
        result = self.string_type.validate("hello")
        assert result.value == "hello"

class TestCtyNumberType:
    def setup_method(self):
        self.number_type = CtyNumber()

    def test_validate_invalid_number(self):
        with pytest.raises(CtyNumberValidationError):
            self.number_type.validate("hello")

    def test_validate_valid_number(self):
        result = self.number_type.validate(123)
        assert result.value == 123

class TestCtyBoolType:
    def setup_method(self):
        self.bool_type = CtyBool()

    def test_validate_invalid_bool(self):
        with pytest.raises(CtyBoolValidationError):
            self.bool_type.validate(123)

    def test_validate_valid_bool(self):
        result = self.bool_type.validate(True)
        assert result.value is True
