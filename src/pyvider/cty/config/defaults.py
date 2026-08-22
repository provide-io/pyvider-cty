#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

import sys

"""Centralized default values for pyvider-cty configuration.
All defaults are defined here instead of inline in field definitions.
"""

# =================================
# Performance and caching defaults
# =================================
ENABLE_TYPE_INFERENCE_CACHE = True  # Enable caching for type inference performance

# =================================
# Validation defaults
# =================================
# Python frames consumed per level of nesting during validation: the
# `with_recursion_detection` wrapper, then the `validate` it wraps. Measured,
# not guessed -- stack depth at the innermost leaf is exactly
# `FRAMES_PER_VALIDATION_LEVEL * levels + 2`.
FRAMES_PER_VALIDATION_LEVEL = 2

# Frames left over for whoever called into validation, so that hitting the
# depth limit is a controlled stop rather than a RecursionError in the caller's
# own stack. Sized for a realistic caller rather than a bare one: 40 was not a
# margin at all, since pytest alone sits deeper than that, and a provider
# handler under gRPC and asyncio is deeper still. Too small a margin turns the
# guard's controlled stop into a crash exactly when the caller is a real
# program rather than a script.
VALIDATION_STACK_MARGIN = 100

# One level held back for CtyDynamic. Its `validate` is guarded and then
# delegates to the concrete type's `validate`, which is guarded too, so a
# dynamic value spends one more guard entry than its nesting depth. Without
# this reserve the advertised limit held for every type except dynamic, which
# stopped one level short of it.
DYNAMIC_DELEGATION_RESERVE = 1

# How much of its own descent the guard must have completed before it will
# attribute a stack overflow to the input's nesting. Below this, the stack ran
# out because the *caller* was already deep, and the input is fine -- degrading
# it to an unknown reports a real attribute value as "known after apply".
MIN_OWNED_OVERFLOW_DEPTH = 8

# Sentinel for "derive the limit"; any positive configured value wins instead.
MAX_VALIDATION_DEPTH_AUTO = 0


_DERIVED_DEPTH_CACHE: dict[tuple[int, int], int] = {}


def default_max_validation_depth() -> int:
    """The deepest nesting the interpreter can actually carry.

    This used to be a flat 500, which was not deliverable. Each level costs two
    Python frames against CPython's 1000-frame limit, so 500 levels needs the
    entire stack with nothing left for the caller: the real ceiling was 496, and
    input nested 497-500 deep came back as a silent unknown despite being inside
    the documented limit.

    Deriving it keeps the promise true under whatever recursion limit is
    actually in force, including a host that has raised it. Set
    `PYVIDER_CTY_MAX_VALIDATION_DEPTH` to override with a fixed value.
    """
    import os

    # The override is read from the environment directly, on every call. Going
    # through CtyConfig meant parsing the whole config, which was too costly to
    # do per validation session -- so it was read once and cached, and an
    # override set after a thread's first validation was then ignored for the
    # life of that thread.
    override = os.environ.get("PYVIDER_CTY_MAX_VALIDATION_DEPTH")
    if override:
        try:
            configured = int(override)
        except ValueError:
            configured = MAX_VALIDATION_DEPTH_AUTO
        if configured > MAX_VALIDATION_DEPTH_AUTO:
            return configured

    # Keyed on the recursion limit so a limit raised after import is picked up,
    # and cached so recomputing it per validation session stays free.
    limit = sys.getrecursionlimit()
    cache_key = (limit, VALIDATION_STACK_MARGIN)
    cached = _DERIVED_DEPTH_CACHE.get(cache_key)
    if cached is not None:
        return cached

    usable = (limit - VALIDATION_STACK_MARGIN) // FRAMES_PER_VALIDATION_LEVEL
    derived = max(1, usable - DYNAMIC_DELEGATION_RESERVE)
    _DERIVED_DEPTH_CACHE[cache_key] = derived
    return derived


