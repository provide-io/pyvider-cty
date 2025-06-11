import pytest

from pyvider.cty.exceptions import CtyStringValidationError
from pyvider.cty.types.primitives.number import (
    CtyNumber,  # For creating CtyValue(CtyNumber)
)
from pyvider.cty.types.primitives.string import CtyString
from pyvider.cty.types.structural.dynamic import CtyDynamic
from pyvider.cty.values import CtyValue


# --- Fixtures ---
@pytest.fixture
def string_type() -> CtyString:
    return CtyString()


# --- Helper Class for str() failure ---
class Unstringable:
    def __str__(self) -> str:
        raise RuntimeError("Cannot be stringified!")

    def __repr__(self) -> str:
        return "<Unstringable instance>"


# --- Tests ---


class TestCtyStringValidate:
    def test_validate_none_is_empty_string(self, string_type: CtyString) -> None:
        val = string_type.validate(None)
        assert val.type == string_type
        assert val.value == ""
        assert not val.is_null  # None becomes empty string, not null CtyValue

    # --- CtyValue Inputs ---
    def test_validate_ctyvalue_string_passthrough(self, string_type: CtyString) -> None:
        original_cty_val = CtyValue(vtype=string_type, value="hello")
        validated_val = string_type.validate(original_cty_val)
        assert validated_val is original_cty_val

    def test_validate_ctyvalue_dynamic_known_non_null_can_str(
        self, string_type: CtyString
    ) -> None:
        # CtyValue(CtyDynamic, 123) -> CtyString("123")
        dynamic_val_num = CtyValue(vtype=CtyDynamic(), value=123)
        validated_val = string_type.validate(dynamic_val_num)
        assert validated_val.type == string_type
        assert validated_val.value == "123"

        # CtyValue(CtyDynamic, True) -> CtyString("True")
        dynamic_val_bool = CtyValue(vtype=CtyDynamic(), value=True)
        validated_bool_val = string_type.validate(dynamic_val_bool)
        assert validated_bool_val.type == string_type
        assert validated_bool_val.value == "True"

    def test_validate_ctyvalue_dynamic_known_unstringable_raises(
        self, string_type: CtyString
    ) -> None:
        unstringable_obj = Unstringable()
        dynamic_val_unstr = CtyValue(vtype=CtyDynamic(), value=unstringable_obj)
        with pytest.raises(
            CtyStringValidationError,
            match=r"Failed to convert CtyDynamic's inner value to string: Cannot be stringified!",
        ):
            string_type.validate(dynamic_val_unstr)

    def test_validate_ctyvalue_dynamic_unknown_propagates(
        self, string_type: CtyString
    ) -> None:
        unknown_dyn_val = CtyValue.unknown(CtyDynamic())
        validated_val = string_type.validate(unknown_dyn_val)
        assert validated_val.is_unknown
        assert validated_val.type == string_type  # Should adopt the target type

    def test_validate_ctyvalue_dynamic_null_is_empty_string(
        self, string_type: CtyString
    ) -> None:
        null_dyn_val = CtyValue.null(CtyDynamic())
        validated_val = string_type.validate(null_dyn_val)
        assert not validated_val.is_null
        assert not validated_val.is_unknown
        assert validated_val.type == string_type
        assert validated_val.value == ""

    def test_validate_ctyvalue_other_type_raises(self, string_type: CtyString) -> None:
        # e.g. CtyValue(CtyNumber, 123)
        number_val = CtyValue(vtype=CtyNumber(), value=123)  # type: ignore
        with pytest.raises(
            CtyStringValidationError,
            match="Value is a CtyValue of type CtyNumber, not CtyString or CtyDynamic",
        ):
            string_type.validate(number_val)

    # --- Direct String Input ---
    def test_validate_direct_string(self, string_type: CtyString) -> None:
        assert string_type.validate("hello").value == "hello"
        assert string_type.validate("").value == ""

    # --- Other Unsupported Inputs ---
    def test_validate_unsupported_type_raises(self, string_type: CtyString) -> None:
        with pytest.raises(
            CtyStringValidationError, match="Value must be a string, got int"
        ):
            string_type.validate(123)
        with pytest.raises(
            CtyStringValidationError, match="Value must be a string, got list"
        ):
            string_type.validate([])
        with pytest.raises(
            CtyStringValidationError, match="Value must be a string, got bool"
        ):
            string_type.validate(True)


class TestCtyStringEqualUsableAs:
    def test_equal_true_same_type(self, string_type: CtyString) -> None:
        assert string_type.equal(CtyString())

    def test_equal_false_different_type(self, string_type: CtyString) -> None:
        assert not string_type.equal(CtyNumber())  # type: ignore

    def test_usable_as_true_same_type(self, string_type: CtyString) -> None:
        assert string_type.usable_as(CtyString())

    def test_usable_as_true_dynamic_type(self, string_type: CtyString) -> None:
        assert string_type.usable_as(CtyDynamic())

    def test_usable_as_false_different_concrete_type(
        self, string_type: CtyString
    ) -> None:
        assert not string_type.usable_as(CtyNumber())  # type: ignore


class TestCtyStringDunderAndFlags:
    def test_str(self, string_type: CtyString) -> None:
        assert str(string_type) == "string"

    def test_is_primitive(self, string_type: CtyString) -> None:
        assert string_type.is_primitive_type()
