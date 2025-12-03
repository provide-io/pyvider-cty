#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from pyvider.cty import (
    CtyList,
    CtyString,
    CtyValue,
)


def test_cty_list_large_list() -> None:
    """Test validation of a large list."""
    large_list = CtyList(element_type=CtyString())
    data = ["item"] * 1000
    validated = large_list.validate(data)

    # Test that we get back a CtyValue containing a list
    assert isinstance(validated, CtyValue)
    assert isinstance(validated.type, CtyList)

    # Test that the length is correct
    assert len(validated) == 1000

    # Test that all elements are CtyString values
    for item in validated.value:
        assert isinstance(item, CtyValue)
        assert isinstance(item.type, CtyString)
        assert item.value == "item"


def test_cty_list_dynamic_schema() -> None:
    """Test validation with dynamically nested structure."""
    dynamic_list = CtyList(element_type=CtyList(element_type=CtyString()))
    validated = dynamic_list.validate([["one", "two"], ["three"]])

    # Test that we get back a CtyValue containing a list
    assert isinstance(validated, CtyValue)
    assert isinstance(validated.type, CtyList)

    # Test that the first element is a CtyValue containing a CtyList with CtyString values
    assert isinstance(validated.value[0], CtyValue)
    assert isinstance(validated.value[0].type, CtyList)
    assert len(validated.value[0].value) == 2
    assert isinstance(validated.value[0].value[0], CtyValue)
    assert isinstance(validated.value[0].value[0].type, CtyString)
    assert validated.value[0].value[0].value == "one"
    assert isinstance(validated.value[0].value[1], CtyValue)
    assert isinstance(validated.value[0].value[1].type, CtyString)
    assert validated.value[0].value[1].value == "two"

    # Test that the second element is a CtyValue containing a CtyList with CtyString values
    assert isinstance(validated.value[1], CtyValue)
    assert isinstance(validated.value[1].type, CtyList)
    assert len(validated.value[1].value) == 1
    assert isinstance(validated.value[1].value[0], CtyValue)
    assert isinstance(validated.value[1].value[0].type, CtyString)
    assert validated.value[1].value[0].value == "three"


# 🌊🪢🔚
