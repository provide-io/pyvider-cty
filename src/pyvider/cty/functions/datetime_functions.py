import re
from datetime import datetime, timedelta, timezone
from typing import Any

from pyvider.cty import CtyNumber, CtyString, CtyValue
from pyvider.cty.exceptions import CtyFunctionError

# A simplified mapping from Go's time layout to Python's strftime format.
# This is not exhaustive but covers common cases.
GO_TO_PYTHON_FORMAT_MAP = {
    "2006": "%Y", "06": "%y", "01": "%m", "Jan": "%b", "January": "%B",
    "02": "%d", "_2": "%e", "15": "%H", "03": "%I", "04": "%M", "05": "%S",
    "PM": "%p", "MST": "%Z", "Z07:00": "%z",
}

def _translate_go_format(go_fmt: str) -> str:
    py_fmt = go_fmt
    for go, py in GO_TO_PYTHON_FORMAT_MAP.items():
        py_fmt = py_fmt.replace(go, py)
    return py_fmt

def formatdate(spec: "CtyValue[Any]", timestamp: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        dt = datetime.fromisoformat(timestamp.value.replace("Z", "+00:00"))
        py_format_spec = _translate_go_format(spec.value)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e

def _parse_duration(duration_str: str) -> timedelta:
    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    if not parts:
        raise ValueError("Invalid duration string")
    total_seconds = 0
    for value, unit in parts:
        val = float(value)
        if unit == "h": total_seconds += val * 3600
        elif unit == "m": total_seconds += val * 60
        elif unit == "s": total_seconds += val
    return timedelta(seconds=total_seconds)

def timeadd(timestamp: "CtyValue[Any]", duration: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        dt = datetime.fromisoformat(timestamp.value.replace("Z", "+00:00"))
        td = _parse_duration(duration.value)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e