# The value at import time, kept for callers that read it directly. The
# authoritative live value is `get_recursion_context().max_depth_allowed`, which
# is derived per context so it tracks a recursion limit changed after import.
MAX_VALIDATION_DEPTH = default_max_validation_depth()

MAX_OBJECT_REVISITS = 100  # Allow many revisits for complex schemas
MAX_VALIDATION_TIME_MS = 30000  # 30 second timeout for pathological cases

# One frame per level once the type parser stops entering a context manager at
# every level; the parse is a plain recursive descent.
FRAMES_PER_TYPE_PARSE_LEVEL = 1

# Room left for whatever called the parser, on the same reasoning as
# VALIDATION_STACK_MARGIN.
TYPE_PARSE_STACK_MARGIN = 100


def default_max_type_nesting_depth() -> int:
    """How deep a Terraform type description may nest before it is refused.

    A type description is decoded from a peer's bytes, so its nesting depth is
    an input rather than a property of this program, and an input that decides
    how much stack to consume is a denial of service. Unbounded, a 1600-level
    description spent seventeen seconds and then raised a bare `RecursionError`
    -- outside the `CtyError` taxonomy, so a caller catching `CtyError` around
    its decoding did not catch it.

    Derived from the live recursion limit rather than fixed, for the same reason
    `default_max_validation_depth` is: a limit that outruns the interpreter is
    not a limit, and a host that raises its recursion limit should get the
    benefit. Real schemas nest in the tens; this lands in the hundreds.
    """
    limit = sys.getrecursionlimit()
    usable = (limit - TYPE_PARSE_STACK_MARGIN) // FRAMES_PER_TYPE_PARSE_LEVEL
    return max(1, usable)


MAX_TYPE_NESTING_DEPTH = default_max_type_nesting_depth()

# =================================
# Codec defaults
# =================================
MSGPACK_EXT_TYPE_CTY = 0
MSGPACK_EXT_TYPE_REFINED_UNKNOWN = 12
MSGPACK_RAW_FALSE = False
MSGPACK_STRICT_MAP_KEY_FALSE = False
MSGPACK_USE_BIN_TYPE_TRUE = True

# Refinement payload field IDs
REFINEMENT_IS_KNOWN_NULL = 1
REFINEMENT_STRING_PREFIX = 2
REFINEMENT_NUMBER_LOWER_BOUND = 3
REFINEMENT_NUMBER_UPPER_BOUND = 4
REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND = 5
REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND = 6

# =================================
# Function operation constants
# =================================
NUMERIC_OPERATIONS = frozenset(["add", "subtract", "multiply", "divide"])
COMPARISON_OPERATIONS = frozenset(["max", "min"])
TIME_UNITS = frozenset(["h", "m", "s"])

# =================================
# Collection defaults
# =================================
EMPTY_LIST_SIZE = 0
NEGATIVE_ONE_LENGTH = -1  # Used for "rest of string" operations

# =================================
# Comparison defaults
# =================================
COMPARISON_OPS_MAP = {
    ">": lambda x, y: x > y,
    ">=": lambda x, y: x >= y,
    "<": lambda x, y: x < y,
    "<=": lambda x, y: x <= y,
}

# =================================
# Parser type kinds
# =================================
TYPE_KIND_LIST = "list"
TYPE_KIND_SET = "set"
TYPE_KIND_MAP = "map"
TYPE_KIND_OBJECT = "object"
TYPE_KIND_TUPLE = "tuple"

# =================================
# Time conversion constants
# =================================
SECONDS_PER_HOUR = 3600
SECONDS_PER_MINUTE = 60
SECONDS_PER_SECOND = 1

# =================================
# Zero/null/boundary values
# =================================
ONE_VALUE = 1
TWO_VALUE = 2

# =================================
# Common thresholds and limits
# =================================
DEFAULT_MAX_ITERATIONS = 1000
DEFAULT_TIMEOUT_SECONDS = 30
MAX_STRING_LENGTH_DISPLAY = 100
MAX_RECURSION_DEPTH = 100
MIN_COLLECTION_SIZE = 0

