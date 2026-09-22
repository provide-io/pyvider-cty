# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""The distribution owns ``pyvider.cty``, not the shared ``pyvider`` root."""

from __future__ import annotations

import base64
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import sysconfig
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

REPOSITORY = Path(__file__).resolve().parents[2]
ROOT_INITIALIZER = "pyvider/__init__.py"
CTY_INITIALIZER = "pyvider/cty/__init__.py"
TYPING_MARKER = "pyvider/cty/py.typed"
RELEASE_VERSION = "0.6.2"


@pytest.fixture(scope="module")
def built_wheel(tmp_path_factory: pytest.TempPathFactory) -> Path:
    build_root = tmp_path_factory.mktemp("wheel-build")
    source = build_root / "source"
    shutil.copytree(REPOSITORY / "src", source / "src", ignore=shutil.ignore_patterns("*.egg-info"))
    for name in ("LICENSE", "README.md", "VERSION", "pyproject.toml"):
        shutil.copy2(REPOSITORY / name, source / name)
    wheelhouse = build_root / "wheelhouse"
    result = subprocess.run(
        [
            "uv",
            "build",
            "--wheel",
            "--out-dir",
            str(wheelhouse),
            "--no-create-gitignore",
        ],
        cwd=source,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    wheels = list(wheelhouse.glob("pyvider_cty-*.whl"))
    assert len(wheels) == 1
    return wheels[0]


def _record_paths(record: Path) -> set[str]:
    with record.open(newline="") as rows:
        return {row[0] for row in csv.reader(rows)}


def _write_synthetic_owner_wheel(destination: Path) -> Path:
    wheel = destination / "synthetic_pyvider_owner-1.0-py3-none-any.whl"
    dist_info = "synthetic_pyvider_owner-1.0.dist-info"
    members = {
        ROOT_INITIALIZER: b'__version__ = "owner-1.0"\nOWNER_MARKER = "preserve-me"\n',
        f"{dist_info}/METADATA": (b"Metadata-Version: 2.4\nName: synthetic-pyvider-owner\nVersion: 1.0\n"),
        f"{dist_info}/WHEEL": (
            b"Wheel-Version: 1.0\n"
            b"Generator: pyvider-cty namespace test\n"
            b"Root-Is-Purelib: true\n"
            b"Tag: py3-none-any\n"
        ),
    }
    record_rows = []
    for name, content in members.items():
        digest = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).rstrip(b"=").decode()
        record_rows.append(f"{name},sha256={digest},{len(content)}\n")
    record_rows.append(f"{dist_info}/RECORD,,\n")
    members[f"{dist_info}/RECORD"] = "".join(record_rows).encode()

    with ZipFile(wheel, "w", ZIP_DEFLATED) as archive:
        for name, content in members.items():
            archive.writestr(name, content)
    return wheel


def test_wheel_uses_the_shared_pyvider_namespace(built_wheel: Path) -> None:
    with ZipFile(built_wheel) as archive:
        members = set(archive.namelist())
        record_name = next(name for name in members if name.endswith(".dist-info/RECORD"))
        record_paths = {row[0] for row in csv.reader(archive.read(record_name).decode().splitlines())}

    assert ROOT_INITIALIZER not in members
    assert ROOT_INITIALIZER not in record_paths
    assert CTY_INITIALIZER in members
    assert TYPING_MARKER in members


def test_wheel_reports_the_release_version(built_wheel: Path) -> None:
    with ZipFile(built_wheel) as archive:
        metadata_name = next(name for name in archive.namelist() if name.endswith(".dist-info/METADATA"))
        metadata = archive.read(metadata_name).decode()

    assert built_wheel.name.startswith(f"pyvider_cty-{RELEASE_VERSION}-")
    assert f"Version: {RELEASE_VERSION}\n" in metadata


def test_source_tree_imports_cty_through_the_namespace(tmp_path: Path) -> None:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(REPOSITORY / "src")
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import json, pathlib, pyvider.cty; "
                "print(json.dumps({'file': str(pathlib.Path(pyvider.cty.__file__).resolve()), "
                "'version': pyvider.cty.__version__}))"
            ),
        ],
        cwd=tmp_path,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    imported = json.loads(result.stdout)
    assert Path(imported["file"]).is_relative_to(REPOSITORY / "src" / "pyvider" / "cty")
    assert imported["version"]


def test_install_does_not_overwrite_an_existing_pyvider_owner(
    built_wheel: Path,
    tmp_path: Path,
) -> None:
    owner_wheel = _write_synthetic_owner_wheel(tmp_path)
    result = subprocess.run(
        ["uv", "venv", "--python", sys.executable, "--no-project", str(tmp_path / "environment")],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    python = tmp_path / "environment" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")

    for wheel in (owner_wheel, built_wheel):
        result = subprocess.run(
            ["uv", "pip", "install", "--python", str(python), "--no-deps", str(wheel)],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr

    purelib = Path(
        subprocess.check_output(
            [str(python), "-c", "import sysconfig; print(sysconfig.get_path('purelib'))"],
            text=True,
        ).strip()
    )
    (purelib / "test-dependencies.pth").write_text(f"{sysconfig.get_path('purelib')}\n")

    owner_initializer = purelib / ROOT_INITIALIZER
    assert owner_initializer.read_text() == '__version__ = "owner-1.0"\nOWNER_MARKER = "preserve-me"\n'

    owner_record = next(purelib.glob("synthetic_pyvider_owner-*.dist-info/RECORD"))
    cty_record = next(purelib.glob("pyvider_cty-*.dist-info/RECORD"))
    assert ROOT_INITIALIZER in _record_paths(owner_record)
    assert ROOT_INITIALIZER not in _record_paths(cty_record)

    result = subprocess.run(
        [
            str(python),
            "-c",
            (
                "import json, pathlib, pyvider, pyvider.cty; "
                "print(json.dumps({'owner': pyvider.__version__, "
                "'marker': pyvider.OWNER_MARKER, "
                "'cty_file': str(pathlib.Path(pyvider.cty.__file__).resolve()), "
                "'cty_version': pyvider.cty.__version__}))"
            ),
        ],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    imported = json.loads(result.stdout)
    assert imported["owner"] == "owner-1.0"
    assert imported["marker"] == "preserve-me"
    assert imported["cty_version"]
    assert Path(imported["cty_file"]).is_relative_to(purelib / "pyvider" / "cty")
