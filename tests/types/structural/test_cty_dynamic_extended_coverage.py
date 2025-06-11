from decimal import Decimal

import pytest

from pyvider.cty.exceptions import CtyValidationError
from pyvider.cty.types.collections import CtyList, CtyMap
from pyvider.cty.types.primitives import CtyBool, CtyNumber, CtyString
from pyvider.cty.types.structural.dynamic import CtyDynamic
from pyvider.cty.values import CtyValue


# --- Fixtures ---
@pytest.fixture
def dynamic_type() -> CtyDynamic:
    return CtyDynamic()


# --- Tests ---


class TestCtyDynamicValidate:
    def test_validate_passthrough_existing_ctyvalue(
        self, dynamic_type: CtyDynamic
    ) -> None:
        """Test that any existing CtyValue passes through validate unchanged."""
        cty_string_val = CtyValue(vtype=CtyString(), value="hello")
        assert dynamic_type.validate(cty_string_val) is cty_string_val

        cty_number_val = CtyValue(vtype=CtyNumber(), value=Decimal(123))
        assert dynamic_type.validate(cty_number_val) is cty_number_val

        unknown_val = CtyValue.unknown(CtyString())
        assert dynamic_type.validate(unknown_val) is unknown_val

        null_string_val = CtyValue.null(CtyString())
        assert dynamic_type.validate(null_string_val) is null_string_val

    def test_validate_raw_string(self, dynamic_type: CtyDynamic) -> None:
        val = dynamic_type.validate("hello")
        assert isinstance(val, CtyValue)
        assert isinstance(val.type, CtyString)
        assert val.value == "hello"

    def test_validate_raw_bool(self, dynamic_type: CtyDynamic) -> None:
        val_true = dynamic_type.validate(True)
        assert isinstance(val_true, CtyValue)
        assert isinstance(val_true.type, CtyBool)
        assert val_true.value is True

        val_false = dynamic_type.validate(False)
        assert isinstance(val_false, CtyValue)
        assert isinstance(val_false.type, CtyBool)
        assert val_false.value is False

    @pytest.mark.parametrize(
        "num_input, expected_decimal_str",
        [
            (123, "123"),
            (123.45, "123.45"),  # String representation for comparison clarity
            (Decimal("3.14"), "3.14"),
        ],
    )
    def test_validate_raw_number(
        self, dynamic_type: CtyDynamic, num_input, expected_decimal_str
    ) -> None:
        val = dynamic_type.validate(num_input)
        assert isinstance(val, CtyValue)
        assert isinstance(val.type, CtyNumber)
        # For floats, Decimal(num_input) is the direct conversion used by the code.
        # Its string form might have more precision than expected_decimal_str.
        if isinstance(num_input, float):
            assert val.value == Decimal(num_input)
            # Check if string form of the float input matches the expected string form if that's important
            # For example, Decimal(123.45) is not Decimal("123.45")
            # A more robust check for floats against a string representation:
            assert str(Decimal(str(num_input))) == expected_decimal_str
        else:  # For int and Decimal inputs
            assert val.value == Decimal(expected_decimal_str)

    def test_validate_raw_list(self, dynamic_type: CtyDynamic) -> None:
        raw_list = ["a", 1, True]
        val = dynamic_type.validate(raw_list)
        assert isinstance(val, CtyValue)
        assert isinstance(val.type, CtyList)
        assert isinstance(val.type.element_type, CtyDynamic)
        assert val.value == raw_list

    def test_validate_raw_dict(self, dynamic_type: CtyDynamic) -> None:
        raw_dict = {"key1": "val1", "key2": 100}
        val = dynamic_type.validate(raw_dict)
        assert isinstance(val, CtyValue)
        assert isinstance(val.type, CtyMap)
        assert isinstance(val.type.key_type, CtyString)
        assert isinstance(val.type.value_type, CtyDynamic)
        assert val.value == raw_dict

    def test_validate_none_is_null_dynamic(self, dynamic_type: CtyDynamic) -> None:
        val = dynamic_type.validate(None)
        assert isinstance(val, CtyValue)
        assert val.type == dynamic_type
        assert val.is_null
        assert val.value is None

    def test_validate_unsupported_type_raises_error(
        self, dynamic_type: CtyDynamic
    ) -> None:
        class Unsupportable:
            pass

        with pytest.raises(
            CtyValidationError, match="Unsupported value for CtyDynamic"
        ):
            dynamic_type.validate(Unsupportable())


class TestCtyDynamicEqualUsableAs:
    def test_equal_true_same_type(self, dynamic_type: CtyDynamic) -> None:
        assert dynamic_type.equal(CtyDynamic())

    def test_equal_false_different_type(self, dynamic_type: CtyDynamic) -> None:
        assert not dynamic_type.equal(CtyString())

    def test_usable_as_true_same_type(self, dynamic_type: CtyDynamic) -> None:
        assert dynamic_type.usable_as(CtyDynamic())

    def test_usable_as_false_different_type(self, dynamic_type: CtyDynamic) -> None:
        assert not dynamic_type.usable_as(CtyString())


class TestCtyDynamicToPython:
    def test_to_python_no_value_attr(self, dynamic_type: CtyDynamic) -> None:
        assert dynamic_type.to_python() is None

    # def test_to_python_with_value_attr(self): # Test removed as CtyDynamic is frozen.
    #     dyn_type_inst = CtyDynamic()
    #     setattr(dyn_type_inst, 'value', "some_value")
    #     assert dyn_type_inst.to_python() == "some_value"
    #     delattr(dyn_type_inst, 'value')


class TestCtyDynamicDunderAndFlags:
    def test_str(self, dynamic_type: CtyDynamic) -> None:
        assert str(dynamic_type) == "CtyDynamic"

    def test_repr(self, dynamic_type: CtyDynamic) -> None:
        assert repr(dynamic_type) == "CtyDynamic()"

    def test_is_primitive(self, dynamic_type: CtyDynamic) -> None:
        assert dynamic_type.is_primitive_type()
