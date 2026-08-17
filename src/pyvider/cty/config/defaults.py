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
ZERO_VALUE = 0
POSITIVE_BOUNDARY = 0
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
ERR_CANNOT_COMPARE = "Cannot compare {type1} with {type2}"
ERR_ALL_ARGS_SAME_TYPE = "All arguments to {op} must be of the same type (all numbers or all strings)"
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
ERR_UNHASHABLE_TYPE = "unhashable type: 'CtyValue[{vtype}]'"

# Conversion type error messages

# Function-specific error messages

# String function error messages
ERR_INDENT_ARGS_MUST_BE_NUMBER_AND_STRING = "indent: arguments must be a number of spaces and a string"
ERR_INDENT_SPACES_MUST_BE_WHOLE = "indent: spaces must be a whole number within the int64 range, got {value}"
ERR_INDENT_SPACES_MUST_NOT_BE_NEGATIVE = "indent: spaces must not be negative, got {spaces}"

# Regular expression error messages
ERR_REGEX_ARGS_MUST_BE_STRINGS = "regex: both arguments must be strings"
ERR_REGEXALL_ARGS_MUST_BE_STRINGS = "regexall: both arguments must be strings"
# Shared by regex and regexall, which decide their result type from the pattern
# by the same rules. Worded as go-cty words them (cty/function/stdlib/regexp.go).
ERR_REGEX_INVALID_PATTERN = "{func}: invalid regexp pattern: {error}"
ERR_REGEX_MIXED_CAPTURE_GROUPS = (
    "{func}: invalid regexp pattern: cannot mix both named and unnamed capture groups"
)
ERR_REGEX_NO_MATCH = "regex: pattern did not match any part of the given string"
ERR_REGEXREPLACE_ALL_ARGS_MUST_BE_STRINGS = "regexreplace: all arguments must be strings"

# Collection function error messages
ERR_CHUNKLIST_ARGS_MUST_BE_LIST_AND_NUMBER = "chunklist: arguments must be a list/tuple and a number"
ERR_CHUNKLIST_SIZE_MUST_BE_POSITIVE = "chunklist: the size argument must be positive"
ERR_CHUNKLIST_TUPLE_NOT_UNIFIABLE = "chunklist: tuple elements have no common type"
ERR_CHUNKLIST_SIZE_MUST_BE_WHOLE = "chunklist: size must be a whole number within the int64 range, got {value}"
ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE = "distinct: input must be a list, set, or tuple, got {type}"
ERR_DISTINCT_ELEMENT_NOT_HASHABLE = "distinct: element of type {type} is not hashable. Error: {error}"
ERR_FLATTEN_INPUT_MUST_BE_LIST_SET_TUPLE = "flatten: can only flatten lists, sets and tuples, got {type}"
ERR_KEYS_INPUT_MUST_BE_MAP_OBJECT = "keys: input must be a map or object, got {type}"
ERR_LENGTH_INPUT_MUST_BE_COLLECTION = "length: input must be a collection, got {type}"
ERR_MERGE_ALL_ARGS_MUST_BE_MAPS_OBJECTS = "merge: all arguments must be maps or objects"
ERR_VALUES_INPUT_MUST_BE_MAP_OBJECT = "values: input must be a map or object, got {type}"

# Stdlib registry error messages
ERR_STDLIB_DUPLICATE_NAME = "two functions are declared as the stdlib function {name!r}: {first} and {second}"

# Logical function error messages
ERR_BOOL_ARG_MUST_BE_BOOL = "{func}: bool required, but received {type}"
ERR_BOOL_ARG_MUST_NOT_BE_NULL = "{func}: argument must not be null"

