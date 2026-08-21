#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Fixtures for the memray suite, which used to come from an undeclared package."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent


@pytest.fixture(scope="session")
def memray_baselines_path() -> Path:
    return Path(__file__).resolve().parent / "baselines.json"


@pytest.fixture(scope="session")
def memray_baseline(memray_baselines_path: Path) -> dict[str, int]:
    if not memray_baselines_path.exists():
        return {}
    loaded: dict[str, int] = json.loads(memray_baselines_path.read_text(encoding="utf-8"))
    return loaded


@pytest.fixture
def memray_output_dir(tmp_path: Path) -> Path:
    """A per-test directory, so a run cannot read a stale profile from the last one."""
    out = tmp_path / "memray"
    out.mkdir(parents=True, exist_ok=True)
    return out


# 🐍🏗️🔚
