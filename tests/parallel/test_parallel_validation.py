"""
Tests for the high-level parallel processing capabilities of the library.
"""
import pytest

from pyvider.cty import CtyList, CtyNumber, CtyObject, CtyString, CtyDynamic
from pyvider.cty.parallel import (
    parallel_validate,
    parallel_convert,
    parallel_to_msgpack,
    parallel_from_msgpack,
)

def test_parallel_validate_correctness():
    """
    Verifies that parallel_validate produces the same correct results as
    validating items serially.
    """
    schema = CtyObject(
        attribute_types={"id": CtyNumber(), "name": CtyString()}
    )
    raw_data = [
        {"id": i, "name": f"item-{i}"} for i in range(100)
    ]
    parallel_results = parallel_validate(schema, raw_data)
    assert len(parallel_results) == 100
    for i, result_val in enumerate(parallel_results):
        assert result_val.type.equal(schema)
        assert result_val["id"].value == i
        assert result_val["name"].value == f"item-{i}"

def test_parallel_convert_correctness():
    """
    Verifies that parallel_convert correctly validates and converts a batch of raw data.
    """
    source_schema = CtyObject(attribute_types={"value": CtyString()})
    target_schema = CtyObject(attribute_types={"value": CtyNumber()})
    raw_data = [{"value": str(i)} for i in range(100)]
    parallel_results = parallel_convert(source_schema, target_schema, raw_data)
    assert len(parallel_results) == 100
    for i, result_val in enumerate(parallel_results):
        assert result_val.type.equal(target_schema)
        assert result_val["value"].type.equal(CtyNumber())
        assert result_val["value"].value == i

def test_parallel_serialization_deserialization_roundtrip():
    """
    Verifies that data can be serialized and deserialized in parallel,
    resulting in identical data.
    """
    schema = CtyList(element_type=CtyObject(
        attribute_types={"id": CtyNumber(), "name": CtyString()}
    ))
    # 1. Start with a list of validated CtyValue objects
    validated_data = [
        schema.element_type.validate({"id": i, "name": f"item-{i}"})
        for i in range(100)
    ]

    # 2. Serialize them to MessagePack in parallel
    packed_bytes_list = parallel_to_msgpack(schema.element_type, validated_data)

    assert len(packed_bytes_list) == 100
    assert all(isinstance(b, bytes) for b in packed_bytes_list)

    # 3. Deserialize them from MessagePack in parallel
    deserialized_values = parallel_from_msgpack(schema.element_type, packed_bytes_list)

    # 4. Verify the round-tripped data is identical to the original
    assert len(deserialized_values) == 100
    assert deserialized_values == validated_data
