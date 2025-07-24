import pytest

from pyvider.cty import CtyNumber, CtyString


class TestCtyValueBaseCoverage:
    def test_len_on_unsupported_type(self) -> None:
        num_val = CtyNumber().validate(123)
        with pytest.raises(TypeError, match="has no len()"):
            len(num_val)

    def test_iter_on_unsupported_type(self) -> None:
        num_val = CtyNumber().validate(123)
        with pytest.raises(TypeError, match="is not iterable"):
            list(num_val)

    def test_getitem_on_unsupported_type(self) -> None:
        str_val = CtyString().validate("hello")
        with pytest.raises(TypeError, match="is not subscriptable"):
            _ = str_val[0]
