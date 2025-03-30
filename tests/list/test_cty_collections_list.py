#
# tests/list/test_cty_collections_list.py
#
import pytest

from pyvider.cty.exceptions import CtyListValidationError
from pyvider.cty import CtyBool, CtyList, CtyNumber, CtyString, CtyTuple


def test_cty_list_large_list():
    """Test validation of a large list."""
    large_list = CtyList(element_type=CtyString())
    data = ["item"] * 1000
    validated = large_list.validate(data)

    # Test that we get back a CtyList
    assert isinstance(validated, CtyList)

    # Test that the length is correct
    assert len(validated) == 1000

    # Test that all elements are CtyString objects with value "item"
    for item in validated.value:
        assert isinstance(item, CtyString)
        assert item.value == "item"

def test_cty_list_dynamic_schema():
    """Test validation with dynamically nested structure."""
    dynamic_list = CtyList(element_type=CtyList(element_type=CtyString()))
    validated = dynamic_list.validate([["one", "two"], ["three"]])

    # Test that we get back a CtyList
    assert isinstance(validated, CtyList)

    # Test that the first element is a CtyList with CtyString values
    assert isinstance(validated[0], CtyList)
    assert len(validated[0].value) == 2
    assert isinstance(validated[0][0], CtyString)
    assert validated[0][0].value == "one"
    assert isinstance(validated[0][1], CtyString)
    assert validated[0][1].value == "two"

    # Test that the second element is a CtyList with a CtyString value
    assert isinstance(validated[1], CtyList)
    assert len(validated[1].value) == 1
    assert isinstance(validated[1][0], CtyString)
    assert validated[1][0].value == "three"

# 🐍🏗️🧪
