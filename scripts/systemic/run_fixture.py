#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Drive the Terraform fixture against the wheel-built 0.5 stack.

`build_stack.py` proves the suite installs and imports. This proves it
*works*: a real Terraform binary, a real gRPC plugin handshake, real resources
created on disk, and a second plan that must come back empty. The unit suites
check these behaviours in isolation; only a plan and an apply check them in
composition, and only a second plan checks that what was written can be read
back as the same value.

The fixture needs three things placed around it, all of them removed
afterwards so the directory stays a source tree rather than a workspace: a
`.venv` symlink (the installer runs in development mode and resolves the
interpreter from the working directory), a `VERSION` file (the installer takes
the provider version from it, and `required_providers` names it), and
Terraform's own state and lock files.

Usage:
    python scripts/systemic/run_fixture.py              # plan, apply, re-plan, destroy
    python scripts/systemic/run_fixture.py --keep       # leave the state behind
    python scripts/systemic/run_fixture.py --plan-only  # stop after the first plan
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess  # nosec
import sys

REPO = Path(__file__).resolve().parents[2]
FIXTURE = REPO / "scripts" / "systemic" / "fixture"
VENV = REPO / ".systemic" / "venv"
PROVIDER_VERSION = "0.5.0"

SCRATCH = (".terraform", ".terraform.lock.hcl", "terraform.tfstate", "terraform.tfstate.backup")


def terraform() -> str:
    for name in ("terraform", "tofu"):
        if found := shutil.which(name):
            return found
    raise SystemExit("neither `terraform` nor `tofu` is on PATH")


def run(*args: str, cwd: Path = FIXTURE, check: bool = True) -> subprocess.CompletedProcess[str]:
    print(f"\n$ {' '.join(Path(a).name if '/' in a else a for a in args)}")
    result = subprocess.run(args, cwd=cwd, text=True, check=False)  # nosec
    if check and result.returncode != 0:
        raise SystemExit(f"failed ({result.returncode}): {' '.join(args)}")
    return result


def clean() -> None:
    for name in (*SCRATCH, ".venv", "VERSION", ".systemic-out"):
        target = FIXTURE / name
        if target.is_symlink() or target.is_file():
            target.unlink(missing_ok=True)
        elif target.is_dir():
            shutil.rmtree(target, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keep", action="store_true", help="leave state and scratch files behind")
    parser.add_argument("--plan-only", action="store_true", help="stop after the first plan")
    args = parser.parse_args()

    if not (VENV / "bin" / "pyvider").is_file():
        raise SystemExit(f"no stack at {VENV}; run scripts/systemic/build_stack.py first")

    tf = terraform()
    clean()
    (FIXTURE / ".venv").symlink_to(VENV)
    (FIXTURE / "VERSION").write_text(f"{PROVIDER_VERSION}\n")

    try:
        run(str(VENV / "bin" / "pyvider"), "install", "--reinstall")
        run(tf, "init", "-no-color", "-input=false")
        run(tf, "plan", "-no-color", "-input=false")
        if args.plan_only:
            return 0

        run(tf, "apply", "-no-color", "-input=false", "-auto-approve")

        # The one that matters most. A second plan reads the state back
        # through the wire codec and compares it with what the resources
        # report; anything that does not survive the round trip shows up here
        # as a diff that never goes away. Exit code 2 means "changes", which
        # for an unchanged configuration is a failure.
        print("\n-- re-planning: an unchanged configuration must produce no diff --")
        again = run(tf, "plan", "-no-color", "-input=false", "-detailed-exitcode", check=False)
        if again.returncode == 2:
            raise SystemExit("the second plan is not empty: something does not round-trip")
        if again.returncode != 0:
            raise SystemExit(f"the second plan failed ({again.returncode})")
        print("   clean -- state round-trips with no drift")

        if not args.keep:
            run(tf, "destroy", "-no-color", "-input=false", "-auto-approve")
    finally:
        if not args.keep:
            clean()

    print("\nsystemic run complete.")
    return 0


if __name__ == "__main__":
    os.environ.setdefault("TF_IN_AUTOMATION", "1")
    sys.exit(main())

# 🌊🪢🔚