# go-cty's own cap on range(): the result has to be buffered in memory, and the
# function exists to make small lists of indices to iterate over.
MAX_RANGE_LENGTH = 1024

# =================================
# Exception message templates
# =================================
# These are used to avoid raw strings in exceptions
ERR_DECODE_REFINED_UNKNOWN = "Failed to decode refined unknown payload: {error}"
ERR_DYNAMIC_MALFORMED = "CtyDynamic value is malformed; its inner value is not a CtyValue instance."
ERR_DECODE_DYNAMIC_TYPE = "Failed to decode dynamic value type spec from JSON"
ERR_VALUE_FOR_OBJECT = "Value for CtyObject must be a dict"
ERR_VALUE_FOR_MAP = "Value for CtyMap must be a dict"
ERR_VALUE_FOR_LIST_SET = "Value for CtyList or CtySet must be iterable"
ERR_VALUE_FOR_TUPLE = "Value for CtyTuple must be a tuple"
ERR_OBJECT_NOT_MSGPACK_SERIALIZABLE = "Object of type {type_name} is not MessagePack serializable"
ERR_MIN_ONE_ARG = "{op} requires at least one argument"
ERR_CANNOT_INFER_FROM_CTY_TYPE = "Cannot infer data type from a CtyType instance: {type_name}"
ERR_CANNOT_INFER_FROM_CTY_VALUE = "Cannot infer data type from a CtyValue instance: {type_name}"
ERR_VALUE_TYPE_NO_LEN = "Values of type {type_name} do not have a length"
ERR_MISSING_REQUIRED_ATTRIBUTE = "Missing required attribute '{name}'"
ERR_MAP_MISSING_REQUIRED_ATTRIBUTE = 'map has no element for required attribute "{name}"'

# Conversion error messages
ERR_CAPSULE_CANNOT_CONVERT = "Capsule type {value_type} cannot be converted to {target_type}"
ERR_CUSTOM_CONVERTER_NON_CTYVALUE = "Custom capsule converter returned a non-CtyValue object"
ERR_CUSTOM_CONVERTER_WRONG_TYPE = (
    "Custom capsule converter returned a value of the wrong type (got {result_type}, want {target_type})"
)
ERR_DYNAMIC_VALUE_NOT_CTYVALUE = "Dynamic value does not contain a CtyValue"
ERR_CANNOT_CONVERT_VALIDATION = "Cannot convert {value_type} to {target_type}: {message}"
ERR_CANNOT_CONVERT_TO_BOOL = "Cannot convert {value_type} to bool"
ERR_CANNOT_CONVERT_TO_TYPE = "{func}: cannot convert {type} to {target}"
ERR_CANNOT_CONVERT_BOOL_CASE = (
    'Cannot convert "{text}" to bool; to convert from string, use lowercase "{lowered}"'
)
ERR_SOURCE_OBJECT_NOT_DICT = "Source object is not a dictionary"
ERR_TUPLE_LENGTH_MISMATCH = "Cannot convert a sequence of {got} elements to a tuple of {want}"
ERR_CANNOT_CONVERT_GENERAL = "Cannot convert from {value_type} to {target_type}"

# Type system error messages
ERR_EXPECTED_CTYTYPE = "Expected CtyType, but got {type_name}"

# Value validation error messages

# Path and navigation error messages

# Collection operation error messages

# Value access error messages
ERR_CANNOT_INDEX_UNKNOWN_NULL_VALUE = "Cannot index into unknown or null value"
ERR_CANNOT_ITERATE_UNKNOWN_VALUE = "Cannot iterate unknown value"
ERR_CANNOT_GET_LENGTH_UNKNOWN_VALUE = "Cannot get length of unknown value"
ERR_CANNOT_GET_RAW_VALUE_UNKNOWN = "Cannot get raw value of unknown value"
ERR_CANNOT_COMPARE_NULL_UNKNOWN = "Cannot compare null or unknown values"

# CtyValue method error messages

