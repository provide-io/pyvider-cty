import unittest

from pyvider.cty import CtyBool, CtyNumber, CtyString
from pyvider.cty.exceptions import CtyValidationError


class TestCtyStringType(unittest.TestCase):
    def setUp(self) -> None:
        self.string_type = CtyString()

    def test_validate_valid_string(self) -> None:
        try:
            self.string_type.validate("hello")
        except CtyValidationError as e:
            self.fail(f"ValidationError raised unexpectedly: {e}")

    def test_validate_invalid_string(self) -> None:
        with self.assertRaises(CtyValidationError):
            self.string_type.validate(123)


class TestCtyNumberType(unittest.TestCase):
    def setUp(self) -> None:
        self.number_type = CtyNumber()

    def test_validate_valid_number(self) -> None:
        try:
            self.number_type.validate(123)
            self.number_type.validate(123.45)
        except CtyValidationError as e:
            self.fail(f"ValidationError raised unexpectedly: {e}")

    def test_validate_invalid_number(self) -> None:
        with self.assertRaises(CtyValidationError):
            self.number_type.validate("string")


class TestCtyBoolType(unittest.TestCase):
    def setUp(self) -> None:
        self.bool_type = CtyBool()

    def test_validate_valid_bool(self) -> None:
        try:
            self.bool_type.validate(True)
            self.bool_type.validate(False)
        except CtyValidationError as e:
            self.fail(f"ValidationError raised unexpectedly: {e}")

    def test_validate_invalid_bool(self) -> None:
        with self.assertRaises(CtyValidationError):
            self.bool_type.validate("not_a_bool")


if __name__ == "__main__":
    unittest.main()
