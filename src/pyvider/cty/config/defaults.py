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
ERR_CONVERT_FN_MUST_BE_CALLABLE = "`convert_fn` must be a callable that accepts 2 arguments"
ERR_EQUAL_FN_MUST_BE_CALLABLE = "`equal_fn` must be a callable that accepts 2 arguments"
ERR_HASH_FN_MUST_BE_CALLABLE = "`hash_fn` must be a callable that accepts 1 argument"
ERR_ELEMENT_TYPE_MUST_BE_CTYTYPE = "element_type must be a CtyType instance, got {type_name}"
ERR_ELEMENT_TYPES_MUST_BE_TUPLE = "element_types must be a tuple, got {type_name}"
ERR_ELEMENT_TYPE_AT_INDEX_MUST_BE_CTYTYPE = "Element type at index {index} must be a CtyType, got {type_name}"
ERR_EXPECTED_CTYTYPE = "Expected CtyType, but got {type_name}"
ERR_EXPECTED_CTYTYPE_FOR_ELEMENT = "Expected CtyType for element_type, got {type_name}"
ERR_OBJECT_TYPE_SPEC_MUST_BE_DICT = "Object type spec must be a dictionary, got {type_name}"
ERR_TUPLE_TYPE_SPEC_MUST_BE_LIST = "Tuple type spec must be a list, got {type_name}"
ERR_ATTRIBUTE_MUST_BE_CTYTYPE = "Attribute '{name}' must be a CtyType, but got {type_name}"
ERR_INVALID_TERRAFORM_TYPE = "Invalid Terraform type specification: {tf_type}"
ERR_UNKNOWN_PRIMITIVE_TYPE = "Unknown primitive type name: '{tf_type}'"

# Value validation error messages
ERR_EXPECTED_DICT_FOR_OBJECT = "Expected a dictionary for CtyObject, got {type_name}"
ERR_EXPECTED_LIST_TUPLE_FOR_TUPLE = "Expected tuple or list, got {type_name}"
ERR_EXPECTED_SET_LIST_TUPLE = "Expected a Python set, frozenset, list, or tuple, got {type_name}"
ERR_EXPECTED_ELEMENTS_COUNT = "Expected {expected} elements, got {actual}"
ERR_OBJECT_ATTRIBUTE_NAME_MUST_BE_STRING = "Object attribute name must be a string, got {type_name}"
ERR_MAP_KEYS_MUST_BE_STRINGS = "Map keys must be strings, but got key of type {type_name}"
ERR_INVALID_MAP_KEY = "Invalid key for map: {key} is not a valid string"
ERR_VALUE_NOT_LIST_TUPLE = "Value to validate is not a list or tuple, but {type_name}"
ERR_INPUT_MUST_BE_DICT = "Input must be a dictionary, got {type_name}."
ERR_VALUE_NOT_INSTANCE = "Value is not an instance of {expected_type}. Got {actual_type}."
ERR_CTYLIST_VALUE_NOT_LIST_TUPLE = "CtyList value is not a list/tuple, but {type_name}"
ERR_LIST_ELEMENTS_CANNOT_BE_NULL = "List elements cannot be null for element type {element_type}"
ERR_CTYOBJECT_VALUE_NOT_DICT = "CtyObject value is not a dict"
ERR_CONTAINER_VALUE_MUST_BE_CTYVALUE = (
    "Container value must be a CtyValue of type {expected_type}, got {actual_value}"
)

# Path and navigation error messages
ERR_CANNOT_APPLY_PATH_NON_CTYVALUE = "Cannot apply path to non-CtyValue: {type_name}"
ERR_CANNOT_RETURN_NON_CTYVALUE_FROM_APPLY_PATH = "Cannot return non-CtyValue from apply_path"
ERR_TUPLE_INDEX_OUT_OF_BOUNDS = "Tuple index {index} out of bounds"
ERR_OBJECT_NO_ATTRIBUTE = "Object has no attribute '{name}'"
ERR_OBJECT_TYPE_NO_ATTRIBUTE = "Object type has no attribute {name}"