# Comparison and type error messages
ERR_CANNOT_COMPARE_CTYVALUE_WITH = "Cannot compare CtyValue with {type_name}"
ERR_CANNOT_COMPARE_DIFFERENT_TYPES = "Cannot compare CtyValues of different types: {type1} and {type2}"
ERR_VALUE_TYPE_NOT_COMPARABLE = "Value of type {type} is not comparable"
ERR_VALUE_TYPE_NO_LEN = "Value of type {type_name} has no len()"
ERR_VALUE_TYPE_NOT_ITERABLE = "Value of type {type_name} is not iterable"
ERR_VALUE_TYPE_NOT_SUBSCRIPTABLE = "Value of type {type_name} is not subscriptable"
# ERR_UNHASHABLE_TYPE is deliberately gone as of 2026-08-17. `CtyValue.__hash__`
# answers for every type now, containers included, so there is no longer a
# message for refusing -- and leaving one behind would advertise a behaviour
# this library does not have.

# Conversion type error messages

# Function-specific error messages

# Numeric function error messages
# go-cty reads both of these through `gocty.FromCtyValue` into a Go `int`, so a
# fraction, an infinity or anything outside the int64 range is refused before the
# function looks at the value.
ERR_SIGNUM_NOT_WHOLE = "signum: number must be a whole number within the int64 range, got {value}"
ERR_PARSEINT_BASE_NOT_WHOLE = "parseint: base must be a whole number within the int64 range, got {value}"

# String function error messages
ERR_INDENT_SPACES_MUST_BE_WHOLE = "indent: spaces must be a whole number within the int64 range, got {value}"
ERR_INDENT_SPACES_MUST_NOT_BE_NEGATIVE = "indent: spaces must not be negative, got {spaces}"
# go-cty's own wording, from `gocty.FromCtyValue` reading `substr`'s offset and
# length into a Go `int`. Left unprefixed because that is the text a caller
# comparing the two implementations sees.
ERR_SUBSTR_ARG_MUST_BE_WHOLE = (
    "value must be a whole number, between -9223372036854775808 and 9223372036854775807"
)
# go-cty's `JoinFunc` is variadic, so it numbers the lists from 1 -- argument 0
# is the separator -- and words the single-list case without a list number.
ERR_JOIN_AT_LEAST_ONE_LIST = "at least one list is required"
ERR_JOIN_ELEMENT_IS_NULL = "element {element} is null; cannot concatenate null values"
ERR_JOIN_ELEMENT_OF_LIST_IS_NULL = "element {element} of list {list} is null; cannot concatenate null values"

# Regular expression error messages
# Shared by regex and regexall, which decide their result type from the pattern
# by the same rules. Worded as go-cty words them (cty/function/stdlib/regexp.go).
ERR_REGEX_INVALID_PATTERN = "{func}: invalid regexp pattern: {error}"
ERR_REGEX_MIXED_CAPTURE_GROUPS = (
    "{func}: invalid regexp pattern: cannot mix both named and unnamed capture groups"
)
ERR_REGEX_NO_MATCH = "regex: pattern did not match any part of the given string"

# Collection function error messages
ERR_CHUNKLIST_ARGS_MUST_BE_LIST_AND_NUMBER = "chunklist: arguments must be a list/tuple and a number"
ERR_CHUNKLIST_SIZE_MUST_BE_POSITIVE = "chunklist: the size argument must be positive"
ERR_CHUNKLIST_TUPLE_NOT_UNIFIABLE = "chunklist: tuple elements have no common type"
ERR_CHUNKLIST_SIZE_MUST_BE_WHOLE = "chunklist: size must be a whole number within the int64 range, got {value}"
ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE = "distinct: input must be a list, set, or tuple, got {type}"
ERR_FLATTEN_INPUT_MUST_BE_LIST_SET_TUPLE = "flatten: can only flatten lists, sets and tuples, got {type}"
ERR_KEYS_INPUT_MUST_BE_MAP_OBJECT = "keys: input must be a map or object, got {type}"
ERR_LENGTH_INPUT_MUST_BE_COLLECTION = "length: input must be a collection, got {type}"
ERR_MERGE_ALL_ARGS_MUST_BE_MAPS_OBJECTS = "merge: all arguments must be maps or objects"
ERR_VALUES_INPUT_MUST_BE_MAP_OBJECT = "values: input must be a map or object, got {type}"

