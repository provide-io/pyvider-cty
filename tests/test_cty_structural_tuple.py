import unittest

from pyvider.exceptions import ValidationError
from pyvider.cty import TFTuple


class TestTFTupleType(unittest.TestCase):
    def setUp(self):
        # Define a tuple with the expected structure (str, int)
        self.tuple_type = TFTuple((str, int))

    def test_validate_valid_tuple(self):
        try:
            self.tuple_type.validate(("hello", 123))
        except ValidationError as e:
            self.fail(f"ValidationError raised unexpectedly: {e}")

    def test_validate_invalid_tuple(self):
        with self.assertRaises(ValidationError):
            self.tuple_type.validate(("hello", "not_an_int"))

    def test_validate_wrong_length(self):
        with self.assertRaises(ValidationError):
            self.tuple_type.validate(("hello",))

    def test_equal(self):
        other_tuple = TFTuple((str, int))
        self.assertTrue(self.tuple_type.equal(other_tuple))

        different_tuple = TFTuple((str, str))
        self.assertFalse(self.tuple_type.equal(different_tuple))

    def test_usable_as(self):
        compatible_tuple = TFTuple((str, int))
        self.assertTrue(self.tuple_type.usable_as(compatible_tuple))

        incompatible_tuple = TFTuple((int, str))
        self.assertFalse(self.tuple_type.usable_as(incompatible_tuple))


if __name__ == "__main__":
    unittest.main()

