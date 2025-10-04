"""
TDD: Ensures the explicit inference_cache_context manager works correctly
and can be nested without creating new caches.
"""

from pyvider.cty.conversion.inference_cache import (
    _container_schema_cache,
    _structural_key_cache,
    inference_cache_context,
)


class TestInferenceCacheContext:
    def test_context_manager_creates_and_clears_cache(self) -> None:
        """
        TDD: Verifies the context manager establishes a cache context and
        properly tears it down upon exit.
        """
        assert _structural_key_cache.get() is None
        assert _container_schema_cache.get() is None

        with inference_cache_context():
            struct_cache = _structural_key_cache.get()
            container_cache = _container_schema_cache.get()
            assert isinstance(struct_cache, dict)
            assert isinstance(container_cache, dict)

            # Add items to prove it's a real cache
            struct_cache[1] = (int,)
            container_cache[(int,)] = "dummy_type"  # type: ignore

        assert _structural_key_cache.get() is None
        assert _container_schema_cache.get() is None

    def test_nested_context_reuses_existing_cache(self) -> None:
        """
        TDD: Verifies that nested calls to the context manager or decorated
        functions reuse the outermost cache context.
        """
        with inference_cache_context():
            outer_struct_cache = _structural_key_cache.get()
            outer_container_cache = _container_schema_cache.get()
            assert outer_struct_cache is not None
            assert outer_container_cache is not None

            outer_struct_cache[1] = (int,)

            with inference_cache_context():
                inner_struct_cache = _structural_key_cache.get()
                # It should be the *same object* as the outer cache
                assert inner_struct_cache is outer_struct_cache
                assert inner_struct_cache.get(1) == (int,)

            # Exiting the inner context should not clear the cache
            assert _structural_key_cache.get() is outer_struct_cache
