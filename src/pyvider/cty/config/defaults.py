from __future__ import annotations

"""Centralized default values for pyvider-cty configuration.
All defaults are defined here instead of inline in field definitions.
"""

# =================================
# Validation defaults
# =================================
MAX_VALIDATION_DEPTH = 500  # Safer default, well below Python's typical limit
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
