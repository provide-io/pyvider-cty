# pyvider/cty/validation/recursion.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Advanced recursion detection for CTY validation.

This module provides sophisticated recursion detection that can distinguish between:
1. Genuine circular references that would cause infinite loops
2. Normal nested data structures with repetitive patterns
3. Deep but finite nesting that should be allowed

The implementation is designed for production IaC requirements where:
- Complex configurations with deep nesting must be supported
- Genuine circular references must be prevented
- Performance must be predictable and measurable
- Debugging and monitoring capabilities are essential
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from functools import wraps
import threading
import time
from typing import Any, cast

from provide.foundation import logger
from provide.foundation.errors import error_boundary

from pyvider.cty.config.defaults import (
    MAX_OBJECT_REVISITS,
    MAX_VALIDATION_DEPTH,
    MAX_VALIDATION_TIME_MS,
)
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


@dataclass
class ValidationNode:
    """Represents a node in the validation graph for cycle detection."""

    object_id: int
    object_type: str
    depth: int
    parent_path: str
    first_seen_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        self.visits = 1


@dataclass
class RecursionContext:
    """Thread-local context for tracking validation recursion."""

    # Object identity tracking for cycle detection
    validation_graph: dict[int, ValidationNode] = field(default_factory=dict)

    # Path tracking for detailed diagnostics
    validation_path: list[str] = field(default_factory=list)

    # Performance monitoring
    max_depth_reached: int = 0
    total_validations: int = 0
    validation_start_time: float = field(default_factory=time.time)

    # Configuration thresholds
    max_depth_allowed: int = MAX_VALIDATION_DEPTH
    max_object_revisits: int = MAX_OBJECT_REVISITS
    max_validation_time_ms: int = MAX_VALIDATION_TIME_MS

    # Flag to indicate validation was stopped due to recursion detection
    validation_stopped: bool = False

    def reset(self) -> None:
        """Reset context for new validation session."""
        self.validation_graph.clear()
        self.validation_path.clear()
        self.max_depth_reached = 0
        self.total_validations = 0
        self.validation_start_time = time.time()
        self.validation_stopped = False


# Thread-local storage for recursion contexts
_thread_local = threading.local()


def x_get_recursion_context__mutmut_orig() -> RecursionContext:
    """Get or create thread-local recursion context."""
    if not hasattr(_thread_local, "recursion_context"):
        _thread_local.recursion_context = RecursionContext()
    return cast(RecursionContext, _thread_local.recursion_context)


def x_get_recursion_context__mutmut_1() -> RecursionContext:
    """Get or create thread-local recursion context."""
    if hasattr(_thread_local, "recursion_context"):
        _thread_local.recursion_context = RecursionContext()
    return cast(RecursionContext, _thread_local.recursion_context)


def x_get_recursion_context__mutmut_2() -> RecursionContext:
    """Get or create thread-local recursion context."""
    if not hasattr(None, "recursion_context"):
        _thread_local.recursion_context = RecursionContext()
    return cast(RecursionContext, _thread_local.recursion_context)


def x_get_recursion_context__mutmut_3() -> RecursionContext:
    """Get or create thread-local recursion context."""
    if not hasattr(_thread_local, None):
        _thread_local.recursion_context = RecursionContext()
    return cast(RecursionContext, _thread_local.recursion_context)


def x_get_recursion_context__mutmut_4() -> RecursionContext:
    """Get or create thread-local recursion context."""
    if not hasattr("recursion_context"):
        _thread_local.recursion_context = RecursionContext()
    return cast(RecursionContext, _thread_local.recursion_context)


def x_get_recursion_context__mutmut_5() -> RecursionContext:
    """Get or create thread-local recursion context."""
    if not hasattr(_thread_local, ):
        _thread_local.recursion_context = RecursionContext()
    return cast(RecursionContext, _thread_local.recursion_context)


def x_get_recursion_context__mutmut_6() -> RecursionContext:
    """Get or create thread-local recursion context."""
    if not hasattr(_thread_local, "XXrecursion_contextXX"):
        _thread_local.recursion_context = RecursionContext()
    return cast(RecursionContext, _thread_local.recursion_context)


def x_get_recursion_context__mutmut_7() -> RecursionContext:
    """Get or create thread-local recursion context."""
    if not hasattr(_thread_local, "RECURSION_CONTEXT"):
        _thread_local.recursion_context = RecursionContext()
    return cast(RecursionContext, _thread_local.recursion_context)


def x_get_recursion_context__mutmut_8() -> RecursionContext:
    """Get or create thread-local recursion context."""
    if not hasattr(_thread_local, "recursion_context"):
        _thread_local.recursion_context = None
    return cast(RecursionContext, _thread_local.recursion_context)


def x_get_recursion_context__mutmut_9() -> RecursionContext:
    """Get or create thread-local recursion context."""
    if not hasattr(_thread_local, "recursion_context"):
        _thread_local.recursion_context = RecursionContext()
    return cast(None, _thread_local.recursion_context)


def x_get_recursion_context__mutmut_10() -> RecursionContext:
    """Get or create thread-local recursion context."""
    if not hasattr(_thread_local, "recursion_context"):
        _thread_local.recursion_context = RecursionContext()
    return cast(RecursionContext, None)


def x_get_recursion_context__mutmut_11() -> RecursionContext:
    """Get or create thread-local recursion context."""
    if not hasattr(_thread_local, "recursion_context"):
        _thread_local.recursion_context = RecursionContext()
    return cast(_thread_local.recursion_context)


def x_get_recursion_context__mutmut_12() -> RecursionContext:
    """Get or create thread-local recursion context."""
    if not hasattr(_thread_local, "recursion_context"):
        _thread_local.recursion_context = RecursionContext()
    return cast(RecursionContext, )

x_get_recursion_context__mutmut_mutants : ClassVar[MutantDict] = {
'x_get_recursion_context__mutmut_1': x_get_recursion_context__mutmut_1, 
    'x_get_recursion_context__mutmut_2': x_get_recursion_context__mutmut_2, 
    'x_get_recursion_context__mutmut_3': x_get_recursion_context__mutmut_3, 
    'x_get_recursion_context__mutmut_4': x_get_recursion_context__mutmut_4, 
    'x_get_recursion_context__mutmut_5': x_get_recursion_context__mutmut_5, 
    'x_get_recursion_context__mutmut_6': x_get_recursion_context__mutmut_6, 
    'x_get_recursion_context__mutmut_7': x_get_recursion_context__mutmut_7, 
    'x_get_recursion_context__mutmut_8': x_get_recursion_context__mutmut_8, 
    'x_get_recursion_context__mutmut_9': x_get_recursion_context__mutmut_9, 
    'x_get_recursion_context__mutmut_10': x_get_recursion_context__mutmut_10, 
    'x_get_recursion_context__mutmut_11': x_get_recursion_context__mutmut_11, 
    'x_get_recursion_context__mutmut_12': x_get_recursion_context__mutmut_12
}

