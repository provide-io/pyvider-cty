# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""The cty distribution owns only ``pyvider.cty`` namespace members."""

from __future__ import annotations

import base64
import csv
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
from typing import cast
import urllib.error
import urllib.request
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

REPOSITORY = Path(__file__).resolve().parents[2]
ROOT_INITIALIZER = "pyvider/__init__.py"
ROOT_TYPING_MARKER = "pyvider/py.typed"
CTY_INITIALIZER = "pyvider/cty/__init__.py"
CTY_TYPING_MARKER = "pyvider/cty/py.typed"
RELEASE_VERSION = "0.6.2"
PUBLISHED_CTY_061_FILENAME = "pyvider_cty-0.6.1-py3-none-any.whl"
PUBLISHED_CTY_061_URL = (
    "https://files.pythonhosted.org/packages/38/9f/"
    "014fbb7c371ae700dd573acb335069f6f89ad24542ebbd92add546d6a309/"
    f"{PUBLISHED_CTY_061_FILENAME}"
)
PUBLISHED_CTY_061_SHA256 = "9d1135f5e8f0ac95f12c1d08331fcab45327d59652f4b16b6f71dd0b829a0673"
PUBLISHED_CTY_061_SIZE = 299_140
PUBLISHED_CTY_061_CACHE_ENV = "PYVIDER_CTY_061_WHEEL"
CANONICAL_INITIALIZER = """#
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from provide.foundation.utils.versioning import get_version

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

__version__ = get_version("pyvider", caller_file=__file__)

__all__ = [
    "__version__",
]

# 🐍🏗️🔚
""".encode()


@dataclass(frozen=True)
class BuiltArtifacts:
    direct_wheel: Path
    sdist: Path
    sdist_wheel: Path


