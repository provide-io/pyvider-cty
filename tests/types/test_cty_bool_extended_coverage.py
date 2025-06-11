from decimal import Decimal

import pytest

from pyvider.cty.exceptions import CtyBoolValidationError
from pyvider.cty.types.primitives.bool import CtyBool
from pyvider.cty.types.primitives.number import CtyNumber  # Added import
from pyvider.cty.types.primitives.string import (
    CtyString,  # For creating CtyValue(CtyString)
)
from pyvider.cty.types.structural.dynamic import CtyDynamic
from pyvider.cty.values import CtyValue


# --- Fixtures ---
@pytest.fixture
def bool_type() -> CtyBool:
    return CtyBool()


# --- Tests ---


class TestCtyBoolValidate:
    def test_validate_none_is_null(self, bool_type: CtyBool) -> None:
        """Test None input to validate returns a null CtyValue."""
        # This case is likely covered by existing tests but good for completeness here.
        val = bool_type.validate(None)
        assert val.is_null
        assert val.type == bool_type

    # --- CtyValue Inputs ---
    def test_validate_ctyvalue_bool_passthrough(self, bool_type: CtyBool) -> None:
        """Test CtyValue(CtyBool) input passes through."""
        original_cty_val = CtyValue(vtype=bool_type, value=True)
        validated_val = bool_type.validate(original_cty_val)
        assert validated_val is original_cty_val

    def test_validate_ctyvalue_unknown_propagates(self, bool_type: CtyBool) -> None:
        """Test unknown CtyValue input propagates as unknown CtyBool."""
        # Create an unknown value of some other type, but whose type is usable_as(bool_type)
        # For this test, let's make it an unknown CtyBool directly.
        unknown_val = CtyValue.unknown(bool_type)
        validated_val = bool_type.validate(unknown_val)
        assert validated_val.is_unknown
        assert validated_val.type == bool_type

    def test_validate_ctyvalue_known_non_bool_unbox_and_validate(
        self, bool_type: CtyBool
    ) -> None:
        """Test CtyValue(non-CtyBool) input has its inner value unboxed and validated."""
        # e.g. CtyValue(CtyString, "true")
        string_val_true = CtyValue(vtype=CtyString(), value="true")
        validated_val = bool_type.validate(string_val_true)
        assert validated_val.type == bool_type
        assert validated_val.value is True

        string_val_0 = CtyValue(vtype=CtyString(), value="0")  # String "0"
        validated_val_0 = bool_type.validate(string_val_0)
        assert validated_val_0.type == bool_type
        assert validated_val_0.value is False

        # CtyValue(CtyNumber, 1)
        num_val_1 = CtyValue(vtype=CtyNumber(), value=Decimal(1))
        validated_num_1 = bool_type.validate(num_val_1)
        assert validated_num_1.type == bool_type
        assert validated_num_1.value is True

        # CtyValue(CtyString, "invalid-bool-str")
        string_val_invalid = CtyValue(vtype=CtyString(), value="xyz")
        with pytest.raises(
            CtyBoolValidationError, match="Cannot convert string 'xyz' to boolean"
        ):
            bool_type.validate(string_val_invalid)

    # --- Python bool Input ---
    def test_validate_python_bool(self, bool_type: CtyBool) -> None:
        """Test Python bool input."""
        assert bool_type.validate(True).value is True
        assert bool_type.validate(False).value is False

    # --- String Inputs ---
    @pytest.mark.parametrize(
        "true_str", ["1", "t", "T", "true", "TRUE", "True", "yes", "YES", "y", "Y"]
    )
    def test_validate_true_strings(self, bool_type: CtyBool, true_str: str) -> None:
        assert bool_type.validate(true_str).value is True

    @pytest.mark.parametrize(
        "false_str", ["0", "f", "F", "false", "FALSE", "False", "no", "NO", "n", "N"]
    )
    def test_validate_false_strings(self, bool_type: CtyBool, false_str: str) -> None:
        assert bool_type.validate(false_str).value is False

    def test_validate_invalid_string(self, bool_type: CtyBool) -> None:
        """Test invalid string input raises CtyBoolValidationError."""
        with pytest.raises(
            CtyBoolValidationError, match="Cannot convert string 'invalid' to boolean"
        ):
            bool_type.validate("invalid")
        with pytest.raises(
            CtyBoolValidationError, match="Cannot convert string '' to boolean"
        ):
            bool_type.validate("")  # Empty string

    # --- Numeric Inputs ---
    def test_validate_numeric_0_and_1(self, bool_type: CtyBool) -> None:
        """Test numeric 0 and 1 inputs."""
        assert bool_type.validate(0).value is False
        assert bool_type.validate(1).value is True
        assert bool_type.validate(0.0).value is False
        assert bool_type.validate(1.0).value is True
        assert bool_type.validate(Decimal(0)).value is False
        assert bool_type.validate(Decimal(1)).value is True

    def test_validate_numeric_not_0_or_1_raises(self, bool_type: CtyBool) -> None:
        """Test numeric inputs other than 0 or 1 raise CtyBoolValidationError."""
        with pytest.raises(
            CtyBoolValidationError, match="Numeric boolean must be 0 or 1, got 2"
        ):
            bool_type.validate(2)
        with pytest.raises(
            CtyBoolValidationError, match="Numeric boolean must be 0 or 1, got -1"
        ):
            bool_type.validate(-1)
        with pytest.raises(
            CtyBoolValidationError, match="Numeric boolean must be 0 or 1, got 0.5"
        ):
            bool_type.validate(0.5)
        with pytest.raises(
            CtyBoolValidationError,
            match=r"Numeric boolean must be 0 or 1, got Decimal\('1.1'\)",
        ):
            bool_type.validate(Decimal("1.1"))

    def test_validate_numeric_float_inf_nan_raises(self, bool_type: CtyBool) -> None:
        """Test float inf/nan raises CtyBoolValidationError."""
        # Decimal(float('inf')) results in Decimal('Infinity'), which is not 0 or 1.
        with pytest.raises(
            CtyBoolValidationError, match="Numeric boolean must be 0 or 1, got inf"
        ):
            bool_type.validate(float("inf"))
        # Decimal(float('nan')) results in Decimal('NaN').
        with pytest.raises(
            CtyBoolValidationError, match="Numeric boolean must be 0 or 1, got nan"
        ):
            bool_type.validate(float("nan"))

    # --- Other Unsupported Inputs ---
    def test_validate_unsupported_type_raises(self, bool_type: CtyBool) -> None:
        """Test unsupported input types raise CtyBoolValidationError."""
        with pytest.raises(
            CtyBoolValidationError,
            match="Value must be a boolean, 0/1, or convertible string; got list: \\[]",
        ):
            bool_type.validate([])
        with pytest.raises(
            CtyBoolValidationError,
            match="Value must be a boolean, 0/1, or convertible string; got dict: {}",
        ):
            bool_type.validate({})


class TestCtyBoolEqualUsableAs:
    def test_equal_true_same_type(self, bool_type: CtyBool) -> None:
        assert bool_type.equal(CtyBool())

    def test_equal_false_different_type(self, bool_type: CtyBool) -> None:
        assert not bool_type.equal(CtyString())  # type: ignore

    def test_usable_as_true_same_type(self, bool_type: CtyBool) -> None:
        assert bool_type.usable_as(CtyBool())

    def test_usable_as_false_different_concrete_type(self, bool_type: CtyBool) -> None:
        assert not bool_type.usable_as(CtyString())  # type: ignore

    def test_usable_as_dynamic_type(self, bool_type: CtyBool) -> None:
        # This depends on CtyBool.usable_as being updated to allow CtyDynamic
        assert bool_type.usable_as(CtyDynamic())


class TestCtyBoolDunderAndFlags:
    def test_str(self, bool_type: CtyBool) -> None:
        assert str(bool_type) == "bool"

    def test_is_primitive(self, bool_type: CtyBool) -> None:
        assert bool_type.is_primitive_type()


# More tests might be needed for CtyValue(CtyDynamic) unboxing paths if complex.
# For now, CtyString/CtyNumber unboxing is representative.
