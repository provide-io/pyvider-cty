import unittest
from pyvider.cty import CtyBool, CtyNumber, CtyString, CtyValue
from pyvider.cty.exceptions import CtyValidationError, CtyStringValidationError

class TestCtyStringType(unittest.TestCase):
    def setUp(self) -> None:
        self.string_type = CtyString()

    def test_validate_valid_string(self) -> None:
        result = self.string_type.validate("hello")
        self.assertIsInstance(result, CtyValue)
        self.assertEqual(result.value, "hello")

    def test_validate_invalid_string(self) -> None:
        # CtyString().validate(123) will now attempt str(123) and succeed.
        # To test failure, we need a value that cannot be converted to a string.
        class Unstringable:
            def __str__(self): raise TypeError("I am not a string!")
        
        with self.assertRaises(CtyStringValidationError):
            self.string_type.validate(Unstringable())

    def test_validate_none_string(self) -> None:
        result = self.string_type.validate(None)
        self.assertTrue(result.is_null)
        self.assertIsInstance(result.type, CtyString)

class TestCtyNumberType(unittest.TestCase):
    def setUp(self) -> None:
        self.number_type = CtyNumber()

    def test_validate_valid_number(self) -> None:
        result = self.number_type.validate(123.45)
        self.assertIsInstance(result, CtyValue)

    def test_validate_invalid_number(self) -> None:
        with self.assertRaises(CtyValidationError):
            self.number_type.validate("not a number")

class TestCtyBoolType(unittest.TestCase):
    def setUp(self) -> None:
        self.bool_type = CtyBool()

    def test_validate_valid_bool(self) -> None:
        result = self.bool_type.validate(True)
        self.assertIsInstance(result, CtyValue)

    def test_validate_invalid_bool(self) -> None:
        with self.assertRaises(CtyValidationError):
            self.bool_type.validate("not a bool")