def get_recursion_context(*args, **kwargs):
    result = _mutmut_trampoline(x_get_recursion_context__mutmut_orig, x_get_recursion_context__mutmut_mutants, args, kwargs)
    return result 

get_recursion_context.__signature__ = _mutmut_signature(x_get_recursion_context__mutmut_orig)
x_get_recursion_context__mutmut_orig.__name__ = 'x_get_recursion_context'


def x_clear_recursion_context__mutmut_orig() -> None:
    """Clear thread-local recursion context."""
    if hasattr(_thread_local, "recursion_context"):
        _thread_local.recursion_context.reset()


def x_clear_recursion_context__mutmut_1() -> None:
    """Clear thread-local recursion context."""
    if hasattr(None, "recursion_context"):
        _thread_local.recursion_context.reset()


def x_clear_recursion_context__mutmut_2() -> None:
    """Clear thread-local recursion context."""
    if hasattr(_thread_local, None):
        _thread_local.recursion_context.reset()


def x_clear_recursion_context__mutmut_3() -> None:
    """Clear thread-local recursion context."""
    if hasattr("recursion_context"):
        _thread_local.recursion_context.reset()


def x_clear_recursion_context__mutmut_4() -> None:
    """Clear thread-local recursion context."""
    if hasattr(_thread_local, ):
        _thread_local.recursion_context.reset()


def x_clear_recursion_context__mutmut_5() -> None:
    """Clear thread-local recursion context."""
    if hasattr(_thread_local, "XXrecursion_contextXX"):
        _thread_local.recursion_context.reset()


def x_clear_recursion_context__mutmut_6() -> None:
    """Clear thread-local recursion context."""
    if hasattr(_thread_local, "RECURSION_CONTEXT"):
        _thread_local.recursion_context.reset()

x_clear_recursion_context__mutmut_mutants : ClassVar[MutantDict] = {
'x_clear_recursion_context__mutmut_1': x_clear_recursion_context__mutmut_1, 
    'x_clear_recursion_context__mutmut_2': x_clear_recursion_context__mutmut_2, 
    'x_clear_recursion_context__mutmut_3': x_clear_recursion_context__mutmut_3, 
    'x_clear_recursion_context__mutmut_4': x_clear_recursion_context__mutmut_4, 
    'x_clear_recursion_context__mutmut_5': x_clear_recursion_context__mutmut_5, 
    'x_clear_recursion_context__mutmut_6': x_clear_recursion_context__mutmut_6
}

def clear_recursion_context(*args, **kwargs):
    result = _mutmut_trampoline(x_clear_recursion_context__mutmut_orig, x_clear_recursion_context__mutmut_mutants, args, kwargs)
    return result 

clear_recursion_context.__signature__ = _mutmut_signature(x_clear_recursion_context__mutmut_orig)
x_clear_recursion_context__mutmut_orig.__name__ = 'x_clear_recursion_context'


