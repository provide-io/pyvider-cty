"""
Generates canonical MessagePack fixtures and a JSON manifest from pyvider.cty.
This script is the "source of truth" for the reverse compatibility test.
"""
import argparse
import json
from decimal import Decimal
from pathlib import Path
from typing import Any

from pyvider.cty import (
    CtyBool, CtyDynamic, CtyList, CtyMap, CtyNumber, CtyObject, CtySet,
    CtyString, CtyTuple, CtyValue
)
from pyvider.cty.codec import cty_to_msgpack
from pyvider.cty.conversion import encode_cty_type_to_wire_json
from pyvider.cty.values.markers import RefinedUnknownValue

_UNKNOWN_SENTINEL = {"$pyvider-cty-special-value": "unknown"}

def get_test_cases() -> dict[str, CtyValue]:
    """Defines all canonical test cases to be generated by Python."""
    tuple_type = CtyTuple(element_types=(CtyString(), CtyNumber()))

    return {
        "string_simple": CtyString().validate("hello from python"),
        "number_simple": CtyNumber().validate(12345),
        "bool_true": CtyBool().validate(True),
        "large_number": CtyNumber().validate(Decimal(2**128)),
        "null_string": CtyValue.null(CtyString()),
        "unknown_unrefined": CtyValue.unknown(CtyNumber()),
        "unknown_refined_str": CtyValue.unknown(
            CtyString(), value=RefinedUnknownValue(string_prefix="py-")
        ),
        "unknown_refined_list": CtyValue.unknown(
            CtyList(element_type=CtyString()),
            value=RefinedUnknownValue(collection_length_lower_bound=1, collection_length_upper_bound=5),
        ),
        "list_of_strings": CtyList(element_type=CtyString()).validate(["py-a", "py-b"]),
        "set_of_numbers": CtySet(element_type=CtyNumber()).validate({100, 200, 300}),
        "map_simple": CtyMap(element_type=CtyBool()).validate({"py_a": True, "py_b": False}),
        "set_of_tuples": CtySet(element_type=tuple_type).validate([("a", 1), ("b", 2)]),
        "deeply_nested_object": CtyObject(
            {
                "id": CtyString(), "enabled": CtyBool(), "ports": CtyList(element_type=CtyNumber()),
                "config": CtyObject({"retries": CtyNumber(), "params": CtyMap(element_type=CtyString())}),
                "metadata": CtyMap(element_type=CtyString()), "extra": CtyString(),
            },
            optional_attributes={"metadata"},
        ).validate({
            "id": "py-obj1", "enabled": True, "ports": [8080, 8443],
            "config": {"retries": 3, "params": {"timeout": "10s"}},
            "metadata": None, "extra": CtyValue.unknown(CtyString()),
        }),
        "dynamic_wrapped_string": CtyDynamic().validate("dynamic from python"),
        "dynamic_wrapped_object": CtyDynamic().validate(
            CtyObject({"key": CtyString()}).validate({"key": "py-value"})
        ),
    }

def cty_to_manifest_native(value: CtyValue) -> Any:
    """Converts a CtyValue to a native Python type suitable for the JSON manifest."""
    if value.is_unknown:
        return _UNKNOWN_SENTINEL
    if value.is_null:
        return None
    
    if isinstance(value.type, CtyDynamic):
        return cty_to_manifest_native(value.value)

    val = value.value
    if isinstance(val, Decimal):
        return str(val)
    if isinstance(val, tuple):
        return [cty_to_manifest_native(item) for item in val]
    if isinstance(val, frozenset):
        native_items = [cty_to_manifest_native(item) for item in val]
        return sorted(native_items, key=repr)
    if isinstance(val, dict):
        return {k: cty_to_manifest_native(v) for k, v in sorted(val.items())}
    
    return val

def main():
    parser = argparse.ArgumentParser(description="Generate pyvider.cty test fixtures.")
    parser.add_argument("-d", "--directory", required=True, type=Path, help="Directory to write fixtures and manifest.")
    args = parser.parse_args()

    output_dir: Path = args.directory
    output_dir.mkdir(parents=True, exist_ok=True)

    test_cases = get_test_cases()
    manifest = {}

    for name, value in test_cases.items():
        msgpack_bytes = cty_to_msgpack(value, value.type)
        (output_dir / f"{name}.msgpack").write_bytes(msgpack_bytes)

        manifest_value = value
        if isinstance(value.type, CtyDynamic):
            manifest_value = value.value

        manifest[name] = {
            "type": encode_cty_type_to_wire_json(manifest_value.type),
            "value": cty_to_manifest_native(value),
            "isUnknown": value.is_unknown,
            "isNull": value.is_null,
        }

    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"✅ Successfully generated {len(test_cases)} fixtures and manifest.json in {output_dir}")

if __name__ == "__main__":
    main()
