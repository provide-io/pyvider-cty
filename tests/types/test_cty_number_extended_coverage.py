from decimal import Decimal

import pytest

from pyvider.cty.exceptions import CtyNumberValidationError
from pyvider.cty.types.primitives.bool import CtyBool  # For testing CtyValue(CtyBool)
from pyvider.cty.types.primitives.number import CtyNumber
from pyvider.cty.types.primitives.string import CtyString
from pyvider.cty.types.structural.dynamic import CtyDynamic
from pyvider.cty.values import CtyValue


# --- Fixtures ---
@pytest.fixture
def number_type() -> CtyNumber:
    return CtyNumber()


# --- Tests ---


class TestCtyNumberValidate:
    def test_validate_none_is_zero(self, number_type: CtyNumber) -> None:
        val = number_type.validate(None)
        assert val.type == number_type
        assert val.value == Decimal(0)

    # --- CtyValue Inputs ---
    def test_validate_ctyvalue_number_passthrough(self, number_type: CtyNumber) -> None:
        original_cty_val = CtyValue(vtype=number_type, value=Decimal(123))
        validated_val = number_type.validate(original_cty_val)
        assert validated_val is original_cty_val

    def test_validate_ctyvalue_unknown_propagates(self, number_type: CtyNumber) -> None:
        # This path is not explicitly in CtyNumber.validate, CtyValue handles unknown propagation generally.
        # However, if an unknown value (of any type, theoretically) was passed,
        # the `isinstance(value, CtyValue)` and `value.is_unknown` checks in other types handle this.
        # CtyNumber's validate doesn't have an explicit `value.is_unknown` check like CtyBool.
        # It relies on CtyValue(CtyNumber).is_unknown or unboxing.
        # For now, this test assumes general CtyValue unknown propagation applies.
        unknown_val = CtyValue.unknown(number_type)
        validated_val = number_type.validate(
            unknown_val
        )  # Should pass through if unknown of same type
        assert validated_val.is_unknown
        assert validated_val.type == number_type

        # What if it's an unknown of a *different* type?
        # CtyNumber.validate has no CtyValue.is_unknown check, so it would try to unbox.
        # Accessing .value on an unknown CtyValue will raise ValueError, which is not currently
        # caught and wrapped by CtyNumberValidationError in that specific path.
        # Instead, an unknown CtyValue of a non-CtyNumber type will fall through.
        unknown_string_val = CtyValue.unknown(CtyString())
        with pytest.raises(
            CtyNumberValidationError,
            match=r"Value must be a number or a string representation of a number, got CtyValue",
        ):
            number_type.validate(unknown_string_val)

    def test_validate_ctyvalue_known_non_number_unbox_and_validate(
        self, number_type: CtyNumber
    ) -> None:
        # CtyValue(CtyString, "123.45")
        string_val_numstr = CtyValue(vtype=CtyString(), value="123.45")
        validated_val = number_type.validate(string_val_numstr)
        assert validated_val.type == number_type
        assert validated_val.value == Decimal("123.45")

        # CtyValue(CtyString, "not-a-number")
        string_val_invalid = CtyValue(vtype=CtyString(), value="not-num")
        with pytest.raises(
            CtyNumberValidationError,
            match="String value 'not-num' inside CtyValue is not a valid number",
        ):
            number_type.validate(string_val_invalid)

        # CtyValue(CtyBool, True) - Python bool True is an instance of int. Decimal(True) is Decimal('1').
        bool_val_true = CtyValue(vtype=CtyBool(), value=True)
        validated_bool_val = number_type.validate(bool_val_true)
        assert validated_bool_val.type == number_type
        assert validated_bool_val.value == Decimal(1)

        # CtyValue(CtyDynamic, "3.14")
        dynamic_val_numstr = CtyValue(vtype=CtyDynamic(), value="3.14")
        validated_dyn_val = number_type.validate(dynamic_val_numstr)
        assert validated_dyn_val.type == number_type
        assert validated_dyn_val.value == Decimal("3.14")

        # CtyValue(CtyDynamic, Decimal(7))
        dynamic_val_decimal = CtyValue(vtype=CtyDynamic(), value=Decimal(7))
        validated_dyn_decimal = number_type.validate(dynamic_val_decimal)
        assert validated_dyn_decimal.type == number_type
        assert validated_dyn_decimal.value == Decimal(7)

    # --- Direct Numeric Inputs ---
    @pytest.mark.parametrize(
        "num_input, expected_decimal_str",
        [
            (123, "123"),
            (-45, "-45"),
            (0, "0"),
            (123.45, "123.45"),  # Input is float
            (-0.5, "-0.5"),  # Input is float
            (Decimal("3.14159"), "3.14159"),
        ],
    )
    def test_validate_direct_numerics(
        self, number_type: CtyNumber, num_input, expected_decimal_str
    ) -> None:
        expected_decimal = Decimal(expected_decimal_str)
        actual_value = number_type.validate(num_input).value

        # For floats, direct comparison with a string-constructed Decimal can be tricky.
        # The code under test does `Decimal(value)`.
        if isinstance(num_input, float):
            # This is the most direct test of what the code produces
            assert actual_value == Decimal(num_input)
            # And it should ideally be equivalent to the string version for well-behaved floats
            # This might require context adjustment for precision if it were to fail for specific floats.
            # For common floats like 123.45, Decimal(123.45) is often not Decimal("123.45").
            # Let's compare string representations for floats if they are not special (inf, nan)
            if not actual_value.is_special():
                assert str(actual_value) == expected_decimal_str
            else:  # if special, direct comparison is fine
                assert actual_value == expected_decimal

        else:  # For int and Decimal inputs
            assert actual_value == expected_decimal

    def test_validate_float_inf_nan_is_validated_to_decimal_special_values(
        self, number_type: CtyNumber
    ) -> None:
        # CtyNumber.validate currently ACCEPTS inf/nan and converts them to Decimal special values.
        inf_val = number_type.validate(float("inf"))
        assert inf_val.type == number_type
        assert inf_val.value.is_infinite() and not inf_val.value.is_signed()

        neg_inf_val = number_type.validate(float("-inf"))
        assert neg_inf_val.type == number_type
        assert neg_inf_val.value.is_infinite() and neg_inf_val.value.is_signed()

        nan_val = number_type.validate(float("nan"))
        assert nan_val.type == number_type
        assert nan_val.value.is_nan()

    # --- String Inputs ---
    @pytest.mark.parametrize(
        "str_input, expected_decimal_str",
        [
            ("123", "123"),
            ("-45", "-45"),
            ("0", "0"),
            ("123.45", "123.45"),
            ("  123.45  ", "123.45"),  # Decimal handles whitespace
            ("1e3", "1000"),
        ],
    )
    def test_validate_string_numerics(
        self, number_type: CtyNumber, str_input, expected_decimal_str
    ) -> None:
        assert number_type.validate(str_input).value == Decimal(expected_decimal_str)

    def test_validate_invalid_string_numeric_raises(
        self, number_type: CtyNumber
    ) -> None:
        with pytest.raises(
            CtyNumberValidationError,
            match="Cannot convert string 'not-a-number' to number",
        ):
            number_type.validate("not-a-number")
        with pytest.raises(
            CtyNumberValidationError, match="Cannot convert string '' to number"
        ):
            number_type.validate("")

    # --- Other Unsupported Inputs ---
    def test_validate_unsupported_type_raises(self, number_type: CtyNumber) -> None:
        with pytest.raises(
            CtyNumberValidationError,
            match=r"Value must be a number or a string representation of a number, got list: \[\]",
        ):
            number_type.validate([])
        with pytest.raises(
            CtyNumberValidationError,
            match=r"Value must be a number or a string representation of a number, got dict: {}",
        ):
            number_type.validate({})

        # Python bools are instances of int, so they are handled by the numeric path.
        # Test with a custom, non-numeric type.
        class SomeOtherType:
            def __repr__(self) -> str:
                return "<SomeOtherType instance>"

        with pytest.raises(
            CtyNumberValidationError,
            match=r"Value must be a number or a string representation of a number, got SomeOtherType: <SomeOtherType instance>",
        ):
            number_type.validate(SomeOtherType())


class TestCtyNumberEqualUsableAs:
    def test_equal_true_same_type(self, number_type: CtyNumber) -> None:
        assert number_type.equal(CtyNumber())

    def test_equal_false_different_type(self, number_type: CtyNumber) -> None:
        assert not number_type.equal(CtyString())  # type: ignore

    def test_usable_as_true_same_type(self, number_type: CtyNumber) -> None:
        assert number_type.usable_as(CtyNumber())

    def test_usable_as_false_different_concrete_type(
        self, number_type: CtyNumber
    ) -> None:
        assert not number_type.usable_as(CtyString())  # type: ignore

    def test_usable_as_dynamic_type(self, number_type: CtyNumber) -> None:
        assert number_type.usable_as(CtyDynamic())


class TestCtyNumberDunderAndFlags:
    def test_str(self, number_type: CtyNumber) -> None:
        assert str(number_type) == "number"

    def test_is_primitive(self, number_type: CtyNumber) -> None:
        assert number_type.is_primitive_type()
