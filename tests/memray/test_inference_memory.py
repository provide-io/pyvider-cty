"""Memory profiling tests for type inference."""

import pytest
from wrknv.memray.runner import run_memray_stress

pytestmark = [pytest.mark.memray, pytest.mark.slow]


def test_inference_allocations(memray_output_dir, memray_baseline, memray_baselines_path):
    """Profile memory allocations in type inference hot path."""
    run_memray_stress(
        script="scripts/memray/memray_inference_stress.py",
        baseline_key="inference_total_allocations",
        output_dir=memray_output_dir,
        baselines=memray_baseline,
        baselines_path=memray_baselines_path,
    )