# Collection operation error messages
ERR_CANNOT_INDEX_NON_COLLECTION_TYPE = "Cannot index into non-collection type {type_name}"
ERR_CANNOT_INDEX_NON_COLLECTION_VALUE = "Cannot index into value of type {type_name}"
ERR_CANNOT_GET_ATTRIBUTE_NON_OBJECT_TYPE = "Cannot get attribute from non-object type {type_name}"
ERR_CANNOT_GET_ATTRIBUTE_NON_OBJECT_VALUE = "Cannot get attribute from non-object value of type {type_name}"
ERR_CANNOT_GET_KEY_NON_MAP_TYPE = "Cannot get key from non-map type {type_name}"
ERR_CANNOT_GET_KEY_NON_MAP_VALUE = "Cannot get key from non-map/non-dynamic value of type {type_name}"
ERR_LIST_INDICES_MUST_BE_INT = "list indices must be integers or slices, not {type_name}"
ERR_TUPLE_INDICES_MUST_BE_INT = "Tuple indices must be integers or slices, not {type_name}"

# Value access error messages
ERR_CANNOT_ACCESS_ELEMENT_NULL_LIST = "Cannot access element at index {index} in a null list."
ERR_CANNOT_GET_ATTRIBUTE_NULL_VALUE = "Cannot get attribute '{name}' from null value"
ERR_CANNOT_INDEX_NULL_VALUE = "Cannot index into null value"
ERR_CANNOT_INDEX_UNKNOWN_NULL_VALUE = "Cannot index into unknown or null value"
ERR_CANNOT_GET_KEY_NULL_VALUE = "Cannot get key from null value"
ERR_CANNOT_ITERATE_UNKNOWN_VALUE = "Cannot iterate unknown value"
ERR_CANNOT_GET_LENGTH_UNKNOWN_VALUE = "Cannot get length of unknown value"
ERR_CANNOT_GET_RAW_VALUE_UNKNOWN = "Cannot get raw value of unknown value"
ERR_CANNOT_COMPARE_NULL_UNKNOWN = "Cannot compare null or unknown values"

# CtyValue method error messages
ERR_APPEND_ONLY_FOR_CTYLIST = "'.append()' can only be used on CtyList values."
ERR_WITH_ELEMENT_AT_ONLY_FOR_CTYLIST = "'.with_element_at()' can only be used on CtyList values."
ERR_WITH_KEY_ONLY_FOR_CTYMAP = "'.with_key()' can only be used on CtyMap values."
ERR_WITHOUT_KEY_ONLY_FOR_CTYMAP = "'.without_key()' can only be used on CtyMap values."
ERR_INTERNAL_VALUE_CTYLIST_MUST_BE_LIST_TUPLE = "Internal value of CtyList must be a list or tuple."
ERR_INTERNAL_VALUE_CTYMAP_MUST_BE_DICT = "Internal value of CtyMap must be a dict."
ERR_LIST_INDEX_OUT_OF_RANGE = "list index out of range"
ERR_TUPLE_INDEX_OUT_OF_RANGE = "tuple index out of range"
ERR_INTERNAL_TUPLE_VALUE_INCONSISTENT = "Internal tuple value is inconsistent with type definition."
ERR_INTERNAL_TUPLE_VALUE_INCONSISTENT_SLICING = (
    "Internal tuple value is inconsistent with type definition for slicing."
)

