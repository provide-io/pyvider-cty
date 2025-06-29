import pytest
import unicodedata
from pyvider.cty.types.primitives import CtyString
from pyvider.cty.values import CtyValue

# Test cases with strings that have different representations but normalize to the same NFC form
# For example, "é" can be represented as a single character (NFC) or 'e' + combining acute accent (NFD)
TEST_CASES = [
    ("e\u0301", "\u00e9"),  # NFD (e + combining acute) vs NFC (é)
    ("a\u0308", "\u00e4"),  # NFD (a + combining diaeresis) vs NFC (ä)
    ("o\u0308", "\u00f6"),  # NFD (o + combining diaeresis) vs NFC (ö)
    ("u\u0308", "\u00fc"),  # NFD (u + combining diaeresis) vs NFC (ü)
    ("n\u0303", "\u00f1"),  # NFD (n + combining tilde) vs NFC (ñ)
    # A more complex example: Angstrom symbol
    ("\u212B", "\u0041\u030A"),  # Angstrom Sign (single char) vs Latin Capital A + Combining Ring Above
    # Decomposed Hangul
    ("한", "한"), # (h + a + n) vs (han)
    ("ㄱㅡㄹ", "글"), # (g + eu + l) vs (geul)
    # String that is already NFC
    ("hello", "hello"),
    ("世界", "世界"),
]

@pytest.mark.parametrize("input_str, expected_nfc_str", TEST_CASES)
def test_string_nfc_normalization_on_validate(input_str: str, expected_nfc_str: str):
    """
    Tests that CtyString().validate() normalizes input strings to NFC.
    """
    cty_string_type = CtyString()

    # Validate the potentially non-NFC string
    validated_value: CtyValue = cty_string_type.validate(input_str)

    assert not validated_value.is_unknown, "Value should not be unknown"
    assert not validated_value.is_null, "Value should not be null"
    assert isinstance(validated_value.value, str), "Internal value should be a string"

    # Check that the stored string is NFC
    assert validated_value.value == expected_nfc_str, \
        f"String '{input_str}' was not normalized to NFC. Expected '{expected_nfc_str}', got '{validated_value.value}'"

    # Double check with unicodedata that the stored value is indeed NFC
    assert unicodedata.is_normalized('NFC', validated_value.value), \
        f"Stored value '{validated_value.value}' is not in NFC form according to unicodedata."

def test_validate_already_ctyvalue_string():
    """
    Tests that if a CtyValue(CtyString) is passed to validate, it's returned as is,
    assuming its internal value is already normalized (which it should be if created by validate).
    """
    cty_string_type = CtyString()

    # Create an initial CtyValue, which should be normalized
    original_nfd = "e\u0301"
    expected_nfc = "\u00e9"
    initial_cty_val = cty_string_type.validate(original_nfd)
    assert initial_cty_val.value == expected_nfc

    # Pass this already validated (and thus normalized) CtyValue back to validate
    revalidated_cty_val = cty_string_type.validate(initial_cty_val)

    assert revalidated_cty_val is initial_cty_val, "Validate should return the same CtyValue instance if type matches and already normalized"
    assert revalidated_cty_val.value == expected_nfc

def test_normalization_with_other_primitive_types():
    """
    Tests that conversion from other primitive types also results in an NFC normalized string.
    """
    cty_string_type = CtyString()

    # Example: an integer that becomes a string
    validated_int_val = cty_string_type.validate(123)
    assert validated_int_val.value == "123"
    assert unicodedata.is_normalized('NFC', validated_int_val.value)

    # Example: a boolean
    validated_bool_val = cty_string_type.validate(True)
    assert validated_bool_val.value == "True" # Python's str(True)
    assert unicodedata.is_normalized('NFC', validated_bool_val.value)

    # Example: a float (string representation should be NFC by default)
    validated_float_val = cty_string_type.validate(123.45)
    assert validated_float_val.value == "123.45"
    assert unicodedata.is_normalized('NFC', validated_float_val.value)

def test_nfc_normalization_for_empty_string():
    cty_string_type = CtyString()
    validated_value = cty_string_type.validate("")
    assert validated_value.value == ""
    assert unicodedata.is_normalized('NFC', validated_value.value)

def test_nfc_normalization_for_already_nfc_string():
    cty_string_type = CtyString()
    nfc_string = "déjà vu" # Already NFC
    validated_value = cty_string_type.validate(nfc_string)
    assert validated_value.value == nfc_string
    assert unicodedata.is_normalized('NFC', validated_value.value)

def test_nfc_normalization_for_nfd_string():
    cty_string_type = CtyString()
    nfd_string = unicodedata.normalize('NFD', "déjà vu")
    expected_nfc_string = "déjà vu"
    validated_value = cty_string_type.validate(nfd_string)
    assert validated_value.value == expected_nfc_string
    assert unicodedata.is_normalized('NFC', validated_value.value)

def test_nfc_normalization_for_nfkc_string_if_it_matters():
    # NFC should handle compatibility decompositions, but NFKC is stronger.
    # For cty, only NFC is typically required. This test is more exploratory.
    cty_string_type = CtyString()
    # Example: "ﬁ" (ligature) vs "fi"
    nfkc_input = "\ufb01" # LATIN SMALL LIGATURE FI
    expected_nfc_from_nfkc = "fi" # After NFKC

    # If we pass NFKC, it should become NFC of that.
    # unicodedata.normalize('NFC', nfkc_input) is still "\ufb01"
    # unicodedata.normalize('NFKC', nfkc_input) is "fi"
    # CtyString should perform NFC on the input. If input is "\ufb01", NFC of that is still "\ufb01".

    validated_value = cty_string_type.validate(nfkc_input)
    assert validated_value.value == nfkc_input # NFC of "\ufb01" is "\ufb01"
    assert unicodedata.is_normalized('NFC', validated_value.value)

    # If the source was already "fi", it stays "fi"
    validated_value_fi = cty_string_type.validate("fi")
    assert validated_value_fi.value == "fi"
    assert unicodedata.is_normalized('NFC', validated_value_fi.value)

@pytest.mark.parametrize(
    "non_string_input, expected_string_output",
    [
        (123, "123"),
        (True, "True"),
        (False, "False"),
        (123.45, "123.45"),
    ]
)
def test_nfc_normalization_from_other_types(non_string_input, expected_string_output):
    cty_string_type = CtyString()
    validated_value = cty_string_type.validate(non_string_input)
    assert validated_value.value == expected_string_output
    assert unicodedata.is_normalized('NFC', validated_value.value), \
        f"Value from {type(non_string_input).__name__} was not NFC normalized."
