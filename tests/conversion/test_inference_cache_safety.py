"""
TDD: Ensures the type inference cache is safe and does not cause correctness
regressions by mis-identifying types based on insufficient cache keys.
"""

from hypothesis import given, strategies as st

from pyvider.cty.conversion import infer_cty_type_from_raw
from pyvider.cty.types import CtyNumber, CtyObject, CtyString


@st.composite
def same_keys_different_types(draw):
    keys = draw(st.lists(st.text(min_size=1), min_size=1, unique=True))
    dict1 = {key: draw(st.text()) for key in keys}
    dict2 = {key: draw(st.integers()) for key in keys}
    return (dict1, dict2)


class TestInferenceCacheSafety:
    @given(data=same_keys_different_types())
    def test_cache_does_not_collide_on_same_keys_different_types(self, data) -> None:
        """
        TDD: Inferring types for two dicts with identical keys but different
        value types must produce two distinct and correct schemas. A naive
        cache might incorrectly return the schema for the first dict when
        asked for the second.
        """
        dict1, dict2 = data

        # Infer type for the first dictionary (all string keys)
        type1 = infer_cty_type_from_raw(dict1)

        # Infer type for the second dictionary (all string keys)
        type2 = infer_cty_type_from_raw(dict2)

        # The inferred types must be different CtyObject schemas.
        assert not type1.equal(type2)

        # Verify the correctness of each inferred type.
        assert isinstance(type1, CtyObject)
        assert all(v.equal(CtyString()) for v in type1.attribute_types.values())

        assert isinstance(type2, CtyObject)
        assert all(v.equal(CtyNumber()) for v in type2.attribute_types.values())
