import pytest
from decimal import Decimal

from pyvider.cty import (
    CtyBool, CtyDynamic, CtyList, CtyMap, CtyNumber, CtyObject, CtyString,
    CtyTuple, CtyValue
)
# FIX: Removed import of deleted function 'infer_and_wrap_native'
from pyvider.cty.conversion.raw_to_cty import infer_cty_type_from_raw

@pytest.mark.parametrize("raw_value, expected_type_cls", [
    ("hello", CtyString), (123, CtyNumber), (3.14, CtyNumber),
    (Decimal("99.9"), CtyNumber), (True, CtyBool), (None, CtyDynamic),
])
def test_infer_primitive_types(raw_value, expected_type_cls):
    """Tests that the type inference correctly identifies primitive types."""
    inferred_type = infer_cty_type_from_raw(raw_value)
    assert isinstance(inferred_type, expected_type_cls)
