#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

import csv
import io
import json
from typing import Any, cast

from pyvider.cty import CtyDynamic, CtyList, CtyObject, CtyString, CtyValue
from pyvider.cty.conversion import cty_to_native
from pyvider.cty.exceptions import CtyFunctionError


def jsonencode(val: CtyValue[Any]) -> CtyValue[Any]:
    if val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        native_val = cty_to_native(val)
        return CtyString().validate(json.dumps(native_val))
    except Exception as e:
        raise CtyFunctionError(f"jsonencode: failed to encode value: {e}") from e


def jsondecode(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"jsondecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyDynamic())
    try:
        val_str = cast(str, val.value)
        native_val = json.loads(val_str)
        result: CtyValue[Any] = CtyDynamic().validate(native_val)
        return result
    except json.JSONDecodeError as e:
        raise CtyFunctionError(f"jsondecode: failed to decode JSON: {e}") from e


def csvdecode(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"csvdecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyList(element_type=CtyObject({})))

    val_str = cast(str, val.value)
    f = io.StringIO(val_str)
    try:
        # The csv module can raise csv.Error for malformed data
        reader = csv.DictReader(f)
        rows = list(reader)
        result: CtyValue[Any] = CtyList(element_type=CtyDynamic()).validate(rows)
        return result
    except Exception as e:
        raise CtyFunctionError(f"csvdecode: failed to decode CSV: {e}") from e


# 🌊🪢🔚
