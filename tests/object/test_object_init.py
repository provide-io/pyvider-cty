import pytest
from pyvider.cty import (
    CtyBool, CtyNumber, CtyObject, CtyString,
)
from pyvider.cty.exceptions import CtyValidationError, InvalidTypeError

@pytest.mark.asyncio
async def test_object_init_empty() -> None:
    obj = CtyObject()
    assert obj.attribute_types == {}
    assert obj.optional_attributes == frozenset()

@pytest.mark.asyncio
async def test_object_init_with_attributes() -> None:
    obj = CtyObject(attribute_types={"name": CtyString(), "age": CtyNumber(), "active": CtyBool()})
    assert set(obj.attribute_types.keys()) == {"name", "age", "active"}
    assert isinstance(obj.attribute_types["name"], CtyString)
    assert obj.optional_attributes == frozenset()

@pytest.mark.asyncio
async def test_object_init_with_optional_attributes() -> None:
    obj = CtyObject(
        attribute_types={"name": CtyString(), "age": CtyNumber()},
        optional_attributes=frozenset(["age"]),
    )
    assert set(obj.attribute_types.keys()) == {"name", "age"}
    assert obj.optional_attributes == frozenset(["age"])

@pytest.mark.asyncio
async def test_object_init_invalid_attribute_type() -> None:
    # FIX: With the new __attrs_post_init__ hook, this now raises InvalidTypeError at construction.
    with pytest.raises(InvalidTypeError):
        CtyObject(attribute_types={"name": CtyString(), "age": "not a type"})

@pytest.mark.asyncio
async def test_object_init_invalid_optional_attribute() -> None:
    obj = CtyObject(
        attribute_types={"name": CtyString(), "age": CtyNumber()},
        optional_attributes=frozenset(["unknown"]),
    )
    # Validation for unknown optionals happens at validation time, not construction.
    with pytest.raises(CtyValidationError, match="Unknown optional attributes: unknown"):
        obj.validate({"name": "test", "age": 1})
