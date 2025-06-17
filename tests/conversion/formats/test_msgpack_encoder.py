#
# tests/conversion/formats/test_msgpack_encoder.py
#

from decimal import Decimal

import msgpack
import pytest

from pyvider.cty import CtyValue
from pyvider.cty.conversion.formats.msgpack import MsgPackEncoder
from pyvider.cty.exceptions import EncodingError
from pyvider.cty.types import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtySet,
    CtyString,
)


class TestMsgPackEncoder:
    def test_encode_decode_string(self) -> None:
        original_value = CtyValue.string("hello cty")
        encoder = MsgPackEncoder()
        encoded_data = encoder.encode(original_value)
        decoded_value = encoder.decode(encoded_data)
        assert decoded_value.type == CtyString()
        assert decoded_value.value == "hello cty"
        assert decoded_value == original_value

    def test_encode_decode_number_int(self) -> None:
        original_value = CtyValue.number(123)
        encoder = MsgPackEncoder()
        encoded_data = encoder.encode(original_value)
        decoded_value = encoder.decode(encoded_data)
        assert decoded_value.type == CtyNumber()
        assert decoded_value.value == Decimal(123)
        assert decoded_value == original_value

    def test_encode_decode_number_decimal(self) -> None:
        original_value = CtyValue.number(Decimal("123.456"))
        encoder = MsgPackEncoder()
        encoded_data = encoder.encode(original_value)
        decoded_value = encoder.decode(encoded_data)
        assert decoded_value.type == CtyNumber()
        assert decoded_value.value == Decimal("123.456")
        assert decoded_value == original_value

    def test_encode_decode_bool_true(self) -> None:
        original_value = CtyValue.bool(True)
        encoder = MsgPackEncoder()
        encoded_data = encoder.encode(original_value)
        decoded_value = encoder.decode(encoded_data)
        assert decoded_value.type == CtyBool()
        assert decoded_value.value is True
        assert decoded_value == original_value

    def test_encode_decode_bool_false(self) -> None:
        original_value = CtyValue.bool(False)
        encoder = MsgPackEncoder()
        encoded_data = encoder.encode(original_value)
        decoded_value = encoder.decode(encoded_data)
        assert decoded_value.type == CtyBool()
        assert decoded_value.value is False
        assert decoded_value == original_value

    def test_encode_decode_null_value(self) -> None:
        original_value = CtyValue.null(CtyString())
        encoder = MsgPackEncoder()
        encoded_data = encoder.encode(original_value)
        decoded_value = encoder.decode(encoded_data)
        assert decoded_value.is_null
        assert decoded_value.type == CtyString()
        assert decoded_value == original_value

    def test_encode_decode_unknown_value(self) -> None:
        original_value = CtyValue.unknown(CtyNumber())
        encoder = MsgPackEncoder()
        encoded_data = encoder.encode(original_value)
        decoded_value = encoder.decode(encoded_data)
        assert decoded_value.is_unknown
        assert decoded_value.type == CtyNumber()
        assert decoded_value.type == original_value.type
        assert decoded_value.is_unknown == original_value.is_unknown

    def test_encode_decode_simple_list_of_strings(self) -> None:
        list_type = CtyList(element_type=CtyString())
        original_value = list_type.validate(["a", "b", "c"])

        encoder = MsgPackEncoder()
        encoded_data = encoder.encode(original_value)
        decoded_value = encoder.decode(encoded_data)

        assert isinstance(decoded_value.type, CtyList)
        assert decoded_value.type.element_type == CtyString()
        assert decoded_value.value == [CtyValue.string("a"), CtyValue.string("b"), CtyValue.string("c")]
        assert decoded_value == original_value

    def test_encode_decode_simple_map_of_strings(self) -> None:
        map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
        original_value = map_type.validate({"key1": "val1", "key2": "val2"})

        expected_decoded_value_map = {
            "key1": CtyValue.string("val1"), "key2": CtyValue.string("val2")
        }

        encoder = MsgPackEncoder()
        encoded_data = encoder.encode(original_value)
        decoded_value = encoder.decode(encoded_data)

        assert isinstance(decoded_value.type, CtyMap)
        assert decoded_value.type.key_type == CtyString()
        assert decoded_value.type.value_type == CtyString()
        assert decoded_value.value == expected_decoded_value_map
        assert decoded_value == original_value


    def test_encode_non_cty_value_raises_type_error(self) -> None:
        encoder = MsgPackEncoder()
        with pytest.raises(EncodingError, match="Failed to encode to MessagePack: Expected CtyValue, got str"):
            encoder.encode("not a cty value")

    def test_decode_invalid_msgpack_raises_encoding_error(self) -> None:
        encoder = MsgPackEncoder()
        invalid_data = b"\xff\xff\xff"
        with pytest.raises(EncodingError, match="Invalid MessagePack"):
            encoder.decode(invalid_data)

    def test_encode_decode_list_with_mixed_types_dynamic(self) -> None:
        list_val_internal = [CtyValue.string("text"), CtyValue.number(100)]
        original_value = CtyList(element_type=CtyDynamic()).validate(list_val_internal)

        encoder = MsgPackEncoder()
        encoded_data = encoder.encode(original_value)
        decoded_value = encoder.decode(encoded_data)

        assert isinstance(decoded_value.type, CtyList)
        assert decoded_value.type.element_type == CtyDynamic()
        assert len(decoded_value.value) == 2
        assert decoded_value.value[0] == CtyValue.string("text")
        assert decoded_value.value[1] == CtyValue.number(100)
        assert decoded_value == original_value


    def test_encode_decode_decimal_precision(self) -> None:
        original_value = CtyValue.number(Decimal("0.12345678901234567890"))
        encoder = MsgPackEncoder()
        encoded_data = encoder.encode(original_value)
        decoded_value = encoder.decode(encoded_data)
        assert decoded_value.type == CtyNumber()
        assert decoded_value.value == Decimal("0.12345678901234567890")

    def test_encode_decode_empty_list(self) -> None:
        original_value = CtyList(element_type=CtyString()).validate([])
        encoder = MsgPackEncoder()
        encoded_data = encoder.encode(original_value)
        decoded_value = encoder.decode(encoded_data)
        assert isinstance(decoded_value.type, CtyList)
        assert decoded_value.type.element_type == CtyString()
        assert decoded_value.value == []
        assert decoded_value == original_value

    def test_encode_decode_empty_map(self) -> None:
        original_value = CtyMap(key_type=CtyString(), value_type=CtyNumber()).validate({})
        encoder = MsgPackEncoder()
        encoded_data = encoder.encode(original_value)
        decoded_value = encoder.decode(encoded_data)
        assert isinstance(decoded_value.type, CtyMap)
        assert decoded_value.type.key_type == CtyString()
        assert decoded_value.type.value_type == CtyNumber()
        assert decoded_value.value == {}
        assert decoded_value == original_value

    def test_decode_untyped_value_inference(self) -> None:
        encoder = MsgPackEncoder()

        raw_dict_string = {"value": "inferred"}
        packed_string = msgpack.packb(raw_dict_string)
        decoded_string = encoder.decode(packed_string, preserve_type=False)
        assert decoded_string == CtyValue.string("inferred")

        raw_dict_number = {"value": 123}
        packed_number = msgpack.packb(raw_dict_number)
        decoded_number = encoder.decode(packed_number, preserve_type=False)
        assert decoded_number == CtyValue.number(Decimal("123"))

        raw_dict_bool = {"value": True}
        packed_bool = msgpack.packb(raw_dict_bool)
        decoded_bool = encoder.decode(packed_bool, preserve_type=False)
        assert decoded_bool == CtyValue.bool(True)

        raw_dict_list = {"value": ["a", 1]}
        packed_list = msgpack.packb(raw_dict_list)
        decoded_list = encoder.decode(packed_list, preserve_type=False)
        assert isinstance(decoded_list.type, CtyList)
        assert decoded_list.type.element_type == CtyDynamic()
        assert decoded_list.value[0].type == CtyString() and decoded_list.value[0].value == "a"
        assert decoded_list.value[1].type == CtyNumber() and decoded_list.value[1].value == Decimal(1)

        raw_dict_map = {"value": {"k1": "v1", "k2": 2}}
        packed_map = msgpack.packb(raw_dict_map)
        decoded_map = encoder.decode(packed_map, preserve_type=False)
        assert isinstance(decoded_map.type, CtyMap)
        assert decoded_map.type.key_type == CtyString()
        assert decoded_map.type.value_type == CtyDynamic()
        assert decoded_map.value["k1"].type == CtyString() and decoded_map.value["k1"].value == "v1"
        assert decoded_map.value["k2"].type == CtyNumber() and decoded_map.value["k2"].value == Decimal(2)

    def test_encode_decode_with_marks(self) -> None:
        original_value = CtyValue.string("marked value").with_marks(("sensitive", "source:user"))
        encoder = MsgPackEncoder()
        encoded_data = encoder.encode(original_value)
        decoded_value = encoder.decode(encoded_data)
        assert decoded_value == original_value
        assert decoded_value.has_mark("sensitive")
        assert decoded_value.has_mark("source:user")

    def test_encode_decode_nested_list(self) -> None:
        inner_list_type = CtyList(element_type=CtyNumber())
        list_of_lists_type = CtyList(element_type=inner_list_type)
        original_value = list_of_lists_type.validate([[1, 2], [3, 4]])

        encoder = MsgPackEncoder()
        encoded_data = encoder.encode(original_value)
        decoded_value = encoder.decode(encoded_data)
        # This test will fail due to encoder bug (nested element type becomes dynamic)
        # until msgpack.py's _create_type_from_name and _value_to_dict are enhanced.
        assert decoded_value == original_value

    def test_encode_decode_map_with_list_value(self) -> None:
        list_type = CtyList(element_type=CtyNumber())
        map_type = CtyMap(key_type=CtyString(), value_type=list_type)
        original_value = map_type.validate({"list_key": [10, 20]})

        encoder = MsgPackEncoder()
        encoded_data = encoder.encode(original_value)
        decoded_value = encoder.decode(encoded_data)
        # This test will fail due to encoder bug (nested list's element type becomes dynamic)
        # until msgpack.py's _create_type_from_name and _value_to_dict are enhanced.
        assert decoded_value == original_value


    def test_decode_unknown_marker_no_type_preservation(self) -> None:
        raw_dict_unknown_no_type = {MsgPackEncoder.UNKNOWN_MARKER: True}
        packed_unknown_no_type = msgpack.packb(raw_dict_unknown_no_type)
        encoder = MsgPackEncoder()
        decoded_value = encoder.decode(packed_unknown_no_type, preserve_type=False)
        assert decoded_value.is_unknown
        assert decoded_value.type == CtyDynamic()

    def test_decode_null_marker_no_type_preservation(self) -> None:
        raw_dict_null_no_type = {MsgPackEncoder.NULL_MARKER: True}
        packed_null_no_type = msgpack.packb(raw_dict_null_no_type)
        encoder = MsgPackEncoder()
        decoded_value = encoder.decode(packed_null_no_type, preserve_type=False)
        assert decoded_value.is_null
        assert decoded_value.type == CtyDynamic()

    def test_encode_decode_dynamic_value_resolved(self) -> None:
        original_value = CtyValue(CtyDynamic(), "dynamic string")
        encoder = MsgPackEncoder()
        encoded_data = encoder.encode(original_value)
        decoded_value = encoder.decode(encoded_data, preserve_type=True)
        assert decoded_value.type == CtyString()
        assert decoded_value.value == "dynamic string"

    def test_msgpack_default_raises_typeerror_for_unsupported(self) -> None:
        class Unsupported: pass
        with pytest.raises(TypeError, match="Object of type Unsupported is not MessagePack serializable"):
            MsgPackEncoder._msgpack_default(Unsupported())

    def test_encode_options_use_bin_type(self) -> None:
        original_value = CtyValue.string("binary data")
        encoder = MsgPackEncoder()
        encoded_bin_true = encoder.encode(original_value, use_bin_type=True)
        decoded_bin_true = encoder.decode(encoded_bin_true)
        assert decoded_bin_true == original_value
        encoded_bin_false = encoder.encode(original_value, use_bin_type=False)
        decoded_bin_false = encoder.decode(encoded_bin_false)
        assert decoded_bin_false == original_value

    def test_decode_options_raw_bytes_incompatible(self) -> None:
        original_value = CtyValue.string("test")
        encoder = MsgPackEncoder()
        encoded_data = encoder.encode(original_value)
        decoded_raw_false = encoder.decode(encoded_data, raw=False)
        assert decoded_raw_false == original_value

        decoded_raw_true = encoder.decode(encoded_data, raw=True)
        assert decoded_raw_true.type == CtyDynamic()
        # Additional logging for debugging the is_null issue
        is_null_result = decoded_raw_true.is_null
        print(f"DEBUG_TEST: decoded_raw_true object: {decoded_raw_true!r}")
        print(f"DEBUG_TEST: is_null_result: {is_null_result!r}")
        print(f"DEBUG_TEST: type(is_null_result): {type(is_null_result)}")
        assert not is_null_result
        assert decoded_raw_true.value == b"test" # Moved this assertion after is_null debugging
        assert not decoded_raw_true.is_unknown

    def test_encode_decode_set_of_strings(self) -> None:
        set_type = CtySet(element_type=CtyString())
        original_value = set_type.validate(frozenset({"apple", "banana", "cherry"}))

        encoder = MsgPackEncoder()
        encoded_data = encoder.encode(original_value)
        decoded_value = encoder.decode(encoded_data)

        assert isinstance(decoded_value.type, CtySet)
        assert decoded_value.type.element_type == CtyString()

        expected_internal_set_elements = {CtyValue.string("apple"), CtyValue.string("banana"), CtyValue.string("cherry")}
        assert isinstance(decoded_value.value, frozenset) # CtySet internal value is a frozenset of CtyValues
        assert decoded_value.value == expected_internal_set_elements # Direct comparison of frozensets of CtyValues

    # --- Tests for CtyUnknown with ExtType(0) ---

    def test_unknown_value_serialization_exttype(self) -> None:
        """Test that CtyUnknown values serialize to msgpack.ExtType(0, b'')."""
        unknown_string_val = CtyValue.unknown(CtyString())
        unknown_number_val = CtyValue.unknown(CtyNumber())

        expected_msgpack_bytes = msgpack.packb(msgpack.ExtType(0, b''))

        assert unknown_string_val.to_msgpack_bytes() == expected_msgpack_bytes
        assert unknown_number_val.to_msgpack_bytes() == expected_msgpack_bytes

    def test_unknown_value_deserialization_exttype(self) -> None:
        """Test that msgpack.ExtType(0, b'') deserializes to CtyUnknown of the target type."""
        unknown_ext_bytes = msgpack.packb(msgpack.ExtType(0, b''))

        # Deserialize as CtyString
        deserialized_val_str = CtyValue.from_msgpack_bytes(unknown_ext_bytes, CtyString())
        assert deserialized_val_str.is_unknown is True
        assert isinstance(deserialized_val_str.type, CtyString)
        with pytest.raises(ValueError): # Cannot access value of unknown
            _ = deserialized_val_str.value

        # Deserialize as CtyNumber
        deserialized_val_num = CtyValue.from_msgpack_bytes(unknown_ext_bytes, CtyNumber())
        assert deserialized_val_num.is_unknown is True
        assert isinstance(deserialized_val_num.type, CtyNumber)
        with pytest.raises(ValueError):
            _ = deserialized_val_num.value

        # Deserialize as CtyDynamic
        deserialized_val_dyn = CtyValue.from_msgpack_bytes(unknown_ext_bytes, CtyDynamic())
        assert deserialized_val_dyn.is_unknown is True
        assert isinstance(deserialized_val_dyn.type, CtyDynamic)
        with pytest.raises(ValueError):
            _ = deserialized_val_dyn.value

    def test_known_value_msgpack_does_not_use_exttype0(self) -> None:
        """Sanity check: known values should not serialize to ExtType(0, b'')."""
        known_val = CtyValue.string("hello")
        msgpack_bytes = known_val.to_msgpack_bytes()

        # Check it's not the unknown sentinel
        assert msgpack_bytes != msgpack.packb(msgpack.ExtType(0, b''))

        # Check it's a valid msgpack dict (map)
        unpacked_data = msgpack.unpackb(msgpack_bytes, raw=False)
        assert isinstance(unpacked_data, dict)
        assert unpacked_data.get("type_name") == "string" # As per _value_to_serializable via to_json_comparable_dict
        assert unpacked_data.get("value") == "hello"

        # Full deserialization check
        deserialized_known = CtyValue.from_msgpack_bytes(msgpack_bytes, CtyString())
        assert deserialized_known.is_unknown is False
        assert deserialized_known.value == "hello"

    def test_encode_decode_dynamic_wrapping_cty_value(self) -> None:
        """Test encoding/decoding of a CtyDynamic value that wraps another CtyValue."""
        encoder = MsgPackEncoder()

        # 1. Create an inner CtyValue (e.g., CtyString)
        inner_value = CtyValue.string("hello_dynamic_world")

        # 2. Create an outer CtyDynamic value that wraps the inner CtyValue
        # CtyDynamic().validate(inner_value) achieves CtyValue(CtyDynamic, inner_value)
        original_dynamic_value = CtyDynamic().validate(inner_value)

        assert isinstance(original_dynamic_value.type, CtyDynamic), "Outer type should be CtyDynamic"
        assert isinstance(original_dynamic_value.value, CtyValue), "Inner value should be a CtyValue instance"
        assert original_dynamic_value.value.type == CtyString(), "Inner CtyValue's type should be CtyString"
        assert original_dynamic_value.value.value == "hello_dynamic_world", "Inner CtyValue's raw value is incorrect"

        # 3. Encode the outer dynamic value
        encoded_data = encoder.encode(original_dynamic_value)

        # 4. Decode the encoded data
        # When decoding, we expect the outer type to be CtyDynamic.
        # The fix ensures the inner CtyValue is also properly reconstructed.
        decoded_dynamic_value = encoder.decode(encoded_data)

        # 5. Assertions
        assert isinstance(decoded_dynamic_value, CtyValue), "Decoded value should be a CtyValue"
        assert isinstance(decoded_dynamic_value.type, CtyDynamic), "Decoded outer type should be CtyDynamic"
        assert not decoded_dynamic_value.is_null, "Decoded value should not be null"
        assert not decoded_dynamic_value.is_unknown, "Decoded value should not be unknown"

        # Check the inner wrapped CtyValue
        inner_decoded_value = decoded_dynamic_value.value
        assert isinstance(inner_decoded_value, CtyValue), "Decoded inner value should be a CtyValue instance"
        assert inner_decoded_value.type == CtyString(), "Decoded inner CtyValue's type should be CtyString"
        assert inner_decoded_value.value == "hello_dynamic_world", "Decoded inner CtyValue's raw value is incorrect"

        # Overall equality check
        assert decoded_dynamic_value == original_dynamic_value, "Decoded dynamic value should equal the original"

        # Test with a number as well
        inner_number_value = CtyValue.number(12345)
        original_dynamic_number = CtyDynamic().validate(inner_number_value)
        encoded_number_data = encoder.encode(original_dynamic_number)
        decoded_dynamic_number = encoder.decode(encoded_number_data)

        assert isinstance(decoded_dynamic_number.type, CtyDynamic)
        inner_decoded_number = decoded_dynamic_number.value
        assert isinstance(inner_decoded_number, CtyValue)
        assert inner_decoded_number.type == CtyNumber()
        assert inner_decoded_number.value == Decimal(12345)
        assert decoded_dynamic_number == original_dynamic_number

    def test_encode_decode_dynamic_wrapping_list(self) -> None:
        """Test CtyDynamic wrapping a CtyList."""
        encoder = MsgPackEncoder()
        # Correct way to create a CtyList value
        list_type = CtyList(element_type=CtyString()) # Fixed: use keyword argument
        inner_list_value = list_type.validate(["a", "b"])
        original_value = CtyDynamic().validate(inner_list_value)

        encoded_data = encoder.encode(original_value)
        decoded_value = encoder.decode(encoded_data)

        assert isinstance(decoded_value.type, CtyDynamic)
        assert isinstance(decoded_value.value, CtyValue)
        assert decoded_value.value.type == CtyList(element_type=CtyString()) # Fixed: use keyword argument
        assert decoded_value.value.value[0].value == "a"
        assert decoded_value.value.value[1].value == "b"
        assert decoded_value == original_value

    def test_decode_dynamic_wrapping_malformed_inner_ctyvalue(self) -> None:
        """Test decoding CtyDynamic where inner value is a dict that looks like CtyValue but is malformed."""
        encoder = MsgPackEncoder()
        # Craft a payload where the inner value is a dictionary representing a CtyValue,
        # but its *type definition* is malformed. Specifically, a CtyList whose
        # element type specification ($E) is not a valid type representation (e.g., an int).
        # This should cause _create_type_from_name() for the inner CtyList's element type
        # to raise an EncodingError (due to the NameError for CtyTypeParseError, or directly if fixed).
        # This EncodingError should then cause the inner _dict_to_value() call to fail.
        # This failure will trigger the 'except Exception' block in the _create_typed_value
        # method (when handling the outer CtyDynamic type), and CtyDynamic().validate()
        # will then be called with the raw malformed_inner_payload_dict dictionary.
        # IMPORTANT: Keys in malformed_inner_payload_dict must be strings if we expect
        # CtyMap(CtyString(), CtyDynamic()).validate() to succeed on it after the fallback.
        malformed_inner_payload_dict = {
            MsgPackEncoder.TYPE_MARKER: "CtyList",
            "$E": 12345, # String key, but value 12345 is invalid for an element type spec
            "value": [1,2]
        }

        outer_dynamic_dict = {
            MsgPackEncoder.TYPE_MARKER: "CtyDynamic",
            "value": malformed_inner_payload_dict
        }

        encoded_data = msgpack.packb(outer_dynamic_dict, default=MsgPackEncoder._msgpack_default, use_bin_type=True)

        # The decode process:
        # 1. Outer type is CtyDynamic. Inner value is malformed_inner_payload_dict.
        # 2. _dict_to_value(malformed_inner_payload_dict) is called.
        # 3. This fails because _create_type_from_name for "$E": 12345 raises EncodingError.
        # 4. The 'except Exception' in _create_typed_value (for CtyDynamic) catches this.
        # 5. processed_value_data remains malformed_inner_payload_dict.
        # 6. CtyDynamic().validate(malformed_inner_payload_dict) is called.
        # 7. This becomes CtyMap(CtyString(), CtyDynamic()).validate(malformed_inner_payload_dict).
        # 8. This map validation succeeds because all keys are strings.

        decoded_value = encoder.decode(encoded_data)

        assert isinstance(decoded_value.type, CtyMap), \
            f"Expected decoded type to be CtyMap after fallback, got {decoded_value.type}"
        assert decoded_value.type.key_type == CtyString()
        assert decoded_value.type.value_type == CtyDynamic()

        expected_map_content = {
            MsgPackEncoder.TYPE_MARKER: CtyValue.string("CtyList"),
            "$E": CtyValue.number(12345),
            "value": CtyValue.list(CtyDynamic(), [CtyValue.number(1), CtyValue.number(2)])
        }
        assert decoded_value.value == expected_map_content, \
            f"Map content mismatch. Got: {decoded_value.value}, Expected: {expected_map_content}"