class RecursionDetector:
    """
    Advanced recursion detector for CTY validation.

    This detector uses sophisticated algorithms to distinguish between:
    - Circular references (object A -> object B -> object A)
    - Deep but finite nesting (legitimate complex configurations)
    - Performance pathological cases (excessive validation time)
    """

    def xǁRecursionDetectorǁ__init____mutmut_orig(self, context: RecursionContext | None = None) -> None:
        self.context = context or get_recursion_context()

    def xǁRecursionDetectorǁ__init____mutmut_1(self, context: RecursionContext | None = None) -> None:
        self.context = None

    def xǁRecursionDetectorǁ__init____mutmut_2(self, context: RecursionContext | None = None) -> None:
        self.context = context and get_recursion_context()
    
    xǁRecursionDetectorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRecursionDetectorǁ__init____mutmut_1': xǁRecursionDetectorǁ__init____mutmut_1, 
        'xǁRecursionDetectorǁ__init____mutmut_2': xǁRecursionDetectorǁ__init____mutmut_2
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRecursionDetectorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁRecursionDetectorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁRecursionDetectorǁ__init____mutmut_orig)
    xǁRecursionDetectorǁ__init____mutmut_orig.__name__ = 'xǁRecursionDetectorǁ__init__'

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_orig(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_1(self, value: Any, current_path: str = "XXXX") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_2(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = None
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_3(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) / 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_4(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() + self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_5(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1001
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_6(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        if elapsed_ms >= self.context.max_validation_time_ms:
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_7(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        if elapsed_ms > self.context.max_validation_time_ms:
            reason = None
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_8(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        if elapsed_ms > self.context.max_validation_time_ms:
            reason = (
                f"Validation timeout after {elapsed_ms:.1f}ms (max: {self.context.max_validation_time_ms}ms)"
            )
            logger.warning(
                None,
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_9(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        if elapsed_ms > self.context.max_validation_time_ms:
            reason = (
                f"Validation timeout after {elapsed_ms:.1f}ms (max: {self.context.max_validation_time_ms}ms)"
            )
            logger.warning(
                "CTY validation timeout exceeded",
                elapsed_ms=None,
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_10(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        if elapsed_ms > self.context.max_validation_time_ms:
            reason = (
                f"Validation timeout after {elapsed_ms:.1f}ms (max: {self.context.max_validation_time_ms}ms)"
            )
            logger.warning(
                "CTY validation timeout exceeded",
                elapsed_ms=elapsed_ms,
                max_allowed_ms=None,
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_11(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        if elapsed_ms > self.context.max_validation_time_ms:
            reason = (
                f"Validation timeout after {elapsed_ms:.1f}ms (max: {self.context.max_validation_time_ms}ms)"
            )
            logger.warning(
                "CTY validation timeout exceeded",
                elapsed_ms=elapsed_ms,
                max_allowed_ms=self.context.max_validation_time_ms,
                path=None,
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_12(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        if elapsed_ms > self.context.max_validation_time_ms:
            reason = (
                f"Validation timeout after {elapsed_ms:.1f}ms (max: {self.context.max_validation_time_ms}ms)"
            )
            logger.warning(
                "CTY validation timeout exceeded",
                elapsed_ms=elapsed_ms,
                max_allowed_ms=self.context.max_validation_time_ms,
                path=current_path,
                trace=None,
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_13(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        if elapsed_ms > self.context.max_validation_time_ms:
            reason = (
                f"Validation timeout after {elapsed_ms:.1f}ms (max: {self.context.max_validation_time_ms}ms)"
            )
            logger.warning(
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_14(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        if elapsed_ms > self.context.max_validation_time_ms:
            reason = (
                f"Validation timeout after {elapsed_ms:.1f}ms (max: {self.context.max_validation_time_ms}ms)"
            )
            logger.warning(
                "CTY validation timeout exceeded",
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_15(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        if elapsed_ms > self.context.max_validation_time_ms:
            reason = (
                f"Validation timeout after {elapsed_ms:.1f}ms (max: {self.context.max_validation_time_ms}ms)"
            )
            logger.warning(
                "CTY validation timeout exceeded",
                elapsed_ms=elapsed_ms,
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_16(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        if elapsed_ms > self.context.max_validation_time_ms:
            reason = (
                f"Validation timeout after {elapsed_ms:.1f}ms (max: {self.context.max_validation_time_ms}ms)"
            )
            logger.warning(
                "CTY validation timeout exceeded",
                elapsed_ms=elapsed_ms,
                max_allowed_ms=self.context.max_validation_time_ms,
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_17(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        if elapsed_ms > self.context.max_validation_time_ms:
            reason = (
                f"Validation timeout after {elapsed_ms:.1f}ms (max: {self.context.max_validation_time_ms}ms)"
            )
            logger.warning(
                "CTY validation timeout exceeded",
                elapsed_ms=elapsed_ms,
                max_allowed_ms=self.context.max_validation_time_ms,
                path=current_path,
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_18(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        if elapsed_ms > self.context.max_validation_time_ms:
            reason = (
                f"Validation timeout after {elapsed_ms:.1f}ms (max: {self.context.max_validation_time_ms}ms)"
            )
            logger.warning(
                "XXCTY validation timeout exceededXX",
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_19(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        if elapsed_ms > self.context.max_validation_time_ms:
            reason = (
                f"Validation timeout after {elapsed_ms:.1f}ms (max: {self.context.max_validation_time_ms}ms)"
            )
            logger.warning(
                "cty validation timeout exceeded",
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_20(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        if elapsed_ms > self.context.max_validation_time_ms:
            reason = (
                f"Validation timeout after {elapsed_ms:.1f}ms (max: {self.context.max_validation_time_ms}ms)"
            )
            logger.warning(
                "CTY VALIDATION TIMEOUT EXCEEDED",
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_21(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        if elapsed_ms > self.context.max_validation_time_ms:
            reason = (
                f"Validation timeout after {elapsed_ms:.1f}ms (max: {self.context.max_validation_time_ms}ms)"
            )
            logger.warning(
                "CTY validation timeout exceeded",
                elapsed_ms=elapsed_ms,
                max_allowed_ms=self.context.max_validation_time_ms,
                path=current_path,
                trace="XXadvanced_recursion_detectionXX",
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_22(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        if elapsed_ms > self.context.max_validation_time_ms:
            reason = (
                f"Validation timeout after {elapsed_ms:.1f}ms (max: {self.context.max_validation_time_ms}ms)"
            )
            logger.warning(
                "CTY validation timeout exceeded",
                elapsed_ms=elapsed_ms,
                max_allowed_ms=self.context.max_validation_time_ms,
                path=current_path,
                trace="ADVANCED_RECURSION_DETECTION",
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_23(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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
            return True, reason

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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_24(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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
        self.context.total_validations = 1
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_25(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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
        self.context.total_validations -= 1
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_26(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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
        self.context.total_validations += 2
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_27(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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
        current_depth = None
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_28(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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
        self.context.max_depth_reached = None

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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_29(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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
        self.context.max_depth_reached = max(None, current_depth)

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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_30(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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
        self.context.max_depth_reached = max(self.context.max_depth_reached, None)

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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_31(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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
        self.context.max_depth_reached = max(current_depth)

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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_32(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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
        self.context.max_depth_reached = max(self.context.max_depth_reached, )

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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_33(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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
        if current_depth >= self.context.max_depth_allowed:
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_34(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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
            reason = None
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_35(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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
                None,
                current_depth=current_depth,
                max_allowed=self.context.max_depth_allowed,
                path=current_path,
                trace="advanced_recursion_detection",
            )
            return False, reason

        # Skip cycle detection for primitive types and simple collections (performance optimization)
        if isinstance(value, (str, int, float, bool, type(None))):
            return True, None

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_36(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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
                current_depth=None,
                max_allowed=self.context.max_depth_allowed,
                path=current_path,
                trace="advanced_recursion_detection",
            )
            return False, reason

        # Skip cycle detection for primitive types and simple collections (performance optimization)
        if isinstance(value, (str, int, float, bool, type(None))):
            return True, None

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_37(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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
                max_allowed=None,
                path=current_path,
                trace="advanced_recursion_detection",
            )
            return False, reason

        # Skip cycle detection for primitive types and simple collections (performance optimization)
        if isinstance(value, (str, int, float, bool, type(None))):
            return True, None

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_38(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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
                path=None,
                trace="advanced_recursion_detection",
            )
            return False, reason

        # Skip cycle detection for primitive types and simple collections (performance optimization)
        if isinstance(value, (str, int, float, bool, type(None))):
            return True, None

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_39(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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
                trace=None,
            )
            return False, reason

        # Skip cycle detection for primitive types and simple collections (performance optimization)
        if isinstance(value, (str, int, float, bool, type(None))):
            return True, None

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_40(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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
                current_depth=current_depth,
                max_allowed=self.context.max_depth_allowed,
                path=current_path,
                trace="advanced_recursion_detection",
            )
            return False, reason

        # Skip cycle detection for primitive types and simple collections (performance optimization)
        if isinstance(value, (str, int, float, bool, type(None))):
            return True, None

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_41(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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
                max_allowed=self.context.max_depth_allowed,
                path=current_path,
                trace="advanced_recursion_detection",
            )
            return False, reason

        # Skip cycle detection for primitive types and simple collections (performance optimization)
        if isinstance(value, (str, int, float, bool, type(None))):
            return True, None

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_42(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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
                path=current_path,
                trace="advanced_recursion_detection",
            )
            return False, reason

        # Skip cycle detection for primitive types and simple collections (performance optimization)
        if isinstance(value, (str, int, float, bool, type(None))):
            return True, None

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_43(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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
                trace="advanced_recursion_detection",
            )
            return False, reason

        # Skip cycle detection for primitive types and simple collections (performance optimization)
        if isinstance(value, (str, int, float, bool, type(None))):
            return True, None

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_44(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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
                )
            return False, reason

        # Skip cycle detection for primitive types and simple collections (performance optimization)
        if isinstance(value, (str, int, float, bool, type(None))):
            return True, None

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_45(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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
                "XXCTY validation depth limit exceededXX",
                current_depth=current_depth,
                max_allowed=self.context.max_depth_allowed,
                path=current_path,
                trace="advanced_recursion_detection",
            )
            return False, reason

        # Skip cycle detection for primitive types and simple collections (performance optimization)
        if isinstance(value, (str, int, float, bool, type(None))):
            return True, None

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_46(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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
                "cty validation depth limit exceeded",
                current_depth=current_depth,
                max_allowed=self.context.max_depth_allowed,
                path=current_path,
                trace="advanced_recursion_detection",
            )
            return False, reason

        # Skip cycle detection for primitive types and simple collections (performance optimization)
        if isinstance(value, (str, int, float, bool, type(None))):
            return True, None

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_47(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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
                "CTY VALIDATION DEPTH LIMIT EXCEEDED",
                current_depth=current_depth,
                max_allowed=self.context.max_depth_allowed,
                path=current_path,
                trace="advanced_recursion_detection",
            )
            return False, reason

        # Skip cycle detection for primitive types and simple collections (performance optimization)
        if isinstance(value, (str, int, float, bool, type(None))):
            return True, None

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_48(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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
                trace="XXadvanced_recursion_detectionXX",
            )
            return False, reason

        # Skip cycle detection for primitive types and simple collections (performance optimization)
        if isinstance(value, (str, int, float, bool, type(None))):
            return True, None

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_49(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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
                trace="ADVANCED_RECURSION_DETECTION",
            )
            return False, reason

        # Skip cycle detection for primitive types and simple collections (performance optimization)
        if isinstance(value, (str, int, float, bool, type(None))):
            return True, None

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_50(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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
            return True, reason

        # Skip cycle detection for primitive types and simple collections (performance optimization)
        if isinstance(value, (str, int, float, bool, type(None))):
            return True, None

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_51(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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
            return False, None

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_52(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) or all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_53(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            None
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_54(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return False, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_55(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = None
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_56(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(None)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_57(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = None

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_58(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(None).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_59(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id not in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_60(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = None
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_61(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits = 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_62(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits -= 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_63(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 2

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_64(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits >= self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_65(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = None
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_66(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    None,
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_67(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=None,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_68(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=None,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_69(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=None,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_70(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=None,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_71(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=None,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_72(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=None,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_73(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace=None,
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_74(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_75(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_76(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_77(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_78(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_79(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_80(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_81(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_82(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "XXCTY circular reference detectedXX",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_83(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "cty circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_84(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY CIRCULAR REFERENCE DETECTED",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_85(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="XXadvanced_recursion_detectionXX",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_86(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="ADVANCED_RECURSION_DETECTION",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_87(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return True, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_88(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                None,
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_89(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=None,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_90(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=None,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_91(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=None,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_92(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=None,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_93(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace=None,
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_94(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_95(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_96(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_97(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_98(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_99(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_100(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "XXCTY object revisitedXX",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_101(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "cty object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_102(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY OBJECT REVISITED",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_103(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="XXadvanced_recursion_detectionXX",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_104(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="ADVANCED_RECURSION_DETECTION",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_105(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = None

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_106(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=None,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_107(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=None,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_108(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=None,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_109(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=None,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_110(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_111(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                depth=current_depth,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_112(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                parent_path=current_path,
            )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_113(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                )

        return True, None

    def xǁRecursionDetectorǁshould_continue_validation__mutmut_114(self, value: Any, current_path: str = "") -> tuple[bool, str | None]:
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
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
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

        # Skip cycle detection for simple lists of primitives
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool, type(None))) for item in value
        ):
            return True, None

        # Sophisticated cycle detection
        value_id = id(value)
        value_type = type(value).__name__

        if value_id in self.context.validation_graph:
            node = self.context.validation_graph[value_id]
            node.visits += 1

            # Allow some revisits for complex but legitimate schemas
            if node.visits > self.context.max_object_revisits:
                reason = (
                    f"Circular reference detected: {value_type} object visited "
                    f"{node.visits} times (max: {self.context.max_object_revisits})"
                )
                logger.debug(
                    "CTY circular reference detected",
                    object_type=value_type,
                    object_id=value_id,
                    visits=node.visits,
                    first_seen_depth=node.depth,
                    current_depth=current_depth,
                    path=current_path,
                    trace="advanced_recursion_detection",
                )
                return False, reason

            # Log revisit for monitoring
            logger.debug(
                "CTY object revisited",
                object_type=value_type,
                object_id=value_id,
                visits=node.visits,
                path=current_path,
                trace="advanced_recursion_detection",
            )
        else:
            # First time seeing this object
            self.context.validation_graph[value_id] = ValidationNode(
                object_id=value_id,
                object_type=value_type,
                depth=current_depth,
                parent_path=current_path,
            )

        return False, None
    
    xǁRecursionDetectorǁshould_continue_validation__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRecursionDetectorǁshould_continue_validation__mutmut_1': xǁRecursionDetectorǁshould_continue_validation__mutmut_1, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_2': xǁRecursionDetectorǁshould_continue_validation__mutmut_2, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_3': xǁRecursionDetectorǁshould_continue_validation__mutmut_3, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_4': xǁRecursionDetectorǁshould_continue_validation__mutmut_4, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_5': xǁRecursionDetectorǁshould_continue_validation__mutmut_5, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_6': xǁRecursionDetectorǁshould_continue_validation__mutmut_6, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_7': xǁRecursionDetectorǁshould_continue_validation__mutmut_7, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_8': xǁRecursionDetectorǁshould_continue_validation__mutmut_8, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_9': xǁRecursionDetectorǁshould_continue_validation__mutmut_9, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_10': xǁRecursionDetectorǁshould_continue_validation__mutmut_10, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_11': xǁRecursionDetectorǁshould_continue_validation__mutmut_11, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_12': xǁRecursionDetectorǁshould_continue_validation__mutmut_12, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_13': xǁRecursionDetectorǁshould_continue_validation__mutmut_13, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_14': xǁRecursionDetectorǁshould_continue_validation__mutmut_14, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_15': xǁRecursionDetectorǁshould_continue_validation__mutmut_15, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_16': xǁRecursionDetectorǁshould_continue_validation__mutmut_16, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_17': xǁRecursionDetectorǁshould_continue_validation__mutmut_17, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_18': xǁRecursionDetectorǁshould_continue_validation__mutmut_18, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_19': xǁRecursionDetectorǁshould_continue_validation__mutmut_19, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_20': xǁRecursionDetectorǁshould_continue_validation__mutmut_20, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_21': xǁRecursionDetectorǁshould_continue_validation__mutmut_21, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_22': xǁRecursionDetectorǁshould_continue_validation__mutmut_22, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_23': xǁRecursionDetectorǁshould_continue_validation__mutmut_23, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_24': xǁRecursionDetectorǁshould_continue_validation__mutmut_24, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_25': xǁRecursionDetectorǁshould_continue_validation__mutmut_25, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_26': xǁRecursionDetectorǁshould_continue_validation__mutmut_26, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_27': xǁRecursionDetectorǁshould_continue_validation__mutmut_27, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_28': xǁRecursionDetectorǁshould_continue_validation__mutmut_28, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_29': xǁRecursionDetectorǁshould_continue_validation__mutmut_29, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_30': xǁRecursionDetectorǁshould_continue_validation__mutmut_30, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_31': xǁRecursionDetectorǁshould_continue_validation__mutmut_31, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_32': xǁRecursionDetectorǁshould_continue_validation__mutmut_32, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_33': xǁRecursionDetectorǁshould_continue_validation__mutmut_33, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_34': xǁRecursionDetectorǁshould_continue_validation__mutmut_34, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_35': xǁRecursionDetectorǁshould_continue_validation__mutmut_35, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_36': xǁRecursionDetectorǁshould_continue_validation__mutmut_36, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_37': xǁRecursionDetectorǁshould_continue_validation__mutmut_37, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_38': xǁRecursionDetectorǁshould_continue_validation__mutmut_38, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_39': xǁRecursionDetectorǁshould_continue_validation__mutmut_39, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_40': xǁRecursionDetectorǁshould_continue_validation__mutmut_40, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_41': xǁRecursionDetectorǁshould_continue_validation__mutmut_41, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_42': xǁRecursionDetectorǁshould_continue_validation__mutmut_42, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_43': xǁRecursionDetectorǁshould_continue_validation__mutmut_43, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_44': xǁRecursionDetectorǁshould_continue_validation__mutmut_44, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_45': xǁRecursionDetectorǁshould_continue_validation__mutmut_45, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_46': xǁRecursionDetectorǁshould_continue_validation__mutmut_46, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_47': xǁRecursionDetectorǁshould_continue_validation__mutmut_47, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_48': xǁRecursionDetectorǁshould_continue_validation__mutmut_48, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_49': xǁRecursionDetectorǁshould_continue_validation__mutmut_49, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_50': xǁRecursionDetectorǁshould_continue_validation__mutmut_50, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_51': xǁRecursionDetectorǁshould_continue_validation__mutmut_51, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_52': xǁRecursionDetectorǁshould_continue_validation__mutmut_52, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_53': xǁRecursionDetectorǁshould_continue_validation__mutmut_53, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_54': xǁRecursionDetectorǁshould_continue_validation__mutmut_54, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_55': xǁRecursionDetectorǁshould_continue_validation__mutmut_55, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_56': xǁRecursionDetectorǁshould_continue_validation__mutmut_56, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_57': xǁRecursionDetectorǁshould_continue_validation__mutmut_57, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_58': xǁRecursionDetectorǁshould_continue_validation__mutmut_58, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_59': xǁRecursionDetectorǁshould_continue_validation__mutmut_59, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_60': xǁRecursionDetectorǁshould_continue_validation__mutmut_60, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_61': xǁRecursionDetectorǁshould_continue_validation__mutmut_61, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_62': xǁRecursionDetectorǁshould_continue_validation__mutmut_62, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_63': xǁRecursionDetectorǁshould_continue_validation__mutmut_63, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_64': xǁRecursionDetectorǁshould_continue_validation__mutmut_64, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_65': xǁRecursionDetectorǁshould_continue_validation__mutmut_65, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_66': xǁRecursionDetectorǁshould_continue_validation__mutmut_66, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_67': xǁRecursionDetectorǁshould_continue_validation__mutmut_67, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_68': xǁRecursionDetectorǁshould_continue_validation__mutmut_68, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_69': xǁRecursionDetectorǁshould_continue_validation__mutmut_69, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_70': xǁRecursionDetectorǁshould_continue_validation__mutmut_70, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_71': xǁRecursionDetectorǁshould_continue_validation__mutmut_71, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_72': xǁRecursionDetectorǁshould_continue_validation__mutmut_72, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_73': xǁRecursionDetectorǁshould_continue_validation__mutmut_73, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_74': xǁRecursionDetectorǁshould_continue_validation__mutmut_74, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_75': xǁRecursionDetectorǁshould_continue_validation__mutmut_75, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_76': xǁRecursionDetectorǁshould_continue_validation__mutmut_76, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_77': xǁRecursionDetectorǁshould_continue_validation__mutmut_77, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_78': xǁRecursionDetectorǁshould_continue_validation__mutmut_78, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_79': xǁRecursionDetectorǁshould_continue_validation__mutmut_79, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_80': xǁRecursionDetectorǁshould_continue_validation__mutmut_80, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_81': xǁRecursionDetectorǁshould_continue_validation__mutmut_81, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_82': xǁRecursionDetectorǁshould_continue_validation__mutmut_82, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_83': xǁRecursionDetectorǁshould_continue_validation__mutmut_83, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_84': xǁRecursionDetectorǁshould_continue_validation__mutmut_84, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_85': xǁRecursionDetectorǁshould_continue_validation__mutmut_85, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_86': xǁRecursionDetectorǁshould_continue_validation__mutmut_86, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_87': xǁRecursionDetectorǁshould_continue_validation__mutmut_87, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_88': xǁRecursionDetectorǁshould_continue_validation__mutmut_88, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_89': xǁRecursionDetectorǁshould_continue_validation__mutmut_89, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_90': xǁRecursionDetectorǁshould_continue_validation__mutmut_90, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_91': xǁRecursionDetectorǁshould_continue_validation__mutmut_91, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_92': xǁRecursionDetectorǁshould_continue_validation__mutmut_92, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_93': xǁRecursionDetectorǁshould_continue_validation__mutmut_93, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_94': xǁRecursionDetectorǁshould_continue_validation__mutmut_94, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_95': xǁRecursionDetectorǁshould_continue_validation__mutmut_95, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_96': xǁRecursionDetectorǁshould_continue_validation__mutmut_96, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_97': xǁRecursionDetectorǁshould_continue_validation__mutmut_97, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_98': xǁRecursionDetectorǁshould_continue_validation__mutmut_98, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_99': xǁRecursionDetectorǁshould_continue_validation__mutmut_99, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_100': xǁRecursionDetectorǁshould_continue_validation__mutmut_100, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_101': xǁRecursionDetectorǁshould_continue_validation__mutmut_101, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_102': xǁRecursionDetectorǁshould_continue_validation__mutmut_102, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_103': xǁRecursionDetectorǁshould_continue_validation__mutmut_103, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_104': xǁRecursionDetectorǁshould_continue_validation__mutmut_104, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_105': xǁRecursionDetectorǁshould_continue_validation__mutmut_105, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_106': xǁRecursionDetectorǁshould_continue_validation__mutmut_106, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_107': xǁRecursionDetectorǁshould_continue_validation__mutmut_107, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_108': xǁRecursionDetectorǁshould_continue_validation__mutmut_108, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_109': xǁRecursionDetectorǁshould_continue_validation__mutmut_109, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_110': xǁRecursionDetectorǁshould_continue_validation__mutmut_110, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_111': xǁRecursionDetectorǁshould_continue_validation__mutmut_111, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_112': xǁRecursionDetectorǁshould_continue_validation__mutmut_112, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_113': xǁRecursionDetectorǁshould_continue_validation__mutmut_113, 
        'xǁRecursionDetectorǁshould_continue_validation__mutmut_114': xǁRecursionDetectorǁshould_continue_validation__mutmut_114
    }
    
    def should_continue_validation(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRecursionDetectorǁshould_continue_validation__mutmut_orig"), object.__getattribute__(self, "xǁRecursionDetectorǁshould_continue_validation__mutmut_mutants"), args, kwargs, self)
        return result 
    
    should_continue_validation.__signature__ = _mutmut_signature(xǁRecursionDetectorǁshould_continue_validation__mutmut_orig)
    xǁRecursionDetectorǁshould_continue_validation__mutmut_orig.__name__ = 'xǁRecursionDetectorǁshould_continue_validation'

    def xǁRecursionDetectorǁenter_validation_scope__mutmut_orig(self, scope_name: str) -> None:
        """Enter a new validation scope for path tracking."""
        self.context.validation_path.append(scope_name)

    def xǁRecursionDetectorǁenter_validation_scope__mutmut_1(self, scope_name: str) -> None:
        """Enter a new validation scope for path tracking."""
        self.context.validation_path.append(None)
    
    xǁRecursionDetectorǁenter_validation_scope__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRecursionDetectorǁenter_validation_scope__mutmut_1': xǁRecursionDetectorǁenter_validation_scope__mutmut_1
    }
    
    def enter_validation_scope(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRecursionDetectorǁenter_validation_scope__mutmut_orig"), object.__getattribute__(self, "xǁRecursionDetectorǁenter_validation_scope__mutmut_mutants"), args, kwargs, self)
        return result 
    
    enter_validation_scope.__signature__ = _mutmut_signature(xǁRecursionDetectorǁenter_validation_scope__mutmut_orig)
    xǁRecursionDetectorǁenter_validation_scope__mutmut_orig.__name__ = 'xǁRecursionDetectorǁenter_validation_scope'

    def exit_validation_scope(self) -> None:
        """Exit the current validation scope."""
        if self.context.validation_path:
            self.context.validation_path.pop()

    def xǁRecursionDetectorǁget_current_path__mutmut_orig(self) -> str:
        """Get the current validation path for diagnostics."""
        return " -> ".join(self.context.validation_path)

    def xǁRecursionDetectorǁget_current_path__mutmut_1(self) -> str:
        """Get the current validation path for diagnostics."""
        return " -> ".join(None)

    def xǁRecursionDetectorǁget_current_path__mutmut_2(self) -> str:
        """Get the current validation path for diagnostics."""
        return "XX -> XX".join(self.context.validation_path)
    
    xǁRecursionDetectorǁget_current_path__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRecursionDetectorǁget_current_path__mutmut_1': xǁRecursionDetectorǁget_current_path__mutmut_1, 
        'xǁRecursionDetectorǁget_current_path__mutmut_2': xǁRecursionDetectorǁget_current_path__mutmut_2
    }
    
    def get_current_path(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRecursionDetectorǁget_current_path__mutmut_orig"), object.__getattribute__(self, "xǁRecursionDetectorǁget_current_path__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_current_path.__signature__ = _mutmut_signature(xǁRecursionDetectorǁget_current_path__mutmut_orig)
    xǁRecursionDetectorǁget_current_path__mutmut_orig.__name__ = 'xǁRecursionDetectorǁget_current_path'

    def xǁRecursionDetectorǁget_performance_metrics__mutmut_orig(self) -> dict[str, Any]:
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

    def xǁRecursionDetectorǁget_performance_metrics__mutmut_1(self) -> dict[str, Any]:
        """Get performance metrics for monitoring and debugging."""
        elapsed_ms = None
        return {
            "total_validations": self.context.total_validations,
            "max_depth_reached": self.context.max_depth_reached,
            "elapsed_ms": elapsed_ms,
            "objects_in_graph": len(self.context.validation_graph),
            "avg_validations_per_ms": self.context.total_validations / max(elapsed_ms, 0.001),
            "current_path": self.get_current_path(),
        }

    def xǁRecursionDetectorǁget_performance_metrics__mutmut_2(self) -> dict[str, Any]:
        """Get performance metrics for monitoring and debugging."""
        elapsed_ms = (time.time() - self.context.validation_start_time) / 1000
        return {
            "total_validations": self.context.total_validations,
            "max_depth_reached": self.context.max_depth_reached,
            "elapsed_ms": elapsed_ms,
            "objects_in_graph": len(self.context.validation_graph),
            "avg_validations_per_ms": self.context.total_validations / max(elapsed_ms, 0.001),
            "current_path": self.get_current_path(),
        }

    def xǁRecursionDetectorǁget_performance_metrics__mutmut_3(self) -> dict[str, Any]:
        """Get performance metrics for monitoring and debugging."""
        elapsed_ms = (time.time() + self.context.validation_start_time) * 1000
        return {
            "total_validations": self.context.total_validations,
            "max_depth_reached": self.context.max_depth_reached,
            "elapsed_ms": elapsed_ms,
            "objects_in_graph": len(self.context.validation_graph),
            "avg_validations_per_ms": self.context.total_validations / max(elapsed_ms, 0.001),
            "current_path": self.get_current_path(),
        }

    def xǁRecursionDetectorǁget_performance_metrics__mutmut_4(self) -> dict[str, Any]:
        """Get performance metrics for monitoring and debugging."""
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1001
        return {
            "total_validations": self.context.total_validations,
            "max_depth_reached": self.context.max_depth_reached,
            "elapsed_ms": elapsed_ms,
            "objects_in_graph": len(self.context.validation_graph),
            "avg_validations_per_ms": self.context.total_validations / max(elapsed_ms, 0.001),
            "current_path": self.get_current_path(),
        }

    def xǁRecursionDetectorǁget_performance_metrics__mutmut_5(self) -> dict[str, Any]:
        """Get performance metrics for monitoring and debugging."""
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        return {
            "XXtotal_validationsXX": self.context.total_validations,
            "max_depth_reached": self.context.max_depth_reached,
            "elapsed_ms": elapsed_ms,
            "objects_in_graph": len(self.context.validation_graph),
            "avg_validations_per_ms": self.context.total_validations / max(elapsed_ms, 0.001),
            "current_path": self.get_current_path(),
        }

    def xǁRecursionDetectorǁget_performance_metrics__mutmut_6(self) -> dict[str, Any]:
        """Get performance metrics for monitoring and debugging."""
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        return {
            "TOTAL_VALIDATIONS": self.context.total_validations,
            "max_depth_reached": self.context.max_depth_reached,
            "elapsed_ms": elapsed_ms,
            "objects_in_graph": len(self.context.validation_graph),
            "avg_validations_per_ms": self.context.total_validations / max(elapsed_ms, 0.001),
            "current_path": self.get_current_path(),
        }

    def xǁRecursionDetectorǁget_performance_metrics__mutmut_7(self) -> dict[str, Any]:
        """Get performance metrics for monitoring and debugging."""
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        return {
            "total_validations": self.context.total_validations,
            "XXmax_depth_reachedXX": self.context.max_depth_reached,
            "elapsed_ms": elapsed_ms,
            "objects_in_graph": len(self.context.validation_graph),
            "avg_validations_per_ms": self.context.total_validations / max(elapsed_ms, 0.001),
            "current_path": self.get_current_path(),
        }

    def xǁRecursionDetectorǁget_performance_metrics__mutmut_8(self) -> dict[str, Any]:
        """Get performance metrics for monitoring and debugging."""
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        return {
            "total_validations": self.context.total_validations,
            "MAX_DEPTH_REACHED": self.context.max_depth_reached,
            "elapsed_ms": elapsed_ms,
            "objects_in_graph": len(self.context.validation_graph),
            "avg_validations_per_ms": self.context.total_validations / max(elapsed_ms, 0.001),
            "current_path": self.get_current_path(),
        }

    def xǁRecursionDetectorǁget_performance_metrics__mutmut_9(self) -> dict[str, Any]:
        """Get performance metrics for monitoring and debugging."""
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        return {
            "total_validations": self.context.total_validations,
            "max_depth_reached": self.context.max_depth_reached,
            "XXelapsed_msXX": elapsed_ms,
            "objects_in_graph": len(self.context.validation_graph),
            "avg_validations_per_ms": self.context.total_validations / max(elapsed_ms, 0.001),
            "current_path": self.get_current_path(),
        }

    def xǁRecursionDetectorǁget_performance_metrics__mutmut_10(self) -> dict[str, Any]:
        """Get performance metrics for monitoring and debugging."""
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        return {
            "total_validations": self.context.total_validations,
            "max_depth_reached": self.context.max_depth_reached,
            "ELAPSED_MS": elapsed_ms,
            "objects_in_graph": len(self.context.validation_graph),
            "avg_validations_per_ms": self.context.total_validations / max(elapsed_ms, 0.001),
            "current_path": self.get_current_path(),
        }

    def xǁRecursionDetectorǁget_performance_metrics__mutmut_11(self) -> dict[str, Any]:
        """Get performance metrics for monitoring and debugging."""
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        return {
            "total_validations": self.context.total_validations,
            "max_depth_reached": self.context.max_depth_reached,
            "elapsed_ms": elapsed_ms,
            "XXobjects_in_graphXX": len(self.context.validation_graph),
            "avg_validations_per_ms": self.context.total_validations / max(elapsed_ms, 0.001),
            "current_path": self.get_current_path(),
        }

    def xǁRecursionDetectorǁget_performance_metrics__mutmut_12(self) -> dict[str, Any]:
        """Get performance metrics for monitoring and debugging."""
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        return {
            "total_validations": self.context.total_validations,
            "max_depth_reached": self.context.max_depth_reached,
            "elapsed_ms": elapsed_ms,
            "OBJECTS_IN_GRAPH": len(self.context.validation_graph),
            "avg_validations_per_ms": self.context.total_validations / max(elapsed_ms, 0.001),
            "current_path": self.get_current_path(),
        }

    def xǁRecursionDetectorǁget_performance_metrics__mutmut_13(self) -> dict[str, Any]:
        """Get performance metrics for monitoring and debugging."""
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        return {
            "total_validations": self.context.total_validations,
            "max_depth_reached": self.context.max_depth_reached,
            "elapsed_ms": elapsed_ms,
            "objects_in_graph": len(self.context.validation_graph),
            "XXavg_validations_per_msXX": self.context.total_validations / max(elapsed_ms, 0.001),
            "current_path": self.get_current_path(),
        }

    def xǁRecursionDetectorǁget_performance_metrics__mutmut_14(self) -> dict[str, Any]:
        """Get performance metrics for monitoring and debugging."""
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        return {
            "total_validations": self.context.total_validations,
            "max_depth_reached": self.context.max_depth_reached,
            "elapsed_ms": elapsed_ms,
            "objects_in_graph": len(self.context.validation_graph),
            "AVG_VALIDATIONS_PER_MS": self.context.total_validations / max(elapsed_ms, 0.001),
            "current_path": self.get_current_path(),
        }

    def xǁRecursionDetectorǁget_performance_metrics__mutmut_15(self) -> dict[str, Any]:
        """Get performance metrics for monitoring and debugging."""
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        return {
            "total_validations": self.context.total_validations,
            "max_depth_reached": self.context.max_depth_reached,
            "elapsed_ms": elapsed_ms,
            "objects_in_graph": len(self.context.validation_graph),
            "avg_validations_per_ms": self.context.total_validations * max(elapsed_ms, 0.001),
            "current_path": self.get_current_path(),
        }

    def xǁRecursionDetectorǁget_performance_metrics__mutmut_16(self) -> dict[str, Any]:
        """Get performance metrics for monitoring and debugging."""
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        return {
            "total_validations": self.context.total_validations,
            "max_depth_reached": self.context.max_depth_reached,
            "elapsed_ms": elapsed_ms,
            "objects_in_graph": len(self.context.validation_graph),
            "avg_validations_per_ms": self.context.total_validations / max(None, 0.001),
            "current_path": self.get_current_path(),
        }

    def xǁRecursionDetectorǁget_performance_metrics__mutmut_17(self) -> dict[str, Any]:
        """Get performance metrics for monitoring and debugging."""
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        return {
            "total_validations": self.context.total_validations,
            "max_depth_reached": self.context.max_depth_reached,
            "elapsed_ms": elapsed_ms,
            "objects_in_graph": len(self.context.validation_graph),
            "avg_validations_per_ms": self.context.total_validations / max(elapsed_ms, None),
            "current_path": self.get_current_path(),
        }

    def xǁRecursionDetectorǁget_performance_metrics__mutmut_18(self) -> dict[str, Any]:
        """Get performance metrics for monitoring and debugging."""
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        return {
            "total_validations": self.context.total_validations,
            "max_depth_reached": self.context.max_depth_reached,
            "elapsed_ms": elapsed_ms,
            "objects_in_graph": len(self.context.validation_graph),
            "avg_validations_per_ms": self.context.total_validations / max(0.001),
            "current_path": self.get_current_path(),
        }

    def xǁRecursionDetectorǁget_performance_metrics__mutmut_19(self) -> dict[str, Any]:
        """Get performance metrics for monitoring and debugging."""
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        return {
            "total_validations": self.context.total_validations,
            "max_depth_reached": self.context.max_depth_reached,
            "elapsed_ms": elapsed_ms,
            "objects_in_graph": len(self.context.validation_graph),
            "avg_validations_per_ms": self.context.total_validations / max(elapsed_ms, ),
            "current_path": self.get_current_path(),
        }

    def xǁRecursionDetectorǁget_performance_metrics__mutmut_20(self) -> dict[str, Any]:
        """Get performance metrics for monitoring and debugging."""
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        return {
            "total_validations": self.context.total_validations,
            "max_depth_reached": self.context.max_depth_reached,
            "elapsed_ms": elapsed_ms,
            "objects_in_graph": len(self.context.validation_graph),
            "avg_validations_per_ms": self.context.total_validations / max(elapsed_ms, 1.001),
            "current_path": self.get_current_path(),
        }

    def xǁRecursionDetectorǁget_performance_metrics__mutmut_21(self) -> dict[str, Any]:
        """Get performance metrics for monitoring and debugging."""
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        return {
            "total_validations": self.context.total_validations,
            "max_depth_reached": self.context.max_depth_reached,
            "elapsed_ms": elapsed_ms,
            "objects_in_graph": len(self.context.validation_graph),
            "avg_validations_per_ms": self.context.total_validations / max(elapsed_ms, 0.001),
            "XXcurrent_pathXX": self.get_current_path(),
        }

    def xǁRecursionDetectorǁget_performance_metrics__mutmut_22(self) -> dict[str, Any]:
        """Get performance metrics for monitoring and debugging."""
        elapsed_ms = (time.time() - self.context.validation_start_time) * 1000
        return {
            "total_validations": self.context.total_validations,
            "max_depth_reached": self.context.max_depth_reached,
            "elapsed_ms": elapsed_ms,
            "objects_in_graph": len(self.context.validation_graph),
            "avg_validations_per_ms": self.context.total_validations / max(elapsed_ms, 0.001),
            "CURRENT_PATH": self.get_current_path(),
        }
    
    xǁRecursionDetectorǁget_performance_metrics__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRecursionDetectorǁget_performance_metrics__mutmut_1': xǁRecursionDetectorǁget_performance_metrics__mutmut_1, 
        'xǁRecursionDetectorǁget_performance_metrics__mutmut_2': xǁRecursionDetectorǁget_performance_metrics__mutmut_2, 
        'xǁRecursionDetectorǁget_performance_metrics__mutmut_3': xǁRecursionDetectorǁget_performance_metrics__mutmut_3, 
        'xǁRecursionDetectorǁget_performance_metrics__mutmut_4': xǁRecursionDetectorǁget_performance_metrics__mutmut_4, 
        'xǁRecursionDetectorǁget_performance_metrics__mutmut_5': xǁRecursionDetectorǁget_performance_metrics__mutmut_5, 
        'xǁRecursionDetectorǁget_performance_metrics__mutmut_6': xǁRecursionDetectorǁget_performance_metrics__mutmut_6, 
        'xǁRecursionDetectorǁget_performance_metrics__mutmut_7': xǁRecursionDetectorǁget_performance_metrics__mutmut_7, 
        'xǁRecursionDetectorǁget_performance_metrics__mutmut_8': xǁRecursionDetectorǁget_performance_metrics__mutmut_8, 
        'xǁRecursionDetectorǁget_performance_metrics__mutmut_9': xǁRecursionDetectorǁget_performance_metrics__mutmut_9, 
        'xǁRecursionDetectorǁget_performance_metrics__mutmut_10': xǁRecursionDetectorǁget_performance_metrics__mutmut_10, 
        'xǁRecursionDetectorǁget_performance_metrics__mutmut_11': xǁRecursionDetectorǁget_performance_metrics__mutmut_11, 
        'xǁRecursionDetectorǁget_performance_metrics__mutmut_12': xǁRecursionDetectorǁget_performance_metrics__mutmut_12, 
        'xǁRecursionDetectorǁget_performance_metrics__mutmut_13': xǁRecursionDetectorǁget_performance_metrics__mutmut_13, 
        'xǁRecursionDetectorǁget_performance_metrics__mutmut_14': xǁRecursionDetectorǁget_performance_metrics__mutmut_14, 
        'xǁRecursionDetectorǁget_performance_metrics__mutmut_15': xǁRecursionDetectorǁget_performance_metrics__mutmut_15, 
        'xǁRecursionDetectorǁget_performance_metrics__mutmut_16': xǁRecursionDetectorǁget_performance_metrics__mutmut_16, 
        'xǁRecursionDetectorǁget_performance_metrics__mutmut_17': xǁRecursionDetectorǁget_performance_metrics__mutmut_17, 
        'xǁRecursionDetectorǁget_performance_metrics__mutmut_18': xǁRecursionDetectorǁget_performance_metrics__mutmut_18, 
        'xǁRecursionDetectorǁget_performance_metrics__mutmut_19': xǁRecursionDetectorǁget_performance_metrics__mutmut_19, 
        'xǁRecursionDetectorǁget_performance_metrics__mutmut_20': xǁRecursionDetectorǁget_performance_metrics__mutmut_20, 
        'xǁRecursionDetectorǁget_performance_metrics__mutmut_21': xǁRecursionDetectorǁget_performance_metrics__mutmut_21, 
        'xǁRecursionDetectorǁget_performance_metrics__mutmut_22': xǁRecursionDetectorǁget_performance_metrics__mutmut_22
    }
    
    def get_performance_metrics(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRecursionDetectorǁget_performance_metrics__mutmut_orig"), object.__getattribute__(self, "xǁRecursionDetectorǁget_performance_metrics__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_performance_metrics.__signature__ = _mutmut_signature(xǁRecursionDetectorǁget_performance_metrics__mutmut_orig)
    xǁRecursionDetectorǁget_performance_metrics__mutmut_orig.__name__ = 'xǁRecursionDetectorǁget_performance_metrics'


def with_recursion_detection(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator for advanced recursion detection in validation functions.
    """

    @wraps(func)
    def wrapper(self: Any, value: Any, *args: Any, **kwargs: Any) -> Any:
        context = get_recursion_context()
        # A call is top-level if the context has not been used yet.
        is_top_level_call = context.total_validations == 0
        if is_top_level_call:
            context.reset()

        detector = RecursionDetector(context)
        scope_name = f"{self.__class__.__name__}.validate(type={type(value).__name__})"

        with error_boundary(
            context={
                "operation": "recursion_detection",
                "type_name": self.__class__.__name__,
                "value_type": type(value).__name__,
                "validation_depth": len(context.validation_path),
                "total_validations": context.total_validations,
            }
        ):
            detector.enter_validation_scope(scope_name)

            try:
                # Check if validation was already stopped by a nested call
                if context.validation_stopped:
                    from pyvider.cty.values import CtyValue

                    return CtyValue.unknown(self)

                should_continue, reason = detector.should_continue_validation(
                    value, detector.get_current_path()
                )
                if not should_continue:
                    from pyvider.cty.values import CtyValue

                    # Set flag to stop all parent validations
                    context.validation_stopped = True

                    logger.warning(
                        "CTY validation stopped due to recursion detection",
                        reason=reason,
                        value_type=type(value).__name__,
                        path=detector.get_current_path(),
                    )
                    return CtyValue.unknown(self)

                # The decorator no longer passes the internal flag down.
                result = func(self, value, *args, **kwargs)

                # Check again after validation in case a nested call stopped validation
                if context.validation_stopped:
                    from pyvider.cty.values import CtyValue

                    return CtyValue.unknown(self)

                return result
            finally:
                detector.exit_validation_scope()

    return wrapper


# 🌊🪢✅🪄
