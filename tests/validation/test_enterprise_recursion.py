#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Comprehensive tests for recursion detection in CTY validation.

These tests ensure the recursion detection system meets production IaC requirements:
- Handle complex real-world configurations with deep nesting
- Detect genuine circular references quickly and accurately
- Provide detailed diagnostics for troubleshooting
- Maintain predictable performance characteristics
- Support monitoring and observability requirements"""

import queue
import threading

from pyvider.cty import CtyDynamic
from pyvider.cty.validation.recursion import (
    RecursionDetector,
    clear_recursion_context,
    get_recursion_context,
)


class TestAdvancedRecursionDetection:
    """Test suite for advanced recursion detection."""

    def setup_method(self) -> None:
        """Reset recursion context before each test."""
        clear_recursion_context()

    def teardown_method(self) -> None:
        """Ensure context is cleared after each test."""
        clear_recursion_context()

    def test_handles_legitimate_deep_nesting(self) -> None:
        """
        Verifies that deep, but finite, nesting succeeds when it is below
        the configured limit.
        """
        # The default limit is 500. We test with 400 levels.
        deep_config = {}
        current = deep_config
        for i in range(1, 400):
            current["nested"] = {"level": i}
            current = current["nested"]

        dynamic_type = CtyDynamic()
        result = dynamic_type.validate(deep_config)

        assert not result.is_unknown, "Legitimate deep nesting should not result in an unknown value."
        context = get_recursion_context()
        assert context.max_depth_reached > 350, "Validation did not reach expected depth."

    def test_exceeding_max_depth_returns_unknown(self) -> None:
        """
        Verifies that exceeding the configured recursion depth limit gracefully
        returns an 'unknown' value instead of raising a RecursionError.
        """
        context = get_recursion_context()
        context.max_depth_allowed = 100  # Set a low limit for this specific test

        deep_config = {}
        current = deep_config
        for i in range(1, 150):  # Create nesting deeper than the limit
            current["nested"] = {"level": i}
            current = current["nested"]

        dynamic_type = CtyDynamic()
        result = dynamic_type.validate(deep_config)

        assert result.is_unknown, "Exceeding max depth should result in an unknown value."

    def test_detects_genuine_circular_references(self) -> None:
        """
        Verifies that a direct circular reference is detected and handled
        by returning an 'unknown' value.
        """
        circular_obj = {"name": "parent"}
        child_obj = {"name": "child", "parent": circular_obj}
        circular_obj["child"] = child_obj

        dynamic_type = CtyDynamic()
        result = dynamic_type.validate(circular_obj)

        assert result.is_unknown, "Circular reference should result in an unknown value."

    def test_performance_monitoring_and_metrics_are_populated(self) -> None:
        """
        Verifies that performance metrics are correctly populated after a
        successful validation run.
        """
        config = {"a": {"b": {"c": [1, 2, 3]}}}
        dynamic_type = CtyDynamic()
        result = dynamic_type.validate(config)

        assert not result.is_unknown
        context = get_recursion_context()
        metrics = RecursionDetector(context).get_performance_metrics()

        assert "total_validations" in metrics
        assert "max_depth_reached" in metrics
        assert "elapsed_ms" in metrics
        assert "objects_in_graph" in metrics
        assert metrics["total_validations"] > 0
        assert metrics["max_depth_reached"] > 0

    def test_concurrent_validation_is_isolated(self) -> None:
        """
        Verifies that concurrent validations in separate threads do not
        interfere with each other's recursion contexts.
        """
        results = queue.Queue()

        def validate_in_thread(config_data, thread_id) -> None:
            try:
                # Each thread gets its own isolated context.
                clear_recursion_context()
                dynamic_type = CtyDynamic()
                result = dynamic_type.validate(config_data)
                context = get_recursion_context()
                metrics = RecursionDetector(context).get_performance_metrics()
                results.put((thread_id, result.is_unknown, metrics))
            except Exception as e:
                results.put((thread_id, e, None))

        # Create two different complex objects
        data1 = {"data": [{"item": i} for i in range(50)]}
        data2 = {"config": {"params": {"p": [i for i in range(50)]}}}

        thread1 = threading.Thread(target=validate_in_thread, args=(data1, 1))
        thread2 = threading.Thread(target=validate_in_thread, args=(data2, 2))

        thread1.start()
        thread2.start()
        thread1.join(timeout=5)
        thread2.join(timeout=5)

        assert not thread1.is_alive(), "Thread 1 timed out"
        assert not thread2.is_alive(), "Thread 2 timed out"

        thread_results = []
        while not results.empty():
            thread_results.append(results.get())

        assert len(thread_results) == 2
        for thread_id, result, metrics in thread_results:
            assert not isinstance(result, Exception), f"Thread {thread_id} failed: {result}"
            assert result is False, f"Thread {thread_id} validation failed (returned unknown)"
            assert metrics["total_validations"] > 0
            assert metrics["max_depth_reached"] > 0


# 🌊🪢🔚
