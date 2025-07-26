"""
TDD Test Suite for Performance Optimization via Caching.

These tests will fail until caching (memoization) is correctly implemented
for the `unify` and `infer_cty_type_from_raw` functions.
"""
import pytest
from unittest.mock import patch

from pyvider.cty import CtyList, CtyNumber, CtyString
from pyvider.cty.conversion import unify, infer_cty_type_from_raw
from pyvider.cty.conversion import explicit as explicit_conversion
from pyvider.cty.conversion import raw_to_cty as raw_to_cty_conversion

# --- TDD for `unify` Caching ---
class TestUnifyCaching:
    def test_unify_is_cached(self):
        """
        TDD: Verifies that the core logic of `unify` is wrapped in a cache.
        Checks for a private helper with `cache_info`, a standard `lru_cache` feature.
        """
        assert hasattr(explicit_conversion, "_unify_frozen"), \
            "TDD FAIL: Expected a private, memoized helper function `_unify_frozen` in explicit.py"

        cached_unify = getattr(explicit_conversion, "_unify_frozen")
        assert hasattr(cached_unify, "cache_info"), \
            "TDD FAIL: `_unify_frozen` does not have .cache_info. It must be decorated with @functools.lru_cache."

    def test_unify_handles_unhashable_input(self):
        """
        TDD: Verifies the public `unify` function accepts unhashable lists
        and hits the cache on subsequent calls with equivalent data.
        """
        try:
            cached_unify = getattr(explicit_conversion, "_unify_frozen")
            cached_unify.cache_clear()
        except (AttributeError, TypeError):
            pytest.fail("Could not find or clear cache on `_unify_frozen`. Implement test_unify_is_cached first.")

        types1 = [CtyList(element_type=CtyString()), CtyList(element_type=CtyNumber())]
        types2 = [CtyList(element_type=CtyString()), CtyList(element_type=CtyNumber())]

        unify(types1)
        misses1 = cached_unify.cache_info().misses
        assert misses1 >= 1, "First call should have been a cache miss."

        unify(types2)
        hits2 = cached_unify.cache_info().hits
        misses2 = cached_unify.cache_info().misses

        assert hits2 >= 1, "TDD FAIL: Cache was not hit on the second call with equivalent types."
        assert misses2 == misses1, "TDD FAIL: Cache missed on the second call when it should have hit."


# --- TDD for `infer_cty_type_from_raw` Caching ---
class TestInferTypeCaching:
    def test_infer_cty_type_from_raw_is_cached(self):
        """
        TDD: Verifies that `infer_cty_type_from_raw` is memoized.
        """
        assert hasattr(raw_to_cty_conversion.infer_cty_type_from_raw, "cache_info"), \
            "TDD FAIL: `infer_cty_type_from_raw` must be decorated with a cache that provides a .cache_info() method."

    def test_cache_handles_unhashable_types(self):
        """
        TDD: Verifies the cache for `infer_cty_type_from_raw` can handle
        unhashable inputs like dicts and lists, which is not possible with
        a naive `@lru_cache` decorator.
        """
        try:
            infer_cache = raw_to_cty_conversion.infer_cty_type_from_raw
            infer_cache.cache_clear()
        except (AttributeError, TypeError):
            pytest.fail("Could not find or clear cache on `infer_cty_type_from_raw`. Implement test_infer_cty_type_from_raw_is_cached first.")

        # Two identical, but distinct, complex dictionaries
        data1 = {"a": [1, "b"], "c": {"d": True}}
        data2 = {"a": [1, "b"], "c": {"d": True}}

        try:
            # First call should be a miss
            infer_cache(data1)
            misses1 = infer_cache.cache_info().misses
            assert misses1 >= 1

            # Second call should be a hit
            infer_cache(data2)
            hits2 = infer_cache.cache_info().hits
            misses2 = infer_cache.cache_info().misses
            
            assert hits2 >= 1, "TDD FAIL: Cache did not hit for an equivalent unhashable dict."
            assert misses2 == misses1, "TDD FAIL: Cache missed for an equivalent unhashable dict."

        except TypeError as e:
            if "unhashable type" in str(e):
                pytest.fail(
                    "TDD FAIL: The cache on `infer_cty_type_from_raw` cannot handle unhashable types like 'dict'. "
                    "A custom memoization decorator is required."
                )
            raise # Re-raise other TypeErrors