# Set operation error messages
ERR_SET_OP_ARG_MUST_BE_SET = "{func}: set required, but received {type}"
ERR_SET_OP_REQUIRES_ONE_SET = "{func}: at least one set must be provided"
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
ERR_ARGUMENT_MUST_NOT_BE_NULL = "{func}: argument {position} must not be null"
ERR_CONCAT_REQUIRES_ONE = "concat: at least one argument is required"
ERR_CONCAT_ARG_MUST_NOT_BE_NULL = "concat: argument must not be null"
ERR_CONCAT_ARGS_MUST_BE_SEQUENCES = "concat: all arguments must be lists or tuples, got {type}"
ERR_SETPRODUCT_REQUIRES_TWO = "setproduct: at least two arguments are required"
ERR_SETPRODUCT_TUPLE_NOT_UNIFIABLE = "setproduct: all elements must be of the same type"
ERR_SETPRODUCT_ARG_MUST_BE_COLLECTION = "setproduct: a set or a list is required, got {type}"
ERR_SETPRODUCT_ARG_MUST_NOT_BE_NULL = "setproduct: argument must not be null"
ERR_SET_OP_INCOMPATIBLE_ELEMENTS = "{func}: given sets must all have compatible element types"

# range() error messages
ERR_RANGE_ARG_COUNT = "range: must have one, two, or three arguments"
ERR_RANGE_ARGS_MUST_BE_NUMBERS = "range: arguments must be numbers, got {type}"
ERR_RANGE_STEP_MUST_NOT_BE_ZERO = "range: step must not be zero"
ERR_RANGE_END_MUST_BE_LESS = "range: end must be less than start when step is negative"
ERR_RANGE_END_MUST_BE_GREATER = "range: end must be greater than start when step is positive"
ERR_RANGE_TOO_MANY_VALUES = (
    "range: more than {limit} values were generated; either decrease the "
    "difference between start and end or use a smaller step"
)

# Type conversion function error messages

# Codec and JSON error messages
ERR_CSVDECODE_ARG_MUST_BE_STRING = "csvdecode: argument must be a string, got {type}"
ERR_CSVDECODE_FAILED = "csvdecode: failed to decode CSV: {error}"
ERR_CSVDECODE_MISSING_HEADER = "csvdecode: missing header line"
ERR_CSVDECODE_DUPLICATE_COLUMN = 'csvdecode: duplicate column name "{name}"'
ERR_CSVDECODE_WRONG_FIELD_COUNT = "csvdecode: CSV parse error on line {line}: wrong number of fields"
ERR_JSONDECODE_ARG_MUST_BE_STRING = "jsondecode: argument must be a string, got {type}"
ERR_JSONDECODE_FAILED = "jsondecode: failed to decode JSON: {error}"
ERR_JSONENCODE_FAILED = "jsonencode: failed to encode value: {error}"

# Date and time function error messages
ERR_FORMATDATE_ARGS_MUST_BE_STRINGS = "formatdate: arguments must be strings"
ERR_FORMATDATE_INVALID_TIMESTAMP = "formatdate: invalid timestamp format: {error}"
ERR_FORMATDATE_INVALID_VERB = 'formatdate: invalid date format verb "{verb}"'
ERR_FORMATDATE_INVALID_VERB_LENGTH = 'formatdate: invalid date format verb "{verb}": {expected}'
ERR_FORMATDATE_UNTERMINATED_LITERAL = "formatdate: unterminated literal '"
ERR_TIMEADD_ARGS_MUST_BE_STRINGS = "timeadd: arguments must be strings"
ERR_TIMEADD_INVALID_FORMAT = "timeadd: invalid argument format: {error}"
ERR_INVALID_DURATION_FORMAT = "Invalid duration string format: '{duration_str}'"
ERR_INVALID_RFC3339_TIMESTAMP = "not a valid RFC3339 timestamp: {timestamp!r}"

# Parsing and validation error messages

# Bytes and capsule function error messages
ERR_BYTESLEN_ARG_MUST_BE_BYTES_CAPSULE = "byteslen: argument must be a Bytes capsule, got {type}"
ERR_BYTESSLICE_ARGS_MUST_BE_BYTES_NUMBER_NUMBER = "bytesslice: arguments must be Bytes capsule, number, number"
ERR_BYTESSLICE_NEGATIVE = "bytesslice: offset and length must be non-negative"
ERR_BYTESSLICE_OFFSET_PAST_END = "bytesslice: offset {offset} is greater than total buffer length {total}"
ERR_BYTESSLICE_PAST_END = (
    "bytesslice: offset {offset} + length {length} is greater than total buffer length {total}"
)

# Generic value operation error messages

# Internal errors

# 🌊🪢🔚
