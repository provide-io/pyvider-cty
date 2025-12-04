#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


import pytest

from pyvider.cty import CtyDynamic, CtyList, CtyNumber, CtyString


class TestCtyListTypeComparison:
    @pytest.fixture
    def string_list_type(self) -> CtyList[str]:
        return CtyList(element_type=CtyString())

    def test_equal_same_element_type(self, string_list_type: CtyList[str]) -> None:
        other_string_list = CtyList(element_type=CtyString())
        assert string_list_type.equal(other_string_list), (
            "String list types with same element type should be equal"
        )
        assert string_list_type == other_string_list, (
            "String list types with same element type should be equal using == operator"
        )

    def test_equal_different_element_type(self, string_list_type: CtyList[str]) -> None:
        number_list_type = CtyList(element_type=CtyNumber())
        assert not string_list_type.equal(number_list_type), (
            "String list type should not equal number list type"
        )
        assert string_list_type != number_list_type, (
            "String list type should not equal number list type using != operator"
        )

    def test_equal_non_list_type(self, string_list_type: CtyList[str]) -> None:
        assert not string_list_type.equal(CtyString()), "List type should not equal non-list type"

    def test_usable_as_same_type(self, string_list_type: CtyList[str]) -> None:
        other_string_list = CtyList(element_type=CtyString())
        assert string_list_type.usable_as(other_string_list), (
            "String list type should be usable as same string list type"
        )

    def test_usable_as_different_type(self, string_list_type: CtyList[str]) -> None:
        number_list_type = CtyList(element_type=CtyNumber())
        assert not string_list_type.usable_as(number_list_type), (
            "String list type should not be usable as number list type"
        )

    def test_usable_as_dynamic(self, string_list_type: CtyList[str]) -> None:
        assert string_list_type.usable_as(CtyDynamic()), "String list type should be usable as dynamic type"


# 🌊🪢🔚
