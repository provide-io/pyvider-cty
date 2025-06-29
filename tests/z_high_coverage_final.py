import pytest
from decimal import Decimal
from pyvider.cty import *
from pyvider.cty.exceptions import *
from pyvider.cty.path import *
from pyvider.cty.values.base import UnrefinedUnknownValue, RefinedUnknownValue
from pyvider.cty.context.validation_context import deeper_validation, get_validation_depth, MAX_VALIDATION_DEPTH

# --- Coverage for `codec.py` ---
def test_codec_shorthand_types():
    assert isinstance(parse_type_string_to_ctytype("{a=string}"), CtyObject)
    assert isinstance(parse_type_string_to_ctytype("[string]"), CtyTuple)
    with pytest.raises(CtyTypeParseError):
        parse_type_string_to_ctytype("nonsense")

# --- Coverage for `context/validation_context.py` ---
def test_validation_depth_context():
    assert get_validation_depth() == 0
    with deeper_validation():
        assert get_validation_depth() == 1
        with deeper_validation():
            assert get_validation_depth() == 2
    assert get_validation_depth() == 0

# --- Coverage for `exceptions/validation.py` ---
def test_validation_exceptions_with_context():
    list_error = CtyListValidationError("bad list", value=[1], index=0)
    assert "At index 0: bad list" in str(list_error)
    map_error = CtyMapValidationError("bad map", value={}, key="a")
    assert "For key 'a': bad map" in str(map_error)
    type_mismatch = CtyTypeMismatchError("mismatch", actual_type="int", expected_type="str")
    assert "Expected str, got int" in str(type_mismatch)
    attr_error = CtyAttributeValidationError("bad attr", attribute_path="user.name")
    assert "Attribute 'user.name': bad attr" in str(attr_error)

# --- Coverage for `path/base.py` ---
def test_path_edge_cases():
    with pytest.raises(ValueError):
        GetAttrStep("")
    obj_type = CtyObject(attribute_types={"name": CtyString()})
    obj_val = obj_type.validate({"name": "test"})
    path = CtyPath.get_attr("name")
    assert path.apply_path_type(obj_type) == CtyString()
    with pytest.raises(AttributePathError):
        path.apply_path_type(CtyString())
    with pytest.raises(AttributePathError):
        CtyPath.key("k").apply_type(CtyString())
    with pytest.raises(AttributePathError):
        CtyPath.key(1).apply_path(CtyString().validate("s"))

# --- Coverage for `types/capsule.py` ---
def test_capsule_type():
    class MyData: pass
    cap_type = CtyCapsule("MyData", MyData)
    assert cap_type.usable_as(CtyDynamic())
    assert not cap_type.usable_as(CtyString())
    assert cap_type.validate(CtyValue.null(cap_type)).is_null
    assert cap_type.validate(CtyValue.unknown(cap_type)).is_unknown
    with pytest.raises(CtyValidationError):
        cap_type.validate(CtyString().validate("foo"))

# --- Coverage for `types/collections/*.py` ---
def test_collection_edge_cases():
    # List
    list_type = CtyList(element_type=CtyDynamic())
    val = list_type.validate([1, "s", True])
    assert len(val.value) == 3
    # Map
    map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
    with pytest.raises(CtyMapValidationError):
        map_type.validate({None: 1}) # Null key
    # Set
    set_type = CtySet(element_type=CtyString())
    with pytest.raises(CtySetValidationError):
        set_type.validate([[]]) # Unhashable element

# --- Coverage for `values/base.py` ---
def test_value_base_edge_cases():
    # unhashable value in hash
    val = CtyList(element_type=CtyString()).validate([["a"]])
    assert isinstance(hash(val), int)
    # contains on non-container
    assert ("a" in CtyString().validate("abc")) is True
    assert (123 in CtyNumber().validate(123)) is True
