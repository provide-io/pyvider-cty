#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


import pytest

from pyvider.cty import CtyList, CtyString, CtyValue


class TestCtyListValueOperations:
    @pytest.fixture
    def string_list_val(self) -> CtyValue[list[str]]:
        list_type = CtyList(element_type=CtyString())
        return list_type.validate(["a", "b", "c", "d", "e"])

    def test_cty_list_access_methods(self, string_list_val: CtyValue[list[str]]) -> None:
        assert string_list_val[2].value == "c", f"Expected 'c' at index 2, but got {string_list_val[2].value}"
        sliced = string_list_val[::2]
        assert isinstance(sliced, CtyValue), f"Expected sliced result to be CtyValue, but got {type(sliced)}"
        assert [item.value for item in sliced.value] == ["a", "c", "e"], (
            f"Expected ['a', 'c', 'e'] from slice [::2], but got {[item.value for item in sliced.value]}"
        )

    def test_cty_list_slice(self, string_list_val: CtyValue[list[str]]) -> None:
        sliced = string_list_val[1:4]
        assert isinstance(sliced, CtyValue), f"Expected sliced result to be CtyValue, but got {type(sliced)}"
        assert [item.value for item in sliced.value] == ["b", "c", "d"], (
            f"Expected ['b', 'c', 'd'] from slice [1:4], but got {[item.value for item in sliced.value]}"
        )


# 🌊🪢🔚
