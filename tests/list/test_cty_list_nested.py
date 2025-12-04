#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


import pytest

from pyvider.cty import (
    CtyList,
    CtyNumber,
    CtyString,
    CtyValue,
)
from pyvider.cty.exceptions import CtyListValidationError


class TestCtyListWithNestedTypes:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.string_list = CtyList(element_type=CtyString())
        self.number_list = CtyList(element_type=CtyNumber())
        self.nested_list = CtyList(element_type=CtyList(element_type=CtyNumber()))

    def test_list_of_lists_of_strings(self) -> None:
        list_of_strings = CtyList(element_type=CtyString())
        list_of_lists = CtyList(element_type=list_of_strings)
        data = [["a", "b"], ["c", "d", "e"], ["f"]]
        result = list_of_lists.validate(data)
        assert isinstance(result, CtyValue) and isinstance(result.type, CtyList)
        assert len(result.value) == 3
        assert all(isinstance(item, CtyValue) and isinstance(item.type, CtyList) for item in result.value)
        assert [item.value for item in result.value[0].value] == ["a", "b"]

    def test_complex_nesting(self) -> None:
        inner_list = CtyList(element_type=CtyNumber())
        middle_list = CtyList(element_type=inner_list)
        outer_list = CtyList(element_type=middle_list)
        data = [[[1, 2], [3, 4]], [[5, 6, 7]], []]
        result = outer_list.validate(data)
        assert isinstance(result, CtyValue) and isinstance(result.type, CtyList)
        assert [item.value for item in result.value[0].value[0].value] == [1, 2]

    def test_validate_nested_list_with_errors(self) -> None:
        nested_list_type = CtyList(element_type=self.number_list)
        data = [[1, 2], [3, "four", 5]]
        with pytest.raises(CtyListValidationError):
            nested_list_type.validate(data)


# 🌊🪢🔚