# Stdlib registry error messages
ERR_STDLIB_DUPLICATE_NAME = "two functions are declared as the stdlib function {name!r}: {first} and {second}"

# Set operation error messages
ERR_SET_OP_ARG_MUST_BE_SET = "{func}: set required, but received {type}"
# This library's own wording, deliberately not go-cty's. go-cty raises these
# bare -- "must have map or object type" -- because HCL wraps them with the
# argument context before an operator sees them; nothing wraps them here, so the
# function names itself and says what it was given. The same shape as the other
# 34 prefixed messages in this file, and the divergence is recorded in
# docs/reference/go-cty-comparison.md.
ERR_FORMAT_TOO_MANY_ARGUMENTS = "format: too many arguments; only {used} used by format string"
ERR_FORMAT_NO_VERBS = "format: too many arguments; no verbs in format string"
ERR_FORMAT_INVALID = "format: invalid format string at offset {offset}"
ERR_FORMAT_UNSUPPORTED_VERB = "format: unsupported verb {verb!r} at offset {offset}"
ERR_FORMAT_UNSUPPORTED_VALUE = "format: unsupported value for {verb!r} at {offset}: {error}"
ERR_FORMAT_NULL_VALUE = "format: unsupported value for {verb!r} at {offset}: null value cannot be formatted"
ERR_FORMAT_REQUIRES_INTEGER = "format: unsupported value for {verb!r} at {offset}: an integer is required"
ERR_FORMAT_NOT_ENOUGH_ARGUMENTS = (
    "format: not enough arguments for {verb!r} at {offset}: need index {want} but have {have} total"
)
ERR_FORMAT_INCONSISTENT_LENGTH = (
    "formatlist: argument {position} has length {length}, "
    "which is inconsistent with argument {other} of length {other_length}"
)

# A failed conversion, said in one line. This used to interpolate the whole
# CtyConversionError, which nests its cause and names Python types, so
# `format("%d", "a")` reported "Cannot represent str value 'a' as Decimal
# (source_type=CtyValue, target_type=number)" to an operator who wrote HCL. The
# detail is still on `__cause__` for a traceback to show; what the diagnostic
# says is now the part a caller can act on. Follows the house habit of naming
# what was given, which go-cty's own "a number is required" does not.
ERR_FORMAT_VALUE_NOT_CONVERTIBLE = "{target} is required, got {source}"

# formatlist names the iteration, because with a list argument the row that
# failed is the thing a caller needs to find. go-cty reports this too, though it
# spells the prefix differently.
ERR_FORMATLIST_ITERATION = "formatlist: iteration {index}: {error}"

ERR_ARGUMENT_MUST_NOT_BE_NULL = "{func}: argument {position} must not be null"
ERR_CONCAT_REQUIRES_ONE = "concat: at least one argument is required"
ERR_CONCAT_ARGS_MUST_BE_SEQUENCES = "concat: all arguments must be lists or tuples, got {type}"
ERR_SETPRODUCT_REQUIRES_TWO = "setproduct: at least two arguments are required"
ERR_SETPRODUCT_TUPLE_NOT_UNIFIABLE = "setproduct: all elements must be of the same type"
ERR_SETPRODUCT_ARG_MUST_BE_COLLECTION = "setproduct: a set or a list is required, got {type}"
ERR_SETPRODUCT_TOO_LARGE = "setproduct: {total} elements exceeds the safety limit of {limit}"

# go-cty's number is a big.Float, which has no NaN, so there is nothing on the
# wire for one to decode into.
ERR_NAN_NOT_SERIALIZABLE = "cannot serialize NaN: cty numbers have no NaN"
ERR_SET_OP_INCOMPATIBLE_ELEMENTS = "{func}: given sets must all have compatible element types"