def _run(command: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, check=False, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    return result


def _published_cty_061(destination: Path) -> Path:
    payload: bytes
    wheel = destination / PUBLISHED_CTY_061_FILENAME
    cached = os.environ.get(PUBLISHED_CTY_061_CACHE_ENV)
    if cached:
        cache_path = Path(cached).expanduser().resolve()
        if not cache_path.is_file():
            raise AssertionError(f"{PUBLISHED_CTY_061_CACHE_ENV} is not a file: {cache_path}")
        payload = cache_path.read_bytes()
    else:
        try:
            # The URL is an immutable HTTPS files.pythonhosted.org constant.
            with urllib.request.urlopen(PUBLISHED_CTY_061_URL, timeout=60) as response:  # nosec B310
                payload = response.read(PUBLISHED_CTY_061_SIZE + 1)
        except urllib.error.URLError as exc:
            raise AssertionError(
                f"could not fetch pinned {PUBLISHED_CTY_061_FILENAME}; set "
                f"{PUBLISHED_CTY_061_CACHE_ENV} to a local copy: {exc}"
            ) from exc

    actual_size = len(payload)
    actual_sha256 = hashlib.sha256(payload).hexdigest()
    assert actual_size == PUBLISHED_CTY_061_SIZE, (
        f"{wheel}: size {actual_size} != pinned size {PUBLISHED_CTY_061_SIZE}"
    )
    assert actual_sha256 == PUBLISHED_CTY_061_SHA256, (
        f"{wheel}: sha256 {actual_sha256} != pinned sha256 {PUBLISHED_CTY_061_SHA256}"
    )
    wheel.write_bytes(payload)
    return wheel


@pytest.fixture(scope="module")
def built_artifacts(tmp_path_factory: pytest.TempPathFactory) -> BuiltArtifacts:
    build_root = tmp_path_factory.mktemp("package-build")
    source = build_root / "source"
    shutil.copytree(REPOSITORY / "src", source / "src", ignore=shutil.ignore_patterns("*.egg-info"))
    for name in ("LICENSE", "README.md", "VERSION", "pyproject.toml"):
        shutil.copy2(REPOSITORY / name, source / name)

    direct_wheelhouse = build_root / "direct-wheel"
    _run(
        [
            "uv",
            "build",
            "--wheel",
            "--out-dir",
            str(direct_wheelhouse),
            "--no-create-gitignore",
        ],
        cwd=source,
    )
    direct_wheel = next(direct_wheelhouse.glob("pyvider_cty-*.whl"))

    sdist_house = build_root / "sdist"
    _run(
        ["uv", "build", "--sdist", "--out-dir", str(sdist_house), "--no-create-gitignore"],
        cwd=source,
    )
    sdist = next(sdist_house.glob("pyvider_cty-*.tar.gz"))

    sdist_wheelhouse = build_root / "sdist-wheel"
    _run(
        [
            "uv",
            "build",
            "--wheel",
            "--out-dir",
            str(sdist_wheelhouse),
            "--no-create-gitignore",
            str(sdist),
        ],
        cwd=build_root,
    )
    sdist_wheel = next(sdist_wheelhouse.glob("pyvider_cty-*.whl"))
    return BuiltArtifacts(direct_wheel=direct_wheel, sdist=sdist, sdist_wheel=sdist_wheel)


@pytest.fixture(scope="module")
def published_cty_061(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return _published_cty_061(tmp_path_factory.mktemp("published-cty-061"))


def _candidate(built_artifacts: BuiltArtifacts, name: str) -> Path:
    if name == "direct_wheel":
        return built_artifacts.direct_wheel
    if name == "sdist_wheel":
        return built_artifacts.sdist_wheel
    raise AssertionError(f"unknown candidate artifact: {name}")


def _record_paths(record: Path) -> set[str]:
    with record.open(newline="") as rows:
        return {row[0] for row in csv.reader(rows)}


def _write_wheel(
    destination: Path,
    *,
    distribution: str,
    version: str,
    members: dict[str, bytes],
    requirements: tuple[str, ...] = (),
) -> Path:
    normalized = distribution.replace("-", "_")
    wheel = destination / f"{normalized}-{version}-py3-none-any.whl"
    dist_info = f"{normalized}-{version}.dist-info"
    requires_dist = "".join(f"Requires-Dist: {requirement}\n" for requirement in requirements)
    contents = {
        **members,
        f"{dist_info}/METADATA": (
            f"Metadata-Version: 2.4\nName: {distribution}\nVersion: {version}\n{requires_dist}"
        ).encode(),
        f"{dist_info}/WHEEL": (
            b"Wheel-Version: 1.0\n"
            b"Generator: pyvider-cty packaging test\n"
            b"Root-Is-Purelib: true\n"
            b"Tag: py3-none-any\n"
        ),
    }
    record_rows = []
    for name, content in contents.items():
        digest = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).rstrip(b"=").decode()
        record_rows.append(f"{name},sha256={digest},{len(content)}\n")
    record_rows.append(f"{dist_info}/RECORD,,\n")
    contents[f"{dist_info}/RECORD"] = "".join(record_rows).encode()

    with ZipFile(wheel, "w", ZIP_DEFLATED) as archive:
        for name, content in contents.items():
            archive.writestr(name, content)
    return wheel


def _synthetic_owner(destination: Path) -> Path:
    return _write_wheel(
        destination,
        distribution="pyvider",
        version="0.8.0",
        members={
            ROOT_INITIALIZER: CANONICAL_INITIALIZER,
            ROOT_TYPING_MARKER: b"",
        },
        requirements=("provide-foundation>=0.4.0",),
    )


def _environment(destination: Path) -> tuple[Path, Path]:
    root = destination / "environment"
    _run(["uv", "venv", "--python", sys.executable, "--no-project", str(root)])
    python = root / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    purelib = Path(
        subprocess.check_output(
            [str(python), "-c", "import sysconfig; print(sysconfig.get_path('purelib'))"],
            text=True,
        ).strip()
    )
    return python, purelib


def _install(python: Path, wheel: Path, *, dependencies: bool = False, reinstall: bool = False) -> None:
    command = ["uv", "pip", "install", "--offline", "--python", str(python)]
    if not dependencies:
        command.append("--no-deps")
    if reinstall:
        command.append("--reinstall")
    command.append(str(wheel))
    _run(command)


def _uninstall(python: Path, distribution: str, *, manager: str = "uv") -> None:
    if manager == "uv":
        _run(["uv", "pip", "uninstall", "--python", str(python), distribution])
        return
    if manager == "pip":
        _run([str(python), "-m", "pip", "uninstall", "--yes", distribution])
        return
    raise AssertionError(f"unknown package manager: {manager}")


def _installed_versions(python: Path, cwd: Path) -> dict[str, str]:
    result = _run(
        [
            str(python),
            "-I",
            "-c",
            (
                "import json, pathlib, pyvider, pyvider.cty; "
                "print(json.dumps({'owner': pyvider.__version__, "
                "'root_file': str(pathlib.Path(pyvider.__file__).resolve()), "
                "'cty': pyvider.cty.__version__, "
                "'cty_file': str(pathlib.Path(pyvider.cty.__file__).resolve())}))"
            ),
        ],
        cwd=cwd,
    )
    return cast(dict[str, str], json.loads(result.stdout))


def test_release_notes_explain_single_ownership_and_migration() -> None:
    release_notes = (REPOSITORY / "CHANGELOG.md").read_text().split("## [0.6.1]", maxsplit=1)[0]

    assert "stops owning" in release_notes
    assert "`pyvider/__init__.py`" in release_notes
    assert "did not own `pyvider/py.typed`" in release_notes
    assert "`pyvider-rpcplugin` 0.5.5" in release_notes
    assert "`Pyvider` 0.8.0" in release_notes
    assert "same operation" in release_notes
    assert "reinstall `Pyvider` afterward" in release_notes


def test_built_artifacts_own_only_the_cty_namespace(built_artifacts: BuiltArtifacts) -> None:
    for wheel in (built_artifacts.direct_wheel, built_artifacts.sdist_wheel):
        with ZipFile(wheel) as archive:
            members = set(archive.namelist())
            record_name = next(name for name in members if name.endswith(".dist-info/RECORD"))
            record_paths = {row[0] for row in csv.reader(archive.read(record_name).decode().splitlines())}

        assert ROOT_INITIALIZER not in members
        assert ROOT_INITIALIZER not in record_paths
        assert ROOT_TYPING_MARKER not in members
        assert ROOT_TYPING_MARKER not in record_paths
        assert CTY_INITIALIZER in members
        assert CTY_TYPING_MARKER in members
        assert CTY_INITIALIZER in record_paths
        assert CTY_TYPING_MARKER in record_paths

    with tarfile.open(built_artifacts.sdist) as archive:
        members = {member.name for member in archive.getmembers()}

    assert not any(member.endswith("/src/pyvider/__init__.py") for member in members)
    assert not any(member.endswith("/src/pyvider/py.typed") for member in members)
    assert any(member.endswith("/src/pyvider/cty/__init__.py") for member in members)
    assert any(member.endswith("/src/pyvider/cty/py.typed") for member in members)


def test_wheels_report_the_release_version(built_artifacts: BuiltArtifacts) -> None:
    for wheel in (built_artifacts.direct_wheel, built_artifacts.sdist_wheel):
        with ZipFile(wheel) as archive:
            metadata_name = next(name for name in archive.namelist() if name.endswith(".dist-info/METADATA"))
            metadata = archive.read(metadata_name).decode()

        assert wheel.name.startswith(f"pyvider_cty-{RELEASE_VERSION}-")
        assert f"Version: {RELEASE_VERSION}\n" in metadata


def test_source_tree_imports_cty(tmp_path: Path) -> None:
    assert not (REPOSITORY / ROOT_INITIALIZER).exists()
    assert not (REPOSITORY / ROOT_TYPING_MARKER).exists()
    assert not (REPOSITORY / ".gitattributes").exists()

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
    assert imported["version"] == RELEASE_VERSION


@pytest.mark.parametrize("candidate_name", ["direct_wheel", "sdist_wheel"])
@pytest.mark.parametrize("order", ["cty-first", "owner-first"])
def test_fresh_coinstall_is_order_independent(
    built_artifacts: BuiltArtifacts,
    candidate_name: str,
    order: str,
    tmp_path: Path,
) -> None:
    candidate = _candidate(built_artifacts, candidate_name)
    owner = _synthetic_owner(tmp_path)
    python, purelib = _environment(tmp_path)

    if order == "cty-first":
        _install(python, candidate, dependencies=True)
        cty_only = _run(
            [str(python), "-I", "-c", "import pyvider.cty; print(pyvider.cty.__version__)"],
            cwd=tmp_path,
        )
        assert cty_only.stdout.strip() == RELEASE_VERSION
        _install(python, owner)
    else:
        _install(python, owner)
        _install(python, candidate, dependencies=True)

    assert (purelib / ROOT_INITIALIZER).read_bytes() == CANONICAL_INITIALIZER
    assert (purelib / ROOT_TYPING_MARKER).read_bytes() == b""
    owner_record = next(purelib.glob("pyvider-*.dist-info/RECORD"))
    cty_record = next(purelib.glob("pyvider_cty-*.dist-info/RECORD"))
    assert ROOT_INITIALIZER in _record_paths(owner_record)
    assert ROOT_TYPING_MARKER in _record_paths(owner_record)
    assert ROOT_INITIALIZER not in _record_paths(cty_record)
    assert ROOT_TYPING_MARKER not in _record_paths(cty_record)

    imported = _installed_versions(python, tmp_path)
    assert imported["owner"] == "0.8.0"
    assert imported["cty"] == RELEASE_VERSION
    assert Path(imported["root_file"]).is_relative_to(purelib / "pyvider")
    assert Path(imported["cty_file"]).is_relative_to(purelib / "pyvider" / "cty")


def test_editable_coinstall_preserves_owner_and_imports_cty(tmp_path: Path) -> None:
    owner = _synthetic_owner(tmp_path)
    python, purelib = _environment(tmp_path)
    _install(python, owner, dependencies=True)

    _run(
        [
            "uv",
            "pip",
            "install",
            "--offline",
            "--python",
            str(python),
            "--no-deps",
            "--editable",
            str(REPOSITORY),
        ]
    )

    assert (purelib / ROOT_INITIALIZER).read_bytes() == CANONICAL_INITIALIZER
    assert (purelib / ROOT_TYPING_MARKER).read_bytes() == b""
    cty_record = next(purelib.glob("pyvider_cty-*.dist-info/RECORD"))
    assert ROOT_INITIALIZER not in _record_paths(cty_record)
    assert ROOT_TYPING_MARKER not in _record_paths(cty_record)
    imported = _installed_versions(python, tmp_path)
    assert imported["owner"] == "0.8.0"
    assert imported["cty"] == RELEASE_VERSION
    assert Path(imported["cty_file"]).is_relative_to(REPOSITORY / "src" / "pyvider" / "cty")


def test_published_cty_061_upgrade_is_remediated_by_reinstalling_the_owner(
    built_artifacts: BuiltArtifacts,
    published_cty_061: Path,
    tmp_path: Path,
) -> None:
    payload = published_cty_061.read_bytes()
    assert published_cty_061.name == PUBLISHED_CTY_061_FILENAME
    assert len(payload) == PUBLISHED_CTY_061_SIZE
    assert hashlib.sha256(payload).hexdigest() == PUBLISHED_CTY_061_SHA256

    for candidate_name in ("direct_wheel", "sdist_wheel"):
        case = tmp_path / candidate_name
        case.mkdir()
        owner = _synthetic_owner(case)
        candidate = _candidate(built_artifacts, candidate_name)
        python, purelib = _environment(case)

        # The published 0.6.1 wheel owns the shared initializer. Its one-time
        # removal during upgrade therefore deletes that path before the new
        # implicit-namespace cty wheel is installed.
        _install(python, published_cty_061)
        _install(python, candidate, dependencies=True)
        assert not list(purelib.glob("pyvider_cty-0.6.1.dist-info"))
        assert not (purelib / ROOT_INITIALIZER).exists()
        cty_only = _run(
            [str(python), "-I", "-c", "import pyvider.cty; print(pyvider.cty.__version__)"],
            cwd=case,
        )
        assert cty_only.stdout.strip() == RELEASE_VERSION

        # Installing or reinstalling the canonical owner is the supported
        # remediation for a direct 0.6.1 -> 0.6.2 subpackage upgrade.
        _install(python, owner, dependencies=True)
        assert (purelib / ROOT_INITIALIZER).read_bytes() == CANONICAL_INITIALIZER
        assert (purelib / ROOT_TYPING_MARKER).read_bytes() == b""
        owner_record = next(purelib.glob("pyvider-*.dist-info/RECORD"))
        cty_record = next(purelib.glob("pyvider_cty-*.dist-info/RECORD"))
        assert ROOT_INITIALIZER in _record_paths(owner_record)
        assert ROOT_TYPING_MARKER in _record_paths(owner_record)
        assert ROOT_INITIALIZER not in _record_paths(cty_record)
        assert ROOT_TYPING_MARKER not in _record_paths(cty_record)
        assert _installed_versions(python, case)["owner"] == "0.8.0"

        _uninstall(python, "pyvider-cty")
        assert not list(purelib.glob("pyvider_cty-*.dist-info"))
        assert not (purelib / CTY_INITIALIZER).exists()
        assert (purelib / ROOT_INITIALIZER).read_bytes() == CANONICAL_INITIALIZER
        assert (purelib / ROOT_TYPING_MARKER).read_bytes() == b""
        owner_only = _run(
            [str(python), "-I", "-c", "import pyvider; print(pyvider.__version__)"],
            cwd=case,
        )
        assert owner_only.stdout.strip() == "0.8.0"


@pytest.mark.parametrize("manager", ["uv", "pip"])
def test_uninstalling_cty_preserves_the_single_root_owner(
    built_artifacts: BuiltArtifacts,
    manager: str,
    tmp_path: Path,
) -> None:
    owner = _synthetic_owner(tmp_path)
    python, purelib = _environment(tmp_path)
    if manager == "pip":
        _run([str(python), "-m", "ensurepip", "--upgrade"])

    _install(python, owner, dependencies=True)
    _install(python, built_artifacts.direct_wheel, dependencies=True)
    assert (purelib / ROOT_INITIALIZER).read_bytes() == CANONICAL_INITIALIZER
    assert (purelib / ROOT_TYPING_MARKER).read_bytes() == b""
    assert (purelib / CTY_INITIALIZER).is_file()
    assert list(purelib.glob("pyvider_cty-*.dist-info"))

    _uninstall(python, "pyvider-cty", manager=manager)

    assert not list(purelib.glob("pyvider_cty-*.dist-info"))
    assert not (purelib / "pyvider/cty").exists()
    assert (purelib / ROOT_INITIALIZER).read_bytes() == CANONICAL_INITIALIZER
    assert (purelib / ROOT_TYPING_MARKER).read_bytes() == b""
    result = _run(
        [str(python), "-I", "-c", "import pyvider; print(pyvider.__version__)"],
        cwd=tmp_path,
    )
    assert result.stdout.strip() == "0.8.0"
    cty_import = subprocess.run(
        [str(python), "-I", "-c", "import pyvider.cty"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert cty_import.returncode != 0
    assert "ModuleNotFoundError" in cty_import.stderr
