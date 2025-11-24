#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Pytest configuration file for the entire test suite.
Includes automated setup for the cross-language compatibility suite."""

from collections.abc import Generator
from pathlib import Path
import shutil
import subprocess
import time

import pytest

from pyvider.cty.validation.recursion import clear_recursion_context

# Note: setproctitle is automatically disabled by provide-testkit's conftest.py
# to prevent pytest-xdist performance issues


def pytest_addoption(parser: pytest.Parser) -> None:
    """Adds custom command-line options to pytest."""
    parser.addoption(
        "--run-benchmarks",
        action="store_true",
        default=False,
        help="Run the performance benchmark tests.",
    )
    parser.addoption(
        "--run-compat",
        action="store_true",
        default=False,
        help="Run the Go/Python cross-language compatibility tests.",
    )


@pytest.fixture(scope="session")
def log_dir(pytestconfig: pytest.Config) -> Path:
    """
    Provides the session-scoped, timestamped log directory path that was
    created during the pytest_configure hook.
    """
    # Retrieve the path that was created and stored in the configure hook.
    return pytestconfig._log_dir


def pytest_configure(config: pytest.Config) -> None:
    """
    Adds custom markers and dynamically configures logging paths before
    any tests are run.
    """
    config.addinivalue_line("markers", "benchmark: mark test as a performance benchmark")
    config.addinivalue_line("markers", "compat: mark test as a cross-language compatibility test")

    # --- Centralized Logging Setup ---
    project_root = config.rootpath
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    log_dir_path = project_root / "logs" / f"test-run-{timestamp}"
    log_dir_path.mkdir(parents=True, exist_ok=True)

    config._log_dir = log_dir_path
    config.option.log_file = str(log_dir_path / "pytest_debug.log")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
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
def go_fixtures(pytestconfig: pytest.Config, log_dir: Path) -> Path:
    """
    A session-scoped fixture that automatically runs the Go fixture generator.
    """
    project_root = pytestconfig.rootpath
    go_compat_dir = project_root / "compatibility" / "go"
    fixture_dir = project_root / "tests" / "fixtures" / "go-cty"

    if not shutil.which("go"):
        pytest.skip("Go runtime not found, skipping cross-language compatibility tests.")

    log_file_path = log_dir / "go-generate-debug.log"

    reporter = pytestconfig.pluginmanager.getplugin("terminalreporter")

    try:
        subprocess.run(
            ["go", "mod", "tidy"],
            cwd=go_compat_dir,
            check=True,
            capture_output=True,
            text=True,
        )

        command = [
            "go",
            "run",
            ".",
            "generate",
            "--directory",
            str(fixture_dir.resolve()),
            "--log-file",
            str(log_file_path.resolve()),
            "--log-level",
            "trace",
        ]

        reporter.write_line(
            f"\n\nInfo: Go compatibility tool logs will be saved to: {log_file_path}",
            bold=True,
        )

        result = subprocess.run(
            command,
            cwd=go_compat_dir,
            check=True,
            capture_output=True,
            text=True,
        )

        (log_dir / "go-generate-stdout.log").write_text(result.stdout)
        (log_dir / "go-generate-stderr.log").write_text(result.stderr)

    except subprocess.CalledProcessError as e:
        reporter.write_line(
            f"❌ Go fixture generator failed. Logs are available at: {log_file_path}",
            red=True,
        )
        pytest.fail(
            f"Go fixture generator failed to run:\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}",
            pytrace=False,
        )
    except FileNotFoundError as e:
        reporter.write_line(
            f"❌ Go fixture generator failed. Logs are available at: {log_file_path}",
            red=True,
        )
        pytest.fail(f"Go fixture generator failed to run: {e}", pytrace=False)

    return fixture_dir


@pytest.fixture(autouse=True)
def clean_recursion_context_fixture() -> Generator[None, None, None]:
    """
    An autouse fixture that ensures the thread-local recursion context is
    cleared before and after every test function runs.
    """
    clear_recursion_context()
    yield
    clear_recursion_context()


@pytest.fixture(autouse=True)
def clear_inference_cache() -> Generator[None, None, None]:
    """
    Clear inference cache before and after each test to ensure test isolation.
    This prevents race conditions and cache pollution between tests.
    """
    from pyvider.cty.conversion.inference_cache import _container_schema_cache, _structural_key_cache

    # Reset ContextVar tokens before test
    _structural_key_cache._context_var.set(None)
    _container_schema_cache._context_var.set(None)
    yield
    # Reset ContextVar tokens after test
    _structural_key_cache._context_var.set(None)
    _container_schema_cache._context_var.set(None)


@pytest.fixture(scope="session", autouse=True)
def configure_foundation_logger_for_tests() -> Generator[None, None, None]:
    """
    Configure Foundation logger to use stdout for test safety.

    Uses provide-foundation's testmode.configure_structlog_for_test_safety()
    to prevent "I/O operation on closed file" errors when running tests in
    parallel or with mutation testing tools (mutmut).

    Only runs on the main process when using pytest-xdist to avoid
    worker process conflicts and hanging issues.
    """
    import os

    # Skip Foundation logger configuration on xdist worker processes
    # Workers inherit the logging configuration from the main process
    # Running this in every worker causes process spawning issues and hangs
    if os.getenv("PYTEST_XDIST_WORKER"):
        yield
        return

    from provide.foundation.testmode import configure_structlog_for_test_safety

    configure_structlog_for_test_safety()

    yield

    # Only reset on main process
    import structlog

    structlog.reset_defaults()


# Terminal reset hook (pytest_sessionfinish) lives in provide-testkit
# See: provide.testkit.conftest.pytest_sessionfinish

# 🌊🪢🔚
