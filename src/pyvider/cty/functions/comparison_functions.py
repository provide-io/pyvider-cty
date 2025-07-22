from typing import Any

from pyvider.cty import CtyBool, CtyNumber, CtyString, CtyValue
from pyvider.cty.exceptions import CtyFunctionError


def equal(a: "CtyValue[Any]", b: "CtyValue[Any]") -> "CtyValue[Any]":
    if a.is_unknown or b.is_unknown:
        return CtyValue.unknown(CtyBool())
    return CtyBool().validate(a == b)


def not_equal(a: "CtyValue[Any]", b: "CtyValue[Any]") -> "CtyValue[Any]":
    if a.is_unknown or b.is_unknown:
        return CtyValue.unknown(CtyBool())
    return CtyBool().validate(a != b)


def _compare(a: "CtyValue[Any]", b: "CtyValue[Any]", op: str) -> "CtyValue[Any]":
    if a.is_unknown or b.is_unknown or a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        raise CtyFunctionError(f"Cannot compare {a.type.ctype} with {b.type.ctype}")
    
    ops = {
        ">": lambda x, y: x > y,
        ">=": lambda x, y: x >= y,
        "<": lambda x, y: x < y,
        "<=": lambda x, y: x <= y,
    }
    return CtyBool().validate(ops[op](a.value, b.value))


def greater_than(a: "CtyValue[Any]", b: "CtyValue[Any]") -> "CtyValue[Any]":
    return _compare(a, b, ">")


def greater_than_or_equal_to(a: "CtyValue[Any]", b: "CtyValue[Any]") -> "CtyValue[Any]":
    return _compare(a, b, ">=")


def less_than(a: "CtyValue[Any]", b: "CtyValue[Any]") -> "CtyValue[Any]":
    return _compare(a, b, "<")


def less_than_or_equal_to(a: "CtyValue[Any]", b: "CtyValue[Any]") -> "CtyValue[Any]":
    return _compare(a, b, "<=")


def _multi_compare(*args: "CtyValue[Any]", op: str) -> "CtyValue[Any]":
    if not args:
        raise CtyFunctionError(f"{op} requires at least one argument")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(args[0].type)
    
    known_args = [v for v in args if not v.is_null]
    if not known_args:
        return CtyValue.null(args[0].type)
        
    is_all_numbers = all(isinstance(v.type, CtyNumber) for v in known_args)
    is_all_strings = all(isinstance(v.type, CtyString) for v in known_args)

    if not (is_all_numbers or is_all_strings):
        raise CtyFunctionError(f"All arguments to {op} must be of the same type (all numbers or all strings)")

    # Use the built-in max/min functions via __builtins__ dictionary
    ops = {"max": __builtins__["max"], "min": __builtins__["min"]}
    result_val = ops[op](known_args, key=lambda v: v.value)
    return result_val


def max_fn(*args: "CtyValue[Any]") -> "CtyValue[Any]":
    return _multi_compare(*args, op="max")


def min_fn(*args: "CtyValue[Any]") -> "CtyValue[Any]":
    return _multi_compare(*args, op="min")
