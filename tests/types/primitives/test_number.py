from decimal import Decimal

import pytest

from pyvider.cty import CtyDynamic, CtyNumber, CtyString
from pyvider.cty.exceptions import CtyNumberValidationError
from pyvider.cty.values import CtyValue


class TestCtyNumber:
    def setup_method(self) -> None:
        self.number_type = CtyNumber()

    def test_validate_cty_value(self) -> None:
        cty_val = CtyValue(CtyNumber(), Decimal("123"))
        result = self.number_type.validate(cty_val)
        assert result.value == Decimal("123")

    def test_validate_cty_value_null(self) -> None:
        cty_val = CtyValue.null(CtyNumber())
        result = self.number_type.validate(cty_val)
        assert result.is_null

    def test_validate_cty_value_unknown(self) -> None:
        cty_val = CtyValue.unknown(CtyNumber())
        result = self.number_type.validate(cty_val)
        assert result.is_unknown

    def test_validate_unknown_value(self) -> None:
        from pyvider.cty.values import CtyValue

        result = self.number_type.validate(CtyValue.unknown(self.number_type))
        assert result.is_unknown

    def test_validate_bool(self) -> None:
        result = self.number_type.validate(True)
        assert result.value == 1
        result = self.number_type.validate(False)
        assert result.value == 0

    def test_validate_invalid_value_raises_exception(self) -> None:
        with pytest.raises(CtyNumberValidationError):
            self.number_type.validate("not a number")

    def test_usable_as(self) -> None:
        assert self.number_type.usable_as(CtyNumber())
        assert self.number_type.usable_as(CtyDynamic())
        assert not self.number_type.usable_as(CtyString())


# 🐍🎯🧪🪄
