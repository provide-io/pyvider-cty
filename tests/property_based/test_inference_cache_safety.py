"""
Property-based test to ensure any future caching in the type inference
logic is safe and does not cause correctness regressions.
"""
from hypothesis import given, strategies as st

from pyvider.cty.conversion import infer_cty_type_from_raw
from pyvider.cty.types import CtyList, CtyMap, CtyNumber, CtyString, CtyDynamic

# A strategy that generates two dictionaries that share the same keys
# but have values of different, incompatible types. This is the exact
# scenario that would break a naive, key-only caching mechanism.
@st.composite
def same_keys_different_types(draw):
    keys = draw(st.lists(st.text(min_size=1), min_size=1, unique=True))
    dict1 = {key: draw(st.text()) for key in keys}
    dict2 = {key: draw(st.lists(st.integers())) for key in keys}
    return (dict1, dict2)

@given(data=same_keys_different_types())
def test_inference_is_correct_for_same_keys_different_types(data):
    """
    Ensures that inferring types for two dicts with identical keys but
    different value types produces two distinct and correct schemas.
    """
    dict1, dict2 = data
    
    # Infer type for the first dictionary (uniform string values)
    type1 = infer_cty_type_from_raw(dict1)
    
    # Infer type for the second dictionary (uniform list-of-int values)
    type2 = infer_cty_type_from_raw(dict2)

    # The inferred types must be different CtyMap schemas.
    # A faulty cache might incorrectly return type1 for the second call.
    assert not type1.equal(type2)

    # Verify the correctness of each inferred type. Since both generated
    # dicts have uniform value types, they should both be inferred as CtyMap.
    assert isinstance(type1, CtyMap)
    assert type1.element_type.equal(CtyString())

    assert isinstance(type2, CtyMap)
    
    # CORRECTED ASSERTION:
    # If any list in the dictionary's values is empty, the unified element
    # type for the lists must be CtyDynamic, as the element type cannot be
    # known. Otherwise, it can be inferred as CtyNumber.
    has_empty_list = any(isinstance(v, list) and not v for v in dict2.values())
    
    if has_empty_list:
        expected_element_type = CtyList(element_type=CtyDynamic())
    else:
        expected_element_type = CtyList(element_type=CtyNumber())
        
    assert type2.element_type.equal(expected_element_type)
