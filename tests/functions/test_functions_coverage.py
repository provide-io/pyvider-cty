import pytest

from pyvider.cty import (
    CtyDynamic,
    CtyList,
    CtyNumber,
    CtyString,
    CtyValue,
)
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import (
    distinct,
    flatten,
    log_fn,
    parseint_fn,
    pow_fn,
    regex,
    regexall,
    sort,
    substr,
)


class TestNumericFunctionsCoverage:
    def test_log_fn_errors(self) -> None:
        with pytest.raises(CtyFunctionError, match="log: number must be positive"):
            log_fn(CtyNumber().validate(-1), CtyNumber().validate(10))
        with pytest.raises(CtyFunctionError, match="log: base must be positive"):
            log_fn(CtyNumber().validate(1), CtyNumber().validate(-10))
        with pytest.raises(CtyFunctionError, match="log: base cannot be 1"):
            log_fn(CtyNumber().validate(1), CtyNumber().validate(1))

    def test_pow_fn_errors(self) -> None:
        with pytest.raises(CtyFunctionError, match="pow: invalid operation"):
            pow_fn(CtyNumber().validate(-1), CtyNumber().validate(0.5))

    def test_parseint_fn_errors(self) -> None:
        with pytest.raises(
            CtyFunctionError, match="parseint: base must be 0 or between 2 and 36"
        ):
            parseint_fn(CtyString().validate("10"), CtyNumber().validate(1))
        with pytest.raises(
            CtyFunctionError, match="parseint: base must be 0 or between 2 and 36"
        ):
            parseint_fn(CtyString().validate("10"), CtyNumber().validate(37))


class TestStringFunctionsCoverage:
    def test_substr_errors(self) -> None:
        with pytest.raises(
            CtyFunctionError, match="substr: length must be non-negative or -1"
        ):
            substr(
                CtyString().validate("hello"),
                CtyNumber().validate(0),
                CtyNumber().validate(-5),
            )

    def test_regex_errors(self) -> None:
        with pytest.raises(CtyFunctionError, match="regex: invalid regular expression"):
            regex(CtyString().validate("hello"), CtyString().validate("["))

    def test_regexall_errors(self) -> None:
        with pytest.raises(
            CtyFunctionError, match="regexall: invalid regular expression"
        ):
            regexall(CtyString().validate("hello"), CtyString().validate("["))


class TestCollectionFunctionsCoverage:
    def test_distinct_unhashable_error(self) -> None:
        with pytest.raises(
            CtyFunctionError, match="distinct: element of type list is not hashable"
        ):
            distinct(
                CtyList(element_type=CtyList(element_type=CtyString())).validate(
                    [["a"], ["b"]]
                )
            )

    def test_flatten_type_error(self) -> None:
        with pytest.raises(
            CtyFunctionError, match="flatten: all elements must be lists or tuples"
        ):
            flatten(CtyList(element_type=CtyString()).validate(["a", "b", "c"]))

    def test_sort_errors(self) -> None:
        with pytest.raises(
            CtyFunctionError, match="sort: elements must be string, number, or bool"
        ):
            sort(
                CtyList(element_type=CtyList(element_type=CtyString())).validate(
                    [["a"], ["b"]]
                )
            )
        with pytest.raises(
            CtyFunctionError,
            match="sort: cannot sort list with null or unknown elements",
        ):
            list_with_null = CtyList(element_type=CtyDynamic()).validate(
                ["a", CtyValue.null(CtyString()), "c"]
            )
            sort(list_with_null)
