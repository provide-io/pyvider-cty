#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Mutation testing: does the suite notice the code being wrong?

Coverage says a line ran. It does not say a test would have failed had the line
been wrong, and every parity bug found on this branch had high coverage over it.
This asks the second question.

Hand-rolled because mutmut 3.5 cannot run against this project. Its trampoline
does `from mutmut.__main__ import record_trampoline_hit`, and that module calls
`set_start_method('fork')` at import time with no `force=True`. Decorators here
run at import time, so the trampoline fires during collection inside a
subprocess where the multiprocessing context is already set, and the run dies
before any mutant executes. Fixing it means patching mutmut in site-packages.
This does the same job in a hundred lines.

    python scripts/mutation_check.py [path ...]

The tests run against each mutant default to `tests/functions/`; set
`MUTATION_TESTS` to a comma-separated list to point elsewhere. A target outside
`src/pyvider/cty/functions/` needs that, and running it against the wrong tests
reports survivors that are really just untested-from-here.

`MUTATION_SAMPLE` raises the per-file sample from its default of 28. The sample
is drawn across the whole file, so in a large one it can miss a small function
entirely -- raise it when the function you changed is what you mean to measure.

Mutates one AST node at a time -- comparison operators, and/or, booleans,
integer constants, a dropped `not` -- runs the tests, restores the file, and
reports the mutations no test noticed. A survivor is either a missing test or an
equivalent mutant. Both are worth knowing, and telling them apart is the point:
do not "fix" a survivor without deciding which it is.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
import os
from pathlib import Path
import random
import subprocess  # nosec
import sys
from typing import cast

DEFAULT_TARGETS = [
    "src/pyvider/cty/functions/datetime_functions.py",
    "src/pyvider/cty/functions/set_functions.py",
    "src/pyvider/cty/functions/bool_functions.py",
    "src/pyvider/cty/functions/encoding_functions.py",
]
TESTS = [path for path in os.environ.get("MUTATION_TESTS", "tests/functions/").split(",") if path]
SAMPLE_PER_FILE = int(os.environ.get("MUTATION_SAMPLE", "28"))
SEED = 20260816
# A mutation that makes the code loop forever is killed in practice; without a
# ceiling the run stalls on it instead.
TEST_TIMEOUT_SECONDS = 120

OPPOSITE = {
    ast.Eq: ast.NotEq,
    ast.NotEq: ast.Eq,
    ast.Lt: ast.LtE,
    ast.LtE: ast.Lt,
    ast.Gt: ast.GtE,
    ast.GtE: ast.Gt,
    ast.Is: ast.IsNot,
    ast.IsNot: ast.Is,
    ast.In: ast.NotIn,
    ast.NotIn: ast.In,
}


@dataclass
class Site:
    kind: str
    index: int
    position: int


class Collect(ast.NodeVisitor):
    """Every node this script knows how to mutate, in a stable order."""

    def __init__(self) -> None:
        self.sites: list[Site] = []
        self.nodes: list[ast.AST] = []

    def _add(self, kind: str, node: ast.AST, index: int = 0) -> None:
        self.sites.append(Site(kind, index, len(self.nodes)))
        self.nodes.append(node)

    def visit_Compare(self, node: ast.Compare) -> None:
        for i, op in enumerate(node.ops):
            if type(op) in OPPOSITE:
                self._add("cmp", node, i)
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        self._add("bool", node)
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, bool):
            self._add("truth", node)
        elif isinstance(node.value, int):
            self._add("int", node)
        self.generic_visit(node)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> None:
        if isinstance(node.op, ast.Not):
            self._add("not", node)
        self.generic_visit(node)


class DropNot(ast.NodeTransformer):
    """Replace one specific `not X` with `X`."""

    def __init__(self, target: ast.AST) -> None:
        self.target = target

    def visit_UnaryOp(self, node: ast.UnaryOp) -> ast.AST:
        self.generic_visit(node)
        return node.operand if node is self.target else node


def apply_mutation(tree: ast.AST, site: Site, node: ast.AST) -> ast.AST:
    match site.kind:
        case "cmp":
            compare = cast_compare(node)
            compare.ops[site.index] = OPPOSITE[type(compare.ops[site.index])]()
        case "bool":
            boolop = cast_boolop(node)
            boolop.op = ast.Or() if isinstance(boolop.op, ast.And) else ast.And()
        case "truth":
            constant = cast_constant(node)
            constant.value = not constant.value
        case "int":
            constant = cast_constant(node)
            constant.value = cast(int, constant.value) + 1
        case "not":
            return cast(ast.AST, DropNot(node).visit(tree))
    return tree


def cast_compare(node: ast.AST) -> ast.Compare:
    assert isinstance(node, ast.Compare)
    return node


def cast_boolop(node: ast.AST) -> ast.BoolOp:
    assert isinstance(node, ast.BoolOp)
    return node


def cast_constant(node: ast.AST) -> ast.Constant:
    assert isinstance(node, ast.Constant)
    return node


def tests_pass() -> bool:
    try:
        result = subprocess.run(  # nosec
            [
                sys.executable,
                "-m",
                "pytest",
                *TESTS,
                "-x",
                "-q",
                "--no-header",
                "-p",
                "no:randomly",
                "--log-cli-level=CRITICAL",
            ],
            capture_output=True,
            timeout=TEST_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return False  # A mutant that hangs is a mutant the suite would catch.
    return result.returncode == 0


def check_file(target: str, rng: random.Random) -> list[tuple[str, int, str]]:
    path = Path(target)
    original = path.read_text()
    collector = Collect()
    collector.visit(ast.parse(original))
    total = len(collector.sites)

    picks = list(range(total))
    rng.shuffle(picks)
    picks = sorted(picks[:SAMPLE_PER_FILE])
    print(f"\n{target}: {total} sites, sampling {len(picks)}", flush=True)

    survivors: list[tuple[str, int, str]] = []
    for pick in picks:
        tree = ast.parse(original)
        fresh = Collect()
        fresh.visit(tree)
        site = fresh.sites[pick]
        node = fresh.nodes[site.position]
        line = getattr(node, "lineno", 0)
        try:
            mutated = apply_mutation(tree, site, node)
            source = ast.unparse(ast.fix_missing_locations(mutated))
            compile(source, target, "exec")
        except (SyntaxError, ValueError, AssertionError):
            continue
        path.write_text(source)
        try:
            survived = tests_pass()
        finally:
            path.write_text(original)
        if survived:
            survivors.append((target, line, site.kind))
            print(f"  SURVIVED {target}:{line} [{site.kind}]", flush=True)
    return survivors


def main() -> int:
    targets = sys.argv[1:] or DEFAULT_TARGETS
    rng = random.Random(SEED)
    survivors: list[tuple[str, int, str]] = []
    for target in targets:
        survivors.extend(check_file(target, rng))

    print(f"\n=== {len(survivors)} survived ===")
    for target, line, kind in survivors:
        print(f"  {target}:{line} ({kind})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# 🌊🪢🔚