# Comparison and type error messages
ERR_CANNOT_COMPARE_CTYVALUE_WITH = "Cannot compare CtyValue with {type_name}"
ERR_CANNOT_COMPARE_DIFFERENT_TYPES = "Cannot compare CtyValues of different types: {type1} and {type2}"
ERR_VALUE_TYPE_NOT_COMPARABLE = "Value of type {type} is not comparable"
ERR_VALUE_TYPE_NO_LEN = "Value of type {type_name} has no len()"
ERR_VALUE_TYPE_NOT_ITERABLE = "Value of type {type_name} is not iterable"
ERR_VALUE_TYPE_NOT_SUBSCRIPTABLE = "Value of type {type_name} is not subscriptable"
ERR_UNHASHABLE_TYPE = "unhashable type: 'CtyValue[{vtype}]'"

# Conversion type error messages
ERR_CANNOT_CONVERT_BOOL = "Cannot convert {type_name} to bool."
ERR_CANNOT_CONVERT_STRING = "Cannot convert {type_name} to string."
ERR_CANNOT_CONVERT_STRING_WITH_ERROR = "Cannot convert {type_name} to string: {error}"
ERR_CANNOT_REPRESENT_AS_DECIMAL = "Cannot represent {type_name} value '{raw_value}' as Decimal"

# Function-specific error messages
ERR_ADD_ARGS_MUST_BE_NUMBERS = "add: arguments must be numbers"
ERR_SUBTRACT_ARGS_MUST_BE_NUMBERS = "subtract: arguments must be numbers"
ERR_MULTIPLY_ARGS_MUST_BE_NUMBERS = "multiply: arguments must be numbers"
ERR_DIVIDE_ARGS_MUST_BE_NUMBERS = "divide: arguments must be numbers"
ERR_DIVIDE_BY_ZERO = "divide by zero"
ERR_MODULO_ARGS_MUST_BE_NUMBERS = "modulo: arguments must be numbers"
ERR_MODULO_BY_ZERO = "modulo by zero"
ERR_NEGATE_ARG_MUST_BE_NUMBER = "negate: argument must be a number"
ERR_POW_ARGS_MUST_BE_NUMBERS = "pow: arguments must be numbers"
ERR_POW_INVALID_OPERATION = "pow: invalid operation: {error}"
ERR_ABS_MUST_BE_NUMBER = "abs: input must be a number, got {type}"
ERR_CEIL_MUST_BE_NUMBER = "ceil: input must be a number, got {type}"
ERR_FLOOR_MUST_BE_NUMBER = "floor: input must be a number, got {type}"
ERR_SIGNUM_MUST_BE_NUMBER = "signum: input must be a number, got {type}"
ERR_INT_MUST_BE_NUMBER = "int: argument must be a number, got {type}"
ERR_LOG_ARGS_MUST_BE_NUMBERS = "log: arguments must be numbers"
ERR_LOG_BASE_CANNOT_BE_ONE = "log: base cannot be 1"
ERR_LOG_BASE_MUST_BE_POSITIVE = "log: base must be positive, got {base}"
ERR_LOG_NUMBER_MUST_BE_POSITIVE = "log: number must be positive, got {number}"
ERR_LOG_MATH_DOMAIN_ERROR = "log: math domain error: {error}"

