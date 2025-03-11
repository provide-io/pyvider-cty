import unittest

from pyvider.cty.exceptions import ValidationError
from pyvider.cty import CtyTuple


class TestCtyTupleType(unittest.TestCase):
    def setUp(self):
        # Define a tuple with the expected structure (str, int)
        self.tuple_type = CtyTuple((str, int))

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
        other_tuple = CtyTuple((str, int))
        self.assertTrue(self.tuple_type.equal(other_tuple))

        different_tuple = CtyTuple((str, str))
        self.assertFalse(self.tuple_type.equal(different_tuple))

    def test_usable_as(self):
        compatible_tuple = CtyTuple((str, int))
        self.assertTrue(self.tuple_type.usable_as(compatible_tuple))

        incompatible_tuple = CtyTuple((int, str))
        self.assertFalse(self.tuple_type.usable_as(incompatible_tuple))


if __name__ == "__main__":
    unittest.main()

