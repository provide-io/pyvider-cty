#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Runs all relevant Python example scripts and checks for unexpected failures."""

import asyncio
from pathlib import Path
import subprocess  # nosec B404
import sys
from typing import Any

# Ensure sources are importable by example scripts
project_root = Path(__file__).resolve().parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def print_section(title: str) -> None:
    print("\n" + "=" * 70)
    print(f"📋 {title}")
    print("=" * 70)


def print_result(script_name: str, success: bool, stdout: str, stderr: str, exit_code: int) -> None:
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"\n--- {script_name} --- {status} ---")
    if stdout:
        print("--- STDOUT ---")
        print(stdout.strip())
    if stderr and not success:
        print("--- STDERR ---")
        print(stderr.strip())
    if not success:
        print(f"Exit Code: {exit_code}")
    print("." * 70)


async def run_script(
    script_path: Path,
    timeout: int = 20,
    args: list[str] | None = None,
    cwd: Path | None = None,
) -> tuple[bool, str, str, int]:
    """Runs a script and returns its success status, stdout, stderr, and exit code."""
    if args is None:
        args = []
    effective_cwd: Path = cwd if cwd is not None else project_root

    command = [sys.executable, str(script_path), *args]
    process = None
    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(effective_cwd),
        )
        stdout_bytes, stderr_bytes = await asyncio.wait_for(process.communicate(), timeout=timeout)
        stdout = stdout_bytes.decode().strip()
        stderr = stderr_bytes.decode().strip()
        raw_exit_code = process.returncode
        exit_code: int = raw_exit_code if raw_exit_code is not None else -1

        success = exit_code == 0
        return success, stdout, stderr, exit_code
    except TimeoutError:
        if process:
            process.terminate()
            await process.wait()
        return False, "", f"Timeout after {timeout}s", -1
    except Exception as e:
        return False, "", f"Execution error: {e}", -1


async def main() -> None:
    examples_dir = Path(__file__).resolve().parent
    overall_success = True
    results: list[tuple[str, bool, str, str, int]] = []

    scripts_to_run: list[dict[str, Any]] = [
        {"file": "getting-started/quick-start.py"},
        {"file": "types/primitives.py"},
        {"file": "types/collections.py"},
        {"file": "types/structural.py"},
        {"file": "types/dynamic.py"},
        {"file": "types/capsule.py"},
        {"file": "advanced/marks.py"},
        {"file": "advanced/functions.py"},
        {"file": "advanced/serialization.py"},
        {"file": "advanced/path-navigation.py"},
        {"file": "advanced/terraform-interop.py"},
    ]

    print_section("Running All Examples")

    for script_info in scripts_to_run:
        script_file = script_info["file"]
        script_args = script_info.get("args", [])

        script_path = examples_dir / script_file
        if not script_path.exists():
            print(f"\nSKIPPING: {script_path.name} (File not found)")
            continue

        print(f"\n⏳ Running: {script_path.name} {' '.join(script_args)}...")

        success, stdout, stderr, exit_code = await run_script(
            script_path,
            args=script_args,
            cwd=project_root,
        )
        results.append((script_path.name, success, stdout, stderr, exit_code))
        if not success:
            overall_success = False
        print_result(script_path.name, success, stdout, stderr, exit_code)

    print_section("Summary")
    all_passed_count = 0
    for _name, success, _, _, _ in results:
        if success:
            all_passed_count += 1

    if overall_success:
        print(f"\n🎉 All {len(results)} executable examples passed!")
        sys.exit(0)
    else:
        failed_count = len(results) - all_passed_count
        print(f"\n❌ {failed_count} example(s) failed out of {len(results)}.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

# 🌊🪢🔚
