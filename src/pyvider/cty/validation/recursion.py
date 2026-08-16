#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Advanced recursion detection for CTY validation.

This module provides sophisticated recursion detection that can distinguish between:
1. Genuine circular references that would cause infinite loops
2. Normal nested data structures with repetitive patterns
3. Deep but finite nesting that should be allowed

The implementation is designed for production IaC requirements where:
- Complex configurations with deep nesting must be supported
- Genuine circular references must be prevented
- Performance must be predictable and measurable
- Debugging and monitoring capabilities are essential"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from functools import wraps
import sys
import threading
import time
from typing import Any, cast

from provide.foundation import logger

from pyvider.cty.config.defaults import (
    DYNAMIC_DELEGATION_RESERVE,
    MAX_OBJECT_REVISITS,
    MAX_VALIDATION_TIME_MS,
    MIN_OWNED_OVERFLOW_DEPTH,
    default_max_validation_depth,
)


def _guard_depth_limit() -> int:
    """What the guard permits.

    A CtyDynamic value spends one guard entry more than its nesting depth,
    because its own guarded `validate` delegates to the concrete type's guarded
    `validate`. The derived limit hands the guard that one extra entry so the
    advertised depth is reachable for every type rather than all but one; the
    other types can therefore reach one level beyond what is advertised, which
    is why the advertised number is a floor and not a ceiling.

    An explicitly configured limit gets no reserve. Someone who asks for a bound
    of 10 means 10, and silently permitting 11 makes the setting a lie.
    """
    import os

    if os.environ.get("PYVIDER_CTY_MAX_VALIDATION_DEPTH"):
        return default_max_validation_depth()
    return default_max_validation_depth() + DYNAMIC_DELEGATION_RESERVE


@dataclass
class RecursionContext:
    """Thread-local context for tracking validation recursion."""

    # Object identity tracking: maps object id -> visit count (lightweight int counter)
    validation_graph: dict[int, int] = field(default_factory=dict)

    # Path tracking for detailed diagnostics (None entries are lightweight depth markers)
    validation_path: list[str | None] = field(default_factory=list)

    # Performance monitoring
    max_depth_reached: int = 0
    total_validations: int = 0
    validation_start_time: float = field(default_factory=time.time)

    # Configuration thresholds
    # Derived per context rather than read from a module constant, so it tracks
    # a recursion limit raised after import. See default_max_validation_depth.
    max_depth_allowed: int = field(default_factory=_guard_depth_limit)
    # The recursion limit `max_depth_allowed` was derived from, so a limit
    # changed later can be noticed without discarding an explicit override.
    derived_from_recursion_limit: int = field(default_factory=sys.getrecursionlimit)
    # What the derivation last produced, so an explicit override that changes
    # is noticed while a caller's hand-set `max_depth_allowed` is left alone.
    derived_depth: int = field(default_factory=_guard_depth_limit)
    max_object_revisits: int = MAX_OBJECT_REVISITS
    max_validation_time_ms: int = MAX_VALIDATION_TIME_MS

    # Flag to indicate validation was stopped due to recursion detection
    validation_stopped: bool = False

    def reset(self) -> None:
        """Reset context for new validation session.

        Re-derives the depth ceiling only when the interpreter's recursion
        limit has actually moved. Contexts are per-thread, so deriving it once
        at construction left each thread pinned to whatever the limit was when
        that thread first validated, and a pool gave different workers
        different ceilings.

        Recomputing unconditionally is wrong in the other direction: a caller
        that sets `max_depth_allowed` explicitly -- which tests and anything
        wanting a tighter bound do -- would have it silently discarded by the
        next top-level validate.
        """
        current_limit = sys.getrecursionlimit()
        derived = _guard_depth_limit()
        if current_limit != self.derived_from_recursion_limit or derived != self.derived_depth:
            self.max_depth_allowed = derived
            self.derived_from_recursion_limit = current_limit
            self.derived_depth = derived
        self.validation_graph.clear()
        self.validation_path.clear()
        self.max_depth_reached = 0
        self.total_validations = 0
        self.validation_start_time = time.time()
        self.validation_stopped = False


# Thread-local storage for recursion contexts
_thread_local = threading.local()


def get_recursion_context() -> RecursionContext:
    """Get or create thread-local recursion context."""
    if not hasattr(_thread_local, "recursion_context"):
        _thread_local.recursion_context = RecursionContext()
    return cast(RecursionContext, _thread_local.recursion_context)


def clear_recursion_context() -> None:
    """Clear thread-local recursion context."""
    if hasattr(_thread_local, "recursion_context"):
        _thread_local.recursion_context.reset()


