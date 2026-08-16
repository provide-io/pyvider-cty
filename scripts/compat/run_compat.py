#!/usr/bin/env python3
"""Build the go-cty harness if needed, then run the cross-language wire checks.

The compatibility suite is gated behind `--run-compat` and needs the `soup-go`
binary, so nothing ran it and the fixture-based version it replaced sat broken
on `main` for some time without anyone noticing. This wraps both steps so
`make compat` is the whole story.

Skips with a clear message, and exit status 0, when neither the harness nor Go
is available -- a machine without the Go toolchain should not fail the build,
but it must say that it checked nothing.
"""

from pathlib import Path
import shutil
import subprocess  # nosec
import sys

REPO = Path(__file__).resolve().parents[2]
HARNESS_SRC = REPO.parent / "tofusoup" / "src" / "tofusoup" / "harness" / "go" / "soup-go"
BINARY = Path("/tmp/soup-go-compat")  # nosec


def ensure_harness() -> Path | None:
    if BINARY.exists():
        return BINARY
    if not HARNESS_SRC.is_dir():
        print(f"soup-go source not found at {HARNESS_SRC}; skipping cross-language checks.")
        return None
    if shutil.which("go") is None:
        print("Go toolchain not installed; skipping cross-language checks.")
        return None
    print(f"Building soup-go harness from {HARNESS_SRC} ...")
    build = subprocess.run(  # nosec
        ["go", "build", "-o", str(BINARY), "./..."], cwd=HARNESS_SRC, check=False
    )
    if build.returncode != 0:
        print("soup-go build failed; skipping cross-language checks.")
        return None
    return BINARY


def main() -> int:
    binary = ensure_harness()
    if binary is None:
        return 0
    result = subprocess.run(  # nosec
        [
            "uv",
            "run",
            "pytest",
            "-q",
            "--no-header",
            "--run-compat",
            "tests/compatibility/",
        ],
        cwd=REPO,
        env={**subprocess.os.environ, "SOUP_GO_BIN": str(binary)},  # type: ignore[attr-defined]
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
