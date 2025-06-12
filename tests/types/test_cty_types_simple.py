import unittest

from pyvider.cty.exceptions import CtyValidationError
from pyvider.cty import CtyBool, CtyNumber, CtyString


class TestCtyStringType(unittest.TestCase):
    def setUp(self):
        self.string_type = CtyString()

    def test_validate_valid_string(self):
        try:
            self.string_type.validate("hello")
        except CtyValidationError as e:
            self.fail(f"ValidationError raised unexpectedly: {e}")

    def test_validate_invalid_string(self):
        with self.assertRaises(CtyValidationError):
            self.string_type.validate(123)

class TestCtyNumberType(unittest.TestCase):
    def setUp(self):
        self.number_type = CtyNumber()

    def test_validate_valid_number(self):
        try:
            self.number_type.validate(123)
            self.number_type.validate(123.45)
        except CtyValidationError as e:
            self.fail(f"ValidationError raised unexpectedly: {e}")

    def test_validate_invalid_number(self):
        with self.assertRaises(CtyValidationError):
            self.number_type.validate("string")

class TestCtyBoolType(unittest.TestCase):
    def setUp(self):
        self.bool_type = CtyBool()

    def test_validate_valid_bool(self):
        try:
            self.bool_type.validate(True)
            self.bool_type.validate(False)
        except CtyValidationError as e:
            self.fail(f"ValidationError raised unexpectedly: {e}")

    def test_validate_invalid_bool(self):
        with self.assertRaises(CtyValidationError):
            self.bool_type.validate("not_a_bool")

if __name__ == "__main__":
    unittest.main()

