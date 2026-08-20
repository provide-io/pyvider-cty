#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Utility functions for pyvider-cty examples.
Provides consistent path resolution and environment setup."""

from decimal import Decimal
import logging
from pathlib import Path
import sys


def setup_example_environment() -> Path:
    """
    Configure Python path for examples to find pyvider modules.
    Returns the project root path.
    """
    # Get project root (examples/../)
    examples_dir = Path(__file__).resolve().parent
    project_root = examples_dir.parent
    src_dir = project_root / "src"

    # Add src to Python path if it exists
    if src_dir.exists() and str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    # Also add project root for examples imports
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    return project_root


def configure_for_example() -> None:
    """
    Configure environment for example execution.
    """
    setup_example_environment()

    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def stdlib_call(name: str, *arguments: object) -> object:
    """One stdlib call, with plain Python in and plain Python out.

    Examples are for reading, and `STDLIB["upper"](CtyString().validate(x)).value`
    buries the point under ceremony. Real code passes `CtyValue`s it already has;
    this only exists so the assertions below read like the answers they check.
    """
    from pyvider.cty.functions import STDLIB

    prepared = [value if hasattr(value, "type") else _as_cty(value) for value in arguments]
    return _as_python(STDLIB[name](*prepared))


def _as_cty(raw: object) -> object:
    from pyvider.cty import CtyBool, CtyList, CtyNumber, CtyString

    if isinstance(raw, bool):
        return CtyBool().validate(raw)
    if isinstance(raw, int | float | Decimal):
        return CtyNumber().validate(raw)
    if isinstance(raw, list):
        return CtyList(element_type=CtyString()).validate(raw)
    return CtyString().validate(raw)


def _as_python(answer: object) -> object:
    value = answer.value  # type: ignore[attr-defined]
    if isinstance(value, tuple):
        return [_as_python(element) for element in value]
    if isinstance(value, dict):
        return {key: _as_python(element) for key, element in value.items()}
    return value


# 🌊🪢🔚
