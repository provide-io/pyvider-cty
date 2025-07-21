from collections.abc import Generator
from contextlib import contextmanager

MAX_VALIDATION_DEPTH: int

@contextmanager
def deeper_validation() -> Generator[None]: ...
def get_validation_depth() -> int: ...
