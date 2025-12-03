#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from pyvider.cty.exceptions.encoding import (
    AttributePathError,
    DeserializationError,
    DynamicValueError,
    InvalidTypeError,
    JsonEncodingError,
    MsgPackEncodingError,
    SerializationError,
    TransformationError,
    WireFormatError,
)
from pyvider.cty.types import CtyString


class TestTransformationError:
    def test_instantiation_with_message_only(self) -> None:
        error = TransformationError("Base transformation error")
        assert str(error) == "Base transformation error"
        assert error.schema is None
        assert error.target_type is None

    def test_instantiation_with_schema(self) -> None:
        schema_obj = {"type": "string"}
        error = TransformationError("Schema error", schema=schema_obj)
        expected_msg = "Schema error (schema_type=dict)"
        assert str(error) == expected_msg
        assert error.schema == schema_obj

    def test_instantiation_with_target_type_with_name(self) -> None:
        target = CtyString
        error = TransformationError("Target type error", target_type=target)
        expected_msg = "Target type error (target_type=CtyString)"
        assert str(error) == expected_msg
        assert error.target_type == target

    def test_instantiation_with_target_type_without_name(self) -> None:
        target_str = "custom_string_type"
        error = TransformationError("Target type error", target_type=target_str)
        expected_msg = f"Target type error (target_type={target_str})"
        assert str(error) == expected_msg
        assert error.target_type == target_str

        class SimpleClass:
            pass

        target_instance = SimpleClass()
        error_instance = TransformationError("Target type error", target_type=target_instance)
        expected_msg_instance = f"Target type error (target_type={target_instance!s})"
        assert str(error_instance) == expected_msg_instance

    def test_instantiation_with_all_params(self) -> None:
        schema_obj = {"type": "number"}
        target = CtyString
        error = TransformationError("Full transform error", schema=schema_obj, target_type=target)
        expected_msg = "Full transform error (schema_type=dict, target_type=CtyString)"
        assert str(error) == expected_msg
        assert error.schema == schema_obj
        assert error.target_type == target


class TestSerializationError:
    def test_instantiation_message_only(self) -> None:
        error = SerializationError("Serialization failure")
        assert str(error) == "Serialization failure"
        assert error.value is None
        assert error.encoding is None

    def test_instantiation_all_params(self) -> None:
        error = SerializationError("Cannot serialize", value="testval", format_name="testformat")
        expected_msg = "TESTFORMAT encoding error: Cannot serialize"
        assert str(error) == expected_msg
        assert error.value == "testval"
        assert error.encoding == "testformat"


class TestDeserializationError:
    def test_instantiation_message_only(self) -> None:
        error = DeserializationError("Deserialization failure")
        assert str(error) == "Deserialization failure"
        assert error.data is None
        assert error.encoding is None

    def test_instantiation_all_params(self) -> None:
        error = DeserializationError("Cannot deserialize", data="testdata", format_name="testformat")
        expected_msg = "TESTFORMAT encoding error: Cannot deserialize"
        assert str(error) == expected_msg
        assert error.data == "testdata"
        assert error.encoding == "testformat"


class TestDynamicValueError:
    def test_instantiation_basic(self) -> None:
        error = DynamicValueError("Dynamic value issue", value="dyn_val")
        expected_msg = "DYNAMICVALUE encoding error: Dynamic value issue"
        assert str(error) == expected_msg
        assert error.value == "dyn_val"
        assert error.encoding == "DynamicValue"


class TestJsonEncodingError:
    def test_instantiation_message_only(self) -> None:
        error = JsonEncodingError("Some JSON problem")  # Changed message
        expected_msg = "JSON encoding error: Some JSON problem"
        assert str(error) == expected_msg
        assert error.data is None
        assert error.operation is None
        assert error.encoding == "json"

    def test_instantiation_all_params(self) -> None:
        error = JsonEncodingError("Specific JSON problem", data="testdata", operation="testop")
        expected_msg = "JSON testop error: Specific JSON problem"
        assert str(error) == expected_msg
        assert error.data == "testdata"
        assert error.operation == "testop"


class TestMsgPackEncodingError:
    def test_instantiation_message_only(self) -> None:
        error = MsgPackEncodingError("Some MsgPack problem")  # Changed message
        expected_msg = "MSGPACK encoding error: Some MsgPack problem"
        assert str(error) == expected_msg
        assert error.data is None
        assert error.operation is None
        assert error.encoding == "msgpack"

    def test_instantiation_all_params(self) -> None:
        error = MsgPackEncodingError("Specific MsgPack problem", data="testdata", operation="testop")
        expected_msg = "MSGPACK testop error: Specific MsgPack problem"
        assert str(error) == expected_msg
        assert error.data == "testdata"
        assert error.operation == "testop"


class TestWireFormatError:
    def test_instantiation_message_only(self) -> None:
        error = WireFormatError("Wire format issue")
        assert str(error) == "Wire format issue"
        assert error.format_type is None
        assert error.operation is None

    def test_instantiation_with_format_type(self) -> None:
        error = WireFormatError("Wire format issue", format_type="test_ft")
        expected_msg = "Wire format issue using test_ft"
        assert str(error) == expected_msg
        assert error.format_type == "test_ft"

    def test_instantiation_with_operation(self) -> None:
        error = WireFormatError("Wire format issue", operation="test_op")
        expected_msg = "Wire format issue during test_op"
        assert str(error) == expected_msg
        assert error.operation == "test_op"

    def test_instantiation_with_all_params(self) -> None:
        error = WireFormatError("Full wire issue", format_type="test_ft", operation="test_op")
        expected_msg = "Full wire issue during test_op using test_ft"
        assert str(error) == expected_msg
        assert error.format_type == "test_ft"
        assert error.operation == "test_op"

    def test_instantiation_with_all_transformation_params(self) -> None:
        """Test WireFormatError also correctly passes TransformationError params."""
        schema_obj = {"type": "object"}
        target = CtyString
        error = WireFormatError(
            "Wire transform issue",
            schema=schema_obj,
            target_type=target,
            format_type="fancy_format",
            operation="transforming",
        )
        expected_msg = "Wire transform issue (schema_type=dict, target_type=CtyString) during transforming using fancy_format"
        assert str(error) == expected_msg
        assert error.schema == schema_obj
        assert error.target_type == target
        assert error.format_type == "fancy_format"
        assert error.operation == "transforming"


class TestAttributePathError:
    def test_instantiation_basic(self) -> None:
        path_obj = "a.b.c"
        value_obj = {"a": {"b": {"c": 1}}}
        error = AttributePathError("Path error", path=path_obj, value=value_obj)
        assert str(error) == "Path error"
        assert error.path == path_obj
        assert error.value == value_obj


class TestInvalidTypeError:
    def test_instantiation_basic(self) -> None:
        invalid_type_obj = int
        error = InvalidTypeError("Invalid type used", invalid_type=invalid_type_obj)
        assert str(error) == "Invalid type used"
        assert error.invalid_type == invalid_type_obj


# 🌊🪢🔚
