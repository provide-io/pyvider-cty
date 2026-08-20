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

import os
from pathlib import Path
import shutil
import subprocess  # nosec
import sys

REPO = Path(__file__).resolve().parents[2]
# Built inside the repository rather than into `/tmp`. A shared temporary
# directory is writable by every account on the machine, and the last-resort
# default in `tests/compatibility/_oracle.py` *executes* whatever it finds at
# its path -- so a binary planted there by another user would have run as
# whoever ran the suite. `.compat/` is gitignored, and `_oracle.py` falls back
# to this same path, so the two agree without either importing the other.
BUILD_DIR = REPO / ".compat"
BINARY = BUILD_DIR / "soup-go"


def harness_source() -> Path:
    """Where the soup-go sources live.

    Defaults to a sibling `tofusoup` checkout, which is the local layout.
    `SOUP_GO_SRC` overrides it, because a layout is not a law: CI checks the
    two repositories out wherever it likes, and a path assumed from one
    machine's directory tree is the reason this script could not run anywhere
    else.
    """
    override = os.environ.get("SOUP_GO_SRC")
    if override:
        return Path(override).expanduser().resolve()
    return REPO.parent / "tofusoup" / "src" / "tofusoup" / "harness" / "go" / "soup-go"


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
    # A laptop without Go should skip; CI must not. Skipping there means the one
    # place the 2322 differential tests run reports success while running none
    # of them, which is the same failure the build-failure branch below already
    # guards against -- just arrived at from the other side.
    required = os.environ.get("COMPAT_REQUIRE") == "1"

    harness_src = harness_source()
    if not harness_src.is_dir():
        message = f"soup-go source not found at {harness_src}"
        if required:
            raise SystemExit(f"{message}; COMPAT_REQUIRE=1, so this is a misconfiguration, not a skip.")
        print(f"{message}; skipping cross-language checks.")
        return None
    if shutil.which("go") is None:
        message = "Go toolchain not installed"
        if required:
            raise SystemExit(f"{message}; COMPAT_REQUIRE=1, so this is a misconfiguration, not a skip.")
        print(f"{message}; skipping cross-language checks.")
        return None
    print(f"Building soup-go harness from {harness_src} ...")
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    build = subprocess.run(  # nosec
        ["go", "build", "-o", str(BINARY), "./..."], cwd=harness_src, check=False
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
