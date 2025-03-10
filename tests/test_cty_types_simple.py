import unittest

from pyvider.exceptions import ValidationError
from pyvider.cty.primitives import TFBool, TFNumber, TFString


class TestTFStringType(unittest.TestCase):
    def setUp(self):
        self.string_type = TFString()

    def test_validate_valid_string(self):
        try:
            self.string_type.validate("hello")
        except ValidationError as e:
            self.fail(f"ValidationError raised unexpectedly: {e}")

    def test_validate_invalid_string(self):
        with self.assertRaises(ValidationError):
            self.string_type.validate(123)

class TestTFNumberType(unittest.TestCase):
    def setUp(self):
        self.number_type = TFNumber()

    def test_validate_valid_number(self):
        try:
            self.number_type.validate(123)
            self.number_type.validate(123.45)
        except ValidationError as e:
            self.fail(f"ValidationError raised unexpectedly: {e}")

    def test_validate_invalid_number(self):
        with self.assertRaises(ValidationError):
            self.number_type.validate("string")

class TestTFBoolType(unittest.TestCase):
    def setUp(self):
        self.bool_type = TFBool()

    def test_validate_valid_bool(self):
        try:
            self.bool_type.validate(True)
            self.bool_type.validate(False)
        except ValidationError as e:
            self.fail(f"ValidationError raised unexpectedly: {e}")

    def test_validate_invalid_bool(self):
        with self.assertRaises(ValidationError):
            self.bool_type.validate("not_a_bool")

if __name__ == "__main__":
    unittest.main()

