import pytest
from pyvider.cty import CtyObject, CtyString, CtyNumber, CtyValue
from pyvider.cty.exceptions import CtyAttributeValidationError, CtyTypeMismatchError

@pytest.mark.asyncio
async def test_attribute_access_error_handling() -> None:
    person_type = CtyObject(attribute_types={"name": CtyString(), "age": CtyNumber()})
    validated = person_type.validate({"name": "Alice", "age": 30})
    with pytest.raises(CtyAttributeValidationError):
        person_type.get_attribute(validated, "unknown")
    with pytest.raises(CtyTypeMismatchError):
        person_type.get_attribute("not a cty value", "name")
