"""
Pytest configuration file for the entire test suite.
"""

import pytest

def pytest_addoption(parser):
    """Adds custom command-line options to pytest."""
    parser.addoption(
        "--run-benchmarks",
        action="store_true",
        default=False,
        help="Run the performance benchmark tests.",
    )

def pytest_configure(config):
    """Adds a custom marker for benchmark tests."""
    config.addinivalue_line(
        "markers", "benchmark: mark test as a performance benchmark"
    )

def pytest_collection_modifyitems(config, items):
    """Skips benchmark tests if --run-benchmarks is not given."""
    if not config.getoption("--run-benchmarks"):
        # --run-benchmarks option not provided, skip the benchmarks
        skip_benchmark = pytest.mark.skip(reason="need --run-benchmarks option to run")
        for item in items:
            if "benchmark" in item.keywords:
                item.add_marker(skip_benchmark)
        return
