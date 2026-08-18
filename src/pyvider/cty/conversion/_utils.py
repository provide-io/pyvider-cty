#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

from typing import Any

from pyvider.cty.config.defaults import (
    ERR_CANNOT_INFER_FROM_CTY_TYPE,
    ERR_CANNOT_INFER_FROM_CTY_VALUE,
)

# pyvider-cty/src/pyvider/cty/conversion/_utils.py
"""Internal conversion utilities to avoid circular dependencies."""


def canonical_sort_key(member: Any) -> Any:
    """The order a set's elements are put in, for a member that may not be one.

    `CtyValue._canonical_sort_key` is total and never raises, so the fallback
    here is only for a member of a *hand-built* value -- `validate` normalises
    every member into a `CtyValue`. Shared rather than restated: this rule
    decides de-duplication, hashing, and the byte order of every serialized set,
    so two callers sorting a set two ways is a diff Terraform sees.
    """
    # Local import to prevent a circular dependency at module load time.
    from pyvider.cty.values import CtyValue

    return member._canonical_sort_key() if isinstance(member, CtyValue) else (0, str(member))


def _attrs_to_dict_safe(inst: Any) -> dict[str, Any]:
    """
    Safely converts an attrs instance to a dict, raising TypeError for CTY
    framework types to prevent accidental misuse during type inference.
    """
    # Local imports to prevent circular dependencies at module load time.
    from pyvider.cty.types import CtyType
    from pyvider.cty.values import CtyValue

    if isinstance(inst, CtyType):
        error_message = ERR_CANNOT_INFER_FROM_CTY_TYPE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)
    if isinstance(inst, CtyValue):
        error_message = ERR_CANNOT_INFER_FROM_CTY_VALUE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)

    res = {}
    # Use getattr to safely access __attrs_attrs__ which may not exist.
    for a in getattr(type(inst), "__attrs_attrs__", []):
        res[a.name] = getattr(inst, a.name)
    return res


# 🌊🪢🔚