# range() error messages
ERR_RANGE_ARG_COUNT = "range: must have one, two, or three arguments"
ERR_RANGE_END_MUST_BE_LESS = "range: end must be less than start when step is negative"
ERR_RANGE_END_MUST_BE_GREATER = "range: end must be greater than start when step is positive"
ERR_RANGE_TOO_MANY_VALUES = (
    "range: more than {limit} values were generated; either decrease the "
    "difference between start and end or use a smaller step"
)

# Type conversion function error messages

# Codec and JSON error messages
ERR_CSVDECODE_FAILED = "csvdecode: failed to decode CSV: {error}"
ERR_CSVDECODE_MISSING_HEADER = "csvdecode: missing header line"
ERR_CSVDECODE_DUPLICATE_COLUMN = 'csvdecode: duplicate column name "{name}"'
ERR_CSVDECODE_WRONG_FIELD_COUNT = "csvdecode: CSV parse error on line {line}: wrong number of fields"
ERR_CSVDECODE_BARE_QUOTE = 'csvdecode: CSV parse error on line {line}: bare " in non-quoted-field'
ERR_CSVDECODE_QUOTE = 'csvdecode: CSV parse error on line {line}: extraneous or missing " in quoted-field'
ERR_JSONDECODE_FAILED = "jsondecode: failed to decode JSON: {error}"
ERR_JSONDECODE_INVALID_FIRST_CHARACTER = "a JSON document cannot begin with the character '{character}'"
ERR_JSONDECODE_UNSUPPORTED_ATTRIBUTE = 'jsondecode: unsupported attribute "{name}"'
ERR_JSONENCODE_FAILED = "jsonencode: failed to encode value: {error}"

# Date and time function error messages
ERR_FORMATDATE_INVALID_TIMESTAMP = "formatdate: invalid timestamp format: {error}"
ERR_FORMATDATE_GO_LAYOUT = (
    "formatdate: {spec!r} looks like Go's reference layout, which this function does not use. "
    "go-cty defines its own scheme -- YYYY, MM, DD, hh, mm, ss, EEEE, MMMM, AA, ZZZZZ -- and "
    "reads digits as literal text, so this would return the format string itself rather than a "
    "formatted date. Rewrite it (2006-01-02 becomes YYYY-MM-DD), or quote it to keep the digits "
    "as literal text: '{spec}'."
)
ERR_FORMATDATE_INVALID_VERB = 'formatdate: invalid date format verb "{verb}"'
ERR_FORMATDATE_INVALID_VERB_LENGTH = 'formatdate: invalid date format verb "{verb}": {expected}'
ERR_FORMATDATE_UNTERMINATED_LITERAL = "formatdate: unterminated literal '"
ERR_TIMEADD_INVALID_FORMAT = "timeadd: invalid argument format: {error}"
ERR_TIMEADD_OUT_OF_RANGE = (
    "timeadd: result is outside the representable range: the year must be between 1 and 9999"
)
ERR_INVALID_DURATION_FORMAT = "Invalid duration string format: '{duration_str}'"
ERR_INVALID_RFC3339_TIMESTAMP = "not a valid RFC3339 timestamp: {timestamp!r}"

# Parsing and validation error messages

# Bytes and capsule function error messages
ERR_BYTESSLICE_OFFSET_AND_LENGTH_MUST_BE_WHOLE = (
    "bytesslice: offset and length must be whole numbers within the int64 range, got {value}"
)
ERR_BYTESSLICE_NEGATIVE = "bytesslice: offset and length must be non-negative"
ERR_BYTESSLICE_OFFSET_PAST_END = "bytesslice: offset {offset} is greater than total buffer length {total}"
ERR_BYTESSLICE_PAST_END = (
    "bytesslice: offset {offset} + length {length} is greater than total buffer length {total}"
)

# Generic value operation error messages

# Internal errors

# 🌊🪢🔚
