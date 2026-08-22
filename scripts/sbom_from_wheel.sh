#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Generate a CycloneDX SBOM for the *built wheel and its dependencies*.
#
# `cyclonedx-py environment` describes whatever is installed in an interpreter,
# so run bare under `uvx` it described the ephemeral tool venv -- cyclonedx-bom
# and its own dependencies, nothing of this package. The wheel is installed into
# a fresh venv here and that venv's interpreter is the one described.
#
# Usage: scripts/sbom_from_wheel.sh <dist-dir> <output-file>
set -euo pipefail

# Pinned: this runs code fetched from PyPI inside the release workflow. Bump
# deliberately, and re-run the script locally against a fresh `uv build` first.
CYCLONEDX_BOM_VERSION="7.3.1"

DIST_DIR="${1:?usage: sbom_from_wheel.sh <dist-dir> <output-file>}"
OUT="${2:?usage: sbom_from_wheel.sh <dist-dir> <output-file>}"

VENV="$(mktemp -d)/sbom-venv"
uv venv --quiet "$VENV"
uv pip install --quiet --python "$VENV/bin/python" "$DIST_DIR"/*.whl
uvx --from "cyclonedx-bom==${CYCLONEDX_BOM_VERSION}" cyclonedx-py environment "$VENV/bin/python" --output-format json -o "$OUT"
echo "SBOM written to $OUT"