# String function error messages
ERR_CHOMP_MUST_BE_STRING = "chomp: input must be a string, got {type}"
ERR_INDENT_ARGS_MUST_BE_NUMBER_AND_STRING = "indent: arguments must be a number of spaces and a string"
ERR_INDENT_SPACES_MUST_BE_WHOLE = "indent: spaces must be a whole number within the int64 range, got {value}"
ERR_INDENT_SPACES_MUST_NOT_BE_NEGATIVE = "indent: spaces must not be negative, got {spaces}"
ERR_JOIN_ARGS_MUST_BE_STRING_AND_LIST = "join: arguments must be string and list/tuple"
ERR_LOWER_MUST_BE_STRING = "lower: input must be a string, got {type}"
ERR_UPPER_MUST_BE_STRING = "upper: input must be a string, got {type}"
ERR_REPLACE_ALL_ARGS_MUST_BE_STRINGS = "replace: all arguments must be strings"
ERR_SPLIT_ARGS_MUST_BE_STRINGS = "split: arguments must be strings"
ERR_STRREV_MUST_BE_STRING = "strrev: input must be a string, got {type}"
ERR_SUBSTR_ARGS_MUST_BE_STRING_NUMBER_NUMBER = "substr: arguments must be string, number, number"
ERR_SUBSTR_OFFSET_MUST_BE_NON_NEGATIVE = "substr: offset must be a non-negative integer"
ERR_SUBSTR_LENGTH_MUST_BE_NON_NEGATIVE_OR_MINUS_ONE = "substr: length must be non-negative or -1"
ERR_TITLE_MUST_BE_STRING = "title: input must be a string, got {type}"
ERR_TRIM_ARGS_MUST_BE_STRINGS = "trim: both arguments must be strings"
ERR_TRIMPREFIX_ARGS_MUST_BE_STRINGS = "trimprefix: both arguments must be strings"
ERR_TRIMSUFFIX_ARGS_MUST_BE_STRINGS = "trimsuffix: both arguments must be strings"
ERR_TRIMSPACE_MUST_BE_STRING = "trimspace: input must be a string, got {type}"

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
ERR_COALESCE_MIN_ONE_ARG = "coalesce must have at least one argument"
ERR_COALESCELIST_NO_NON_EMPTY_LIST = "coalescelist: no non-empty list or tuple found in arguments"
ERR_COMPACT_ARG_MUST_BE_COLLECTION_OF_STRINGS = "compact: argument must be a list, set, or tuple of strings"
ERR_CONCAT_ALL_ARGS_MUST_BE_LISTS = "concat: all arguments must be lists or tuples"
ERR_CONTAINS_COLLECTION_MUST_BE_LIST_SET_TUPLE = (
    "contains: collection must be a list, set, or tuple, got {type}"
)
ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE = "distinct: input must be a list, set, or tuple, got {type}"
ERR_DISTINCT_ELEMENT_NOT_HASHABLE = "distinct: element of type {type} is not hashable. Error: {error}"
ERR_ELEMENT_CANNOT_USE_WITH_EMPTY_LIST = "element: cannot use element function with an empty list"
ERR_ELEMENT_COLLECTION_MUST_BE_LIST_TUPLE = "element: collection must be a list or tuple"
ERR_FLATTEN_INPUT_MUST_BE_LIST_SET_TUPLE = "flatten: can only flatten lists, sets and tuples, got {type}"
ERR_HASINDEX_COLLECTION_MUST_BE_LIST_TUPLE_MAP_OBJECT = (
    "hasindex: collection must be a list, tuple, map, or object, got {type}"
)
ERR_INDEX_KEY_DOES_NOT_EXIST = "index: key does not exist in collection"
ERR_KEYS_INPUT_MUST_BE_MAP_OBJECT = "keys: input must be a map or object, got {type}"
ERR_LENGTH_INPUT_MUST_BE_COLLECTION = "length: input must be a collection, got {type}"
ERR_LOOKUP_COLLECTION_MUST_BE_MAP_OBJECT = "lookup: collection must be a map or object"
ERR_MERGE_ALL_ARGS_MUST_BE_MAPS_OBJECTS = "merge: all arguments must be maps or objects"
ERR_REVERSE_INPUT_MUST_BE_LIST_TUPLE = "reverse: input must be a list or tuple"
ERR_SETPRODUCT_ALL_ARGS_MUST_BE_COLLECTIONS = "setproduct: all arguments must be collections"
ERR_SLICE_ARGS_MUST_BE_START_END_NUMBERS = "slice: start and end must be numbers"
ERR_SLICE_INPUT_MUST_BE_LIST_TUPLE = "slice: input must be a list or tuple, got {type}"
ERR_SORT_INPUT_VALUE_NOT_ITERABLE = "sort: input value is not iterable"
ERR_SORT_INPUT_MUST_BE_LIST_SET_TUPLE = "sort: input must be a list, set, or tuple, got {type}"
ERR_SORT_CANNOT_SORT_WITH_NULL_UNKNOWN = (
    "sort: cannot sort list with null or unknown elements at index {index}."
)
ERR_SORT_ELEMENTS_MUST_BE_STRING_NUMBER_BOOL = "sort: elements must be string, number, or bool. Found: {type}"
ERR_VALUES_INPUT_MUST_BE_MAP_OBJECT = "values: input must be a map or object, got {type}"
ERR_ZIPMAP_ARGS_MUST_BE_LISTS = "zipmap: arguments must be lists or tuples"

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
ERR_TOBOOL_CANNOT_CONVERT = "tobool: cannot convert {type} to bool"
ERR_TOSTRING_CANNOT_CONVERT = "tostring: cannot convert {type} to number"

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
ERR_PARSEINT_ARGS_MUST_BE_STRING_NUMBER = "parseint: arguments must be string and number"
ERR_PARSEINT_BASE_INVALID = "parseint: base must be 0 or between 2 and 36, got {base}"
ERR_FAILED_DECODE_DYNAMIC_TYPE_VALIDATION = (
    "Failed to decode dynamic value type spec from JSON during validation"
)
ERR_FAILED_PROCESS_ELEMENT_FOR_SET = "Failed to process element for set: {error}"
ERR_ERROR_AT_STEP = "Error at step {step_num} ({step}): {error}"
ERR_ERROR_AT_TYPE_STEP = "Error at type step {step_num} ({step}): {error}"

