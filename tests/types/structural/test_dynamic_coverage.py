from pyvider.cty.types import CtyDynamic, CtyList, CtyString


def test_validate_with_wire_format_invalid_json() -> None:
    dynamic_type = CtyDynamic()
    value = [b"{not-json}", "hello"]
    result = dynamic_type.validate(value)
    
    # The result should be a CtyDynamic value wrapping a CtyList
    assert isinstance(result.type, CtyDynamic)
    assert isinstance(result.value.type, CtyList)
    assert result.value.type.element_type.equal(CtyString())
    # The raw value should contain the original bytes object, which gets decoded
    assert result.raw_value == ["{not-json}", "hello"]
