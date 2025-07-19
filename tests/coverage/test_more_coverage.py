import pytest
from pyvider.cty import CtyNumber, CtyString, CtyValue, CtyList, CtyBool, CtyDynamic, CtyObject, CtySet, CtyTuple
from pyvider.cty.functions import (
    abs_fn,
    ceil_fn,
    floor_fn,
    log_fn,
    pow_fn,
    signum_fn,
    parseint_fn,
    chomp,
    strrev,
    trimspace,
    indent,
    substr,
    trim,
    title,
    trimprefix,
    trimsuffix,
    regex,
    regexall,
    distinct,
    flatten,
    sort,
)
from pyvider.cty.exceptions import CtyFunctionError, CtyValidationError
from pyvider.cty.path import CtyPath, GetAttrStep, IndexStep, KeyStep
from pyvider.cty.marks import CtyMark
from pyvider.cty.types.collections.list import CtyList
from pyvider.cty.types.collections.map import CtyMap
from pyvider.cty.types.collections.set import CtySet
from pyvider.cty.types.structural.object import CtyObject
from pyvider.cty.types.structural.tuple import CtyTuple
from pyvider.cty.types.primitives.bool import CtyBool
from pyvider.cty.types.primitives.number import CtyNumber
from pyvider.cty.types.primitives.string import CtyString
from pyvider.cty.types.structural.dynamic import CtyDynamic
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack

def test_codec_coverage():
    # Test for codec branch that is not covered
    value = CtyValue.unknown(CtyString())
    schema = CtyString()
    msgpack_data = cty_to_msgpack(value, schema)
    new_value = cty_from_msgpack(msgpack_data, schema)
    assert new_value.is_unknown

def test_raw_to_cty_coverage():
    # Test for raw_to_cty branch that is not covered
    from pyvider.cty.conversion.raw_to_cty import infer_cty_type_from_raw
    assert infer_cty_type_from_raw(1j).equal(CtyDynamic())
    assert infer_cty_type_from_raw({1: "a"}).equal(CtyMap(element_type=CtyString()))

def test_numeric_functions_coverage():
    # Test for numeric_functions branches that are not covered
    with pytest.raises(CtyFunctionError):
        abs_fn(CtyString().validate("a"))
    with pytest.raises(CtyFunctionError):
        ceil_fn(CtyString().validate("a"))
    with pytest.raises(CtyFunctionError):
        floor_fn(CtyString().validate("a"))
    with pytest.raises(CtyFunctionError):
        log_fn(CtyString().validate("a"), CtyNumber().validate(10))
    with pytest.raises(CtyFunctionError):
        log_fn(CtyNumber().validate(10), CtyString().validate("a"))
    with pytest.raises(CtyFunctionError):
        pow_fn(CtyString().validate("a"), CtyNumber().validate(2))
    with pytest.raises(CtyFunctionError):
        pow_fn(CtyNumber().validate(2), CtyString().validate("a"))
    with pytest.raises(CtyFunctionError):
        signum_fn(CtyString().validate("a"))
    with pytest.raises(CtyFunctionError):
        parseint_fn(CtyNumber().validate(1), CtyNumber().validate(10))
    with pytest.raises(CtyFunctionError):
        parseint_fn(CtyString().validate("a"), CtyString().validate("b"))

