"""
Performance Characterization Tool for pyvider.cty

This script provides a stable, repeatable way to measure the performance of
the core data conversion pipeline, independent of the pytest-benchmark framework.

It runs multiple trials of a realistic workload and calculates statistics
(mean, median, standard deviation, p95, p99) to establish a performance
baseline for the library.

Usage:
    python scripts/performance_characterization.py
"""
import random
import statistics
import time
from typing import Any

from pyvider.cty import CtyDynamic
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack
from pyvider.cty.conversion import cty_to_native

# --- Configuration ---
NUM_TRIALS = 10  # Number of full runs to perform
NUM_OBJECTS_PER_TRIAL = 2000  # Number of objects to process in each run
NESTING_DEPTH = 3  # Depth of the generated data structures

# --- Data Generation (adapted from performance tests) ---

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
    round trip on a single data object.
    """
    # 1. Validate (includes type inference)
    cty_val = schema.validate(raw_data)
    # 2. Serialize
    packed = cty_to_msgpack(cty_val, schema)
    # 3. Deserialize
    unpacked_val = cty_from_msgpack(packed, schema)
    # 4. Convert back to native
    _ = cty_to_native(unpacked_val)

# --- Main Execution Logic ---

def main() -> None:
    """Main function to run the performance characterization."""
    print("--- pyvider.cty Performance Characterization ---")
    print(f"Configuration: {NUM_TRIALS} trials, {NUM_OBJECTS_PER_TRIAL} objects/trial, depth={NESTING_DEPTH}\n")

    trial_durations: list[float] = []
    schema = CtyDynamic()

    for i in range(NUM_TRIALS):
        print(f"Running trial {i + 1}/{NUM_TRIALS}...", end="", flush=True)
        
        # CORRECTED: Generate data BEFORE the timer starts for the trial.
        # This isolates the measurement to only the cty operations.
        test_data = [
            generate_complex_object_data(NESTING_DEPTH)
            for _ in range(NUM_OBJECTS_PER_TRIAL)
        ]

        start_time = time.perf_counter()
        for raw_obj in test_data:
            core_roundtrip_operation(raw_obj, schema)
        end_time = time.perf_counter()
        
        duration_ms = (end_time - start_time) * 1000
        trial_durations.append(duration_ms)
        print(f" done. ({duration_ms:.2f} ms)")

    print("\n--- Performance Results ---")
    
    # Calculate statistics
    mean_duration = statistics.mean(trial_durations)
    median_duration = statistics.median(trial_durations)
    if len(trial_durations) > 1:
        stdev_duration = statistics.stdev(trial_durations)
    else:
        stdev_duration = 0.0

    # Calculate operations per second based on the mean duration
    ops_per_sec = (NUM_OBJECTS_PER_TRIAL / mean_duration) * 1000

    # Calculate percentiles
    sorted_durations = sorted(trial_durations)
    p95_index = int(len(sorted_durations) * 0.95)
    p99_index = int(len(sorted_durations) * 0.99)
    p95 = sorted_durations[p95_index]
    p99 = sorted_durations[p99_index]

    print(f"Objects per trial:    {NUM_OBJECTS_PER_TRIAL}")
    print(f"Total trials:         {NUM_TRIALS}")
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
