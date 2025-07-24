"""
Pytest configuration file for the entire test suite.
Includes automated setup for the cross-language compatibility suite.
"""
import os
import shutil
import subprocess
import time
from pathlib import Path

import pytest

def pytest_addoption(parser):
    """Adds custom command-line options to pytest."""
    parser.addoption(
        "--run-benchmarks", action="store_true", default=False,
        help="Run the performance benchmark tests.",
    )
    parser.addoption(
        "--run-compat", action="store_true", default=False,
        help="Run the Go/Python cross-language compatibility tests.",
    )

def pytest_configure(config):
    """Adds custom markers."""
    config.addinivalue_line("markers", "benchmark: mark test as a performance benchmark")
    config.addinivalue_line("markers", "compat: mark test as a cross-language compatibility test")

def pytest_collection_modifyitems(config, items):
    """Skips tests based on command-line options."""
    if not config.getoption("--run-benchmarks"):
        skip_benchmark = pytest.mark.skip(reason="need --run-benchmarks option to run")
        for item in items:
            if "benchmark" in item.keywords:
                item.add_marker(skip_benchmark)
    
    if not config.getoption("--run-compat"):
        skip_compat = pytest.mark.skip(reason="need --run-compat option to run")
        for item in items:
            if "compat" in item.keywords:
                item.add_marker(skip_compat)

@pytest.fixture(scope="session")
def go_fixtures(pytestconfig) -> Path:
    """
    A session-scoped fixture that automatically runs the Go fixture generator.
    This ensures that the canonical `.msgpack` files from go-cty are always
    present before the compatibility tests run.
    """
    project_root = Path(__file__).parent.parent
    go_compat_dir = project_root / "compatibility" / "go"
    fixture_dir = project_root / "tests" / "fixtures" / "go-cty"

    if not shutil.which("go"):
        pytest.skip("Go runtime not found, skipping cross-language compatibility tests.")

    logs_dir = project_root / "logs"
    os.makedirs(logs_dir, exist_ok=True)
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    log_file_path = logs_dir / f"gocompat-{timestamp}.log"
    
    reporter = pytestconfig.pluginmanager.getplugin("terminalreporter")

    try:
        subprocess.run(
            ["go", "mod", "tidy"],
            cwd=go_compat_dir, check=True, capture_output=True, text=True,
        )
        
        # The Go tool now defaults to debug, so we only need to provide the log file.
        command = [
            "go", "run", ".",
            "generate",
            "--directory", str(fixture_dir.resolve()),
            "--log-file", str(log_file_path.resolve()),
        ]
        
        reporter.write_line(f"\n\nℹ️  Go compatibility tool logs will be saved to: {log_file_path}", bold=True)
        
        result = subprocess.run(
            command,
            cwd=go_compat_dir, check=True, capture_output=True, text=True,
        )
        
        if result.stdout or result.stderr:
            reporter.write_line("--- Go Fixture Generator Console Output ---", bold=True)
            if result.stdout:
                reporter.write_line("--- STDOUT ---")
                reporter.write(result.stdout)
            if result.stderr:
                reporter.write_line("--- STDERR ---")
                reporter.write(result.stderr)
            reporter.write_line("-----------------------------------------", bold=True)

    except subprocess.CalledProcessError as e:
        reporter.write_line(f"❌ Go fixture generator failed. Logs are available at: {log_file_path}", red=True)
        pytest.fail(
            f"Go fixture generator failed to run:\n"
            f"STDOUT:\n{e.stdout}\n"
            f"STDERR:\n{e.stderr}",
            pytrace=False
        )
    except FileNotFoundError as e:
        reporter.write_line(f"❌ Go fixture generator failed. Logs are available at: {log_file_path}", red=True)
        pytest.fail(f"Go fixture generator failed to run: {e}", pytrace=False)

    return fixture_dir
