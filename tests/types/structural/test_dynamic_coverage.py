import pytest
from pyvider.cty.types.structural.dynamic import CtyDynamic
from pyvider.cty.values import CtyValue
from pyvider.cty.types import CtyString

from pyvider.cty.types import CtyList


def test_validate_with_wire_format_invalid_json():
    dynamic_type = CtyDynamic()
    value = [b"{not-json}", "hello"]
    result = dynamic_type.validate(value)
    assert result.type.equal(CtyList(element_type=CtyString()))
    assert result.value[0].value == "{not-json}"
    assert result.value[1].value == "hello"
