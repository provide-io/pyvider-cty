#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Build the whole 0.5 suite from source and install it, wheels only.

Every day-to-day check in this workspace runs against editable path
dependencies: `pyproject.toml` points `pyvider-cty` at `../pyvider-cty`, and
the same for its siblings. That is the right thing for development and the
wrong thing for believing a release. The parity tracker records the overlay
hiding a live bug in both directions -- once making failures invisible, once
making a green run unreproducible for anyone without the overlay -- and a
suite of forty-three breaking changes is exactly when that matters.

So this builds a wheel for every workspace package in the runtime closure,
creates an empty virtual environment, and installs the wheels into it with no
path dependency anywhere. Anything not developed here resolves from PyPI at
whatever the current version is, which is the other half of the question:
the suite should work against today's dependencies, not against a lockfile
someone refreshed a year ago.

It then checks the thing worth checking -- that no module is being imported
from a source tree. An editable install that leaks in makes the whole exercise
measure the same overlay it was built to avoid.

Usage:
    python scripts/systemic/build_stack.py                # build and install
    python scripts/systemic/build_stack.py --keep         # reuse existing wheels
    python scripts/systemic/build_stack.py --dest DIR     # where to put it
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess  # nosec
import sys
import tomllib

REPO = Path(__file__).resolve().parents[2]
WORKSPACE = Path(os.environ.get("PYV_WORKSPACE", REPO.parent)).resolve()

# What the provider stack needs at runtime. Dev-only packages (provide-testkit
# and friends) are deliberately absent: this environment exists to run a
# provider, not to run the test suites, and pulling the test stack in would
# drag editable dependencies back through the side door.
ROOTS = ("pyvider-cty", "pyvider", "pyvider-components")


def local_packages() -> dict[str, Path]:
    """Every workspace directory that looks like an installable package.

    Two directories can declare the same distribution name, and one of them
    can be an abandoned scratch copy: `pyvider-schema-work` declares itself
    `pyvider` at 0.4.0 alongside the real `pyvider` at 0.5.0. Keyed naively by
    name and taken in directory order, the scratch copy wins and the whole
    stack is quietly built from it. So a directory whose own name matches the
    distribution is preferred, and anything still ambiguous is an error --
    guessing here means shipping the wrong source.
    """
    candidates: dict[str, list[Path]] = {}
    for candidate in sorted(WORKSPACE.iterdir()):
        pyproject = candidate / "pyproject.toml"
        if not candidate.is_dir() or candidate.name.startswith("_") or not pyproject.is_file():
            continue
        try:
            name = tomllib.loads(pyproject.read_text())["project"]["name"]
        except (tomllib.TOMLDecodeError, KeyError):
            continue
        candidates.setdefault(name, []).append(candidate)

    found: dict[str, Path] = {}
    for name, paths in candidates.items():
        if len(paths) == 1:
            found[name] = paths[0]
            continue
        exact = [path for path in paths if path.name == name]
        if len(exact) == 1:
            print(f"note: {name} is declared by {len(paths)} directories; using {exact[0].name}")
            found[name] = exact[0]
            continue
        listing = ", ".join(str(path) for path in paths)
        raise SystemExit(f"{name} is declared by several directories and none matches by name: {listing}")
    return found


def requirement_name(spec: str) -> str:
    """`provide-foundation[all]>=0.5.0` -> `provide-foundation`."""
    for delimiter in ("[", ">", "<", "=", "!", "~", ";", " "):
        spec = spec.split(delimiter)[0]
    return spec.strip()


def closure(roots: tuple[str, ...], packages: dict[str, Path]) -> list[str]:
    """The workspace packages reachable from `roots`, roots included.

    Walks declared dependencies rather than assuming a list, because the list
    is exactly the thing that goes stale: `pyvider-rpcplugin` and `pyvider-hcl`
    are both reached only through a sibling, and neither is obvious from here.
    """
    seen: list[str] = []
    queue = list(roots)
    while queue:
        name = queue.pop(0)
        if name in seen or name not in packages:
            continue
        seen.append(name)
        pyproject = tomllib.loads((packages[name] / "pyproject.toml").read_text())
        for spec in pyproject.get("project", {}).get("dependencies", []):
            queue.append(requirement_name(spec))
    return seen


def run(*args: str, cwd: Path | None = None) -> None:
    result = subprocess.run(args, cwd=cwd, check=False)  # nosec
    if result.returncode != 0:
        raise SystemExit(f"failed ({result.returncode}): {' '.join(args)}")


PROBE = """
import importlib.metadata as metadata, json
names = json.loads({names!r})
versions = {{}}
for dist in names:
    try:
        versions[dist] = metadata.version(dist)
    except metadata.PackageNotFoundError:
        versions[dist] = None
import pyvider, pyvider.components, pyvider.cty
paths = [pyvider.cty.__file__, pyvider.__file__, pyvider.components.__file__]
print(json.dumps({{"versions": versions, "paths": paths}}))
"""


