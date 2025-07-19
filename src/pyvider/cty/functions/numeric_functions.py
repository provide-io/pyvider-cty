from decimal import Decimal, InvalidOperation
import math

from pyvider.cty import CtyNumber, CtyString, CtyValue
from pyvider.cty.exceptions import CtyFunctionError


def add(a: CtyValue, b: CtyValue) -> CtyValue:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("add: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    return CtyNumber().validate(a.value + b.value)

def subtract(a: CtyValue, b: CtyValue) -> CtyValue:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("subtract: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    return CtyNumber().validate(a.value - b.value)

def multiply(a: CtyValue, b: CtyValue) -> CtyValue:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    return CtyNumber().validate(a.value * b.value)

def divide(a: CtyValue, b: CtyValue) -> CtyValue:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == 0:
        raise CtyFunctionError("divide by zero")
    return CtyNumber().validate(a.value / b.value)

def modulo(a: CtyValue, b: CtyValue) -> CtyValue:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == 0:
        raise CtyFunctionError("modulo by zero")
    return CtyNumber().validate(math.fmod(a.value, b.value))

def negate(a: CtyValue) -> CtyValue:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null or a.is_unknown:
        return CtyValue.unknown(CtyNumber())
    return CtyNumber().validate(-a.value)

def abs_fn(input_val: "CtyValue[Any]") -> "CtyValue[Any]":
    """
    Returns the absolute value of a number.
    """
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    val = input_val.value
    return CtyNumber().validate(abs(val))

def ceil_fn(input_val: "CtyValue[Any]") -> "CtyValue[Any]":
    """
    Returns the smallest integer greater than or equal to a number.
    """
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"ceil: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    val = input_val.value
    return CtyNumber().validate(Decimal(math.ceil(val)))

def floor_fn(input_val: "CtyValue[Any]") -> "CtyValue[Any]":
    """
    Returns the largest integer less than or equal to a number.
    """
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"floor: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    val = input_val.value
    return CtyNumber().validate(Decimal(math.floor(val)))

def log_fn(num_val: "CtyValue[Any]", base_val: "CtyValue[Any]") -> "CtyValue[Any]":
    """
    Returns the logarithm of a number in a given base.
    """
    if not isinstance(num_val.type, CtyNumber):
        raise CtyFunctionError(f"log: number input must be a number, got {num_val.type.ctype}")
    if not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError(f"log: base input must be a number, got {base_val.type.ctype}")

    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())

    num = num_val.value
    base = base_val.value

    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")

    try:
        # Use float for math.log, then convert back to Decimal for CtyNumber
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}")


def pow_fn(num_val: "CtyValue[Any]", power_val: "CtyValue[Any]") -> "CtyValue[Any]":
    """
    Returns a number raised to the power of another number.
    """
    if not isinstance(num_val.type, CtyNumber):
        raise CtyFunctionError(f"pow: number input must be a number, got {num_val.type.ctype}")
    if not isinstance(power_val.type, CtyNumber):
        raise CtyFunctionError(f"pow: power input must be a number, got {power_val.type.ctype}")

    if num_val.is_null or num_val.is_unknown or power_val.is_null or power_val.is_unknown:
        return CtyValue.unknown(CtyNumber())

    num = num_val.value
    power = power_val.value

    try:
        # Decimal's __pow__ handles this well, including negative/fractional exponents
        result = num ** power
        return CtyNumber().validate(result)
    except InvalidOperation as e: # e.g. fractional power of negative number
        raise CtyFunctionError(f"pow: invalid operation: {e}")


def signum_fn(input_val: "CtyValue[Any]") -> "CtyValue[Any]":
    """
    Returns the sign of a number (-1 if < 0, 0 if == 0, 1 if > 0).
    """
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"signum: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val # Passthrough, or unknown number if specifically unknown.
                        # Go-cty returns unknown for unknown input. Let's align.
        # return CtyValue.unknown(CtyNumber()) if input_val.is_unknown else input_val

    val = input_val.value
    if val < 0:
        return CtyNumber().validate(Decimal("-1"))
    elif val > 0:
        return CtyNumber().validate(Decimal("1"))
    else:
        return CtyNumber().validate(Decimal("0"))

def parseint_fn(str_val: "CtyValue[Any]", base_val: "CtyValue[Any]") -> "CtyValue[Any]":
    """
    Parses a string to an integer in a given base.
    Base must be 0 or between 2 and 62.
    """
    if not isinstance(str_val.type, CtyString):
        raise CtyFunctionError(f"parseint: input string must be a string, got {str_val.type.ctype}")
    if not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError(f"parseint: base must be a number, got {base_val.type.ctype}")

    if str_val.is_null or str_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())

    s = str_val.value
    base = int(base_val.value) # Base must be an integer

    # go-cty's parseint has base 0 for auto-detection (0x, 0), and 2-36 for others.
    # Python's int() with base 0 handles "0x", "0o", "0b" prefixes.
    # For other bases, Python's int() handles 2-36.
    # go-cty extends this to 62 using 0-9, a-z, A-Z. Python's int() does not support beyond 36.
    # This implementation will match Python's int() behavior for simplicity for now.
    # For bases > 36, a custom implementation would be needed.

    if not (base == 0 or 2 <= base <= 36): # Python's int() limitation
         raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")

    try:
        # Python's int() correctly handles prefixes like "0x" if base is 0 or 16.
        # If base is specified (not 0), prefixes are not allowed unless matching the base.
        # e.g. int("0xff", 0) works, int("0xff", 16) works, int("0xff", 10) fails.
        #      int("077", 0) works (octal), int("077", 8) works.
        #      int("0b101", 0) works (binary), int("0b101", 2) works.
        # This behavior is consistent with go-cty's general approach.

        # Handle potential CtyNumber representation of base
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except ValueError:
        # Could not convert string to int with the given base
        # Return null as per go-cty's behavior for parseint on failure
        return CtyValue.null(CtyNumber())
    except TypeError: # e.g. if s is not a string-like type after .value
        raise CtyFunctionError("parseint: invalid input string for parsing")

# TODO: Register these functions.
# Example registration (hypothetical, as with string_functions):
# from pyvider.cty.functions.core import CtyFunction, FunctionParameter
# abs_func = CtyFunction(
#     name="abs",
#     description="Returns the absolute value of a number.",
#     return_type=CtyNumber(),
#     parameters=[FunctionParameter(name="num", type=CtyNumber())],
#     impl_fn=lambda num: abs_fn(num)
# )
# ... and so on for ceil_fn, floor_fn, log_fn, pow_fn, signum_fn, parseint_fn