# Bytes and capsule function error messages
ERR_BYTESLEN_ARG_MUST_BE_BYTES_CAPSULE = "byteslen: argument must be a Bytes capsule, got {type}"
ERR_BYTESSLICE_ARGS_MUST_BE_BYTES_NUMBER_NUMBER = "bytesslice: arguments must be Bytes capsule, number, number"
ERR_BYTESSLICE_NEGATIVE = "bytesslice: offset and length must be non-negative"
ERR_BYTESSLICE_OFFSET_PAST_END = "bytesslice: offset {offset} is greater than total buffer length {total}"
ERR_BYTESSLICE_PAST_END = (
    "bytesslice: offset {offset} + length {length} is greater than total buffer length {total}"
)

# Generic value operation error messages
ERR_GET_OPERATION_NON_MAP_CTYVALUE = "get operation called on non-map CtyValue"
ERR_GET_ATTRIBUTE_REQUIRES_CTYVALUE_OBJECT = "get_attribute requires a CtyValue object"
ERR_ATTRIBUTE_CANNOT_BE_NULL = "Attribute cannot be null"
ERR_ATTRIBUTE_NAME_CANNOT_BE_EMPTY = "Attribute name cannot be empty"
ERR_UNKNOWN_ATTRIBUTES = "Unknown attributes: {attributes}"
ERR_UNKNOWN_OPTIONAL_ATTRIBUTES = "Unknown optional attributes: {attributes}"

# Internal errors
ERR_INTERNAL_CTYVALUE_CTYLIST_NOT_LIST_TUPLE = (
    "Internal error: CtyValue of CtyList type does not wrap a list/tuple, got {type_name}"
)
ERR_INTERNAL_CTYVALUE_CTYMAP_NOT_DICT = (
    "Internal error: CtyValue of CtyMap type does not wrap a dict, got {type_name}"
)
ERR_EXPECTED_CTYVALUE_CTYLIST = "Expected CtyValue with CtyList type, got CtyValue with {type_name}"
ERR_EXPECTED_CTYVALUE_LIST = "Expected CtyValue[CtyList], got {type_name}"
ERR_EXPECTED_LIST_TUPLE_CTYVALUE_LIST = "Expected list, tuple, or CtyValue list, got {type_name}"

# 🌊🪢🔚
