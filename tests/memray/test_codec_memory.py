"""Memory profiling tests for msgpack codec."""
import pytest
from wrknv.memray.runner import run_memray_stress

pytestmark = [pytest.mark.memray, pytest.mark.slow]


def test_codec_allocations(memray_output_dir, memray_baseline, memray_baselines_path):
    """Profile memory allocations in msgpack codec hot path."""
    run_memray_stress(
        script="scripts/memray/memray_codec_stress.py",
        baseline_key="codec_total_allocations",
        output_dir=memray_output_dir,
        baselines=memray_baseline,
        baselines_path=memray_baselines_path,
    )
