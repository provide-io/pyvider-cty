# pyvider-cty/src/pyvider/cty/conversion/_cache.py
"""
Provides a thread-safe, context-aware caching mechanism for type inference
to improve performance and ensure concurrent safety.
"""
from collections.abc import Callable, Generator
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from typing import Any, TypeVar

from ..types import CtyType

F = TypeVar("F", bound=Callable[..., Any])

# Context variables for the caches. Using `None` as a default indicates
# that no cache context is active.
_structural_key_cache: ContextVar[dict[int, tuple[Any, ...]] | None] = ContextVar(
    "_structural_key_cache", default=None
)
_container_schema_cache: ContextVar[
    dict[tuple[Any, ...], CtyType[Any]] | None
] = ContextVar("_container_schema_cache", default=None)


def get_structural_key_cache() -> dict[int, tuple[Any, ...]] | None:
    """Gets the current structural key cache from the context."""
    return _structural_key_cache.get()


def get_container_schema_cache() -> dict[tuple[Any, ...], CtyType[Any]] | None:
    """Gets the current container schema cache from the context."""
    return _container_schema_cache.get()


@contextmanager
def inference_cache_context() -> Generator[None, None, None]:
    """
    A context manager that provides an isolated inference cache for the duration
    of its context. Always creates a new isolated cache for thread safety.
    """
    # Always create a new isolated cache to ensure thread safety.
    # Save previous values to restore them later (if any).
    prev_struct = _structural_key_cache.get()
    prev_container = _container_schema_cache.get()

    token_struct = _structural_key_cache.set({})
    token_container = _container_schema_cache.set({})
    try:
        yield
    finally:
        _structural_key_cache.reset(token_struct)
        _container_schema_cache.reset(token_container)


def with_inference_cache(func: F) -> F:
    """
    A decorator that provides an isolated inference cache for the duration
    of the decorated function's execution by using the context manager.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        with inference_cache_context():
            return func(*args, **kwargs)

    return wrapper  # type: ignore
