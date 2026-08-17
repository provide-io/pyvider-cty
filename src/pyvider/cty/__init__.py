#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

from provide.foundation.utils import get_version

__version__ = get_version("pyvider-cty", caller_file=__file__)

from pyvider.cty.conformance import ConformanceError, conformance_errors
from pyvider.cty.conversion import convert, unify
from pyvider.cty.exceptions import (
    CtyAttributeValidationError,
    CtyConversionError,
    CtyListValidationError,
    CtyMapValidationError,
    CtySetValidationError,
    CtyTupleValidationError,
    CtyTypeMismatchError,
    CtyTypeParseError,
    CtyValidationError,
)
from pyvider.cty.json_codec import cty_from_json, cty_to_json, implied_json_type
from pyvider.cty.mark_paths import PathMarks, mark_with_paths, unmark_deep_with_paths
from pyvider.cty.marks import CtyMark
from pyvider.cty.parser import parse_tf_type_to_ctytype, parse_type_string_to_ctytype
from pyvider.cty.types import (
    BytesCapsule,
    CtyBool,
    CtyCapsule,
    CtyCapsuleWithOps,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyType,
)
from pyvider.cty.unknown import unknown_as_null
from pyvider.cty.values import CtyValue
from pyvider.cty.walk import deep_values, transform, walk

"""
The pyvider.cty package is a pure-Python implementation of the concepts
from HashiCorp's `cty` library, providing a rich type system for the framework.
"""

__all__ = [
    "BytesCapsule",
    "ConformanceError",
    "CtyAttributeValidationError",
    "CtyBool",
    "CtyCapsule",
    "CtyCapsuleWithOps",
    "CtyConversionError",
    "CtyDynamic",
    "CtyList",
    "CtyListValidationError",
    "CtyMap",
    "CtyMapValidationError",
    "CtyMark",
    "CtyNumber",
    "CtyObject",
    "CtySet",
    "CtySetValidationError",
    "CtyString",
    "CtyTuple",
    "CtyTupleValidationError",
    "CtyType",
    "CtyTypeMismatchError",
    "CtyTypeParseError",
    "CtyValidationError",
    "CtyValue",
    "PathMarks",
    "__version__",
    "conformance_errors",
    "convert",
    "cty_from_json",
    "cty_to_json",
    "deep_values",
    "implied_json_type",
    "mark_with_paths",
    "parse_tf_type_to_ctytype",
    "parse_type_string_to_ctytype",
    "transform",
    "unify",
    "unknown_as_null",
    "unmark_deep_with_paths",
    "walk",
]

# 🌊🪢🔚
