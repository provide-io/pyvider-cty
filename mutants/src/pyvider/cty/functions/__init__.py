# pyvider/cty/functions/__init__.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

# pyvider-cty/src/pyvider/cty/functions/__init__.py
# This file makes the 'functions' module a package.
from pyvider.cty.functions.bytes_functions import byteslen, bytesslice
from pyvider.cty.functions.collection_functions import (
    chunklist,
    coalescelist,
    compact,
    concat,
    contains,
    distinct,
    element,
    flatten,
    hasindex,
    index,
    keys,
    length,
    lookup,
    merge,
    reverse,
    setproduct,
    slice,
    sort,
    values,
    zipmap,
)
from pyvider.cty.functions.comparison_functions import (
    equal,
    greater_than,
    greater_than_or_equal_to,
    less_than,
    less_than_or_equal_to,
    max_fn,
    min_fn,
    not_equal,
)
from pyvider.cty.functions.conversion_functions import to_bool, to_number, to_string
from pyvider.cty.functions.datetime_functions import formatdate, timeadd
from pyvider.cty.functions.encoding_functions import csvdecode, jsondecode, jsonencode
from pyvider.cty.functions.numeric_functions import (
    abs_fn,
    add,
    ceil_fn,
    divide,
    floor_fn,
    int_fn,
    log_fn,
    modulo,
    multiply,
    negate,
    parseint_fn,
    pow_fn,
    signum_fn,
    subtract,
)
from pyvider.cty.functions.string_functions import (
    chomp,
    indent,
    join,
    lower,
    regex,
    regexall,
    regexreplace,
    replace,
    split,
    strrev,
    substr,
    title,
    trim,
    trimprefix,
    trimspace,
    trimsuffix,
    upper,
)
from pyvider.cty.functions.structural_functions import coalesce

__all__ = [
    "abs_fn",
    "add",
    "byteslen",
    "bytesslice",
    "ceil_fn",
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
    "floor_fn",
    "formatdate",
    "greater_than",
    "greater_than_or_equal_to",
    "hasindex",
    "indent",
    "index",
    "int_fn",
    "join",
    "jsondecode",
    "jsonencode",
    "keys",
    "length",
    "less_than",
    "less_than_or_equal_to",
    "log_fn",
    "lookup",
    "lower",
    "max_fn",
    "merge",
    "min_fn",
    "modulo",
    "multiply",
    "negate",
    "not_equal",
    "parseint_fn",
    "pow_fn",
    "regex",
    "regexall",
    "regexreplace",
    "replace",
    "reverse",
    "setproduct",
    "signum_fn",
    "slice",
    "sort",
    "split",
    "strrev",
    "substr",
    "subtract",
    "timeadd",
    "title",
    "to_bool",
    "to_number",
    "to_string",
    "trim",
    "trimprefix",
    "trimspace",
    "trimsuffix",
    "upper",
    "values",
    "zipmap",
]
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result
# 🌊🪢📦🪄
