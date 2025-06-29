# pyvider-cty/tests/functions/test_string_functions.py
import pytest
from pyvider.cty import CtyString, CtyNumber, CtyValue
from pyvider.cty.functions.string_functions import chomp, strrev, trimspace
from pyvider.cty.exceptions import CtyFunctionError

class TestStringFunctions:

    # --- Tests for chomp ---
    @pytest.mark.parametrize("input_str, expected_str", [
        ("hello\n", "hello"),
        ("hello\r\n", "hello"),
        ("hello\n\r", "hello\n\r"), # Not a standard single newline
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
        assert isinstance(result.type, CtyString)

    def test_chomp_null_unknown(self):
        null_val = CtyValue.null(CtyString())
        unknown_val = CtyValue.unknown(CtyString())
        assert chomp(null_val) is null_val
        assert chomp(unknown_val) is unknown_val

    def test_chomp_invalid_type(self):
        num_val = CtyNumber().validate(123)
        with pytest.raises(CtyFunctionError, match="chomp: input must be a string, got number"):
            chomp(num_val)

    # --- Tests for strrev ---
    @pytest.mark.parametrize("input_str, expected_str", [
        ("hello", "olleh"),
        ("racecar", "racecar"),
        ("", ""),
        ("a", "a"),
        ("こんにちは", "はちにんこ"), # Unicode test
    ])
    def test_strrev_various_inputs(self, input_str, expected_str):
        cty_input = CtyString().validate(input_str)
        result = strrev(cty_input)
        assert result.value == expected_str
        assert isinstance(result.type, CtyString)

    def test_strrev_null_unknown(self):
        null_val = CtyValue.null(CtyString())
        unknown_val = CtyValue.unknown(CtyString())
        assert strrev(null_val) is null_val
        assert strrev(unknown_val) is unknown_val

    def test_strrev_invalid_type(self):
        num_val = CtyNumber().validate(123)
        with pytest.raises(CtyFunctionError, match="strrev: input must be a string, got number"):
            strrev(num_val)

    # --- Tests for trimspace ---
    @pytest.mark.parametrize("input_str, expected_str", [
        ("  hello  ", "hello"),
        ("\t\n hello \r\f\v", "hello"), # All Python standard whitespace chars
        ("hello", "hello"),
        ("", ""),
        ("   ", ""),
        ("hello world", "hello world"), # Inner space preserved
        ("　こんにちは　", "こんにちは"), # Full-width space (Unicode whitespace)
    ])
    def test_trimspace_various_inputs(self, input_str, expected_str):
        cty_input = CtyString().validate(input_str)
        result = trimspace(cty_input)
        assert result.value == expected_str
        assert isinstance(result.type, CtyString)

    def test_trimspace_null_unknown(self):
        null_val = CtyValue.null(CtyString())
        unknown_val = CtyValue.unknown(CtyString())
        assert trimspace(null_val) is null_val
        assert trimspace(unknown_val) is unknown_val

    def test_trimspace_invalid_type(self):
        num_val = CtyNumber().validate(123)
        with pytest.raises(CtyFunctionError, match="trimspace: input must be a string, got number"):
            trimspace(num_val)
