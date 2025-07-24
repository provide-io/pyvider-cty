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
        assert cty_to_native(123) == 123
        assert cty_to_native(None) is None

    def test_cty_to_native_nested_collections(self) -> None:
        list_type = CtyList(element_type=CtyList(element_type=CtyNumber()))
        cty_val = list_type.validate([[1, 2], [3]])
        native_val = cty_to_native(cty_val)
        assert native_val == [[1, 2], [3]]

    def test_cty_to_native_with_set_and_tuple(self) -> None:
        from pyvider.cty import CtySet, CtyTuple

        set_type = CtySet(element_type=CtyString())
        cty_set = set_type.validate({"a", "b"})
        assert sorted(cty_to_native(cty_set)) == ["a", "b"]

        set_type_num = CtySet(element_type=CtyNumber())
        cty_set_num = set_type_num.validate({1, 2})
        assert sorted(cty_to_native(cty_set_num)) == [1, 2]

        tuple_type = CtyTuple(element_types=(CtyString(), CtyNumber()))
        cty_tuple = tuple_type.validate(("a", 1))
        assert cty_to_native(cty_tuple) == ("a", 1)

        tuple_type_mixed = CtyTuple(
            element_types=(
                CtyString(),
                CtyNumber(),
                CtyList(element_type=CtyString()),
            )
        )
        cty_tuple_mixed = tuple_type_mixed.validate(("a", 1, ["b", "c"]))
        assert cty_to_native(cty_tuple_mixed) == ("a", 1, ["b", "c"])

    def test_cty_to_native_with_repeated_values(self) -> None:
        """Test cty_to_native with a list containing repeated values."""
        list_type = CtyList(element_type=CtyString())
        cty_val = list_type.validate(["a", "b", "a"])
        native_val = cty_to_native(cty_val)
        assert native_val == ["a", "b", "a"]
