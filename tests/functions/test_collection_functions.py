# pyvider-cty/tests/functions/test_collection_functions.py
import pytest
from decimal import Decimal
from pyvider.cty import (
    CtyList, CtySet, CtyTuple, CtyDynamic, CtyString, CtyNumber, CtyBool,
    CtyValue
)
from pyvider.cty.functions.collection_functions import distinct, flatten, sort
from pyvider.cty.exceptions import CtyFunctionError, CtyTypeValidationError


class TestCollectionFunctions:

    # --- Tests for distinct ---
    def test_distinct_list_primitives(self):
        list_type = CtyList(element_type=CtyString())
        input_val = list_type.validate(["a", "b", "a", "c", "b"])
        result = distinct(input_val)
        assert isinstance(result.type, CtyList)
        assert result.type.element_type.equals(CtyString())
        # Order of first appearance preserved
        assert [v.value for v in result.value] == ["a", "b", "c"]

    def test_distinct_list_mixed_types_becomes_dynamic(self):
        # Input list implicitly dynamic due to mixed Python types
        input_val = CtyList(element_type=CtyDynamic()).validate([ # Corrected
            CtyString().validate("a"),
            CtyNumber().validate(1),
            CtyString().validate("a"),
            CtyBool().validate(True),
            CtyNumber().validate(1)
        ])
        result = distinct(input_val)
        assert isinstance(result.type, CtyList)
        assert result.type.element_type.is_dynamic_type()

        expected_values_repr = [
            repr(CtyString().validate("a")),
            repr(CtyNumber().validate(1)),
            repr(CtyBool().validate(True))
        ]
        actual_values_repr = [repr(v) for v in result.value]
        assert actual_values_repr == expected_values_repr

    def test_distinct_empty_list(self):
        list_type = CtyList(element_type=CtyNumber()) # Corrected
        input_val = list_type.validate([])
        result = distinct(input_val)
        assert len(result.value) == 0
        assert result.type.element_type.equals(CtyNumber())

    def test_distinct_set_input(self):
        set_type = CtySet(element_type=CtyNumber()) # Corrected
        # Sets inherently have unique elements, but distinct should still work and return a list
        input_val = set_type.validate({1, 2, 3})
        result = distinct(input_val)
        assert isinstance(result.type, CtyList)
        assert result.type.element_type.equals(CtyNumber())
        # Order from set is not guaranteed, so check content
        assert sorted([v.value for v in result.value]) == [Decimal("1"), Decimal("2"), Decimal("3")]

    def test_distinct_tuple_input_homogeneous(self):
        tuple_type = CtyTuple((CtyString(), CtyString(), CtyString()))
        input_val = tuple_type.validate(("x", "y", "x"))
        result = distinct(input_val)
        assert isinstance(result.type, CtyList)
        assert result.type.element_type.equals(CtyString())
        assert [v.value for v in result.value] == ["x", "y"]

    def test_distinct_tuple_input_heterogeneous_becomes_dynamic_list(self):
        tuple_type = CtyTuple((CtyString(), CtyNumber(), CtyString()))
        input_val = tuple_type.validate(("x", 1, "x"))
        result = distinct(input_val)
        assert isinstance(result.type, CtyList)
        assert result.type.element_type.is_dynamic_type()

        expected_values_repr = [repr(CtyString().validate("x")), repr(CtyNumber().validate(1))]
        actual_values_repr = [repr(v) for v in result.value]
        assert actual_values_repr == expected_values_repr


    def test_distinct_unhashable_elements_error(self):
        # list of lists; CtyList values are not hashable
        list_of_lists_type = CtyList(element_type=CtyList(element_type=CtyString())) # Corrected
        input_val = list_of_lists_type.validate([["a"], ["b"], ["a"]])
        with pytest.raises(CtyFunctionError, match="distinct: element of type CtyList\\(string\\) is not hashable"):
            distinct(input_val)

    def test_distinct_null_unknown(self):
        null_list = CtyValue.null(CtyList(element_type=CtyString())) # Corrected
        unknown_list = CtyValue.unknown(CtyList(element_type=CtyString())) # Corrected
        assert distinct(null_list) is null_list
        assert distinct(unknown_list) is unknown_list

    def test_distinct_invalid_input_type(self):
        str_val = CtyString().validate("not a collection")
        with pytest.raises(CtyFunctionError, match="distinct: input must be a list, set, or tuple, got string"):
            distinct(str_val)

    # --- Tests for flatten ---
    def test_flatten_list_of_lists_primitives(self):
        list_of_lists_type = CtyList(element_type=CtyList(element_type=CtyNumber())) # Corrected
        input_val = list_of_lists_type.validate([[1, 2], [3], [], [4, 5]])
        result = flatten(input_val)
        assert isinstance(result.type, CtyList)
        assert result.type.element_type.equals(CtyNumber())
        assert [v.value for v in result.value] == [Decimal("1"), Decimal("2"), Decimal("3"), Decimal("4"), Decimal("5")]

    def test_flatten_list_of_tuples(self):
        list_of_tuples_type = CtyList(element_type=CtyTuple(element_types=(CtyString(), CtyNumber()))) # Corrected
        input_val = list_of_tuples_type.validate([("a", 1), ("b", 2)])
        result = flatten(input_val) # Elements are CtyString, CtyNumber
        assert isinstance(result.type, CtyList)
        assert result.type.element_type.is_dynamic_type() # Because tuple elements were different

        actual_values = [(v.value.type.ctype, v.value.value) for v in result.value]
        expected_values = [("string", "a"), ("number", Decimal("1")), ("string", "b"), ("number", Decimal("2"))]
        assert actual_values == expected_values


    def test_flatten_tuple_of_lists(self):
        tuple_of_lists_type = CtyTuple(element_types=(CtyList(element_type=CtyString()), CtyList(element_type=CtyBool()))) # Corrected
        input_val = tuple_of_lists_type.validate((["x", "y"], [True]))
        result = flatten(input_val)
        assert isinstance(result.type, CtyList)
        assert result.type.element_type.is_dynamic_type() # String and Bool make it dynamic
        actual_values = [(v.value.type.ctype, v.value.value) for v in result.value]
        expected_values = [("string", "x"), ("string", "y"), ("bool", True)]
        assert actual_values == expected_values

    def test_flatten_mixed_inner_types_becomes_dynamic(self):
        # list(list(string), list(number)) -> becomes list(dynamic)
        # This requires the outer list to be list(dynamic) or list(union_type)
        # Let's use list(dynamic) for the input outer list
        list_str = CtyList(element_type=CtyString()).validate(["a", "b"]) # Corrected
        list_num = CtyList(element_type=CtyNumber()).validate([1, 2]) # Corrected
        input_val = CtyList(element_type=CtyDynamic()).validate([list_str, list_num]) # Corrected

        result = flatten(input_val)
        assert isinstance(result.type, CtyList)
        assert result.type.element_type.is_dynamic_type()

        actual_values = [(v.value.type.ctype, v.value.value) for v in result.value]
        expected_values = [("string", "a"), ("string", "b"), ("number", Decimal("1")), ("number", Decimal("2"))]
        assert actual_values == expected_values

    def test_flatten_empty_outer_list(self):
        list_of_lists_type = CtyList(element_type=CtyList(element_type=CtyString())) # Corrected
        input_val = list_of_lists_type.validate([])
        result = flatten(input_val)
        assert len(result.value) == 0
        assert result.type.element_type.equals(CtyString()) # Element type inferred from list(list(string))

    def test_flatten_list_of_empty_lists(self):
        list_of_lists_type = CtyList(element_type=CtyList(element_type=CtyNumber())) # Corrected
        input_val = list_of_lists_type.validate([[], []])
        result = flatten(input_val)
        assert len(result.value) == 0
        assert result.type.element_type.equals(CtyNumber())

    def test_flatten_null_unknown(self):
        null_list = CtyValue.null(CtyList(element_type=CtyList(element_type=CtyString()))) # Corrected
        unknown_list = CtyValue.unknown(CtyList(element_type=CtyList(element_type=CtyString()))) # Corrected
        assert flatten(null_list) is null_list
        assert flatten(unknown_list) is unknown_list

    def test_flatten_inner_element_null(self):
        # list contains a null list: [ list(string), null ]
        list_str = CtyList(element_type=CtyString()).validate(["a"]) # Corrected
        null_inner_list = CtyValue.null(CtyList(element_type=CtyString())) # Corrected
        input_val = CtyList(element_type=CtyDynamic()).validate([list_str, null_inner_list]) # Corrected
        result = flatten(input_val)
        assert [v.value for v in result.value] == ["a"]
        assert result.type.element_type.equals(CtyString()) # Inferred from non-null elements


    def test_flatten_inner_element_unknown(self):
        list_str = CtyList(element_type=CtyString()).validate(["a"]) # Corrected
        unknown_inner_list = CtyValue.unknown(CtyList(element_type=CtyString())) # Corrected
        input_val = CtyList(element_type=CtyDynamic()).validate([list_str, unknown_inner_list]) # Corrected
        result = flatten(input_val)
        assert result.is_unknown
        assert result.type.equals(CtyList(element_type=CtyDynamic())) # Corrected


    def test_flatten_invalid_input_type(self):
        str_val = CtyString().validate("not a list of lists")
        with pytest.raises(CtyFunctionError, match="flatten: input must be a list or tuple, got string"):
            flatten(str_val)

    def test_flatten_element_not_a_collection(self):
        # list(string, list(number)) -> error because first element "hello" is not a list/tuple
        str_elem = CtyString().validate("hello")
        list_elem = CtyList(element_type=CtyNumber()).validate([1,2]) # Corrected
        input_val = CtyList(element_type=CtyDynamic()).validate([str_elem, list_elem]) # Corrected
        with pytest.raises(CtyFunctionError, match="flatten: all elements of the input list/tuple must themselves be lists or tuples; found element of type string"):
            flatten(input_val)

    # --- Tests for sort ---
    @pytest.mark.parametrize("input_list, expected_sorted_list, el_type", [
        (["c", "a", "b"], ["a", "b", "c"], CtyString()),
        ([3, 1, 2], [Decimal("1"), Decimal("2"), Decimal("3")], CtyNumber()),
        ([True, False, True], [False, True, True], CtyBool()),
        ([], [], CtyString()) # Empty list
    ])
    def test_sort_primitives(self, input_list, expected_sorted_list, el_type):
        list_type = CtyList(element_type=el_type) # Corrected
        input_val = list_type.validate(input_list)
        result = sort(input_val)
        assert isinstance(result.type, CtyList)
        assert result.type.element_type.equals(el_type)
        assert [v.value for v in result.value] == expected_sorted_list

    def test_sort_set_input(self):
        set_type = CtySet(element_type=CtyNumber())
        input_val = set_type.validate({5,0,10})
        result = sort(input_val)
        assert isinstance(result.type, CtyList)
        assert result.type.element_type.equals(CtyNumber())
        assert [v.value for v in result.value] == [Decimal("0"), Decimal("5"), Decimal("10")]


    def test_sort_tuple_input(self):
        tuple_type = CtyTuple(element_types=(CtyString(), CtyString(), CtyString())) # Corrected
        input_val = tuple_type.validate(("z", "a", "m"))
        result = sort(input_val)
        assert isinstance(result.type, CtyList)
        assert result.type.element_type.equals(CtyString())
        assert [v.value for v in result.value] == ["a", "m", "z"]


    def test_sort_mixed_convertible_primitives(self):
        # e.g. list of numbers and bools (bools convert to numbers)
        # First element determines sort type. If [1, True, 0, False] -> numbers
        # If [True, 1, False, 0] -> bools (1 becomes True, 0 becomes False)

        # Case 1: First element is Number
        input_data1 = [2, True, 1, False] # True -> 1, False -> 0
        input_val1 = CtyList(element_type=CtyDynamic()).validate([
            CtyNumber().validate(2), CtyBool().validate(True),
            CtyNumber().validate(1), CtyBool().validate(False)
        ])
        result1 = sort(input_val1)
        assert result1.type.element_type.equals(CtyNumber())
        assert [v.value for v in result1.value] == [Decimal("0"), Decimal("1"), Decimal("1"), Decimal("2")]

        # Case 2: First element is Bool
        input_data2 = [True, 2, False, 1, 0] # 2->True, 1->True, 0->False
        input_val2 = CtyList(element_type=CtyDynamic()).validate([
            CtyBool().validate(True), CtyNumber().validate(2),
            CtyBool().validate(False), CtyNumber().validate(1), CtyNumber().validate(0)
        ])
        result2 = sort(input_val2)
        assert result2.type.element_type.equals(CtyBool())
        # Sorted: [False, False, True, True, True] (0, False, 1, 2, True)
        assert [v.value for v in result2.value] == [False, False, True, True, True]


    def test_sort_non_primitive_elements_error(self):
        list_type = CtyList(CtyList(CtyString())) # List of lists
        input_val = list_type.validate([["a"], ["b"]])
        with pytest.raises(CtyFunctionError, match="sort: elements must be string, number, or bool for sorting. Found type: CtyList\\(string\\)"):
            sort(input_val)

    def test_sort_incompatible_mixed_types_error(self):
        # e.g. list of string and number
        input_val = CtyList(CtyDynamic()).validate([CtyString().validate("a"), CtyNumber().validate(1)])
        with pytest.raises(CtyFunctionError, match="sort: all elements must be compatible for sorting. Element at index 1 of type number is not compatible with first element type string"):
            sort(input_val)

    def test_sort_list_with_null_element_error(self):
        input_val = CtyList(CtyString()).validate(["a", None, "c"])
        with pytest.raises(CtyFunctionError, match="sort: cannot sort list with null or unknown elements at index 1"):
            sort(input_val)

    def test_sort_list_with_unknown_element_error(self):
        input_val = CtyList(CtyDynamic()).validate([CtyString().validate("a"), CtyValue.unknown(CtyString())])
        with pytest.raises(CtyFunctionError, match="sort: cannot sort list with null or unknown elements at index 1"):
            sort(input_val)

    def test_sort_null_unknown_input(self):
        null_list = CtyValue.null(CtyList(CtyString()))
        unknown_list = CtyValue.unknown(CtyList(CtyString()))
        assert sort(null_list) is null_list
        assert sort(unknown_list) is unknown_list

    def test_sort_invalid_input_type(self):
        map_val = CtyMap(CtyString(), CtyString()).validate({"a":"b"})
        with pytest.raises(CtyFunctionError, match="sort: input must be a list, set, or tuple, got map"):
            sort(map_val)

    def test_sort_empty_tuple_input(self):
        # Sorting an empty tuple should result in an empty list(dynamic)
        empty_tuple = CtyTuple(tuple()).validate(tuple())
        result = sort(empty_tuple)
        assert isinstance(result.type, CtyList)
        assert result.type.element_type.is_dynamic_type()
        assert len(result.value) == 0

    def test_sort_empty_set_input(self):
        # Sorting an empty set(string) should result in an empty list(string)
        empty_set = CtySet(CtyString()).validate(set())
        result = sort(empty_set)
        assert isinstance(result.type, CtyList)
        assert result.type.element_type.equals(CtyString())
        assert len(result.value) == 0

    # Distinct with more complex, but hashable, elements like tuples
    def test_distinct_list_of_tuples(self):
        tuple_el_type = CtyTuple((CtyString(), CtyNumber()))
        list_type = CtyList(tuple_el_type)

        # Raw data for input CtyValues
        t1_raw = ("a", 1)
        t2_raw = ("b", 2)

        # Create CtyValue instances for these tuples
        # distinct operates on a list of CtyValues
        cty_t1 = tuple_el_type.validate(t1_raw)
        cty_t2 = tuple_el_type.validate(t2_raw)

        # Input list: [CtyTuple("a",1), CtyTuple("b",2), CtyTuple("a",1)]
        input_val = list_type._from_validated_values([cty_t1, cty_t2, cty_t1])

        result = distinct(input_val)
        assert isinstance(result.type, CtyList)
        assert result.type.element_type.equals(tuple_el_type)

        # Expected: [CtyTuple("a",1), CtyTuple("b",2)]
        assert len(result.value) == 2
        assert result.value[0].equals(cty_t1)
        assert result.value[1].equals(cty_t2)

        # Verify values if needed
        assert result.value[0].value[0].value == "a"
        assert result.value[0].value[1].value == Decimal("1")
        assert result.value[1].value[0].value == "b"
        assert result.value[1].value[1].value == Decimal("2")

    def test_flatten_list_of_empty_tuples(self):
        # list(tuple())
        empty_tuple_type = CtyTuple(tuple())
        list_of_empty_tuples_type = CtyList(empty_tuple_type)
        input_val = list_of_empty_tuples_type.validate([tuple(), tuple()])
        result = flatten(input_val) # Should result in list(dynamic) if empty tuple implies dynamic element
        assert len(result.value) == 0
        assert result.type.element_type.is_dynamic_type() # Flattening empty tuples yields no elements, type becomes dynamic

    def test_flatten_tuple_of_empty_lists(self):
        # tuple(list(string), list(number)) where lists are empty
        empty_list_str_type = CtyList(CtyString())
        empty_list_num_type = CtyList(CtyNumber())
        tuple_type = CtyTuple((empty_list_str_type, empty_list_num_type))
        input_val = tuple_type.validate(([], []))
        result = flatten(input_val)
        assert len(result.value) == 0
        # Element type becomes dynamic because tuple could hold list(X), list(Y)
        assert result.type.element_type.is_dynamic_type()