class RecursionDetector:
    """
    Advanced recursion detector for CTY validation.

    This detector uses sophisticated algorithms to distinguish between:
    - Circular references (object A -> object B -> object A)
    - Deep but finite nesting (legitimate complex configurations)
    - Performance pathological cases (excessive validation time)
    """

    def __init__(self, context: RecursionContext | None = None) -> None:
        self.context = context or get_recursion_context()

    def should_continue_validation(self, value: Any, current_path: str = "", /) -> tuple[bool, str | None]:
        """
        Determine if validation should continue for the given value.

        Returns:
            (should_continue, reason_if_stopped)

        Production requirements:
        - Must handle legitimate deep nesting (1000+ levels)
        - Must detect genuine circular references quickly
        - Must provide detailed diagnostics for debugging
        - Must have predictable performance characteristics
        """

        # Performance safeguards - prevent pathological cases
        # Only check time every 64 validations to reduce time.time() overhead
        if self.context.total_validations & 63 == 0:
            elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        else:
            elapsed_ms = 0.0
        if elapsed_ms > self.context.max_validation_time_ms:
            reason = (
                f"Validation timeout after {elapsed_ms:.1f}ms (max: {self.context.max_validation_time_ms}ms)"
            )
            logger.warning(
                "CTY validation timeout exceeded",
                elapsed_ms=elapsed_ms,
                max_allowed_ms=self.context.max_validation_time_ms,
                path=current_path,
                trace="advanced_recursion_detection",
            )
            return False, reason

        # Update context
        self.context.total_validations += 1
        current_depth = len(self.context.validation_path)
        self.context.max_depth_reached = max(self.context.max_depth_reached, current_depth)

        # Depth safeguards - only trigger for truly deep recursion
        if current_depth > self.context.max_depth_allowed:
            reason = f"Maximum nesting depth exceeded: {current_depth} > {self.context.max_depth_allowed}"
            logger.warning(
                "CTY validation depth limit exceeded",
                current_depth=current_depth,
                max_allowed=self.context.max_depth_allowed,
                path=current_path,
                trace="advanced_recursion_detection",
            )
            return False, reason

        # Skip cycle detection for primitive types and simple collections (performance optimization)
        if isinstance(value, (str, int, float, bool, type(None))):
            return True, None

        # Skip cycle detection for simple lists/tuples of primitives
        if isinstance(value, (list, tuple)) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Lightweight cycle detection using visit counters
        value_id = id(value)
        visits = self.context.validation_graph.get(value_id, 0) + 1
        self.context.validation_graph[value_id] = visits

        if visits > self.context.max_object_revisits:
            value_type = type(value).__name__
            reason = (
                f"Circular reference detected: {value_type} object visited "
                f"{visits} times (max: {self.context.max_object_revisits})"
            )
            logger.debug(
                "CTY circular reference detected",
                object_type=value_type,
                object_id=value_id,
                visits=visits,
                current_depth=current_depth,
                path=current_path,
                trace="advanced_recursion_detection",
            )
            return False, reason

        return True, None

    def enter_validation_scope(self, scope_name: str) -> None:
        """Enter a new validation scope for path tracking."""
        self.context.validation_path.append(scope_name)

    def exit_validation_scope(self) -> None:
        """Exit the current validation scope."""
        if self.context.validation_path:
            self.context.validation_path.pop()

    def get_current_path(self) -> str:
        """Get the current validation path for diagnostics."""
        return " -> ".join(s for s in self.context.validation_path if s is not None)

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get performance metrics for monitoring and debugging."""
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        return {
            "total_validations": self.context.total_validations,
            "max_depth_reached": self.context.max_depth_reached,
            "elapsed_ms": elapsed_ms,
            "objects_in_graph": len(self.context.validation_graph),
            "avg_validations_per_ms": self.context.total_validations / max(elapsed_ms, 0.001),
            "current_path": self.get_current_path(),
        }


# How many of the innermost frames to inspect when deciding whether a
# RecursionError came from cty's own descent. The stack that ran out is the
# one at the bottom; a handful of frames is enough to tell whose it is.
_OVERFLOW_FRAMES_INSPECTED = 5


def _unknown_with_source_marks(value: Any, source_type: Any) -> Any:
    """An unknown of `source_type` carrying every mark found in `value`.

    Stopping validation is exactly when a value must not quietly lose its
    sensitivity: the caller gets an unknown either way, and an unmarked unknown
    is the silent declassification this mechanism exists to prevent.
    """
    from pyvider.cty.marks import collect_marks_deep
    from pyvider.cty.values import CtyValue

    unknown = CtyValue.unknown(source_type)
    marks = collect_marks_deep(value)
    return unknown.with_marks(marks) if marks else unknown


def _recover_from_overflow(exc: RecursionError, context: RecursionContext, value: Any, owner: Any) -> Any:
    """Turn a stack overflow inside cty's own descent into a controlled stop.

    Re-raises anything that did not originate here. An overflow raised by
    something cty called -- capsule code, a custom converter, a self-referential
    raw structure -- is a broken input, and converting it to an unknown would
    make it indistinguishable from a legitimately undecided one.

    Ownership is decided from where the overflow happened, not from how deep the
    validation path is. Depth was the wrong question in both directions: a
    caller already 700 frames deep overflows cty at a shallow validation depth
    and had its crash re-raised, while an infinite recursion in user code at a
    deep validation path was swallowed into an unknown.

    Everything here competes for the small overshoot CPython allows during
    cleanup, so the order matters: the degraded result is built first, and
    logging -- which goes through structlog and needs several frames -- is
    attempted last and allowed to fail.
    """
    tb = exc.__traceback__
    frames = []
    while tb is not None:
        frames.append(tb.tb_frame)
        tb = tb.tb_next

    ours = False
    for frame in frames[-_OVERFLOW_FRAMES_INSPECTED:]:
        if frame.f_globals.get("__name__", "").startswith("pyvider.cty"):
            ours = True
            break

    # Both conditions are needed. The traceback says the stack ran out in cty's
    # code; the depth says cty's own descent is what consumed it. Without the
    # second, a caller already ~990 frames deep validating a *two-level* value
    # overflowed inside cty and had a perfectly valid input degraded to an
    # unknown -- silently, since degrading raises nothing.
    if not ours or len(context.validation_path) < MIN_OWNED_OVERFLOW_DEPTH:
        raise exc

    context.validation_stopped = True

    try:
        degraded = _unknown_with_source_marks(value, owner)
    except RecursionError:
        # Not enough stack left even to collect the marks. Crashing is the safer
        # failure: an unknown whose marks could not be gathered would silently
        # declassify a sensitive value.
        raise exc from None

    # `contextlib.suppress` would read better but is a context manager, and
    # entering one costs frames this path does not have.
    try:  # noqa: SIM105
        logger.warning(
            "CTY validation hit Python recursion depth while validating value",
            value_type=type(value).__name__,
            recursion_limit=sys.getrecursionlimit(),
            depth=len(context.validation_path),
            path=f"{owner.__class__.__name__}.validate(type={type(value).__name__})",
        )
    except RecursionError:
        # Best effort. Losing the diagnostic is preferable to losing the
        # controlled stop it was describing.
        pass

    return degraded


def with_recursion_detection(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator for advanced recursion detection in validation functions.
    """
    # Pre-allocate a single detector instance per decorated function.
    # The detector is stateless — context comes from thread-local storage.
    _detector = RecursionDetector()

    @wraps(func)
    def wrapper(self: Any, value: Any, *args: Any, **kwargs: Any) -> Any:
        context = get_recursion_context()
        # A call is top-level if the validation path is empty, meaning no
        # parent frame is active.  Using the path (not total_validations) lets
        # the context retain post-run metrics for inspection while still
        # correctly detecting the start of a fresh top-level validation.
        is_top_level_call = not context.validation_path
        if is_top_level_call:
            context.reset()

        # Bind detector to current thread's context (avoids per-call allocation)
        _detector.context = context

        # Use None as a lightweight depth marker instead of an f-string scope name.
        # The actual scope string is only constructed on the error path.
        context.validation_path.append(None)

        # Marks are restored here rather than by a second decorator layered over
        # this one. Every wrapper around a recursive validate keeps its frame
        # alive for the whole descent, so a separate @preserves_marks on these
        # types cost a third frame per nesting level and dropped the maximum
        # validatable depth by a third. Leaf types, which cannot recurse, use
        # the decorator; see validation/marks.py.
        #
        # Two frames per level is a published number: FRAMES_PER_VALIDATION_LEVEL
        # is what the advertised depth limit is derived from. Adding a frame here
        # without updating it makes that limit undeliverable again.
        #
        # Every exit from here goes through reapply_marks, including the guard's
        # early ones. Stopping validation is exactly when a value must not
        # quietly lose its sensitivity: the caller gets an unknown either way,
        # and an unmarked unknown is the same silent declassification this whole
        # mechanism exists to prevent.
        from pyvider.cty.validation.marks import reapply_marks

        try:
            # Check if validation was already stopped by a nested call
            if context.validation_stopped:
                return _unknown_with_source_marks(value, self)

            should_continue, reason = _detector.should_continue_validation(value)
            if not should_continue:
                # Set flag to stop all parent validations
                context.validation_stopped = True

                # Only construct debug strings on the error path
                scope_name = f"{self.__class__.__name__}.validate(type={type(value).__name__})"
                logger.warning(
                    "CTY validation stopped due to recursion detection",
                    reason=reason,
                    value_type=type(value).__name__,
                    path=scope_name,
                )
                return _unknown_with_source_marks(value, self)

            # The decorator no longer passes the internal flag down.
            result = func(self, value, *args, **kwargs)

            # Check again after validation in case a nested call stopped validation
            if context.validation_stopped:
                return _unknown_with_source_marks(value, self)

            return reapply_marks(value, result)
        except RecursionError as exc:
            return _recover_from_overflow(exc, context, value, self)
        finally:
            if context.validation_path:
                context.validation_path.pop()

    return wrapper


# 🌊🪢🔚
