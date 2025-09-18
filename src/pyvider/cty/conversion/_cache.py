from __future__ import annotations

from collections.abc import Callable, Generator
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from typing import Any, TypeVar

from pyvider.cty.types import CtyType

F = TypeVar("F", bound=Callable[..., Any])

# pyvider-cty/src/pyvider/cty/conversion/_cache.py
"""
Provides a thread-safe, context-aware caching mechanism for type inference
to improve performance and ensure concurrent safety.
"""

F = TypeVar("F", bound=Callable[..., Any])

# Context variables for the caches. Using `None` as a default indicates
# that no cache context is active.
_structural_key_cache: ContextVar[dict[int, tuple[Any, ...]] | None] = ContextVar[
    dict[int, tuple[Any, ...]] | None
]("_structural_key_cache", default=None)
_container_schema_cache: ContextVar[dict[tuple[Any, ...], CtyType[Any]] | None] = ContextVar[
    dict[tuple[Any, ...], CtyType[Any]] | None
]("_container_schema_cache", default=None)


def get_structural_key_cache() -> dict[int, tuple[Any, ...]] | None:
    """Gets the current structural key cache from the context."""
    return _structural_key_cache.get()


def get_container_schema_cache() -> dict[tuple[Any, ...], CtyType[Any]] | None:
    """Gets the current container schema cache from the context."""
    return _container_schema_cache.get()


@contextmanager
def inference_cache_context() -> Generator[None]:
    """
    A context manager that provides an isolated inference cache for the duration
    of its context. If a cache is already active, it reuses the existing one.
    Respects the configuration setting for enabling/disabling caches.
    """
    # Import here to avoid circular dependencies
    from pyvider.cty.config.runtime import CtyConfig

    config = CtyConfig.get_current()
    if not config.enable_type_inference_cache:
        # Caching is disabled - just yield without setting up caches
        yield
        return

    if _structural_key_cache.get() is None:
        token_struct = _structural_key_cache.set({})
        token_container = _container_schema_cache.set({})
        try:
            yield
        finally:
            _structural_key_cache.reset(token_struct)
            _container_schema_cache.reset(token_container)
    else:
        # A cache is already active, so just yield to the inner block.
        yield


def with_inference_cache(func: F) -> F:
    """
    A decorator that provides an isolated inference cache for the duration
    of the decorated function's execution by using the context manager.
    Ensures thread safety by providing each thread with its own cache context.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Always use inference cache context for proper thread isolation
        # ContextVar provides thread-local storage automatically
        with inference_cache_context():
            return func(*args, **kwargs)

    return wrapper  # type: ignore
