from pyvider.cty.types.primitives.number import CtyNumber
from pyvider.cty.values import UnknownValue


def test_validate_unknown_value() -> None:
    number_type = CtyNumber()
    unknown_value = UnknownValue()
    result = number_type.validate(unknown_value)
    assert result.is_unknown
    assert result.type.equal(number_type)


# 🐍🎯🧪🪄
