from pyvider.cty.types.primitives.bool import CtyBool
from pyvider.cty.values import UnknownValue


def test_validate_unknown_value() -> None:
    bool_type = CtyBool()
    unknown_value = UnknownValue()
    result = bool_type.validate(unknown_value)
    assert result.is_unknown
    assert result.type.equal(bool_type)


# 🐍🎯🧪🪄
