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

    def test_validate_none_string(self) -> None:
        """Test that validating None raises CtyStringValidationError."""
        from pyvider.cty.exceptions import (
            CtyStringValidationError,  # Ensure specific exception
        )
        with self.assertRaisesRegex(CtyStringValidationError, "String value cannot be None."):
            self.string_type.validate(None)

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

class TestCtyTypePrimitiveCheck(unittest.TestCase):
    def test_is_primitive_type(self):
        from pyvider.cty.types import (
            CtyList,
            CtyMap,
            CtySet,
            CtyObject,
            CtyTuple,
            CtyDynamic,
        )
        # Primitive types
        self.assertTrue(CtyString().is_primitive_type())
        self.assertTrue(CtyNumber().is_primitive_type())
        self.assertTrue(CtyBool().is_primitive_type())

        # Non-primitive types
        self.assertFalse(CtyList(element_type=CtyString()).is_primitive_type())
        self.assertFalse(CtyMap(key_type=CtyString(), value_type=CtyString()).is_primitive_type()) # Assuming value_type as CtyString for the test
        self.assertFalse(CtySet(element_type=CtyString()).is_primitive_type())
        self.assertFalse(CtyObject({"attr": CtyString()}).is_primitive_type())
        self.assertFalse(CtyTuple((CtyString(), CtyNumber())).is_primitive_type()) # Changed list to tuple
        self.assertFalse(CtyDynamic().is_primitive_type())

if __name__ == "__main__":
    unittest.main()

