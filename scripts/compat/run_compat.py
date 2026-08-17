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
    """Rebuild the harness from source, every run.

    The rebuild used to be skipped whenever the binary already existed, which
    made the oracle age out of date without saying so: the harness grew whole-
    stdlib coverage and a `cty unify` command, and the suite went on asking a
    binary built the day before, whose answer to two thirds of the sweep was
    "unknown function". An oracle that is not rebuilt is not an oracle, it is a
    fixture with a compiler. `go build` is incremental, so paying for it on
    every run costs about a second and removes the failure mode.

    A build failure deliberately does *not* fall back to whatever binary is
    lying around -- that is the same staleness, chosen on purpose. Point
    SOUP_GO_BIN at a binary and run pytest directly if you need that.
    """
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
        # A failed build is not a missing toolchain. The machine can check and
        # could not, and exiting 0 here made `make compat` green while checking
        # nothing -- which is the exact reading this script exists to prevent.
        print("soup-go build failed.")
        raise SystemExit(1)
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
