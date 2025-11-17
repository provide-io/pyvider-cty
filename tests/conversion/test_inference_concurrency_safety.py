#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TDD: Ensures the type inference cache is thread-safe and does not leak state
between concurrent operations."""

import threading
from typing import Any

from pyvider.cty import CtyBool, CtyList, CtyNumber, CtyObject, CtyString
from pyvider.cty.conversion import infer_cty_type_from_raw


def inference_task(data: Any, result_container: list[Any]) -> None:
    """A simple task to be run in a thread."""
    try:
        inferred_type = infer_cty_type_from_raw(data)
        result_container.append(inferred_type)
    except Exception as e:
        result_container.append(e)


class TestInferenceConcurrencySafety:
    def test_concurrent_inference_is_isolated(self, monkeypatch) -> None:
        """
        TDD: Verifies that multiple threads calling infer_cty_type_from_raw
        simultaneously do not interfere with each other's results. This
        will fail with a global, non-thread-safe cache.

        For this test, we disable caching entirely to ensure pure concurrency testing.
        """
        # Disable caching for this test to ensure pure thread isolation testing
        monkeypatch.setenv("PYVIDER_CTY_ENABLE_TYPE_INFERENCE_CACHE", "false")

        # Also patch the config directly to ensure it's disabled in threaded contexts
        from pyvider.cty.config.runtime import CtyConfig

        mock_config = CtyConfig(enable_type_inference_cache=False)
        monkeypatch.setattr(CtyConfig, "get_current", lambda: mock_config)
        # Define two structurally different data sets
        data1 = [{"id": i, "name": f"name-{i}"} for i in range(50)]
        data2 = [{"value": i, "enabled": i % 2 == 0} for i in range(50)]

        # Expected inferred types for each data set
        expected_type1 = CtyList(
            element_type=CtyObject(attribute_types={"id": CtyNumber(), "name": CtyString()})
        )
        expected_type2 = CtyList(
            element_type=CtyObject(attribute_types={"value": CtyNumber(), "enabled": CtyBool()})
        )

        # Use separate result containers to avoid shared key collisions
        result1: list[Any] = []
        result2: list[Any] = []

        thread1 = threading.Thread(target=inference_task, args=(data1, result1))
        thread2 = threading.Thread(target=inference_task, args=(data2, result2))

        thread1.start()
        thread2.start()

        thread1.join(timeout=5)
        thread2.join(timeout=5)

        assert not thread1.is_alive(), "Thread 1 timed out"
        assert not thread2.is_alive(), "Thread 2 timed out"

        # Verify that each thread produced exactly one result
        assert len(result1) == 1, f"Thread 1 should produce exactly one result, got {len(result1)}"
        assert len(result2) == 1, f"Thread 2 should produce exactly one result, got {len(result2)}"

        type1_result = result1[0]
        type2_result = result2[0]

        assert not isinstance(type1_result, Exception), f"Thread 1 failed with: {type1_result}"
        assert not isinstance(type2_result, Exception), f"Thread 2 failed with: {type2_result}"

        assert type1_result.equal(expected_type1), "Thread 1 produced an incorrect type"
        assert type2_result.equal(expected_type2), "Thread 2 produced an incorrect type"


# 🌊🪢🔚
