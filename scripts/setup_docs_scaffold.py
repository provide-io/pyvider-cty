#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Put the shared documentation scaffolding where `mkdocs.yml` expects it.

`mkdocs.yml` opens with `INHERIT: .provide/foundry/base-mkdocs.yml`, and that
directory is gitignored -- it holds a vendored copy of scaffolding whose home is
the `provide-foundry` package, not this repository. Nothing here ever put it
there, so `mkdocs build` worked only on a machine where some other tool had
already done so, and failed from a clean clone. No CI job built the
documentation, so nothing caught that.

`provide.foundry.config.extract_base_mkdocs` is the mechanism foundry already
ships for this; the gap was only that this repository never called it.
"""

from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    try:
        from provide.foundry.config import extract_base_mkdocs
    except ModuleNotFoundError:
        print(
            "provide-foundry is not installed. It is in the `docs` dependency group:\n"
            "    uv sync --group docs",
            file=sys.stderr,
        )
        return 1

    inherited = extract_base_mkdocs(REPO_ROOT)
    if not inherited.is_file():
        print(f"extract_base_mkdocs did not produce {inherited}", file=sys.stderr)
        return 1

    print(f"docs scaffolding ready: {inherited.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# 🌊🪢🔚
