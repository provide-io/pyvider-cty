import pytest

from pyvider.cty import CtyList, CtyNumber, CtyString, CtyValue
from pyvider.cty.conversion import cty_to_native


class TestAdapterCoverage:
    def test_cty_to_native_unknown_raises_error(self) -> None:
        unknown_val = CtyValue.unknown(CtyString())
        with pytest.raises(ValueError, match="Cannot convert an unknown CtyValue"):
            cty_to_native(unknown_val)

    def test_cty_to_native_already_native(self) -> None:
        assert cty_to_native("already native") == "already native"

    def test_cty_to_native_nested_collections(self) -> None:
        list_type = CtyList(element_type=CtyList(element_type=CtyNumber()))
        cty_val = list_type.validate([[1, 2], [3]])
        native_val = cty_to_native(cty_val)
        assert native_val == [[1, 2], [3]]
