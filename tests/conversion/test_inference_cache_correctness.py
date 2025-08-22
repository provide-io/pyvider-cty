"""
TDD: Ensures the structural cache correctly distinguishes between list-like
and dict-like containers, even when they contain identical values.
"""
import pytest
from pyvider.cty.conversion import infer_cty_type_from_raw
from pyvider.cty.types import CtyList, CtyMap, CtyNumber, CtyObject, CtyString

class TestInferenceCacheCorrectness:
    def test_cache_distinguishes_list_from_dict_with_same_values(self):
        """
        TDD: A list of values and a dict of values must not have colliding
        cache keys. This tests that the container type is part of the key.
        """
        # These two structures contain the exact same CtyValue objects.
        # A naive cache that only looks at child values might collide.
        list_of_vals = [{"a": 1}, {"b": 2}]
        dict_of_vals = {"k1": {"a": 1}, "k2": {"b": 2}}

        # Inferring the list first should not poison the cache for the dict.
        list_type = infer_cty_type_from_raw(list_of_vals)
        dict_type = infer_cty_type_from_raw(dict_of_vals)

        assert isinstance(list_type, CtyList)
        # It's a list of objects with different keys, so element type is dynamic.
        assert list_type.element_type.is_dynamic_type()

        assert isinstance(dict_type, CtyObject)
        assert isinstance(dict_type.attribute_types["k1"], CtyObject)
