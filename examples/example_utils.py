#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Utility functions for pyvider-cty examples.
Provides consistent path resolution and environment setup."""

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

# 🌊🪢🔚
