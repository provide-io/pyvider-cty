from decimal import Decimal
import pytest
from pyvider.cty import CtyBool, CtyDynamic, CtyList, CtyMap, CtyNumber, CtyObject, CtySet, CtyString, CtyTuple, CtyValue

@pytest.fixture
def string_type() -> CtyString: return CtyString()
@pytest.fixture
def list_of_string_type(string_type: CtyString) -> CtyList: return CtyList(element_type=string_type)

def test_empty_value_for_collections(list_of_string_type):
    assert CtyList(element_type=CtyString()).validate([]).is_empty() is True
    assert CtyMap(element_type=CtyNumber()).validate({}).is_empty() is True
    assert CtySet(element_type=CtyBool()).validate(set()).is_empty() is True
