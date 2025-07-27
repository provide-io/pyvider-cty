"""
Provides high-level, parallelized operations for pyvider.cty.

This module contains functions that use multiprocessing to speed up
bulk operations on large collections of data. It uses a Pool initializer
to send the schema to each worker process only once, minimizing the
serialization overhead that would otherwise make parallelization inefficient.
"""
import multiprocessing
import os
from collections.abc import Iterable
from typing import Any

from .codec import cty_from_msgpack, cty_to_msgpack
from .conversion import convert
from .types import CtyType
from .values import CtyValue

# --- Worker-Global State ---
# These global variables will be populated in each worker process by the initializer.
# This avoids the extreme overhead of pickling the complex schema objects for every task.
_worker_schema: CtyType | None = None
_worker_source_schema: CtyType | None = None
_worker_target_schema: CtyType | None = None

# --- Initializer and Worker Functions ---

def _initializer(
    schema: CtyType | None = None,
    source_schema: CtyType | None = None,
    target_schema: CtyType | None = None,
) -> None:
    """
    This function runs once per worker process, setting up the global
    schemas for that process.
    """
    global _worker_schema, _worker_source_schema, _worker_target_schema
    if schema:
        _worker_schema = schema
    if source_schema:
        _worker_source_schema = source_schema
    if target_schema:
        _worker_target_schema = target_schema

def _validate_worker(raw_data: Any) -> CtyValue:
    """Worker for parallel_validate. Uses the initialized global schema."""
    if _worker_schema is None:
        raise RuntimeError("Worker schema not initialized.")
    return _worker_schema.validate(raw_data)

def _convert_worker(raw_data: Any) -> CtyValue:
    """Worker for parallel_convert. Uses initialized global schemas."""
    if _worker_source_schema is None or _worker_target_schema is None:
        raise RuntimeError("Worker schemas not initialized for conversion.")
    validated_val = _worker_source_schema.validate(raw_data)
    return convert(validated_val, _worker_target_schema)

def _to_msgpack_worker(cty_val: CtyValue) -> bytes:
    """Worker for parallel_to_msgpack. Uses the initialized global schema."""
    if _worker_schema is None:
        raise RuntimeError("Worker schema not initialized.")
    return cty_to_msgpack(cty_val, _worker_schema)

def _from_msgpack_worker(packed_bytes: bytes) -> CtyValue:
    """Worker for parallel_from_msgpack. Uses the initialized global schema."""
    if _worker_schema is None:
        raise RuntimeError("Worker schema not initialized.")
    return cty_from_msgpack(packed_bytes, _worker_schema)

# --- Public API Functions ---

def parallel_validate(
    schema: CtyType, data_iterable: Iterable[Any], *, chunk_size: int | None = None
) -> list[CtyValue]:
    cpu_count = os.cpu_count() or 1
    initargs = (schema,)
    with multiprocessing.Pool(processes=cpu_count, initializer=_initializer, initargs=initargs) as pool:
        return pool.map(_validate_worker, data_iterable, chunksize=chunk_size)

def parallel_convert(
    source_schema: CtyType, target_schema: CtyType, data_iterable: Iterable[Any], *, chunk_size: int | None = None
) -> list[CtyValue]:
    cpu_count = os.cpu_count() or 1
    initargs = (None, source_schema, target_schema)
    with multiprocessing.Pool(processes=cpu_count, initializer=_initializer, initargs=initargs) as pool:
        return pool.map(_convert_worker, data_iterable, chunksize=chunk_size)

def parallel_to_msgpack(
    schema: CtyType, cty_value_iterable: Iterable[CtyValue], *, chunk_size: int | None = None
) -> list[bytes]:
    cpu_count = os.cpu_count() or 1
    initargs = (schema,)
    with multiprocessing.Pool(processes=cpu_count, initializer=_initializer, initargs=initargs) as pool:
        return pool.map(_to_msgpack_worker, cty_value_iterable, chunksize=chunk_size)

def parallel_from_msgpack(
    schema: CtyType, bytes_iterable: Iterable[bytes], *, chunk_size: int | None = None
) -> list[CtyValue]:
    cpu_count = os.cpu_count() or 1
    initargs = (schema,)
    with multiprocessing.Pool(processes=cpu_count, initializer=_initializer, initargs=initargs) as pool:
        return pool.map(_from_msgpack_worker, bytes_iterable, chunksize=chunk_size)
