"""
TDD: Ensures the type inference cache is thread-safe and does not leak state
between concurrent operations.
"""
import threading
from typing import Any

import pytest

from pyvider.cty import CtyBool, CtyList, CtyNumber, CtyObject, CtyString
from pyvider.cty.conversion import infer_cty_type_from_raw


def inference_task(data: Any, results: dict[int, Any]) -> None:
    """A simple task to be run in a thread."""
    try:
        inferred_type = infer_cty_type_from_raw(data)
        results[threading.get_ident()] = inferred_type
    except Exception as e:
        results[threading.get_ident()] = e


class TestInferenceConcurrencySafety:
    def test_concurrent_inference_is_isolated(self) -> None:
        """
        TDD: Verifies that multiple threads calling infer_cty_type_from_raw
        simultaneously do not interfere with each other's results. This
        will fail with a global, non-thread-safe cache.
        """
        # Define two structurally different data sets
        data1 = [{"id": i, "name": f"name-{i}"} for i in range(50)]
        data2 = [{"value": i, "enabled": i % 2 == 0} for i in range(50)]

        # Expected inferred types for each data set
        expected_type1 = CtyList(
            element_type=CtyObject(
                attribute_types={"id": CtyNumber(), "name": CtyString()}
            )
        )
        expected_type2 = CtyList(
            element_type=CtyObject(
                attribute_types={"value": CtyNumber(), "enabled": CtyBool()}
            )
        )

        results: dict[int, Any] = {}
        thread1 = threading.Thread(target=inference_task, args=(data1, results))
        thread2 = threading.Thread(target=inference_task, args=(data2, results))

        thread1.start()
        thread2.start()

        thread1.join(timeout=5)
        thread2.join(timeout=5)

        assert not thread1.is_alive(), "Thread 1 timed out"
        assert not thread2.is_alive(), "Thread 2 timed out"

        # Verify that each thread produced the correct result for its data
        type1_result = results.get(thread1.ident)
        type2_result = results.get(thread2.ident)

        assert not isinstance(
            type1_result, Exception
        ), f"Thread 1 failed with: {type1_result}"
        assert not isinstance(
            type2_result, Exception
        ), f"Thread 2 failed with: {type2_result}"

        assert type1_result.equal(
            expected_type1
        ), "Thread 1 produced an incorrect type"
        assert type2_result.equal(
            expected_type2
        ), "Thread 2 produced an incorrect type"


# 🐍🎯🧪🪄
