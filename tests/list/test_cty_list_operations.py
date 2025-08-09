import pytest

from pyvider.cty import CtyList, CtyString, CtyValue


class TestCtyListValueOperations:
    @pytest.fixture
    def string_list_val(self) -> CtyValue[list[str]]:
        list_type = CtyList(element_type=CtyString())
        return list_type.validate(["a", "b", "c", "d", "e"])

    def test_cty_list_access_methods(
        self, string_list_val: CtyValue[list[str]]
    ) -> None:
        assert string_list_val[2].value == "c"
        sliced = string_list_val[::2]
        assert isinstance(sliced, CtyValue)
        assert [item.value for item in sliced.value] == ["a", "c", "e"]

    def test_cty_list_slice(self, string_list_val: CtyValue[list[str]]) -> None:
        sliced = string_list_val[1:4]
        assert isinstance(sliced, CtyValue)
        assert [item.value for item in sliced.value] == ["b", "c", "d"]


# 🐍🎯🧪🪄
