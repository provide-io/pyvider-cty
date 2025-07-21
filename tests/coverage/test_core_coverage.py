import msgpack
import pytest

from pyvider.cty import (
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyValue,
)
from pyvider.cty.codec import _ext_hook, cty_to_msgpack
from pyvider.cty.conversion import cty_to_native, infer_cty_type_from_raw
from pyvider.cty.conversion.type_encoder import encode_cty_type_to_wire_json
from pyvider.cty.exceptions import (
    AttributePathError,
    CtyAttributeValidationError,
    DeserializationError,
)
from pyvider.cty.path import CtyPath


class TestCodecCoverage:
    def test_ext_hook_with_malformed_payload(self) -> None:
        malformed_payload = b"\x81\x01"  # Incomplete msgpack map
        with pytest.raises(
            DeserializationError, match="Failed to decode refined unknown payload"
        ):
            _ext_hook(12, malformed_payload)

    def test_serialization_of_very_large_integer(self) -> None:
        large_int = 2**128
        cty_val = CtyNumber().validate(large_int)
        packed_bytes = cty_to_msgpack(cty_val, CtyNumber())
        unpacked = msgpack.unpackb(packed_bytes, raw=False)
        assert unpacked == str(large_int)


class TestConversionCoverage:
    def test_infer_map_with_non_identifier_keys(self) -> None:
        data = {"key-with-hyphen": 1, "another_key": 2}
        inferred_type = infer_cty_type_from_raw(data)
        assert isinstance(inferred_type, CtyMap)

    def test_cty_to_native_with_set_and_tuple(self) -> None:
        set_val = CtySet(element_type=CtyNumber()).validate({1, 2, 3})
        native_set = cty_to_native(set_val)
        # Convert to list for sorted comparison as set order is not guaranteed
        assert sorted(list(native_set)) == [1, 2, 3]

        tuple_val = CtyTuple(element_types=(CtyString(), CtyNumber())).validate(
            ("a", 1)
        )
        native_tuple = cty_to_native(tuple_val)
        assert native_tuple == ("a", 1)

    def test_type_encoder_with_invalid_type(self) -> None:
        with pytest.raises(TypeError):
            encode_cty_type_to_wire_json("not a cty type")


class TestPathCoverage:
    def test_apply_path_to_invalid_targets(self) -> None:
        obj_val = CtyObject(attribute_types={"name": CtyString()}).validate(
            {"name": "test"}
        )
        list_val = CtyList(element_type=CtyString()).validate(["a", "b"])
        null_val = CtyValue.null(CtyObject(attribute_types={"name": CtyString()}))

        with pytest.raises(
            AttributePathError, match="Cannot get attribute from non-object value"
        ):
            CtyPath.get_attr("name").apply_path(list_val)

        with pytest.raises(AttributePathError, match="Cannot index into value of type"):
            CtyPath.index(0).apply_path(obj_val)

        with pytest.raises(
            AttributePathError, match=r"Cannot get attribute '.*' from null value"
        ):
            CtyPath.get_attr("name").apply_path(null_val)


class TestTypesCoverage:
    def test_map_get_with_default(self) -> None:
        map_type = CtyMap(element_type=CtyString())
        map_val = map_type.validate({"a": "present"})
        default_val = CtyString().validate("default")
        assert map_type.get(map_val, "a", default_val).value == "present"
        assert map_type.get(map_val, "b", default_val).value == "default"

    def test_map_usable_as_dynamic(self) -> None:
        map_type = CtyMap(element_type=CtyString())
        assert map_type.usable_as(CtyDynamic())
        assert not map_type.usable_as(CtyObject(attribute_types={}))

    def test_object_with_unknown_optional_attribute(self) -> None:
        obj_type = CtyObject(
            attribute_types={"name": CtyString()},
            optional_attributes=frozenset(["age"]),
        )
        with pytest.raises(
            CtyAttributeValidationError, match="Unknown optional attributes: age"
        ):
            obj_type.validate({"name": "test"})
