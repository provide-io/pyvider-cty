import pytest
from pyvider.cty import CtyString, CtyNumber, CtyValue, CtyFunctionError
from pyvider.cty.functions import chomp, strrev, trimspace

class TestStringFunctions:
    @pytest.mark.parametrize("input_str, expected_str", [
        ("hello\n", "hello"),
        ("hello\r\n", "hello"),
        ("hello\n\r", "hello\n"), # rstrip will remove the \r, but not the \n before it
        ("hello", "hello"),
        ("\n", ""),
        ("\r\n", ""),
        ("", ""),
        ("multi\nline\n", "multi\nline"),
        ("multi\r\nline\r\n", "multi\r\nline"),
    ])
    def test_chomp_various_inputs(self, input_str, expected_str):
        cty_input = CtyString().validate(input_str)
        result = chomp(cty_input)
        assert result.value == expected_str

    def test_chomp_null_unknown(self):
        assert chomp(CtyValue.null(CtyString())).is_null
        assert chomp(CtyValue.unknown(CtyString())).is_unknown

    def test_chomp_invalid_type(self):
        with pytest.raises(CtyFunctionError):
            chomp(CtyNumber().validate(123))

    @pytest.mark.parametrize("input_str, expected_str", [
        ("hello", "olleh"),
        ("racecar", "racecar"),
        ("", ""),
        ("a", "a"),
        ("こんにちは", "はちにんこ"),
    ])
    def test_strrev_various_inputs(self, input_str, expected_str):
        cty_input = CtyString().validate(input_str)
        result = strrev(cty_input)
        assert result.value == expected_str

    def test_strrev_null_unknown(self):
        assert strrev(CtyValue.null(CtyString())).is_null
        assert strrev(CtyValue.unknown(CtyString())).is_unknown

    def test_strrev_invalid_type(self):
        with pytest.raises(CtyFunctionError):
            strrev(CtyNumber().validate(123))

    @pytest.mark.parametrize("input_str, expected_str", [
        ("  hello  ", "hello"),
        ("\t\n hello \r\x0c\x0b", "hello"),
        ("hello", "hello"),
        ("", ""),
        ("   ", ""),
        ("hello world", "hello world"),
        ("　こんにちは　", "こんにちは"),
    ])
    def test_trimspace_various_inputs(self, input_str, expected_str):
        cty_input = CtyString().validate(input_str)
        result = trimspace(cty_input)
        assert result.value == expected_str

    def test_trimspace_null_unknown(self):
        assert trimspace(CtyValue.null(CtyString())).is_null
        assert trimspace(CtyValue.unknown(CtyString())).is_unknown

    def test_trimspace_invalid_type(self):
        with pytest.raises(CtyFunctionError):
            trimspace(CtyNumber().validate(123))