def verify(venv: Path, members: list[str]) -> None:
    """Report the installed versions, and refuse a source-tree import.

    The check is whether each module resolves inside this environment's own
    site-packages -- not whether its path mentions the workspace, which it
    always does when the environment is built underneath the workspace. An
    editable install shows up as a path into some package's `src/`.
    """
    print("\nverifying nothing is being imported from a source tree ...")
    probe = subprocess.run(  # nosec
        [str(venv / "bin" / "python"), "-c", PROBE.format(names=json.dumps(members))],
        capture_output=True,
        text=True,
        check=False,
    )
    if probe.returncode != 0:
        print(probe.stderr.strip())
        raise SystemExit("the installed suite does not import")

    report = json.loads(probe.stdout.strip().splitlines()[-1])
    for name, version in report["versions"].items():
        print(f"  {name:24} {version or 'MISSING'}")

    site_packages = str((venv / "lib").resolve())
    leaked = [path for path in report["paths"] if not str(Path(path).resolve()).startswith(site_packages)]
    if leaked:
        for path in leaked:
            print(f"  LEAK: {path}")
        raise SystemExit("an editable install leaked in; this environment proves nothing")
    print("  no source-tree imports -- this is a wheel-only environment\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    # Deliberately not under `build/`: setuptools owns that name, and this
    # script clears it for every package it builds -- including this one.
    parser.add_argument("--dest", type=Path, default=REPO / ".systemic")
    parser.add_argument("--keep", action="store_true", help="reuse wheels already built")
    parser.add_argument("--python", default="3.11")
    args = parser.parse_args()

    packages = local_packages()
    missing = [name for name in ROOTS if name not in packages]
    if missing:
        raise SystemExit(f"not found under {WORKSPACE}: {', '.join(missing)}")

    members = closure(ROOTS, packages)
    print(f"workspace: {WORKSPACE}")
    print(f"local closure ({len(members)}): {', '.join(members)}\n")

    dest = args.dest.resolve()
    wheels, venv = dest / "wheels", dest / "venv"
    if not args.keep and dest.exists():
        shutil.rmtree(dest)
    wheels.mkdir(parents=True, exist_ok=True)

    if not args.keep:
        for name in members:
            source = packages[name]
            # Clear the package's own build/ and dist/ first. This is not
            # hygiene, it is correctness: a stale build/ directory made
            # setuptools emit a wheel stamped 0.4.0 while the package's
            # VERSION file said 0.5.0, and nothing downstream would have
            # noticed until a release was already published under the wrong
            # number.
            for stale in ("build", "dist"):
                victim = source / stale
                # Never delete a directory this run is writing into. The
                # default output used to live under this repository's own
                # `build/`, so building pyvider-cty deleted the wheels
                # directory out from under the loop that was filling it.
                if victim == dest or victim in dest.parents:
                    continue
                shutil.rmtree(victim, ignore_errors=True)

            # Build into a directory of its own, so what this package produced
            # can be identified exactly. Globbing a shared output directory by
            # name cannot do that -- `pyvider-*.whl` is ambiguous the moment a
            # sibling is named `pyvider-something`, and the version check that
            # depended on it silently passed while the wrong wheel sat there.
            print(f"building {name} ...")
            staging = dest / "staging" / name
            shutil.rmtree(staging, ignore_errors=True)
            staging.mkdir(parents=True)
            run("uv", "build", "--wheel", "--out-dir", str(staging), cwd=source)

            produced = sorted(staging.glob("*.whl"))
            if len(produced) != 1:
                raise SystemExit(f"{name}: expected one wheel, got {[w.name for w in produced]}")
            wheel = produced[0]

            declared = (source / "VERSION").read_text().strip() if (source / "VERSION").is_file() else None
            if declared and f"-{declared}-" not in wheel.name:
                raise SystemExit(
                    f"{name}: VERSION says {declared} but the build produced {wheel.name}. "
                    "A stale build/ directory does this; so does another process writing to "
                    "the source tree while this runs."
                )
            print(f"  {wheel.name}")
            shutil.move(str(wheel), wheels / wheel.name)
        shutil.rmtree(dest / "staging", ignore_errors=True)

    print("\ncreating a clean environment ...")
    if venv.exists():
        shutil.rmtree(venv)
    run("uv", "venv", str(venv), "--python", args.python)

    # --find-links makes the freshly built wheels the only way to satisfy the
    # >=0.5.0 floors, since PyPI has nothing above 0.4.x for these. Everything
    # else resolves normally, and therefore currently.
    print("installing the suite ...")
    roots = [str(next(wheels.glob(f"{name.replace('-', '_')}-*.whl"))) for name in ROOTS]
    run(
        "uv",
        "pip",
        "install",
        "--python",
        str(venv / "bin" / "python"),
        "--find-links",
        str(wheels),
        *roots,
    )

    verify(venv, members)

    print(f"ready: {venv}")
    print(f"  {venv / 'bin' / 'pyvider'} components list")
    print("  see scripts/systemic/README.md for the Terraform run")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# 🌊🪢🔚
