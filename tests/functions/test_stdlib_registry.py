#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The registry that maps go-cty's function names onto this package's.

The two vocabularies cannot be made to coincide. `and`, `or` and `not` are
Python keywords, so no Python function can carry those names; seven more --
`abs`, `int`, `max`, `min`, `pow`, `range`, `slice` -- would shadow builtins
that the surrounding modules actually call. So the Terraform name is data, and
this is where it lives.

These are guards, not behaviour tests: the behaviour is covered against the
live oracle in the compatibility sweep. What they protect is that the mapping
stays complete and stays honest, which is exactly what the sweep's own
hand-maintained copy of it failed to do -- it silently skipped fourteen
functions while reporting them as covered.
"""

from __future__ import annotations

import builtins
import keyword

import pytest

import pyvider.cty.functions as F
from pyvider.cty.functions import STDLIB

# go-cty's stdlib, as its own function names. Kept as a literal rather than
# read from the oracle so that this file states what parity means without
# needing a Go binary present.
GO_CTY_STDLIB = frozenset(
    {
        "abs",
        "add",
        "and",
        "byteslen",
        "bytesslice",
        "ceil",
        "chomp",
        "chunklist",
        "coalesce",
        "coalescelist",
        "compact",
        "concat",
        "contains",
        "csvdecode",
        "distinct",
        "divide",
        "element",
        "equal",
        "flatten",
        "floor",
        "format",
        "formatdate",
        "formatlist",
        "greaterthan",
        "greaterthanorequalto",
        "hasindex",
        "indent",
        "index",
        "int",
        "join",
        "jsondecode",
        "jsonencode",
        "keys",
        "length",
        "lessthan",
        "lessthanorequalto",
        "log",
        "lookup",
        "lower",
        "max",
        "merge",
        "min",
        "modulo",
        "multiply",
        "negate",
        "not",
        "notequal",
        "or",
        "parseint",
        "pow",
        "range",
        "regex",
        "regexall",
        "regexreplace",
        "replace",
        "reverselist",
        "sethaselement",
        "setintersection",
        "setproduct",
        "setsubtract",
        "setsymmetricdifference",
        "setunion",
        "signum",
        "slice",
        "sort",
        "split",
        "strrev",
        "substr",
        "subtract",
        "timeadd",
        "title",
        "tobool",
        "tonumber",
        "tostring",
        "trim",
        "trimprefix",
        "trimspace",
        "trimsuffix",
        "upper",
        "values",
        "zipmap",
    }
)

# Ports that have not landed yet. An entry here is a promise, so the test below
# fails if one is implemented and left in the list.
NOT_YET_PORTED = frozenset({"strlen", "assertnotnull"})


class TestTheRegistryIsComplete:
    def test_every_exported_function_is_registered(self) -> None:
        """A function reachable by import but not by name is half-published.

        The registry is the surface that speaks Terraform, so anything missing
        from it is invisible to a caller dispatching by name.
        """
        registered = {fn.__name__ for fn in STDLIB.values()}
        exported = set(F.__all__) - {"STDLIB"}

        assert exported - registered == set()

    def test_every_registered_name_is_a_go_cty_name(self) -> None:
        """No invented names. The registry's whole value is that it is go-cty's."""
        assert set(STDLIB) - GO_CTY_STDLIB == set()

    def test_the_unported_list_names_only_unported_functions(self) -> None:
        assert NOT_YET_PORTED & set(STDLIB) == set()

    def test_everything_else_in_go_cty_is_registered(self) -> None:
        assert GO_CTY_STDLIB - set(STDLIB) - NOT_YET_PORTED == set()


class TestTheNamesCouldNotHaveBeenPythonIdentifiers:
    """Why this is a dict and not just consistent function naming.

    Pinned as a test because it is the entire justification for the design, and
    it is the kind of reasoning that gets re-litigated once it is only a comment.
    """

    def test_three_names_are_python_keywords(self) -> None:
        assert {name for name in STDLIB if keyword.iskeyword(name)} == {"and", "or", "not"}

    def test_seven_more_would_shadow_builtins_the_modules_call(self) -> None:
        """`slice` is the proof this is not hypothetical.

        `collection_functions.py` defines `slice` and does shadow the builtin;
        it only gets away with it because that module never calls the builtin.
        `range` in the same module and `max` in `numeric_functions.py` are both
        called, so those two would break outright. `format` joined the list when
        it was ported, and it is the sharpest case yet: `format_functions.py`
        calls the builtin `format` on almost every line of its number rendering.
        """
        shadowing = {name for name in STDLIB if not keyword.iskeyword(name) and hasattr(builtins, name)}

        assert shadowing == {"abs", "format", "int", "max", "min", "pow", "range", "slice"}

    def test_most_functions_already_carry_go_ctys_name(self) -> None:
        """The mapping is the exception, not the rule: only the awkward ones differ."""
        same = {name for name, fn in STDLIB.items() if fn.__name__ == name}

        assert len(same) >= 55


class TestTheRegistryIsUsable:
    @pytest.mark.parametrize("name", ["and", "or", "not", "range", "max", "setunion"])
    def test_a_name_no_python_function_could_carry(self, name: str) -> None:
        assert callable(STDLIB[name])

    def test_dispatch_returns_the_same_object_as_the_import(self) -> None:
        assert STDLIB["setunion"] is F.setunion
        assert STDLIB["and"] is F.and_fn
        assert STDLIB["reverselist"] is F.reverse

    def test_calling_through_the_registry_works(self) -> None:
        from pyvider.cty import CtyBool

        assert STDLIB["not"](CtyBool().validate(True)).value is False


class TestTheRegistryRefusesAClash:
    def test_two_functions_cannot_claim_one_name(self) -> None:
        """The failure this guards is silent otherwise: last one registered wins."""
        from pyvider.cty.functions._framework import stdlib_function

        with pytest.raises(ValueError, match="are declared as the stdlib function"):

            @stdlib_function("upper")
            def definitely_not_upper() -> None: ...


# 🌊🪢🔚
