#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""jsondecode and csvdecode against go-cty's `json.go` and `csv.go`.

Both used to return a value wrapped in `dynamic`. That is not a cosmetic
difference: the type is what crosses the wire to Terraform, so a decoded
document arrived describing itself as dynamic rather than as the object or
tuple it is.
"""

from decimal import Decimal

import pytest

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyTuple,
)
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import csvdecode, jsondecode


def S(v: str) -> object:
    return CtyString().validate(v)


class TestJSONDecodeImpliedType:
    """go-cty's json.ImpliedType: an object becomes an object, an array a tuple."""

    def test_an_object_becomes_an_object_not_a_map(self) -> None:
        decoded = jsondecode(S('{"a": 1, "b": "x"}'))

        assert decoded.type == CtyObject(attribute_types={"a": CtyNumber(), "b": CtyString()})

    def test_an_array_becomes_a_tuple_not_a_list(self) -> None:
        """JSON promises nothing about an array's members sharing a type."""
        decoded = jsondecode(S('[1, "a", true]'))

        assert decoded.type == CtyTuple(element_types=(CtyNumber(), CtyString(), CtyBool()))

    @pytest.mark.parametrize(
        ("document", "expected"),
        [
            ('"x"', CtyString()),
            ("1", CtyNumber()),
            ("1.5", CtyNumber()),
            ("true", CtyBool()),
            ("false", CtyBool()),
        ],
    )
    def test_a_scalar_document(self, document: str, expected: object) -> None:
        assert jsondecode(S(document)).type == expected

    def test_a_null_document_is_dynamic_and_null(self) -> None:
        """A JSON null carries no type information for ImpliedType to read."""
        decoded = jsondecode(S("null"))

        assert decoded.type == CtyDynamic()
        assert decoded.is_null

    def test_a_null_member_is_a_dynamic_attribute(self) -> None:
        decoded = jsondecode(S('{"a": null}'))

        assert decoded.type == CtyObject(attribute_types={"a": CtyDynamic()})

    def test_nesting(self) -> None:
        decoded = jsondecode(S('{"a": {"b": [1, {"c": true}]}}'))

        assert decoded.type == CtyObject(
            attribute_types={
                "a": CtyObject(
                    attribute_types={
                        "b": CtyTuple(
                            element_types=(
                                CtyNumber(),
                                CtyObject(attribute_types={"c": CtyBool()}),
                            )
                        )
                    }
                )
            }
        )

    def test_an_empty_object_and_an_empty_array(self) -> None:
        assert jsondecode(S("{}")).type == CtyObject(attribute_types={})
        assert jsondecode(S("[]")).type == CtyTuple(element_types=())

    def test_numbers_do_not_go_through_float64(self) -> None:
        """go-cty decodes into a big.Float; a float64 hop would round first."""
        decoded = jsondecode(S("[0.1234567890123456789012345678901234567890]"))

        assert decoded[0].value == Decimal("0.1234567890123456789012345678901234567890")

    def test_invalid_json_is_refused(self) -> None:
        with pytest.raises(CtyFunctionError, match="failed to decode JSON"):
            jsondecode(S("{not json}"))


class TestCSVDecode:
    def test_the_result_is_a_list_of_objects_of_strings(self) -> None:
        """CSV carries no type information, so go-cty does not infer one."""
        decoded = csvdecode(S("a,b\n1,2"))

        assert decoded.type == CtyList(
            element_type=CtyObject(attribute_types={"a": CtyString(), "b": CtyString()})
        )
        assert decoded.raw_value == [{"a": "1", "b": "2"}]

    def test_a_header_with_no_rows_is_an_empty_list_of_that_type(self) -> None:
        decoded = csvdecode(S("a,b"))

        assert decoded.type == CtyList(
            element_type=CtyObject(attribute_types={"a": CtyString(), "b": CtyString()})
        )
        assert decoded.raw_value == []

    def test_quoted_fields(self) -> None:
        assert csvdecode(S('a,b\n"x,y",2')).raw_value == [{"a": "x,y", "b": "2"}]

    def test_blank_lines_are_skipped(self) -> None:
        """Go's csv.Reader drops them; Python's hands back an empty record."""
        assert csvdecode(S("a,b\n1,2\n\n3,4")).raw_value == [
            {"a": "1", "b": "2"},
            {"a": "3", "b": "4"},
        ]

    def test_no_header_line(self) -> None:
        with pytest.raises(CtyFunctionError, match="missing header line"):
            csvdecode(S(""))

    def test_a_duplicate_column_name(self) -> None:
        with pytest.raises(CtyFunctionError, match="duplicate column name"):
            csvdecode(S("a,a\n1,2"))

    @pytest.mark.parametrize("document", ["a,b\n1", "a,b\n1,2,3", "a,b\n1,2\n3"])
    def test_a_ragged_row(self, document: str) -> None:
        """Go fixes FieldsPerRecord from the header, so a short row is an error."""
        with pytest.raises(CtyFunctionError, match="wrong number of fields"):
            csvdecode(S(document))


# 🌊🪢🔚
