import pytest

from pyvider.cty.codec import CtyTypeParseError, parse_type_string_to_ctytype
from pyvider.cty.types import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
)


class TestParseTypeStringToCtyType:
    @pytest.mark.parametrize(
        "type_str, expected_type",
        [
            ("string", CtyString()),
            ("number", CtyNumber()),
            ("bool", CtyBool()),
            ("dynamic", CtyDynamic()),
            (" list(string) ", CtyList(element_type=CtyString())),
            ("set(number)", CtySet(element_type=CtyNumber())),
            (
                "map(bool)",
                CtyMap(key_type=CtyString(), value_type=CtyBool()),
            ),  # Default key type CtyString
            ("list(dynamic)", CtyList(element_type=CtyDynamic())),
        ],
    )
    def test_simple_and_basic_collection_types(self, type_str, expected_type) -> None:
        assert parse_type_string_to_ctytype(type_str) == expected_type

    def test_nested_list(self) -> None:
        assert parse_type_string_to_ctytype("list(list(string))") == CtyList(
            element_type=CtyList(element_type=CtyString())
        )

    def test_map_with_list_value(self) -> None:
        expected = CtyMap(
            key_type=CtyString(), value_type=CtyList(element_type=CtyNumber())
        )
        assert parse_type_string_to_ctytype("map(list(number))") == expected

    def test_set_of_maps(self) -> None:
        expected = CtySet(
            element_type=CtyMap(key_type=CtyString(), value_type=CtyString())
        )
        assert parse_type_string_to_ctytype("set(map(string))") == expected

    # Object type tests
    def test_simple_object(self) -> None:
        expected = CtyObject({"name": CtyString(), "age": CtyNumber()})
        assert (
            parse_type_string_to_ctytype("object({name=string,age=number})") == expected
        )
        assert (
            parse_type_string_to_ctytype("object({ name = string , age = number })")
            == expected
        )  # Test with spaces

    def test_object_with_no_attributes(self) -> None:
        assert parse_type_string_to_ctytype("object({})") == CtyObject({})
        assert parse_type_string_to_ctytype("object({   })") == CtyObject({})

    def test_object_with_complex_attribute_types(self) -> None:
        expected = CtyObject(
            {
                "user": CtyObject({"id": CtyString(), "active": CtyBool()}),
                "tags": CtyList(element_type=CtyString()),
            }
        )
        type_str = "object({user=object({id=string,active=bool}),tags=list(string)})"
        assert parse_type_string_to_ctytype(type_str) == expected

    def test_object_nested_deeply(self) -> None:
        # object({config=object({ports=list(object({internal=number,external=number}))})})
        expected = CtyObject(
            {
                "config": CtyObject(
                    {
                        "ports": CtyList(
                            element_type=CtyObject(
                                {"internal": CtyNumber(), "external": CtyNumber()}
                            )
                        )
                    }
                )
            }
        )
        type_str = "object({config=object({ports=list(object({internal=number,external=number}))})})"
        assert parse_type_string_to_ctytype(type_str) == expected

    # Tuple type tests
    def test_simple_tuple(self) -> None:
        expected = CtyTuple((CtyString(), CtyNumber()))
        assert parse_type_string_to_ctytype("tuple([string,number])") == expected
        assert (
            parse_type_string_to_ctytype("tuple([ string , number ])") == expected
        )  # Test with spaces

    def test_tuple_with_no_elements(self) -> None:
        assert parse_type_string_to_ctytype("tuple([])") == CtyTuple(tuple())
        assert parse_type_string_to_ctytype("tuple([   ])") == CtyTuple(tuple())

    def test_tuple_with_complex_element_types(self) -> None:
        expected = CtyTuple(
            (CtyObject({"id": CtyString()}), CtyList(element_type=CtyString()))
        )
        type_str = "tuple([object({id=string}),list(string)])"
        assert parse_type_string_to_ctytype(type_str) == expected

    def test_tuple_nested_deeply(self) -> None:
        # tuple([string, object({data=list(tuple([number, bool]))})])
        expected = CtyTuple(
            (
                CtyString(),
                CtyObject(
                    {"data": CtyList(element_type=CtyTuple((CtyNumber(), CtyBool())))}
                ),
            )
        )
        type_str = "tuple([string,object({data=list(tuple([number,bool]))})])"
        assert parse_type_string_to_ctytype(type_str) == expected

    # Error handling tests
    @pytest.mark.parametrize(
        "invalid_type_str, error_message_part",
        [
            (
                "list(string",
                "Unknown or invalid CTY type string: list(string",
            ),  # Missing closing paren
            (
                "set(number",
                "Unknown or invalid CTY type string: set(number",
            ),  # Missing closing paren
            (
                "map(bool",
                "Unknown or invalid CTY type string: map(bool",
            ),  # Missing closing paren
            (
                "object({name=string",
                "Unknown or invalid CTY type string: object({name=string",
            ),  # Missing closing brace
            (
                "object({name=})",
                "Empty attribute type string for attribute 'name' in 'name='",
            ),  # Empty type for attr
            (
                "object({=string})",
                "Empty attribute name in object string: '=string'",
            ),  # Empty name for attr - Adjusted
            (
                "object({name:string})",
                "Invalid attribute format in object string: 'name:string' in 'name:string'",
            ),  # Colon instead of equals
            (
                "tuple([string",
                "Unknown or invalid CTY type string: tuple([string",
            ),  # Missing closing bracket
            (
                "tuple([string,])",
                "Empty type string found in tuple elements: 'string,'",
            ),  # Trailing comma leads to empty element
            ("list(unknown_type)", "Unknown or invalid CTY type string: unknown_type"),
            ("invalid", "Unknown or invalid CTY type string: invalid"),
            # ("object({name=string,age=number,})", "empty attribute string in object"), # This now passes due to trailing comma tolerance
            (
                "tuple([string,number,])",
                "Empty type string found in tuple elements: 'string,number,'",
            ),  # Trailing comma leads to empty element
            (
                "object({data=list(object({id=string}))",
                "Unknown or invalid CTY type string:",
            ),  # Missing closing } for outer object
            (
                "map(list(number)",
                "Unknown or invalid CTY type string: list(number",
            ),  # Error from inner parse
        ],
    )
    def test_invalid_type_strings(self, invalid_type_str, error_message_part) -> None:
        with pytest.raises(CtyTypeParseError) as excinfo:
            parse_type_string_to_ctytype(invalid_type_str)
        assert error_message_part.lower() in str(excinfo.value).lower()

    def test_object_with_empty_attribute_name(self) -> None:
        with pytest.raises(
            CtyTypeParseError, match="Empty attribute name in object string: '=string'"
        ):  # Adjusted
            parse_type_string_to_ctytype("object({=string})")

    def test_object_with_empty_attribute_type(self) -> None:
        with pytest.raises(
            CtyTypeParseError,
            match="Empty attribute type string for attribute 'name' in 'name='",
        ):
            parse_type_string_to_ctytype("object({name=})")

    def test_tuple_with_empty_element_type(self) -> None:
        # This test is for "tuple([string,])" -> error on the empty part
        with pytest.raises(
            CtyTypeParseError,
            match="Empty type string found in tuple elements: 'string,'",
        ):
            parse_type_string_to_ctytype("tuple([string,])")

    def test_very_complex_nested_structure(self) -> None:
        type_str = (
            "object({data=list(tuple([string, map(object({config=set(number)}))]))})"
        )
        expected = CtyObject(
            {
                "data": CtyList(
                    element_type=CtyTuple(
                        (
                            CtyString(),
                            CtyMap(
                                key_type=CtyString(),
                                value_type=CtyObject(
                                    {"config": CtySet(element_type=CtyNumber())}
                                ),
                            ),
                        )
                    )
                )
            }
        )
        assert parse_type_string_to_ctytype(type_str) == expected

    def test_spacing_robustness(self) -> None:
        type_str = "  object ( { name = string , info = list ( number ) } )  "
        expected = CtyObject(
            {"name": CtyString(), "info": CtyList(element_type=CtyNumber())}
        )
        assert parse_type_string_to_ctytype(type_str) == expected

    def test_empty_string_input(self) -> None:
        with pytest.raises(
            CtyTypeParseError, match="Unknown or invalid CTY type string: "
        ):
            parse_type_string_to_ctytype("")

    def test_unbalanced_delimiters(self) -> None:
        with pytest.raises(
            CtyTypeParseError, match="Unknown or invalid CTY type string"
        ):
            parse_type_string_to_ctytype("list(string")  # Missing )
        with pytest.raises(
            CtyTypeParseError, match="Unknown or invalid CTY type string"
        ):
            parse_type_string_to_ctytype("object({name=string)")  # Missing }
        with pytest.raises(
            CtyTypeParseError, match="Unknown or invalid CTY type string"
        ):
            parse_type_string_to_ctytype("tuple([string)")  # Missing ]
        # This specific error for object({name=string,age=number() is because it fails the main regexes
        # and falls through to the generic "Unknown or invalid" error.
        with pytest.raises(
            CtyTypeParseError,
            match="Unknown or invalid CTY type string: object\\(\\{name=string,age=number\\(\\)",
        ):
            parse_type_string_to_ctytype("object({name=string,age=number()")  # Extra (

    def test_trailing_comma_in_object(self) -> None:
        # Trailing comma in object should be accepted and ignored
        expected = CtyObject({"name": CtyString()})
        assert parse_type_string_to_ctytype("object({name=string,})") == expected
        expected_multiple = CtyObject({"name": CtyString(), "age": CtyNumber()})
        assert (
            parse_type_string_to_ctytype("object({name=string,age=number,})")
            == expected_multiple
        )

    def test_trailing_comma_in_tuple(self) -> None:
        # A trailing comma in a tuple type string that results in an empty element type IS an error.
        with pytest.raises(
            CtyTypeParseError,
            match="Empty type string found in tuple elements: 'string,'",
        ):
            parse_type_string_to_ctytype("tuple([string,])")

        # An empty element due to adjacent commas is also an error.
        with pytest.raises(
            CtyTypeParseError,
            match="Empty type string found in tuple elements: 'string,,number'",
        ):  # Adjusted
            parse_type_string_to_ctytype("tuple([string,,number])")

    # Test cases from JsonEncoder._create_type_from_name (used in original file)
    @pytest.mark.parametrize(
        "type_str, expected_type_class",
        [
            ("string", CtyString),
            ("number", CtyNumber),
            ("bool", CtyBool),
            ("dynamic", CtyDynamic),
            ("list(string)", CtyList),
            ("map(number)", CtyMap),
            ("set(bool)", CtySet),
            ("object({name=string})", CtyObject),
            ("tuple([number,string])", CtyTuple),
        ],
    )
    def test_compatibility_with_json_encoder_example_strings(
        self, type_str, expected_type_class
    ) -> None:
        cty_type = parse_type_string_to_ctytype(type_str)
        assert isinstance(cty_type, expected_type_class)

        if type_str == "list(string)":
            assert cty_type.element_type == CtyString()
        if type_str == "map(number)":
            assert cty_type.key_type == CtyString()  # Default key type
            assert cty_type.value_type == CtyNumber()
        if type_str == "set(bool)":
            assert cty_type.element_type == CtyBool()
        if type_str == "object({name=string})":
            assert "name" in cty_type.attribute_types
            assert cty_type.attribute_types["name"] == CtyString()
        if type_str == "tuple([number,string])":
            assert len(cty_type.element_types) == 2
            assert cty_type.element_types[0] == CtyNumber()
            assert cty_type.element_types[1] == CtyString()
