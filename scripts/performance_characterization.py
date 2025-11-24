#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Performance Characterization Tool for pyvider.cty

This script provides a stable, repeatable way to measure the performance of
the core data conversion pipeline, independent of the pytest-benchmark framework.

It now utilizes multiprocessing to leverage all available CPU cores, providing
a more accurate measure of maximum throughput and system resource utilization.

Usage:
    python scripts/performance_characterization.py"""

import functools
import multiprocessing
import os
import random
import statistics
import time
from typing import Any

from pyvider.cty import CtyDynamic
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack
from pyvider.cty.conversion import cty_to_native

# --- Configuration ---
NUM_TRIALS = 5  # Fewer trials needed as each is more intensive
NUM_OBJECTS_PER_TRIAL = 10000  # Increased object count for a more substantial workload
NESTING_DEPTH = 3  # Depth of the generated data structures

# --- Data Generation ---


def generate_complex_object_data(depth: int) -> dict[str, Any]:
    """Generates a unique, nested Python dictionary."""
    if depth <= 0:
        return {
            "id": f"leaf-{random.randint(1000, 9999)}",
            "value": random.random() * 100,
            "enabled": random.choice([True, False]),
        }
    return {
        "id": f"node-{depth}-{random.randint(100, 999)}",
        "timestamp": time.time(),
        "metadata": {"source": "profiler", "version": "1.0"},
        "children": [generate_complex_object_data(depth - 1) for _ in range(2)],
    }


# --- Core Operation ---


def core_roundtrip_operation(raw_data: dict[str, Any], schema: CtyDynamic) -> None:
    """
    Performs a full validate -> serialize -> deserialize -> convert_to_native
    round trip on a single data object. This is the unit of work for each process.
    """
    cty_val = schema.validate(raw_data)
    packed = cty_to_msgpack(cty_val, schema)
    unpacked_val = cty_from_msgpack(packed, schema)
    _ = cty_to_native(unpacked_val)


# --- Main Execution Logic ---


def main() -> None:
    """Main function to run the performance characterization."""
    cpu_count = os.cpu_count() or 1
    print("--- pyvider.cty Parallel Performance Characterization ---")
    print(f"Utilizing {cpu_count} CPU cores.")
    print(
        f"Configuration: {NUM_TRIALS} trials, {NUM_OBJECTS_PER_TRIAL} objects/trial, depth={NESTING_DEPTH}\n"
    )

    trial_durations: list[float] = []
    schema = CtyDynamic()

    # Create a partial function to pass the static 'schema' argument to the worker processes.
    workload = functools.partial(core_roundtrip_operation, schema=schema)

    with multiprocessing.Pool(processes=cpu_count) as pool:
        for i in range(NUM_TRIALS):
            print(f"Running trial {i + 1}/{NUM_TRIALS}...", end="", flush=True)

            test_data = [generate_complex_object_data(NESTING_DEPTH) for _ in range(NUM_OBJECTS_PER_TRIAL)]

            start_time = time.perf_counter()
            # Distribute the workload across the process pool.
            # pool.map will chunk the data and send it to worker processes.
            pool.map(workload, test_data)
            end_time = time.perf_counter()

            duration_ms = (end_time - start_time) * 1000
            trial_durations.append(duration_ms)
            print(f" done. ({duration_ms:.2f} ms)")

    print("\n--- Performance Results ---")

    mean_duration = statistics.mean(trial_durations)
    median_duration = statistics.median(trial_durations)
    stdev_duration = statistics.stdev(trial_durations) if len(trial_durations) > 1 else 0.0
    ops_per_sec = (NUM_OBJECTS_PER_TRIAL / mean_duration) * 1000
    sorted_durations = sorted(trial_durations)
    p95 = sorted_durations[int(len(sorted_durations) * 0.95)]
    p99 = sorted_durations[int(len(sorted_durations) * 0.99)]

    print(f"Objects per trial:    {NUM_OBJECTS_PER_TRIAL}")
    print(f"Total trials:         {NUM_TRIALS}")
    print(f"Worker Processes:     {cpu_count}")
    print("-" * 27)
    print(f"Mean duration:        {mean_duration:.2f} ms")
    print(f"Median duration:      {median_duration:.2f} ms")
    print(f"Std Dev:              {stdev_duration:.2f} ms")
    print(f"P95 Latency:          {p95:.2f} ms")
    print(f"P99 Latency:          {p99:.2f} ms")
    print("-" * 27)
    print(f"Operations/sec:       {ops_per_sec:,.2f}")
    print("\n--- Characterization Complete ---")


if __name__ == "__main__":
    main()

# 🌊🪢🔚
