"""
Pytest configuration file for the entire test suite.
Includes automated setup for the cross-language compatibility suite.
"""
import shutil
import subprocess
from pathlib import Path

import pytest

def pytest_addoption(parser):
    """Adds custom command-line options to pytest."""
    parser.addoption(
        "--run-benchmarks", action="store_true", default=False,
        help="Run the performance benchmark tests.",
    )

def pytest_configure(config):
    """Adds a custom marker for benchmark tests."""
    config.addinivalue_line("markers", "benchmark: mark test as a performance benchmark")

def pytest_collection_modifyitems(config, items):
    """Skips benchmark tests if --run-benchmarks is not given."""
    if not config.getoption("--run-benchmarks"):
        skip_benchmark = pytest.mark.skip(reason="need --run-benchmarks option to run")
        for item in items:
            if "benchmark" in item.keywords:
                item.add_marker(skip_benchmark)
        return

@pytest.fixture(scope="session")
def go_fixtures(tmp_path_factory) -> Path:
    """Runs the Go->Python fixture generator."""
    project_root = Path(__file__).parent.parent
    go_gen_dir = project_root / "compatibility" / "go"
    fixture_dir = project_root / "tests" / "fixtures" / "go-cty"
    if not shutil.which("go"): pytest.skip("Go runtime not found.")
    try:
        subprocess.run(["go", "mod", "tidy"], cwd=go_gen_dir, check=True, capture_output=True, text=True)
        subprocess.run(["go", "run", ".", "-directory", str(fixture_dir.resolve())], cwd=go_gen_dir, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Go fixture generator failed:\n--- STDOUT ---\n{e.stdout}\n--- STDERR ---\n{e.stderr}", pytrace=False)
    return fixture_dir

@pytest.fixture(scope="session")
def python_to_go_verification(tmp_path_factory) -> None:
    """Runs the Python->Go fixture generator and verifier."""
    project_root = Path(__file__).parent.parent
    py_gen_script = project_root / "compatibility" / "python" / "generator.py"
    go_verify_dir = project_root / "compatibility" / "go" / "verifier"
    fixture_dir = tmp_path_factory.mktemp("py_fixtures")

    # 1. Run Python generator
    try:
        subprocess.run([shutil.which("python"), str(py_gen_script), "-d", str(fixture_dir)], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Python fixture generator failed:\n--- STDOUT ---\n{e.stdout}\n--- STDERR ---\n{e.stderr}", pytrace=False)

    # 2. Run Go verifier
    if not shutil.which("go"): pytest.skip("Go runtime not found.")
    try:
        subprocess.run(["go", "mod", "tidy"], cwd=go_verify_dir, check=True, capture_output=True, text=True)
        subprocess.run(["go", "run", ".", "-directory", str(fixture_dir)], cwd=go_verify_dir, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Go fixture verifier failed:\n--- STDOUT ---\n{e.stdout}\n--- STDERR ---\n{e.stderr}", pytrace=False)