def test_string_functions_coverage():
    # Test for string_functions branches that are not covered
    with pytest.raises(CtyFunctionError):
        chomp(CtyNumber().validate(1))
    with pytest.raises(CtyFunctionError):
        strrev(CtyNumber().validate(1))
    with pytest.raises(CtyFunctionError):
        trimspace(CtyNumber().validate(1))
    with pytest.raises(CtyFunctionError):
        indent(CtyNumber().validate(1), CtyString().validate("a"))
    with pytest.raises(CtyFunctionError):
        indent(CtyString().validate("a"), CtyNumber().validate(1))
    with pytest.raises(CtyFunctionError):
        substr(CtyNumber().validate(1), CtyNumber().validate(0), CtyNumber().validate(1))
    with pytest.raises(CtyFunctionError):
        substr(CtyString().validate("a"), CtyString().validate("b"), CtyNumber().validate(1))
    with pytest.raises(CtyFunctionError):
        substr(CtyString().validate("a"), CtyNumber().validate(0), CtyString().validate("b"))
    with pytest.raises(CtyFunctionError):
        trim(CtyNumber().validate(1), CtyString().validate("a"))
    with pytest.raises(CtyFunctionError):
        trim(CtyString().validate("a"), CtyNumber().validate(1))
    with pytest.raises(CtyFunctionError):
        title(CtyNumber().validate(1))
    with pytest.raises(CtyFunctionError):
        trimprefix(CtyNumber().validate(1), CtyString().validate("a"))
    with pytest.raises(CtyFunctionError):
        trimprefix(CtyString().validate("a"), CtyNumber().validate(1))
    with pytest.raises(CtyFunctionError):
        trimsuffix(CtyNumber().validate(1), CtyString().validate("a"))
    with pytest.raises(CtyFunctionError):
        trimsuffix(CtyString().validate("a"), CtyNumber().validate(1))
    with pytest.raises(CtyFunctionError):
        regex(CtyNumber().validate(1), CtyString().validate("a"))
    with pytest.raises(CtyFunctionError):
        regex(CtyString().validate("a"), CtyNumber().validate(1))
    with pytest.raises(CtyFunctionError):
        regexall(CtyNumber().validate(1), CtyString().validate("a"))
    with pytest.raises(CtyFunctionError):
        regexall(CtyString().validate("a"), CtyNumber().validate(1))

def test_collection_functions_coverage():
    # Test for collection_functions branches that are not covered
    with pytest.raises(CtyFunctionError):
        distinct(CtyNumber().validate(1))
    with pytest.raises(CtyFunctionError):
        flatten(CtyNumber().validate(1))
    with pytest.raises(CtyFunctionError):
        sort(CtyNumber().validate(1))

from pyvider.cty.exceptions import AttributePathError
from pyvider.cty.types.capsule import CtyCapsule

def test_path_coverage():
    # Test for path branches that are not covered
    with pytest.raises(AttributePathError):
        GetAttrStep("a").apply(CtyNumber().validate(1))
    with pytest.raises(AttributePathError):
        IndexStep(0).apply(CtyNumber().validate(1))
    with pytest.raises(AttributePathError):
        KeyStep("a").apply(CtyNumber().validate(1))
    with pytest.raises(AttributePathError):
        CtyPath([GetAttrStep("a")]).apply_path(1)
    with pytest.raises(AttributePathError):
        CtyPath([IndexStep(0)]).apply_path(1)
    with pytest.raises(AttributePathError):
        CtyPath([KeyStep("a")]).apply_path(1)

def test_types_coverage():
    # Test for types branches that are not covered
    with pytest.raises(CtyValidationError):
        CtyBool().validate(1.1)
    with pytest.raises(CtyValidationError):
        CtyNumber().validate("a")
    with pytest.raises(CtyValidationError):
        CtyString().validate(set())
    with pytest.raises(CtyValidationError):
        CtyList(element_type=CtyString()).validate(1)
    with pytest.raises(CtyValidationError):
        CtyMap(element_type=CtyString()).validate(1)
    with pytest.raises(CtyValidationError):
        CtySet(element_type=CtyString()).validate(1)
    with pytest.raises(CtyValidationError):
        CtyTuple(element_types=(CtyString(),)).validate(1)
    with pytest.raises(CtyValidationError):
        CtyObject(attribute_types={"a": CtyString()}).validate(1)
    with pytest.raises(CtyValidationError):
        CtyCapsule("a", int).validate(set())
    assert CtyDynamic().validate(1j).is_unknown
