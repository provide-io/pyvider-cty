# pyvider/cty/codec.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from decimal import Decimal
import json
from typing import Any, cast

import msgpack  # type: ignore
from provide.foundation.errors import error_boundary

from pyvider.cty.config.defaults import (
    ERR_DECODE_DYNAMIC_TYPE,
    ERR_DECODE_REFINED_UNKNOWN,
    ERR_DYNAMIC_MALFORMED,
    ERR_OBJECT_NOT_MSGPACK_SERIALIZABLE,
    ERR_VALUE_FOR_LIST_SET,
    ERR_VALUE_FOR_MAP,
    ERR_VALUE_FOR_OBJECT,
    ERR_VALUE_FOR_TUPLE,
    MSGPACK_EXT_TYPE_CTY,
    MSGPACK_EXT_TYPE_REFINED_UNKNOWN,
    MSGPACK_RAW_FALSE,
    MSGPACK_STRICT_MAP_KEY_FALSE,
    MSGPACK_USE_BIN_TYPE_TRUE,
    REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND,
    REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND,
    REFINEMENT_IS_KNOWN_NULL,
    REFINEMENT_NUMBER_LOWER_BOUND,
    REFINEMENT_NUMBER_UPPER_BOUND,
    REFINEMENT_STRING_PREFIX,
    TWO_VALUE,
)
from pyvider.cty.conversion import encode_cty_type_to_wire_json
from pyvider.cty.exceptions import (
    CtyValidationError,
    DeserializationError,
    SerializationError,
)
from pyvider.cty.parser import parse_tf_type_to_ctytype
from pyvider.cty.types import (
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyObject,
    CtySet,
    CtyTuple,
    CtyType,
)
from pyvider.cty.values import CtyValue
from pyvider.cty.values.markers import (
    UNREFINED_UNKNOWN,
    RefinedUnknownValue,
    UnknownValue,
)
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


def x__decode_number_value__mutmut_orig(val: Any) -> Decimal:
    """Decode a numeric value from bytes or other format to Decimal."""
    if isinstance(val, bytes):
        return Decimal(val.decode("utf-8"))
    return Decimal(val)


def x__decode_number_value__mutmut_1(val: Any) -> Decimal:
    """Decode a numeric value from bytes or other format to Decimal."""
    if isinstance(val, bytes):
        return Decimal(None)
    return Decimal(val)


def x__decode_number_value__mutmut_2(val: Any) -> Decimal:
    """Decode a numeric value from bytes or other format to Decimal."""
    if isinstance(val, bytes):
        return Decimal(val.decode(None))
    return Decimal(val)


def x__decode_number_value__mutmut_3(val: Any) -> Decimal:
    """Decode a numeric value from bytes or other format to Decimal."""
    if isinstance(val, bytes):
        return Decimal(val.decode("XXutf-8XX"))
    return Decimal(val)


def x__decode_number_value__mutmut_4(val: Any) -> Decimal:
    """Decode a numeric value from bytes or other format to Decimal."""
    if isinstance(val, bytes):
        return Decimal(val.decode("UTF-8"))
    return Decimal(val)


def x__decode_number_value__mutmut_5(val: Any) -> Decimal:
    """Decode a numeric value from bytes or other format to Decimal."""
    if isinstance(val, bytes):
        return Decimal(val.decode("utf-8"))
    return Decimal(None)

x__decode_number_value__mutmut_mutants : ClassVar[MutantDict] = {
'x__decode_number_value__mutmut_1': x__decode_number_value__mutmut_1, 
    'x__decode_number_value__mutmut_2': x__decode_number_value__mutmut_2, 
    'x__decode_number_value__mutmut_3': x__decode_number_value__mutmut_3, 
    'x__decode_number_value__mutmut_4': x__decode_number_value__mutmut_4, 
    'x__decode_number_value__mutmut_5': x__decode_number_value__mutmut_5
}

def _decode_number_value(*args, **kwargs):
    result = _mutmut_trampoline(x__decode_number_value__mutmut_orig, x__decode_number_value__mutmut_mutants, args, kwargs)
    return result 

_decode_number_value.__signature__ = _mutmut_signature(x__decode_number_value__mutmut_orig)
x__decode_number_value__mutmut_orig.__name__ = 'x__decode_number_value'


def x__extract_refinements_from_payload__mutmut_orig(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_1(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = None

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_2(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL not in payload:
        refinements["is_known_null"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_3(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = None
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_4(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["XXis_known_nullXX"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_5(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["IS_KNOWN_NULL"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_6(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX not in payload:
        refinements["string_prefix"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_7(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = None
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_8(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["XXstring_prefixXX"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_9(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["STRING_PREFIX"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_10(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND not in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_11(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = None
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_12(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["XXnumber_lower_boundXX"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_13(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["NUMBER_LOWER_BOUND"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_14(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(None),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_15(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][1]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_16(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][2],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_17(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND not in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_18(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = None
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_19(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["XXnumber_upper_boundXX"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_20(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["NUMBER_UPPER_BOUND"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_21(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(None),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_22(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][1]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_23(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][2],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_24(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND not in payload:
        refinements["collection_length_lower_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_25(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = None
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_26(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["XXcollection_length_lower_boundXX"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_27(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["COLLECTION_LENGTH_LOWER_BOUND"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_28(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND not in payload:
        refinements["collection_length_upper_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_29(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["collection_length_upper_bound"] = None

    return refinements


def x__extract_refinements_from_payload__mutmut_30(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["XXcollection_length_upper_boundXX"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements


def x__extract_refinements_from_payload__mutmut_31(payload: dict[int, Any]) -> dict[str, Any]:
    """Extract refinement data from a msgpack payload."""
    refinements = {}

    if REFINEMENT_IS_KNOWN_NULL in payload:
        refinements["is_known_null"] = payload[REFINEMENT_IS_KNOWN_NULL]
    if REFINEMENT_STRING_PREFIX in payload:
        refinements["string_prefix"] = payload[REFINEMENT_STRING_PREFIX]
    if REFINEMENT_NUMBER_LOWER_BOUND in payload:
        refinements["number_lower_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_LOWER_BOUND][0]),
            payload[REFINEMENT_NUMBER_LOWER_BOUND][1],
        )
    if REFINEMENT_NUMBER_UPPER_BOUND in payload:
        refinements["number_upper_bound"] = (
            _decode_number_value(payload[REFINEMENT_NUMBER_UPPER_BOUND][0]),
            payload[REFINEMENT_NUMBER_UPPER_BOUND][1],
        )
    if REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND in payload:
        refinements["collection_length_lower_bound"] = payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND]
    if REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND in payload:
        refinements["COLLECTION_LENGTH_UPPER_BOUND"] = payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND]

    return refinements

x__extract_refinements_from_payload__mutmut_mutants : ClassVar[MutantDict] = {
'x__extract_refinements_from_payload__mutmut_1': x__extract_refinements_from_payload__mutmut_1, 
    'x__extract_refinements_from_payload__mutmut_2': x__extract_refinements_from_payload__mutmut_2, 
    'x__extract_refinements_from_payload__mutmut_3': x__extract_refinements_from_payload__mutmut_3, 
    'x__extract_refinements_from_payload__mutmut_4': x__extract_refinements_from_payload__mutmut_4, 
    'x__extract_refinements_from_payload__mutmut_5': x__extract_refinements_from_payload__mutmut_5, 
    'x__extract_refinements_from_payload__mutmut_6': x__extract_refinements_from_payload__mutmut_6, 
    'x__extract_refinements_from_payload__mutmut_7': x__extract_refinements_from_payload__mutmut_7, 
    'x__extract_refinements_from_payload__mutmut_8': x__extract_refinements_from_payload__mutmut_8, 
    'x__extract_refinements_from_payload__mutmut_9': x__extract_refinements_from_payload__mutmut_9, 
    'x__extract_refinements_from_payload__mutmut_10': x__extract_refinements_from_payload__mutmut_10, 
    'x__extract_refinements_from_payload__mutmut_11': x__extract_refinements_from_payload__mutmut_11, 
    'x__extract_refinements_from_payload__mutmut_12': x__extract_refinements_from_payload__mutmut_12, 
    'x__extract_refinements_from_payload__mutmut_13': x__extract_refinements_from_payload__mutmut_13, 
    'x__extract_refinements_from_payload__mutmut_14': x__extract_refinements_from_payload__mutmut_14, 
    'x__extract_refinements_from_payload__mutmut_15': x__extract_refinements_from_payload__mutmut_15, 
    'x__extract_refinements_from_payload__mutmut_16': x__extract_refinements_from_payload__mutmut_16, 
    'x__extract_refinements_from_payload__mutmut_17': x__extract_refinements_from_payload__mutmut_17, 
    'x__extract_refinements_from_payload__mutmut_18': x__extract_refinements_from_payload__mutmut_18, 
    'x__extract_refinements_from_payload__mutmut_19': x__extract_refinements_from_payload__mutmut_19, 
    'x__extract_refinements_from_payload__mutmut_20': x__extract_refinements_from_payload__mutmut_20, 
    'x__extract_refinements_from_payload__mutmut_21': x__extract_refinements_from_payload__mutmut_21, 
    'x__extract_refinements_from_payload__mutmut_22': x__extract_refinements_from_payload__mutmut_22, 
    'x__extract_refinements_from_payload__mutmut_23': x__extract_refinements_from_payload__mutmut_23, 
    'x__extract_refinements_from_payload__mutmut_24': x__extract_refinements_from_payload__mutmut_24, 
    'x__extract_refinements_from_payload__mutmut_25': x__extract_refinements_from_payload__mutmut_25, 
    'x__extract_refinements_from_payload__mutmut_26': x__extract_refinements_from_payload__mutmut_26, 
    'x__extract_refinements_from_payload__mutmut_27': x__extract_refinements_from_payload__mutmut_27, 
    'x__extract_refinements_from_payload__mutmut_28': x__extract_refinements_from_payload__mutmut_28, 
    'x__extract_refinements_from_payload__mutmut_29': x__extract_refinements_from_payload__mutmut_29, 
    'x__extract_refinements_from_payload__mutmut_30': x__extract_refinements_from_payload__mutmut_30, 
    'x__extract_refinements_from_payload__mutmut_31': x__extract_refinements_from_payload__mutmut_31
}

def _extract_refinements_from_payload(*args, **kwargs):
    result = _mutmut_trampoline(x__extract_refinements_from_payload__mutmut_orig, x__extract_refinements_from_payload__mutmut_mutants, args, kwargs)
    return result 

_extract_refinements_from_payload.__signature__ = _mutmut_signature(x__extract_refinements_from_payload__mutmut_orig)
x__extract_refinements_from_payload__mutmut_orig.__name__ = 'x__extract_refinements_from_payload'


def x__decode_refined_unknown_payload__mutmut_orig(data: bytes) -> RefinedUnknownValue:
    """Decode a refined unknown value from msgpack data."""
    try:
        payload = msgpack.unpackb(data, raw=MSGPACK_RAW_FALSE, strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE)
        refinements = _extract_refinements_from_payload(payload)
        return RefinedUnknownValue(**refinements)
    except Exception as e:
        error_message = ERR_DECODE_REFINED_UNKNOWN.format(error=e)
        raise DeserializationError(error_message) from e


def x__decode_refined_unknown_payload__mutmut_1(data: bytes) -> RefinedUnknownValue:
    """Decode a refined unknown value from msgpack data."""
    try:
        payload = None
        refinements = _extract_refinements_from_payload(payload)
        return RefinedUnknownValue(**refinements)
    except Exception as e:
        error_message = ERR_DECODE_REFINED_UNKNOWN.format(error=e)
        raise DeserializationError(error_message) from e


def x__decode_refined_unknown_payload__mutmut_2(data: bytes) -> RefinedUnknownValue:
    """Decode a refined unknown value from msgpack data."""
    try:
        payload = msgpack.unpackb(None, raw=MSGPACK_RAW_FALSE, strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE)
        refinements = _extract_refinements_from_payload(payload)
        return RefinedUnknownValue(**refinements)
    except Exception as e:
        error_message = ERR_DECODE_REFINED_UNKNOWN.format(error=e)
        raise DeserializationError(error_message) from e


def x__decode_refined_unknown_payload__mutmut_3(data: bytes) -> RefinedUnknownValue:
    """Decode a refined unknown value from msgpack data."""
    try:
        payload = msgpack.unpackb(data, raw=None, strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE)
        refinements = _extract_refinements_from_payload(payload)
        return RefinedUnknownValue(**refinements)
    except Exception as e:
        error_message = ERR_DECODE_REFINED_UNKNOWN.format(error=e)
        raise DeserializationError(error_message) from e


def x__decode_refined_unknown_payload__mutmut_4(data: bytes) -> RefinedUnknownValue:
    """Decode a refined unknown value from msgpack data."""
    try:
        payload = msgpack.unpackb(data, raw=MSGPACK_RAW_FALSE, strict_map_key=None)
        refinements = _extract_refinements_from_payload(payload)
        return RefinedUnknownValue(**refinements)
    except Exception as e:
        error_message = ERR_DECODE_REFINED_UNKNOWN.format(error=e)
        raise DeserializationError(error_message) from e


def x__decode_refined_unknown_payload__mutmut_5(data: bytes) -> RefinedUnknownValue:
    """Decode a refined unknown value from msgpack data."""
    try:
        payload = msgpack.unpackb(raw=MSGPACK_RAW_FALSE, strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE)
        refinements = _extract_refinements_from_payload(payload)
        return RefinedUnknownValue(**refinements)
    except Exception as e:
        error_message = ERR_DECODE_REFINED_UNKNOWN.format(error=e)
        raise DeserializationError(error_message) from e


def x__decode_refined_unknown_payload__mutmut_6(data: bytes) -> RefinedUnknownValue:
    """Decode a refined unknown value from msgpack data."""
    try:
        payload = msgpack.unpackb(data, strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE)
        refinements = _extract_refinements_from_payload(payload)
        return RefinedUnknownValue(**refinements)
    except Exception as e:
        error_message = ERR_DECODE_REFINED_UNKNOWN.format(error=e)
        raise DeserializationError(error_message) from e


def x__decode_refined_unknown_payload__mutmut_7(data: bytes) -> RefinedUnknownValue:
    """Decode a refined unknown value from msgpack data."""
    try:
        payload = msgpack.unpackb(data, raw=MSGPACK_RAW_FALSE, )
        refinements = _extract_refinements_from_payload(payload)
        return RefinedUnknownValue(**refinements)
    except Exception as e:
        error_message = ERR_DECODE_REFINED_UNKNOWN.format(error=e)
        raise DeserializationError(error_message) from e


def x__decode_refined_unknown_payload__mutmut_8(data: bytes) -> RefinedUnknownValue:
    """Decode a refined unknown value from msgpack data."""
    try:
        payload = msgpack.unpackb(data, raw=MSGPACK_RAW_FALSE, strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE)
        refinements = None
        return RefinedUnknownValue(**refinements)
    except Exception as e:
        error_message = ERR_DECODE_REFINED_UNKNOWN.format(error=e)
        raise DeserializationError(error_message) from e


def x__decode_refined_unknown_payload__mutmut_9(data: bytes) -> RefinedUnknownValue:
    """Decode a refined unknown value from msgpack data."""
    try:
        payload = msgpack.unpackb(data, raw=MSGPACK_RAW_FALSE, strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE)
        refinements = _extract_refinements_from_payload(None)
        return RefinedUnknownValue(**refinements)
    except Exception as e:
        error_message = ERR_DECODE_REFINED_UNKNOWN.format(error=e)
        raise DeserializationError(error_message) from e


def x__decode_refined_unknown_payload__mutmut_10(data: bytes) -> RefinedUnknownValue:
    """Decode a refined unknown value from msgpack data."""
    try:
        payload = msgpack.unpackb(data, raw=MSGPACK_RAW_FALSE, strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE)
        refinements = _extract_refinements_from_payload(payload)
        return RefinedUnknownValue(**refinements)
    except Exception as e:
        error_message = None
        raise DeserializationError(error_message) from e


def x__decode_refined_unknown_payload__mutmut_11(data: bytes) -> RefinedUnknownValue:
    """Decode a refined unknown value from msgpack data."""
    try:
        payload = msgpack.unpackb(data, raw=MSGPACK_RAW_FALSE, strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE)
        refinements = _extract_refinements_from_payload(payload)
        return RefinedUnknownValue(**refinements)
    except Exception as e:
        error_message = ERR_DECODE_REFINED_UNKNOWN.format(error=None)
        raise DeserializationError(error_message) from e


def x__decode_refined_unknown_payload__mutmut_12(data: bytes) -> RefinedUnknownValue:
    """Decode a refined unknown value from msgpack data."""
    try:
        payload = msgpack.unpackb(data, raw=MSGPACK_RAW_FALSE, strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE)
        refinements = _extract_refinements_from_payload(payload)
        return RefinedUnknownValue(**refinements)
    except Exception as e:
        error_message = ERR_DECODE_REFINED_UNKNOWN.format(error=e)
        raise DeserializationError(None) from e

x__decode_refined_unknown_payload__mutmut_mutants : ClassVar[MutantDict] = {
'x__decode_refined_unknown_payload__mutmut_1': x__decode_refined_unknown_payload__mutmut_1, 
    'x__decode_refined_unknown_payload__mutmut_2': x__decode_refined_unknown_payload__mutmut_2, 
    'x__decode_refined_unknown_payload__mutmut_3': x__decode_refined_unknown_payload__mutmut_3, 
    'x__decode_refined_unknown_payload__mutmut_4': x__decode_refined_unknown_payload__mutmut_4, 
    'x__decode_refined_unknown_payload__mutmut_5': x__decode_refined_unknown_payload__mutmut_5, 
    'x__decode_refined_unknown_payload__mutmut_6': x__decode_refined_unknown_payload__mutmut_6, 
    'x__decode_refined_unknown_payload__mutmut_7': x__decode_refined_unknown_payload__mutmut_7, 
    'x__decode_refined_unknown_payload__mutmut_8': x__decode_refined_unknown_payload__mutmut_8, 
    'x__decode_refined_unknown_payload__mutmut_9': x__decode_refined_unknown_payload__mutmut_9, 
    'x__decode_refined_unknown_payload__mutmut_10': x__decode_refined_unknown_payload__mutmut_10, 
    'x__decode_refined_unknown_payload__mutmut_11': x__decode_refined_unknown_payload__mutmut_11, 
    'x__decode_refined_unknown_payload__mutmut_12': x__decode_refined_unknown_payload__mutmut_12
}

def _decode_refined_unknown_payload(*args, **kwargs):
    result = _mutmut_trampoline(x__decode_refined_unknown_payload__mutmut_orig, x__decode_refined_unknown_payload__mutmut_mutants, args, kwargs)
    return result 

_decode_refined_unknown_payload.__signature__ = _mutmut_signature(x__decode_refined_unknown_payload__mutmut_orig)
x__decode_refined_unknown_payload__mutmut_orig.__name__ = 'x__decode_refined_unknown_payload'


def x__ext_hook__mutmut_orig(code: int, data: bytes) -> Any:
    match code:
        case 0:
            return UNREFINED_UNKNOWN
        case 12:
            return _decode_refined_unknown_payload(data)
        case _:
            # Per protocol, any other extension code is an unrefined unknown.
            return UNREFINED_UNKNOWN


def x__ext_hook__mutmut_1(code: int, data: bytes) -> Any:
    match code:
        case 12:
            return _decode_refined_unknown_payload(data)
        case _:
            # Per protocol, any other extension code is an unrefined unknown.
            return UNREFINED_UNKNOWN


def x__ext_hook__mutmut_2(code: int, data: bytes) -> Any:
    match code:
        case 0:
            return UNREFINED_UNKNOWN
        case _:
            # Per protocol, any other extension code is an unrefined unknown.
            return UNREFINED_UNKNOWN


def x__ext_hook__mutmut_3(code: int, data: bytes) -> Any:
    match code:
        case 0:
            return UNREFINED_UNKNOWN
        case 12:
            return _decode_refined_unknown_payload(data)


def x__ext_hook__mutmut_4(code: int, data: bytes) -> Any:
    match code:
        case 1:
            return UNREFINED_UNKNOWN
        case 12:
            return _decode_refined_unknown_payload(data)
        case _:
            # Per protocol, any other extension code is an unrefined unknown.
            return UNREFINED_UNKNOWN


def x__ext_hook__mutmut_5(code: int, data: bytes) -> Any:
    match code:
        case 0:
            return UNREFINED_UNKNOWN
        case 13:
            return _decode_refined_unknown_payload(data)
        case _:
            # Per protocol, any other extension code is an unrefined unknown.
            return UNREFINED_UNKNOWN


def x__ext_hook__mutmut_6(code: int, data: bytes) -> Any:
    match code:
        case 0:
            return UNREFINED_UNKNOWN
        case 12:
            return _decode_refined_unknown_payload(None)
        case _:
            # Per protocol, any other extension code is an unrefined unknown.
            return UNREFINED_UNKNOWN

x__ext_hook__mutmut_mutants : ClassVar[MutantDict] = {
'x__ext_hook__mutmut_1': x__ext_hook__mutmut_1, 
    'x__ext_hook__mutmut_2': x__ext_hook__mutmut_2, 
    'x__ext_hook__mutmut_3': x__ext_hook__mutmut_3, 
    'x__ext_hook__mutmut_4': x__ext_hook__mutmut_4, 
    'x__ext_hook__mutmut_5': x__ext_hook__mutmut_5, 
    'x__ext_hook__mutmut_6': x__ext_hook__mutmut_6
}

def _ext_hook(*args, **kwargs):
    result = _mutmut_trampoline(x__ext_hook__mutmut_orig, x__ext_hook__mutmut_mutants, args, kwargs)
    return result 

_ext_hook.__signature__ = _mutmut_signature(x__ext_hook__mutmut_orig)
x__ext_hook__mutmut_orig.__name__ = 'x__ext_hook'


def x__serialize_unknown__mutmut_orig(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_1(value: CtyValue[Any]) -> Any:
    if isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_2(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(None, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_3(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, None)
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_4(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_5(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, )
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_6(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"XXXX")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_7(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_8(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_9(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = None
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_10(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_11(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = None
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_12(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_13(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = None
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_14(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_15(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = None
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_16(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = None
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_17(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode(None), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_18(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(None).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_19(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("XXutf-8XX"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_20(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("UTF-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_21(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_22(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = None
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_23(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = None
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_24(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode(None), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_25(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(None).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_26(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("XXutf-8XX"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_27(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("UTF-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_28(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_29(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = None
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_30(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_31(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = None
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_32(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_33(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(None, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_34(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, None)
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_35(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_36(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, )
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_37(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"XXXX")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_38(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_39(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_40(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = None
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_41(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(None)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, packed_payload)


def x__serialize_unknown__mutmut_42(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(None, packed_payload)


def x__serialize_unknown__mutmut_43(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, None)


def x__serialize_unknown__mutmut_44(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(packed_payload)


def x__serialize_unknown__mutmut_45(value: CtyValue[Any]) -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None:
        payload[REFINEMENT_IS_KNOWN_NULL] = value.value.is_known_null
    if value.value.string_prefix is not None:
        payload[REFINEMENT_STRING_PREFIX] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[REFINEMENT_NUMBER_LOWER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[REFINEMENT_NUMBER_UPPER_BOUND] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_LOWER_BOUND] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None:
        payload[REFINEMENT_COLLECTION_LENGTH_UPPER_BOUND] = value.value.collection_length_upper_bound
    if not payload:
        return msgpack.ExtType(MSGPACK_EXT_TYPE_CTY, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(MSGPACK_EXT_TYPE_REFINED_UNKNOWN, )

x__serialize_unknown__mutmut_mutants : ClassVar[MutantDict] = {
'x__serialize_unknown__mutmut_1': x__serialize_unknown__mutmut_1, 
    'x__serialize_unknown__mutmut_2': x__serialize_unknown__mutmut_2, 
    'x__serialize_unknown__mutmut_3': x__serialize_unknown__mutmut_3, 
    'x__serialize_unknown__mutmut_4': x__serialize_unknown__mutmut_4, 
    'x__serialize_unknown__mutmut_5': x__serialize_unknown__mutmut_5, 
    'x__serialize_unknown__mutmut_6': x__serialize_unknown__mutmut_6, 
    'x__serialize_unknown__mutmut_7': x__serialize_unknown__mutmut_7, 
    'x__serialize_unknown__mutmut_8': x__serialize_unknown__mutmut_8, 
    'x__serialize_unknown__mutmut_9': x__serialize_unknown__mutmut_9, 
    'x__serialize_unknown__mutmut_10': x__serialize_unknown__mutmut_10, 
    'x__serialize_unknown__mutmut_11': x__serialize_unknown__mutmut_11, 
    'x__serialize_unknown__mutmut_12': x__serialize_unknown__mutmut_12, 
    'x__serialize_unknown__mutmut_13': x__serialize_unknown__mutmut_13, 
    'x__serialize_unknown__mutmut_14': x__serialize_unknown__mutmut_14, 
    'x__serialize_unknown__mutmut_15': x__serialize_unknown__mutmut_15, 
    'x__serialize_unknown__mutmut_16': x__serialize_unknown__mutmut_16, 
    'x__serialize_unknown__mutmut_17': x__serialize_unknown__mutmut_17, 
    'x__serialize_unknown__mutmut_18': x__serialize_unknown__mutmut_18, 
    'x__serialize_unknown__mutmut_19': x__serialize_unknown__mutmut_19, 
    'x__serialize_unknown__mutmut_20': x__serialize_unknown__mutmut_20, 
    'x__serialize_unknown__mutmut_21': x__serialize_unknown__mutmut_21, 
    'x__serialize_unknown__mutmut_22': x__serialize_unknown__mutmut_22, 
    'x__serialize_unknown__mutmut_23': x__serialize_unknown__mutmut_23, 
    'x__serialize_unknown__mutmut_24': x__serialize_unknown__mutmut_24, 
    'x__serialize_unknown__mutmut_25': x__serialize_unknown__mutmut_25, 
    'x__serialize_unknown__mutmut_26': x__serialize_unknown__mutmut_26, 
    'x__serialize_unknown__mutmut_27': x__serialize_unknown__mutmut_27, 
    'x__serialize_unknown__mutmut_28': x__serialize_unknown__mutmut_28, 
    'x__serialize_unknown__mutmut_29': x__serialize_unknown__mutmut_29, 
    'x__serialize_unknown__mutmut_30': x__serialize_unknown__mutmut_30, 
    'x__serialize_unknown__mutmut_31': x__serialize_unknown__mutmut_31, 
    'x__serialize_unknown__mutmut_32': x__serialize_unknown__mutmut_32, 
    'x__serialize_unknown__mutmut_33': x__serialize_unknown__mutmut_33, 
    'x__serialize_unknown__mutmut_34': x__serialize_unknown__mutmut_34, 
    'x__serialize_unknown__mutmut_35': x__serialize_unknown__mutmut_35, 
    'x__serialize_unknown__mutmut_36': x__serialize_unknown__mutmut_36, 
    'x__serialize_unknown__mutmut_37': x__serialize_unknown__mutmut_37, 
    'x__serialize_unknown__mutmut_38': x__serialize_unknown__mutmut_38, 
    'x__serialize_unknown__mutmut_39': x__serialize_unknown__mutmut_39, 
    'x__serialize_unknown__mutmut_40': x__serialize_unknown__mutmut_40, 
    'x__serialize_unknown__mutmut_41': x__serialize_unknown__mutmut_41, 
    'x__serialize_unknown__mutmut_42': x__serialize_unknown__mutmut_42, 
    'x__serialize_unknown__mutmut_43': x__serialize_unknown__mutmut_43, 
    'x__serialize_unknown__mutmut_44': x__serialize_unknown__mutmut_44, 
    'x__serialize_unknown__mutmut_45': x__serialize_unknown__mutmut_45
}

def _serialize_unknown(*args, **kwargs):
    result = _mutmut_trampoline(x__serialize_unknown__mutmut_orig, x__serialize_unknown__mutmut_mutants, args, kwargs)
    return result 

_serialize_unknown.__signature__ = _mutmut_signature(x__serialize_unknown__mutmut_orig)
x__serialize_unknown__mutmut_orig.__name__ = 'x__serialize_unknown'


def x__serialize_dynamic__mutmut_orig(value: CtyValue[Any]) -> list[Any]:
    inner_value = value.value
    if not isinstance(inner_value, CtyValue):
        raise SerializationError(
            ERR_DYNAMIC_MALFORMED,
            value=value,
        )

    actual_type = inner_value.type
    serializable_inner = _convert_value_to_serializable(inner_value, actual_type)

    type_spec_json = encode_cty_type_to_wire_json(actual_type)
    type_spec_bytes = json.dumps(type_spec_json, separators=(",", ":")).encode("utf-8")
    return [type_spec_bytes, serializable_inner]


def x__serialize_dynamic__mutmut_1(value: CtyValue[Any]) -> list[Any]:
    inner_value = None
    if not isinstance(inner_value, CtyValue):
        raise SerializationError(
            ERR_DYNAMIC_MALFORMED,
            value=value,
        )

    actual_type = inner_value.type
    serializable_inner = _convert_value_to_serializable(inner_value, actual_type)

    type_spec_json = encode_cty_type_to_wire_json(actual_type)
    type_spec_bytes = json.dumps(type_spec_json, separators=(",", ":")).encode("utf-8")
    return [type_spec_bytes, serializable_inner]


def x__serialize_dynamic__mutmut_2(value: CtyValue[Any]) -> list[Any]:
    inner_value = value.value
    if isinstance(inner_value, CtyValue):
        raise SerializationError(
            ERR_DYNAMIC_MALFORMED,
            value=value,
        )

    actual_type = inner_value.type
    serializable_inner = _convert_value_to_serializable(inner_value, actual_type)

    type_spec_json = encode_cty_type_to_wire_json(actual_type)
    type_spec_bytes = json.dumps(type_spec_json, separators=(",", ":")).encode("utf-8")
    return [type_spec_bytes, serializable_inner]


def x__serialize_dynamic__mutmut_3(value: CtyValue[Any]) -> list[Any]:
    inner_value = value.value
    if not isinstance(inner_value, CtyValue):
        raise SerializationError(
            None,
            value=value,
        )

    actual_type = inner_value.type
    serializable_inner = _convert_value_to_serializable(inner_value, actual_type)

    type_spec_json = encode_cty_type_to_wire_json(actual_type)
    type_spec_bytes = json.dumps(type_spec_json, separators=(",", ":")).encode("utf-8")
    return [type_spec_bytes, serializable_inner]


def x__serialize_dynamic__mutmut_4(value: CtyValue[Any]) -> list[Any]:
    inner_value = value.value
    if not isinstance(inner_value, CtyValue):
        raise SerializationError(
            ERR_DYNAMIC_MALFORMED,
            value=None,
        )

    actual_type = inner_value.type
    serializable_inner = _convert_value_to_serializable(inner_value, actual_type)

    type_spec_json = encode_cty_type_to_wire_json(actual_type)
    type_spec_bytes = json.dumps(type_spec_json, separators=(",", ":")).encode("utf-8")
    return [type_spec_bytes, serializable_inner]


def x__serialize_dynamic__mutmut_5(value: CtyValue[Any]) -> list[Any]:
    inner_value = value.value
    if not isinstance(inner_value, CtyValue):
        raise SerializationError(
            value=value,
        )

    actual_type = inner_value.type
    serializable_inner = _convert_value_to_serializable(inner_value, actual_type)

    type_spec_json = encode_cty_type_to_wire_json(actual_type)
    type_spec_bytes = json.dumps(type_spec_json, separators=(",", ":")).encode("utf-8")
    return [type_spec_bytes, serializable_inner]


def x__serialize_dynamic__mutmut_6(value: CtyValue[Any]) -> list[Any]:
    inner_value = value.value
    if not isinstance(inner_value, CtyValue):
        raise SerializationError(
            ERR_DYNAMIC_MALFORMED,
            )

    actual_type = inner_value.type
    serializable_inner = _convert_value_to_serializable(inner_value, actual_type)

    type_spec_json = encode_cty_type_to_wire_json(actual_type)
    type_spec_bytes = json.dumps(type_spec_json, separators=(",", ":")).encode("utf-8")
    return [type_spec_bytes, serializable_inner]


def x__serialize_dynamic__mutmut_7(value: CtyValue[Any]) -> list[Any]:
    inner_value = value.value
    if not isinstance(inner_value, CtyValue):
        raise SerializationError(
            ERR_DYNAMIC_MALFORMED,
            value=value,
        )

    actual_type = None
    serializable_inner = _convert_value_to_serializable(inner_value, actual_type)

    type_spec_json = encode_cty_type_to_wire_json(actual_type)
    type_spec_bytes = json.dumps(type_spec_json, separators=(",", ":")).encode("utf-8")
    return [type_spec_bytes, serializable_inner]


def x__serialize_dynamic__mutmut_8(value: CtyValue[Any]) -> list[Any]:
    inner_value = value.value
    if not isinstance(inner_value, CtyValue):
        raise SerializationError(
            ERR_DYNAMIC_MALFORMED,
            value=value,
        )

    actual_type = inner_value.type
    serializable_inner = None

    type_spec_json = encode_cty_type_to_wire_json(actual_type)
    type_spec_bytes = json.dumps(type_spec_json, separators=(",", ":")).encode("utf-8")
    return [type_spec_bytes, serializable_inner]


def x__serialize_dynamic__mutmut_9(value: CtyValue[Any]) -> list[Any]:
    inner_value = value.value
    if not isinstance(inner_value, CtyValue):
        raise SerializationError(
            ERR_DYNAMIC_MALFORMED,
            value=value,
        )

    actual_type = inner_value.type
    serializable_inner = _convert_value_to_serializable(None, actual_type)

    type_spec_json = encode_cty_type_to_wire_json(actual_type)
    type_spec_bytes = json.dumps(type_spec_json, separators=(",", ":")).encode("utf-8")
    return [type_spec_bytes, serializable_inner]


def x__serialize_dynamic__mutmut_10(value: CtyValue[Any]) -> list[Any]:
    inner_value = value.value
    if not isinstance(inner_value, CtyValue):
        raise SerializationError(
            ERR_DYNAMIC_MALFORMED,
            value=value,
        )

    actual_type = inner_value.type
    serializable_inner = _convert_value_to_serializable(inner_value, None)

    type_spec_json = encode_cty_type_to_wire_json(actual_type)
    type_spec_bytes = json.dumps(type_spec_json, separators=(",", ":")).encode("utf-8")
    return [type_spec_bytes, serializable_inner]


def x__serialize_dynamic__mutmut_11(value: CtyValue[Any]) -> list[Any]:
    inner_value = value.value
    if not isinstance(inner_value, CtyValue):
        raise SerializationError(
            ERR_DYNAMIC_MALFORMED,
            value=value,
        )

    actual_type = inner_value.type
    serializable_inner = _convert_value_to_serializable(actual_type)

    type_spec_json = encode_cty_type_to_wire_json(actual_type)
    type_spec_bytes = json.dumps(type_spec_json, separators=(",", ":")).encode("utf-8")
    return [type_spec_bytes, serializable_inner]


def x__serialize_dynamic__mutmut_12(value: CtyValue[Any]) -> list[Any]:
    inner_value = value.value
    if not isinstance(inner_value, CtyValue):
        raise SerializationError(
            ERR_DYNAMIC_MALFORMED,
            value=value,
        )

    actual_type = inner_value.type
    serializable_inner = _convert_value_to_serializable(inner_value, )

    type_spec_json = encode_cty_type_to_wire_json(actual_type)
    type_spec_bytes = json.dumps(type_spec_json, separators=(",", ":")).encode("utf-8")
    return [type_spec_bytes, serializable_inner]


def x__serialize_dynamic__mutmut_13(value: CtyValue[Any]) -> list[Any]:
    inner_value = value.value
    if not isinstance(inner_value, CtyValue):
        raise SerializationError(
            ERR_DYNAMIC_MALFORMED,
            value=value,
        )

    actual_type = inner_value.type
    serializable_inner = _convert_value_to_serializable(inner_value, actual_type)

    type_spec_json = None
    type_spec_bytes = json.dumps(type_spec_json, separators=(",", ":")).encode("utf-8")
    return [type_spec_bytes, serializable_inner]


def x__serialize_dynamic__mutmut_14(value: CtyValue[Any]) -> list[Any]:
    inner_value = value.value
    if not isinstance(inner_value, CtyValue):
        raise SerializationError(
            ERR_DYNAMIC_MALFORMED,
            value=value,
        )

    actual_type = inner_value.type
    serializable_inner = _convert_value_to_serializable(inner_value, actual_type)

    type_spec_json = encode_cty_type_to_wire_json(None)
    type_spec_bytes = json.dumps(type_spec_json, separators=(",", ":")).encode("utf-8")
    return [type_spec_bytes, serializable_inner]


def x__serialize_dynamic__mutmut_15(value: CtyValue[Any]) -> list[Any]:
    inner_value = value.value
    if not isinstance(inner_value, CtyValue):
        raise SerializationError(
            ERR_DYNAMIC_MALFORMED,
            value=value,
        )

    actual_type = inner_value.type
    serializable_inner = _convert_value_to_serializable(inner_value, actual_type)

    type_spec_json = encode_cty_type_to_wire_json(actual_type)
    type_spec_bytes = None
    return [type_spec_bytes, serializable_inner]


def x__serialize_dynamic__mutmut_16(value: CtyValue[Any]) -> list[Any]:
    inner_value = value.value
    if not isinstance(inner_value, CtyValue):
        raise SerializationError(
            ERR_DYNAMIC_MALFORMED,
            value=value,
        )

    actual_type = inner_value.type
    serializable_inner = _convert_value_to_serializable(inner_value, actual_type)

    type_spec_json = encode_cty_type_to_wire_json(actual_type)
    type_spec_bytes = json.dumps(type_spec_json, separators=(",", ":")).encode(None)
    return [type_spec_bytes, serializable_inner]


def x__serialize_dynamic__mutmut_17(value: CtyValue[Any]) -> list[Any]:
    inner_value = value.value
    if not isinstance(inner_value, CtyValue):
        raise SerializationError(
            ERR_DYNAMIC_MALFORMED,
            value=value,
        )

    actual_type = inner_value.type
    serializable_inner = _convert_value_to_serializable(inner_value, actual_type)

    type_spec_json = encode_cty_type_to_wire_json(actual_type)
    type_spec_bytes = json.dumps(None, separators=(",", ":")).encode("utf-8")
    return [type_spec_bytes, serializable_inner]


def x__serialize_dynamic__mutmut_18(value: CtyValue[Any]) -> list[Any]:
    inner_value = value.value
    if not isinstance(inner_value, CtyValue):
        raise SerializationError(
            ERR_DYNAMIC_MALFORMED,
            value=value,
        )

    actual_type = inner_value.type
    serializable_inner = _convert_value_to_serializable(inner_value, actual_type)

    type_spec_json = encode_cty_type_to_wire_json(actual_type)
    type_spec_bytes = json.dumps(type_spec_json, separators=None).encode("utf-8")
    return [type_spec_bytes, serializable_inner]


def x__serialize_dynamic__mutmut_19(value: CtyValue[Any]) -> list[Any]:
    inner_value = value.value
    if not isinstance(inner_value, CtyValue):
        raise SerializationError(
            ERR_DYNAMIC_MALFORMED,
            value=value,
        )

    actual_type = inner_value.type
    serializable_inner = _convert_value_to_serializable(inner_value, actual_type)

    type_spec_json = encode_cty_type_to_wire_json(actual_type)
    type_spec_bytes = json.dumps(separators=(",", ":")).encode("utf-8")
    return [type_spec_bytes, serializable_inner]


def x__serialize_dynamic__mutmut_20(value: CtyValue[Any]) -> list[Any]:
    inner_value = value.value
    if not isinstance(inner_value, CtyValue):
        raise SerializationError(
            ERR_DYNAMIC_MALFORMED,
            value=value,
        )

    actual_type = inner_value.type
    serializable_inner = _convert_value_to_serializable(inner_value, actual_type)

    type_spec_json = encode_cty_type_to_wire_json(actual_type)
    type_spec_bytes = json.dumps(type_spec_json, ).encode("utf-8")
    return [type_spec_bytes, serializable_inner]


def x__serialize_dynamic__mutmut_21(value: CtyValue[Any]) -> list[Any]:
    inner_value = value.value
    if not isinstance(inner_value, CtyValue):
        raise SerializationError(
            ERR_DYNAMIC_MALFORMED,
            value=value,
        )

    actual_type = inner_value.type
    serializable_inner = _convert_value_to_serializable(inner_value, actual_type)

    type_spec_json = encode_cty_type_to_wire_json(actual_type)
    type_spec_bytes = json.dumps(type_spec_json, separators=("XX,XX", ":")).encode("utf-8")
    return [type_spec_bytes, serializable_inner]


def x__serialize_dynamic__mutmut_22(value: CtyValue[Any]) -> list[Any]:
    inner_value = value.value
    if not isinstance(inner_value, CtyValue):
        raise SerializationError(
            ERR_DYNAMIC_MALFORMED,
            value=value,
        )

    actual_type = inner_value.type
    serializable_inner = _convert_value_to_serializable(inner_value, actual_type)

    type_spec_json = encode_cty_type_to_wire_json(actual_type)
    type_spec_bytes = json.dumps(type_spec_json, separators=(",", "XX:XX")).encode("utf-8")
    return [type_spec_bytes, serializable_inner]


def x__serialize_dynamic__mutmut_23(value: CtyValue[Any]) -> list[Any]:
    inner_value = value.value
    if not isinstance(inner_value, CtyValue):
        raise SerializationError(
            ERR_DYNAMIC_MALFORMED,
            value=value,
        )

    actual_type = inner_value.type
    serializable_inner = _convert_value_to_serializable(inner_value, actual_type)

    type_spec_json = encode_cty_type_to_wire_json(actual_type)
    type_spec_bytes = json.dumps(type_spec_json, separators=(",", ":")).encode("XXutf-8XX")
    return [type_spec_bytes, serializable_inner]


def x__serialize_dynamic__mutmut_24(value: CtyValue[Any]) -> list[Any]:
    inner_value = value.value
    if not isinstance(inner_value, CtyValue):
        raise SerializationError(
            ERR_DYNAMIC_MALFORMED,
            value=value,
        )

    actual_type = inner_value.type
    serializable_inner = _convert_value_to_serializable(inner_value, actual_type)

    type_spec_json = encode_cty_type_to_wire_json(actual_type)
    type_spec_bytes = json.dumps(type_spec_json, separators=(",", ":")).encode("UTF-8")
    return [type_spec_bytes, serializable_inner]

x__serialize_dynamic__mutmut_mutants : ClassVar[MutantDict] = {
'x__serialize_dynamic__mutmut_1': x__serialize_dynamic__mutmut_1, 
    'x__serialize_dynamic__mutmut_2': x__serialize_dynamic__mutmut_2, 
    'x__serialize_dynamic__mutmut_3': x__serialize_dynamic__mutmut_3, 
    'x__serialize_dynamic__mutmut_4': x__serialize_dynamic__mutmut_4, 
    'x__serialize_dynamic__mutmut_5': x__serialize_dynamic__mutmut_5, 
    'x__serialize_dynamic__mutmut_6': x__serialize_dynamic__mutmut_6, 
    'x__serialize_dynamic__mutmut_7': x__serialize_dynamic__mutmut_7, 
    'x__serialize_dynamic__mutmut_8': x__serialize_dynamic__mutmut_8, 
    'x__serialize_dynamic__mutmut_9': x__serialize_dynamic__mutmut_9, 
    'x__serialize_dynamic__mutmut_10': x__serialize_dynamic__mutmut_10, 
    'x__serialize_dynamic__mutmut_11': x__serialize_dynamic__mutmut_11, 
    'x__serialize_dynamic__mutmut_12': x__serialize_dynamic__mutmut_12, 
    'x__serialize_dynamic__mutmut_13': x__serialize_dynamic__mutmut_13, 
    'x__serialize_dynamic__mutmut_14': x__serialize_dynamic__mutmut_14, 
    'x__serialize_dynamic__mutmut_15': x__serialize_dynamic__mutmut_15, 
    'x__serialize_dynamic__mutmut_16': x__serialize_dynamic__mutmut_16, 
    'x__serialize_dynamic__mutmut_17': x__serialize_dynamic__mutmut_17, 
    'x__serialize_dynamic__mutmut_18': x__serialize_dynamic__mutmut_18, 
    'x__serialize_dynamic__mutmut_19': x__serialize_dynamic__mutmut_19, 
    'x__serialize_dynamic__mutmut_20': x__serialize_dynamic__mutmut_20, 
    'x__serialize_dynamic__mutmut_21': x__serialize_dynamic__mutmut_21, 
    'x__serialize_dynamic__mutmut_22': x__serialize_dynamic__mutmut_22, 
    'x__serialize_dynamic__mutmut_23': x__serialize_dynamic__mutmut_23, 
    'x__serialize_dynamic__mutmut_24': x__serialize_dynamic__mutmut_24
}

def _serialize_dynamic(*args, **kwargs):
    result = _mutmut_trampoline(x__serialize_dynamic__mutmut_orig, x__serialize_dynamic__mutmut_mutants, args, kwargs)
    return result 

_serialize_dynamic.__signature__ = _mutmut_signature(x__serialize_dynamic__mutmut_orig)
x__serialize_dynamic__mutmut_orig.__name__ = 'x__serialize_dynamic'


def x__serialize_object_value__mutmut_orig(inner_val: Any, schema: CtyObject) -> dict[str, Any]:
    """Serialize a CtyObject value."""
    if not isinstance(inner_val, dict):
        raise TypeError(ERR_VALUE_FOR_OBJECT)
    return {
        k: _convert_value_to_serializable(v, schema.attribute_types[k]) for k, v in sorted(inner_val.items())
    }


def x__serialize_object_value__mutmut_1(inner_val: Any, schema: CtyObject) -> dict[str, Any]:
    """Serialize a CtyObject value."""
    if isinstance(inner_val, dict):
        raise TypeError(ERR_VALUE_FOR_OBJECT)
    return {
        k: _convert_value_to_serializable(v, schema.attribute_types[k]) for k, v in sorted(inner_val.items())
    }


def x__serialize_object_value__mutmut_2(inner_val: Any, schema: CtyObject) -> dict[str, Any]:
    """Serialize a CtyObject value."""
    if not isinstance(inner_val, dict):
        raise TypeError(None)
    return {
        k: _convert_value_to_serializable(v, schema.attribute_types[k]) for k, v in sorted(inner_val.items())
    }


def x__serialize_object_value__mutmut_3(inner_val: Any, schema: CtyObject) -> dict[str, Any]:
    """Serialize a CtyObject value."""
    if not isinstance(inner_val, dict):
        raise TypeError(ERR_VALUE_FOR_OBJECT)
    return {
        k: _convert_value_to_serializable(None, schema.attribute_types[k]) for k, v in sorted(inner_val.items())
    }


def x__serialize_object_value__mutmut_4(inner_val: Any, schema: CtyObject) -> dict[str, Any]:
    """Serialize a CtyObject value."""
    if not isinstance(inner_val, dict):
        raise TypeError(ERR_VALUE_FOR_OBJECT)
    return {
        k: _convert_value_to_serializable(v, None) for k, v in sorted(inner_val.items())
    }


def x__serialize_object_value__mutmut_5(inner_val: Any, schema: CtyObject) -> dict[str, Any]:
    """Serialize a CtyObject value."""
    if not isinstance(inner_val, dict):
        raise TypeError(ERR_VALUE_FOR_OBJECT)
    return {
        k: _convert_value_to_serializable(schema.attribute_types[k]) for k, v in sorted(inner_val.items())
    }


def x__serialize_object_value__mutmut_6(inner_val: Any, schema: CtyObject) -> dict[str, Any]:
    """Serialize a CtyObject value."""
    if not isinstance(inner_val, dict):
        raise TypeError(ERR_VALUE_FOR_OBJECT)
    return {
        k: _convert_value_to_serializable(v, ) for k, v in sorted(inner_val.items())
    }


def x__serialize_object_value__mutmut_7(inner_val: Any, schema: CtyObject) -> dict[str, Any]:
    """Serialize a CtyObject value."""
    if not isinstance(inner_val, dict):
        raise TypeError(ERR_VALUE_FOR_OBJECT)
    return {
        k: _convert_value_to_serializable(v, schema.attribute_types[k]) for k, v in sorted(None)
    }

x__serialize_object_value__mutmut_mutants : ClassVar[MutantDict] = {
'x__serialize_object_value__mutmut_1': x__serialize_object_value__mutmut_1, 
    'x__serialize_object_value__mutmut_2': x__serialize_object_value__mutmut_2, 
    'x__serialize_object_value__mutmut_3': x__serialize_object_value__mutmut_3, 
    'x__serialize_object_value__mutmut_4': x__serialize_object_value__mutmut_4, 
    'x__serialize_object_value__mutmut_5': x__serialize_object_value__mutmut_5, 
    'x__serialize_object_value__mutmut_6': x__serialize_object_value__mutmut_6, 
    'x__serialize_object_value__mutmut_7': x__serialize_object_value__mutmut_7
}

def _serialize_object_value(*args, **kwargs):
    result = _mutmut_trampoline(x__serialize_object_value__mutmut_orig, x__serialize_object_value__mutmut_mutants, args, kwargs)
    return result 

_serialize_object_value.__signature__ = _mutmut_signature(x__serialize_object_value__mutmut_orig)
x__serialize_object_value__mutmut_orig.__name__ = 'x__serialize_object_value'


def x__serialize_map_value__mutmut_orig(inner_val: Any, schema: CtyMap[Any]) -> dict[str, Any]:
    """Serialize a CtyMap value."""
    if not isinstance(inner_val, dict):
        raise TypeError(ERR_VALUE_FOR_MAP)
    return {k: _convert_value_to_serializable(v, schema.element_type) for k, v in sorted(inner_val.items())}


def x__serialize_map_value__mutmut_1(inner_val: Any, schema: CtyMap[Any]) -> dict[str, Any]:
    """Serialize a CtyMap value."""
    if isinstance(inner_val, dict):
        raise TypeError(ERR_VALUE_FOR_MAP)
    return {k: _convert_value_to_serializable(v, schema.element_type) for k, v in sorted(inner_val.items())}


def x__serialize_map_value__mutmut_2(inner_val: Any, schema: CtyMap[Any]) -> dict[str, Any]:
    """Serialize a CtyMap value."""
    if not isinstance(inner_val, dict):
        raise TypeError(None)
    return {k: _convert_value_to_serializable(v, schema.element_type) for k, v in sorted(inner_val.items())}


def x__serialize_map_value__mutmut_3(inner_val: Any, schema: CtyMap[Any]) -> dict[str, Any]:
    """Serialize a CtyMap value."""
    if not isinstance(inner_val, dict):
        raise TypeError(ERR_VALUE_FOR_MAP)
    return {k: _convert_value_to_serializable(None, schema.element_type) for k, v in sorted(inner_val.items())}


def x__serialize_map_value__mutmut_4(inner_val: Any, schema: CtyMap[Any]) -> dict[str, Any]:
    """Serialize a CtyMap value."""
    if not isinstance(inner_val, dict):
        raise TypeError(ERR_VALUE_FOR_MAP)
    return {k: _convert_value_to_serializable(v, None) for k, v in sorted(inner_val.items())}


def x__serialize_map_value__mutmut_5(inner_val: Any, schema: CtyMap[Any]) -> dict[str, Any]:
    """Serialize a CtyMap value."""
    if not isinstance(inner_val, dict):
        raise TypeError(ERR_VALUE_FOR_MAP)
    return {k: _convert_value_to_serializable(schema.element_type) for k, v in sorted(inner_val.items())}


def x__serialize_map_value__mutmut_6(inner_val: Any, schema: CtyMap[Any]) -> dict[str, Any]:
    """Serialize a CtyMap value."""
    if not isinstance(inner_val, dict):
        raise TypeError(ERR_VALUE_FOR_MAP)
    return {k: _convert_value_to_serializable(v, ) for k, v in sorted(inner_val.items())}


def x__serialize_map_value__mutmut_7(inner_val: Any, schema: CtyMap[Any]) -> dict[str, Any]:
    """Serialize a CtyMap value."""
    if not isinstance(inner_val, dict):
        raise TypeError(ERR_VALUE_FOR_MAP)
    return {k: _convert_value_to_serializable(v, schema.element_type) for k, v in sorted(None)}

x__serialize_map_value__mutmut_mutants : ClassVar[MutantDict] = {
'x__serialize_map_value__mutmut_1': x__serialize_map_value__mutmut_1, 
    'x__serialize_map_value__mutmut_2': x__serialize_map_value__mutmut_2, 
    'x__serialize_map_value__mutmut_3': x__serialize_map_value__mutmut_3, 
    'x__serialize_map_value__mutmut_4': x__serialize_map_value__mutmut_4, 
    'x__serialize_map_value__mutmut_5': x__serialize_map_value__mutmut_5, 
    'x__serialize_map_value__mutmut_6': x__serialize_map_value__mutmut_6, 
    'x__serialize_map_value__mutmut_7': x__serialize_map_value__mutmut_7
}

def _serialize_map_value(*args, **kwargs):
    result = _mutmut_trampoline(x__serialize_map_value__mutmut_orig, x__serialize_map_value__mutmut_mutants, args, kwargs)
    return result 

_serialize_map_value.__signature__ = _mutmut_signature(x__serialize_map_value__mutmut_orig)
x__serialize_map_value__mutmut_orig.__name__ = 'x__serialize_map_value'


def x__serialize_collection_value__mutmut_orig(inner_val: Any, schema: CtyList[Any] | CtySet[Any]) -> list[Any]:
    """Serialize a CtyList or CtySet value."""
    if not hasattr(inner_val, "__iter__"):
        raise TypeError(ERR_VALUE_FOR_LIST_SET)
    items = (
        sorted(list(inner_val), key=lambda v: v._canonical_sort_key())
        if isinstance(schema, CtySet)
        else inner_val
    )
    return [_convert_value_to_serializable(item, schema.element_type) for item in items]


def x__serialize_collection_value__mutmut_1(inner_val: Any, schema: CtyList[Any] | CtySet[Any]) -> list[Any]:
    """Serialize a CtyList or CtySet value."""
    if hasattr(inner_val, "__iter__"):
        raise TypeError(ERR_VALUE_FOR_LIST_SET)
    items = (
        sorted(list(inner_val), key=lambda v: v._canonical_sort_key())
        if isinstance(schema, CtySet)
        else inner_val
    )
    return [_convert_value_to_serializable(item, schema.element_type) for item in items]


def x__serialize_collection_value__mutmut_2(inner_val: Any, schema: CtyList[Any] | CtySet[Any]) -> list[Any]:
    """Serialize a CtyList or CtySet value."""
    if not hasattr(None, "__iter__"):
        raise TypeError(ERR_VALUE_FOR_LIST_SET)
    items = (
        sorted(list(inner_val), key=lambda v: v._canonical_sort_key())
        if isinstance(schema, CtySet)
        else inner_val
    )
    return [_convert_value_to_serializable(item, schema.element_type) for item in items]


def x__serialize_collection_value__mutmut_3(inner_val: Any, schema: CtyList[Any] | CtySet[Any]) -> list[Any]:
    """Serialize a CtyList or CtySet value."""
    if not hasattr(inner_val, None):
        raise TypeError(ERR_VALUE_FOR_LIST_SET)
    items = (
        sorted(list(inner_val), key=lambda v: v._canonical_sort_key())
        if isinstance(schema, CtySet)
        else inner_val
    )
    return [_convert_value_to_serializable(item, schema.element_type) for item in items]


def x__serialize_collection_value__mutmut_4(inner_val: Any, schema: CtyList[Any] | CtySet[Any]) -> list[Any]:
    """Serialize a CtyList or CtySet value."""
    if not hasattr("__iter__"):
        raise TypeError(ERR_VALUE_FOR_LIST_SET)
    items = (
        sorted(list(inner_val), key=lambda v: v._canonical_sort_key())
        if isinstance(schema, CtySet)
        else inner_val
    )
    return [_convert_value_to_serializable(item, schema.element_type) for item in items]


def x__serialize_collection_value__mutmut_5(inner_val: Any, schema: CtyList[Any] | CtySet[Any]) -> list[Any]:
    """Serialize a CtyList or CtySet value."""
    if not hasattr(inner_val, ):
        raise TypeError(ERR_VALUE_FOR_LIST_SET)
    items = (
        sorted(list(inner_val), key=lambda v: v._canonical_sort_key())
        if isinstance(schema, CtySet)
        else inner_val
    )
    return [_convert_value_to_serializable(item, schema.element_type) for item in items]


def x__serialize_collection_value__mutmut_6(inner_val: Any, schema: CtyList[Any] | CtySet[Any]) -> list[Any]:
    """Serialize a CtyList or CtySet value."""
    if not hasattr(inner_val, "XX__iter__XX"):
        raise TypeError(ERR_VALUE_FOR_LIST_SET)
    items = (
        sorted(list(inner_val), key=lambda v: v._canonical_sort_key())
        if isinstance(schema, CtySet)
        else inner_val
    )
    return [_convert_value_to_serializable(item, schema.element_type) for item in items]


def x__serialize_collection_value__mutmut_7(inner_val: Any, schema: CtyList[Any] | CtySet[Any]) -> list[Any]:
    """Serialize a CtyList or CtySet value."""
    if not hasattr(inner_val, "__ITER__"):
        raise TypeError(ERR_VALUE_FOR_LIST_SET)
    items = (
        sorted(list(inner_val), key=lambda v: v._canonical_sort_key())
        if isinstance(schema, CtySet)
        else inner_val
    )
    return [_convert_value_to_serializable(item, schema.element_type) for item in items]


def x__serialize_collection_value__mutmut_8(inner_val: Any, schema: CtyList[Any] | CtySet[Any]) -> list[Any]:
    """Serialize a CtyList or CtySet value."""
    if not hasattr(inner_val, "__iter__"):
        raise TypeError(None)
    items = (
        sorted(list(inner_val), key=lambda v: v._canonical_sort_key())
        if isinstance(schema, CtySet)
        else inner_val
    )
    return [_convert_value_to_serializable(item, schema.element_type) for item in items]


def x__serialize_collection_value__mutmut_9(inner_val: Any, schema: CtyList[Any] | CtySet[Any]) -> list[Any]:
    """Serialize a CtyList or CtySet value."""
    if not hasattr(inner_val, "__iter__"):
        raise TypeError(ERR_VALUE_FOR_LIST_SET)
    items = None
    return [_convert_value_to_serializable(item, schema.element_type) for item in items]


def x__serialize_collection_value__mutmut_10(inner_val: Any, schema: CtyList[Any] | CtySet[Any]) -> list[Any]:
    """Serialize a CtyList or CtySet value."""
    if not hasattr(inner_val, "__iter__"):
        raise TypeError(ERR_VALUE_FOR_LIST_SET)
    items = (
        sorted(None, key=lambda v: v._canonical_sort_key())
        if isinstance(schema, CtySet)
        else inner_val
    )
    return [_convert_value_to_serializable(item, schema.element_type) for item in items]


def x__serialize_collection_value__mutmut_11(inner_val: Any, schema: CtyList[Any] | CtySet[Any]) -> list[Any]:
    """Serialize a CtyList or CtySet value."""
    if not hasattr(inner_val, "__iter__"):
        raise TypeError(ERR_VALUE_FOR_LIST_SET)
    items = (
        sorted(list(inner_val), key=None)
        if isinstance(schema, CtySet)
        else inner_val
    )
    return [_convert_value_to_serializable(item, schema.element_type) for item in items]


def x__serialize_collection_value__mutmut_12(inner_val: Any, schema: CtyList[Any] | CtySet[Any]) -> list[Any]:
    """Serialize a CtyList or CtySet value."""
    if not hasattr(inner_val, "__iter__"):
        raise TypeError(ERR_VALUE_FOR_LIST_SET)
    items = (
        sorted(key=lambda v: v._canonical_sort_key())
        if isinstance(schema, CtySet)
        else inner_val
    )
    return [_convert_value_to_serializable(item, schema.element_type) for item in items]


def x__serialize_collection_value__mutmut_13(inner_val: Any, schema: CtyList[Any] | CtySet[Any]) -> list[Any]:
    """Serialize a CtyList or CtySet value."""
    if not hasattr(inner_val, "__iter__"):
        raise TypeError(ERR_VALUE_FOR_LIST_SET)
    items = (
        sorted(list(inner_val), )
        if isinstance(schema, CtySet)
        else inner_val
    )
    return [_convert_value_to_serializable(item, schema.element_type) for item in items]


def x__serialize_collection_value__mutmut_14(inner_val: Any, schema: CtyList[Any] | CtySet[Any]) -> list[Any]:
    """Serialize a CtyList or CtySet value."""
    if not hasattr(inner_val, "__iter__"):
        raise TypeError(ERR_VALUE_FOR_LIST_SET)
    items = (
        sorted(list(None), key=lambda v: v._canonical_sort_key())
        if isinstance(schema, CtySet)
        else inner_val
    )
    return [_convert_value_to_serializable(item, schema.element_type) for item in items]


def x__serialize_collection_value__mutmut_15(inner_val: Any, schema: CtyList[Any] | CtySet[Any]) -> list[Any]:
    """Serialize a CtyList or CtySet value."""
    if not hasattr(inner_val, "__iter__"):
        raise TypeError(ERR_VALUE_FOR_LIST_SET)
    items = (
        sorted(list(inner_val), key=lambda v: None)
        if isinstance(schema, CtySet)
        else inner_val
    )
    return [_convert_value_to_serializable(item, schema.element_type) for item in items]


def x__serialize_collection_value__mutmut_16(inner_val: Any, schema: CtyList[Any] | CtySet[Any]) -> list[Any]:
    """Serialize a CtyList or CtySet value."""
    if not hasattr(inner_val, "__iter__"):
        raise TypeError(ERR_VALUE_FOR_LIST_SET)
    items = (
        sorted(list(inner_val), key=lambda v: v._canonical_sort_key())
        if isinstance(schema, CtySet)
        else inner_val
    )
    return [_convert_value_to_serializable(None, schema.element_type) for item in items]


def x__serialize_collection_value__mutmut_17(inner_val: Any, schema: CtyList[Any] | CtySet[Any]) -> list[Any]:
    """Serialize a CtyList or CtySet value."""
    if not hasattr(inner_val, "__iter__"):
        raise TypeError(ERR_VALUE_FOR_LIST_SET)
    items = (
        sorted(list(inner_val), key=lambda v: v._canonical_sort_key())
        if isinstance(schema, CtySet)
        else inner_val
    )
    return [_convert_value_to_serializable(item, None) for item in items]


def x__serialize_collection_value__mutmut_18(inner_val: Any, schema: CtyList[Any] | CtySet[Any]) -> list[Any]:
    """Serialize a CtyList or CtySet value."""
    if not hasattr(inner_val, "__iter__"):
        raise TypeError(ERR_VALUE_FOR_LIST_SET)
    items = (
        sorted(list(inner_val), key=lambda v: v._canonical_sort_key())
        if isinstance(schema, CtySet)
        else inner_val
    )
    return [_convert_value_to_serializable(schema.element_type) for item in items]


def x__serialize_collection_value__mutmut_19(inner_val: Any, schema: CtyList[Any] | CtySet[Any]) -> list[Any]:
    """Serialize a CtyList or CtySet value."""
    if not hasattr(inner_val, "__iter__"):
        raise TypeError(ERR_VALUE_FOR_LIST_SET)
    items = (
        sorted(list(inner_val), key=lambda v: v._canonical_sort_key())
        if isinstance(schema, CtySet)
        else inner_val
    )
    return [_convert_value_to_serializable(item, ) for item in items]

x__serialize_collection_value__mutmut_mutants : ClassVar[MutantDict] = {
'x__serialize_collection_value__mutmut_1': x__serialize_collection_value__mutmut_1, 
    'x__serialize_collection_value__mutmut_2': x__serialize_collection_value__mutmut_2, 
    'x__serialize_collection_value__mutmut_3': x__serialize_collection_value__mutmut_3, 
    'x__serialize_collection_value__mutmut_4': x__serialize_collection_value__mutmut_4, 
    'x__serialize_collection_value__mutmut_5': x__serialize_collection_value__mutmut_5, 
    'x__serialize_collection_value__mutmut_6': x__serialize_collection_value__mutmut_6, 
    'x__serialize_collection_value__mutmut_7': x__serialize_collection_value__mutmut_7, 
    'x__serialize_collection_value__mutmut_8': x__serialize_collection_value__mutmut_8, 
    'x__serialize_collection_value__mutmut_9': x__serialize_collection_value__mutmut_9, 
    'x__serialize_collection_value__mutmut_10': x__serialize_collection_value__mutmut_10, 
    'x__serialize_collection_value__mutmut_11': x__serialize_collection_value__mutmut_11, 
    'x__serialize_collection_value__mutmut_12': x__serialize_collection_value__mutmut_12, 
    'x__serialize_collection_value__mutmut_13': x__serialize_collection_value__mutmut_13, 
    'x__serialize_collection_value__mutmut_14': x__serialize_collection_value__mutmut_14, 
    'x__serialize_collection_value__mutmut_15': x__serialize_collection_value__mutmut_15, 
    'x__serialize_collection_value__mutmut_16': x__serialize_collection_value__mutmut_16, 
    'x__serialize_collection_value__mutmut_17': x__serialize_collection_value__mutmut_17, 
    'x__serialize_collection_value__mutmut_18': x__serialize_collection_value__mutmut_18, 
    'x__serialize_collection_value__mutmut_19': x__serialize_collection_value__mutmut_19
}

def _serialize_collection_value(*args, **kwargs):
    result = _mutmut_trampoline(x__serialize_collection_value__mutmut_orig, x__serialize_collection_value__mutmut_mutants, args, kwargs)
    return result 

_serialize_collection_value.__signature__ = _mutmut_signature(x__serialize_collection_value__mutmut_orig)
x__serialize_collection_value__mutmut_orig.__name__ = 'x__serialize_collection_value'


def x__serialize_tuple_value__mutmut_orig(inner_val: Any, schema: CtyTuple) -> list[Any]:
    """Serialize a CtyTuple value."""
    if not isinstance(inner_val, tuple):
        raise TypeError(ERR_VALUE_FOR_TUPLE)
    return [_convert_value_to_serializable(item, schema.element_types[i]) for i, item in enumerate(inner_val)]


def x__serialize_tuple_value__mutmut_1(inner_val: Any, schema: CtyTuple) -> list[Any]:
    """Serialize a CtyTuple value."""
    if isinstance(inner_val, tuple):
        raise TypeError(ERR_VALUE_FOR_TUPLE)
    return [_convert_value_to_serializable(item, schema.element_types[i]) for i, item in enumerate(inner_val)]


def x__serialize_tuple_value__mutmut_2(inner_val: Any, schema: CtyTuple) -> list[Any]:
    """Serialize a CtyTuple value."""
    if not isinstance(inner_val, tuple):
        raise TypeError(None)
    return [_convert_value_to_serializable(item, schema.element_types[i]) for i, item in enumerate(inner_val)]


def x__serialize_tuple_value__mutmut_3(inner_val: Any, schema: CtyTuple) -> list[Any]:
    """Serialize a CtyTuple value."""
    if not isinstance(inner_val, tuple):
        raise TypeError(ERR_VALUE_FOR_TUPLE)
    return [_convert_value_to_serializable(None, schema.element_types[i]) for i, item in enumerate(inner_val)]


def x__serialize_tuple_value__mutmut_4(inner_val: Any, schema: CtyTuple) -> list[Any]:
    """Serialize a CtyTuple value."""
    if not isinstance(inner_val, tuple):
        raise TypeError(ERR_VALUE_FOR_TUPLE)
    return [_convert_value_to_serializable(item, None) for i, item in enumerate(inner_val)]


def x__serialize_tuple_value__mutmut_5(inner_val: Any, schema: CtyTuple) -> list[Any]:
    """Serialize a CtyTuple value."""
    if not isinstance(inner_val, tuple):
        raise TypeError(ERR_VALUE_FOR_TUPLE)
    return [_convert_value_to_serializable(schema.element_types[i]) for i, item in enumerate(inner_val)]


def x__serialize_tuple_value__mutmut_6(inner_val: Any, schema: CtyTuple) -> list[Any]:
    """Serialize a CtyTuple value."""
    if not isinstance(inner_val, tuple):
        raise TypeError(ERR_VALUE_FOR_TUPLE)
    return [_convert_value_to_serializable(item, ) for i, item in enumerate(inner_val)]


def x__serialize_tuple_value__mutmut_7(inner_val: Any, schema: CtyTuple) -> list[Any]:
    """Serialize a CtyTuple value."""
    if not isinstance(inner_val, tuple):
        raise TypeError(ERR_VALUE_FOR_TUPLE)
    return [_convert_value_to_serializable(item, schema.element_types[i]) for i, item in enumerate(None)]

x__serialize_tuple_value__mutmut_mutants : ClassVar[MutantDict] = {
'x__serialize_tuple_value__mutmut_1': x__serialize_tuple_value__mutmut_1, 
    'x__serialize_tuple_value__mutmut_2': x__serialize_tuple_value__mutmut_2, 
    'x__serialize_tuple_value__mutmut_3': x__serialize_tuple_value__mutmut_3, 
    'x__serialize_tuple_value__mutmut_4': x__serialize_tuple_value__mutmut_4, 
    'x__serialize_tuple_value__mutmut_5': x__serialize_tuple_value__mutmut_5, 
    'x__serialize_tuple_value__mutmut_6': x__serialize_tuple_value__mutmut_6, 
    'x__serialize_tuple_value__mutmut_7': x__serialize_tuple_value__mutmut_7
}

def _serialize_tuple_value(*args, **kwargs):
    result = _mutmut_trampoline(x__serialize_tuple_value__mutmut_orig, x__serialize_tuple_value__mutmut_mutants, args, kwargs)
    return result 

_serialize_tuple_value.__signature__ = _mutmut_signature(x__serialize_tuple_value__mutmut_orig)
x__serialize_tuple_value__mutmut_orig.__name__ = 'x__serialize_tuple_value'


def x__serialize_decimal_value__mutmut_orig(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_1(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = None
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_2(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val / 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_3(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 2 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_4(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 != 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_5(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 1
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_6(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = None
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_7(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = None

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_8(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) or exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_9(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent > 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_10(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 1

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_11(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = None
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_12(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(None)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_13(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if +(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_14(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2 * 63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_15(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(3**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_16(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**64) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_17(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) < int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_18(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val <= 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_19(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2 * 63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_20(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 3**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_21(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**64:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_22(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(None)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_23(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = None

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_24(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(None)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_25(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = None
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_26(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(None)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_27(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = None

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_28(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(None)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_29(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "XX.XX" in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_30(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." not in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_31(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = None
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_32(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(None)[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_33(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split("XX.XX")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_34(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[2]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_35(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) >= 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_36(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 21:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_37(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = None

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_38(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(None)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_39(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val != roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_40(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str != float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(decimal_val)


def x__serialize_decimal_value__mutmut_41(decimal_val: Decimal) -> int | float | str:
    """Serialize a Decimal value for MessagePack encoding.

    Returns int for integers in int64 range, str for large integers, or float for non-integers.
    For non-integers, checks if float conversion would lose precision and encodes as string if so.
    """
    try:
        # Check if it's a whole number
        is_integer = decimal_val % 1 == 0
    except Exception:
        # For extremely large numbers, check using as_tuple()
        _sign, _digits, exponent = decimal_val.as_tuple()
        is_integer = isinstance(exponent, int) and exponent >= 0

    if is_integer:
        int_val = int(decimal_val)
        # MessagePack only supports int64 range natively (-2^63 to 2^63-1)
        # For values outside this range, encode as string (matches go-cty behavior)
        if -(2**63) <= int_val < 2**63:
            return int_val
        else:
            return str(int_val)
    else:
        # For non-integers, check if converting to float would lose precision
        # This matches go-cty's behavior of preserving exact decimal values
        float_val = float(decimal_val)

        # Strategy: Detect if the Decimal has float artifacts (from being created via Decimal(float))
        # vs being created from a clean source like Decimal("123.456789012345678901234567890").
        #
        # Float artifacts look like very long decimal expansions (e.g., ...28421709430404...)
        # that come from binary floating point representation.
        #
        # Key insight: If the decimal's string representation has many digits (>16 significant figures
        # after decimal point) and differs from the float's string representation, it's likely artifacts.

        original_str = str(decimal_val)
        float_str = str(float_val)

        # Check if the original string has float artifacts (very long precision)
        # Float64 has ~15-17 significant decimal digits. If we see more than 20 digits after
        # the decimal point, it's likely float representation artifacts.
        if "." in original_str:
            decimal_part = original_str.split(".")[1]
            if len(decimal_part) > 20:
                # This looks like float artifacts - just use the float
                return float_val

        # Convert float back to Decimal via its string representation to check precision loss
        roundtrip_decimal = Decimal(float_str)

        # If round-trip through float preserves the value, no precision loss
        if decimal_val == roundtrip_decimal:
            return float_val

        # If the string representations are equal, use float (they're equivalent)
        if original_str == float_str:
            return float_val

        # Otherwise, preserve as string to maintain precision beyond float64
        return str(None)

x__serialize_decimal_value__mutmut_mutants : ClassVar[MutantDict] = {
'x__serialize_decimal_value__mutmut_1': x__serialize_decimal_value__mutmut_1, 
    'x__serialize_decimal_value__mutmut_2': x__serialize_decimal_value__mutmut_2, 
    'x__serialize_decimal_value__mutmut_3': x__serialize_decimal_value__mutmut_3, 
    'x__serialize_decimal_value__mutmut_4': x__serialize_decimal_value__mutmut_4, 
    'x__serialize_decimal_value__mutmut_5': x__serialize_decimal_value__mutmut_5, 
    'x__serialize_decimal_value__mutmut_6': x__serialize_decimal_value__mutmut_6, 
    'x__serialize_decimal_value__mutmut_7': x__serialize_decimal_value__mutmut_7, 
    'x__serialize_decimal_value__mutmut_8': x__serialize_decimal_value__mutmut_8, 
    'x__serialize_decimal_value__mutmut_9': x__serialize_decimal_value__mutmut_9, 
    'x__serialize_decimal_value__mutmut_10': x__serialize_decimal_value__mutmut_10, 
    'x__serialize_decimal_value__mutmut_11': x__serialize_decimal_value__mutmut_11, 
    'x__serialize_decimal_value__mutmut_12': x__serialize_decimal_value__mutmut_12, 
    'x__serialize_decimal_value__mutmut_13': x__serialize_decimal_value__mutmut_13, 
    'x__serialize_decimal_value__mutmut_14': x__serialize_decimal_value__mutmut_14, 
    'x__serialize_decimal_value__mutmut_15': x__serialize_decimal_value__mutmut_15, 
    'x__serialize_decimal_value__mutmut_16': x__serialize_decimal_value__mutmut_16, 
    'x__serialize_decimal_value__mutmut_17': x__serialize_decimal_value__mutmut_17, 
    'x__serialize_decimal_value__mutmut_18': x__serialize_decimal_value__mutmut_18, 
    'x__serialize_decimal_value__mutmut_19': x__serialize_decimal_value__mutmut_19, 
    'x__serialize_decimal_value__mutmut_20': x__serialize_decimal_value__mutmut_20, 
    'x__serialize_decimal_value__mutmut_21': x__serialize_decimal_value__mutmut_21, 
    'x__serialize_decimal_value__mutmut_22': x__serialize_decimal_value__mutmut_22, 
    'x__serialize_decimal_value__mutmut_23': x__serialize_decimal_value__mutmut_23, 
    'x__serialize_decimal_value__mutmut_24': x__serialize_decimal_value__mutmut_24, 
    'x__serialize_decimal_value__mutmut_25': x__serialize_decimal_value__mutmut_25, 
    'x__serialize_decimal_value__mutmut_26': x__serialize_decimal_value__mutmut_26, 
    'x__serialize_decimal_value__mutmut_27': x__serialize_decimal_value__mutmut_27, 
    'x__serialize_decimal_value__mutmut_28': x__serialize_decimal_value__mutmut_28, 
    'x__serialize_decimal_value__mutmut_29': x__serialize_decimal_value__mutmut_29, 
    'x__serialize_decimal_value__mutmut_30': x__serialize_decimal_value__mutmut_30, 
    'x__serialize_decimal_value__mutmut_31': x__serialize_decimal_value__mutmut_31, 
    'x__serialize_decimal_value__mutmut_32': x__serialize_decimal_value__mutmut_32, 
    'x__serialize_decimal_value__mutmut_33': x__serialize_decimal_value__mutmut_33, 
    'x__serialize_decimal_value__mutmut_34': x__serialize_decimal_value__mutmut_34, 
    'x__serialize_decimal_value__mutmut_35': x__serialize_decimal_value__mutmut_35, 
    'x__serialize_decimal_value__mutmut_36': x__serialize_decimal_value__mutmut_36, 
    'x__serialize_decimal_value__mutmut_37': x__serialize_decimal_value__mutmut_37, 
    'x__serialize_decimal_value__mutmut_38': x__serialize_decimal_value__mutmut_38, 
    'x__serialize_decimal_value__mutmut_39': x__serialize_decimal_value__mutmut_39, 
    'x__serialize_decimal_value__mutmut_40': x__serialize_decimal_value__mutmut_40, 
    'x__serialize_decimal_value__mutmut_41': x__serialize_decimal_value__mutmut_41
}

def _serialize_decimal_value(*args, **kwargs):
    result = _mutmut_trampoline(x__serialize_decimal_value__mutmut_orig, x__serialize_decimal_value__mutmut_mutants, args, kwargs)
    return result 

_serialize_decimal_value.__signature__ = _mutmut_signature(x__serialize_decimal_value__mutmut_orig)
x__serialize_decimal_value__mutmut_orig.__name__ = 'x__serialize_decimal_value'


def x__convert_value_to_serializable__mutmut_orig(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(value)
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value)

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(inner_val, schema)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(inner_val, schema)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(CtyList[Any] | CtySet[Any], schema)  # type: ignore[redundant-cast]
        return _serialize_collection_value(inner_val, schema_narrowed)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(inner_val, schema)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def x__convert_value_to_serializable__mutmut_1(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if isinstance(value, CtyValue):
        value = schema.validate(value)
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value)

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(inner_val, schema)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(inner_val, schema)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(CtyList[Any] | CtySet[Any], schema)  # type: ignore[redundant-cast]
        return _serialize_collection_value(inner_val, schema_narrowed)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(inner_val, schema)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def x__convert_value_to_serializable__mutmut_2(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if not isinstance(value, CtyValue):
        value = None
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value)

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(inner_val, schema)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(inner_val, schema)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(CtyList[Any] | CtySet[Any], schema)  # type: ignore[redundant-cast]
        return _serialize_collection_value(inner_val, schema_narrowed)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(inner_val, schema)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def x__convert_value_to_serializable__mutmut_3(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(None)
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value)

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(inner_val, schema)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(inner_val, schema)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(CtyList[Any] | CtySet[Any], schema)  # type: ignore[redundant-cast]
        return _serialize_collection_value(inner_val, schema_narrowed)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(inner_val, schema)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def x__convert_value_to_serializable__mutmut_4(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(value)
    if value.is_unknown:
        return _serialize_unknown(None)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value)

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(inner_val, schema)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(inner_val, schema)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(CtyList[Any] | CtySet[Any], schema)  # type: ignore[redundant-cast]
        return _serialize_collection_value(inner_val, schema_narrowed)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(inner_val, schema)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def x__convert_value_to_serializable__mutmut_5(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(value)
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(None)

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(inner_val, schema)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(inner_val, schema)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(CtyList[Any] | CtySet[Any], schema)  # type: ignore[redundant-cast]
        return _serialize_collection_value(inner_val, schema_narrowed)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(inner_val, schema)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def x__convert_value_to_serializable__mutmut_6(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(value)
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value)

    inner_val = None
    if isinstance(schema, CtyObject):
        return _serialize_object_value(inner_val, schema)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(inner_val, schema)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(CtyList[Any] | CtySet[Any], schema)  # type: ignore[redundant-cast]
        return _serialize_collection_value(inner_val, schema_narrowed)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(inner_val, schema)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def x__convert_value_to_serializable__mutmut_7(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(value)
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value)

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(None, schema)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(inner_val, schema)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(CtyList[Any] | CtySet[Any], schema)  # type: ignore[redundant-cast]
        return _serialize_collection_value(inner_val, schema_narrowed)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(inner_val, schema)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def x__convert_value_to_serializable__mutmut_8(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(value)
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value)

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(inner_val, None)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(inner_val, schema)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(CtyList[Any] | CtySet[Any], schema)  # type: ignore[redundant-cast]
        return _serialize_collection_value(inner_val, schema_narrowed)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(inner_val, schema)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def x__convert_value_to_serializable__mutmut_9(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(value)
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value)

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(schema)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(inner_val, schema)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(CtyList[Any] | CtySet[Any], schema)  # type: ignore[redundant-cast]
        return _serialize_collection_value(inner_val, schema_narrowed)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(inner_val, schema)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def x__convert_value_to_serializable__mutmut_10(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(value)
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value)

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(inner_val, )
    if isinstance(schema, CtyMap):
        return _serialize_map_value(inner_val, schema)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(CtyList[Any] | CtySet[Any], schema)  # type: ignore[redundant-cast]
        return _serialize_collection_value(inner_val, schema_narrowed)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(inner_val, schema)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def x__convert_value_to_serializable__mutmut_11(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(value)
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value)

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(inner_val, schema)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(None, schema)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(CtyList[Any] | CtySet[Any], schema)  # type: ignore[redundant-cast]
        return _serialize_collection_value(inner_val, schema_narrowed)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(inner_val, schema)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def x__convert_value_to_serializable__mutmut_12(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(value)
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value)

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(inner_val, schema)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(inner_val, None)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(CtyList[Any] | CtySet[Any], schema)  # type: ignore[redundant-cast]
        return _serialize_collection_value(inner_val, schema_narrowed)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(inner_val, schema)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def x__convert_value_to_serializable__mutmut_13(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(value)
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value)

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(inner_val, schema)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(schema)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(CtyList[Any] | CtySet[Any], schema)  # type: ignore[redundant-cast]
        return _serialize_collection_value(inner_val, schema_narrowed)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(inner_val, schema)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def x__convert_value_to_serializable__mutmut_14(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(value)
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value)

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(inner_val, schema)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(inner_val, )
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(CtyList[Any] | CtySet[Any], schema)  # type: ignore[redundant-cast]
        return _serialize_collection_value(inner_val, schema_narrowed)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(inner_val, schema)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def x__convert_value_to_serializable__mutmut_15(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(value)
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value)

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(inner_val, schema)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(inner_val, schema)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = None  # type: ignore[redundant-cast]
        return _serialize_collection_value(inner_val, schema_narrowed)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(inner_val, schema)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def x__convert_value_to_serializable__mutmut_16(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(value)
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value)

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(inner_val, schema)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(inner_val, schema)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(None, schema)  # type: ignore[redundant-cast]
        return _serialize_collection_value(inner_val, schema_narrowed)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(inner_val, schema)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def x__convert_value_to_serializable__mutmut_17(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(value)
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value)

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(inner_val, schema)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(inner_val, schema)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(CtyList[Any] | CtySet[Any], None)  # type: ignore[redundant-cast]
        return _serialize_collection_value(inner_val, schema_narrowed)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(inner_val, schema)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def x__convert_value_to_serializable__mutmut_18(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(value)
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value)

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(inner_val, schema)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(inner_val, schema)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(schema)  # type: ignore[redundant-cast]
        return _serialize_collection_value(inner_val, schema_narrowed)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(inner_val, schema)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def x__convert_value_to_serializable__mutmut_19(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(value)
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value)

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(inner_val, schema)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(inner_val, schema)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(CtyList[Any] | CtySet[Any], )  # type: ignore[redundant-cast]
        return _serialize_collection_value(inner_val, schema_narrowed)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(inner_val, schema)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def x__convert_value_to_serializable__mutmut_20(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(value)
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value)

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(inner_val, schema)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(inner_val, schema)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(CtyList[Any] & CtySet[Any], schema)  # type: ignore[redundant-cast]
        return _serialize_collection_value(inner_val, schema_narrowed)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(inner_val, schema)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def x__convert_value_to_serializable__mutmut_21(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(value)
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value)

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(inner_val, schema)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(inner_val, schema)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(CtyList[Any] | CtySet[Any], schema)  # type: ignore[redundant-cast]
        return _serialize_collection_value(None, schema_narrowed)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(inner_val, schema)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def x__convert_value_to_serializable__mutmut_22(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(value)
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value)

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(inner_val, schema)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(inner_val, schema)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(CtyList[Any] | CtySet[Any], schema)  # type: ignore[redundant-cast]
        return _serialize_collection_value(inner_val, None)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(inner_val, schema)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def x__convert_value_to_serializable__mutmut_23(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(value)
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value)

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(inner_val, schema)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(inner_val, schema)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(CtyList[Any] | CtySet[Any], schema)  # type: ignore[redundant-cast]
        return _serialize_collection_value(schema_narrowed)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(inner_val, schema)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def x__convert_value_to_serializable__mutmut_24(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(value)
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value)

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(inner_val, schema)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(inner_val, schema)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(CtyList[Any] | CtySet[Any], schema)  # type: ignore[redundant-cast]
        return _serialize_collection_value(inner_val, )
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(inner_val, schema)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def x__convert_value_to_serializable__mutmut_25(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(value)
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value)

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(inner_val, schema)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(inner_val, schema)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(CtyList[Any] | CtySet[Any], schema)  # type: ignore[redundant-cast]
        return _serialize_collection_value(inner_val, schema_narrowed)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(None, schema)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def x__convert_value_to_serializable__mutmut_26(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(value)
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value)

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(inner_val, schema)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(inner_val, schema)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(CtyList[Any] | CtySet[Any], schema)  # type: ignore[redundant-cast]
        return _serialize_collection_value(inner_val, schema_narrowed)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(inner_val, None)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def x__convert_value_to_serializable__mutmut_27(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(value)
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value)

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(inner_val, schema)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(inner_val, schema)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(CtyList[Any] | CtySet[Any], schema)  # type: ignore[redundant-cast]
        return _serialize_collection_value(inner_val, schema_narrowed)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(schema)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def x__convert_value_to_serializable__mutmut_28(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(value)
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value)

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(inner_val, schema)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(inner_val, schema)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(CtyList[Any] | CtySet[Any], schema)  # type: ignore[redundant-cast]
        return _serialize_collection_value(inner_val, schema_narrowed)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(inner_val, )
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(inner_val)
    return inner_val


def x__convert_value_to_serializable__mutmut_29(value: CtyValue[Any], schema: CtyType[Any]) -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(value)
    if value.is_unknown:
        return _serialize_unknown(value)
    if value.is_null:
        return None
    if isinstance(schema, CtyDynamic):
        return _serialize_dynamic(value)

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return _serialize_object_value(inner_val, schema)
    if isinstance(schema, CtyMap):
        return _serialize_map_value(inner_val, schema)
    if isinstance(schema, CtyList | CtySet):
        schema_narrowed = cast(CtyList[Any] | CtySet[Any], schema)  # type: ignore[redundant-cast]
        return _serialize_collection_value(inner_val, schema_narrowed)
    if isinstance(schema, CtyTuple):
        return _serialize_tuple_value(inner_val, schema)
    if isinstance(inner_val, Decimal):
        return _serialize_decimal_value(None)
    return inner_val

x__convert_value_to_serializable__mutmut_mutants : ClassVar[MutantDict] = {
'x__convert_value_to_serializable__mutmut_1': x__convert_value_to_serializable__mutmut_1, 
    'x__convert_value_to_serializable__mutmut_2': x__convert_value_to_serializable__mutmut_2, 
    'x__convert_value_to_serializable__mutmut_3': x__convert_value_to_serializable__mutmut_3, 
    'x__convert_value_to_serializable__mutmut_4': x__convert_value_to_serializable__mutmut_4, 
    'x__convert_value_to_serializable__mutmut_5': x__convert_value_to_serializable__mutmut_5, 
    'x__convert_value_to_serializable__mutmut_6': x__convert_value_to_serializable__mutmut_6, 
    'x__convert_value_to_serializable__mutmut_7': x__convert_value_to_serializable__mutmut_7, 
    'x__convert_value_to_serializable__mutmut_8': x__convert_value_to_serializable__mutmut_8, 
    'x__convert_value_to_serializable__mutmut_9': x__convert_value_to_serializable__mutmut_9, 
    'x__convert_value_to_serializable__mutmut_10': x__convert_value_to_serializable__mutmut_10, 
    'x__convert_value_to_serializable__mutmut_11': x__convert_value_to_serializable__mutmut_11, 
    'x__convert_value_to_serializable__mutmut_12': x__convert_value_to_serializable__mutmut_12, 
    'x__convert_value_to_serializable__mutmut_13': x__convert_value_to_serializable__mutmut_13, 
    'x__convert_value_to_serializable__mutmut_14': x__convert_value_to_serializable__mutmut_14, 
    'x__convert_value_to_serializable__mutmut_15': x__convert_value_to_serializable__mutmut_15, 
    'x__convert_value_to_serializable__mutmut_16': x__convert_value_to_serializable__mutmut_16, 
    'x__convert_value_to_serializable__mutmut_17': x__convert_value_to_serializable__mutmut_17, 
    'x__convert_value_to_serializable__mutmut_18': x__convert_value_to_serializable__mutmut_18, 
    'x__convert_value_to_serializable__mutmut_19': x__convert_value_to_serializable__mutmut_19, 
    'x__convert_value_to_serializable__mutmut_20': x__convert_value_to_serializable__mutmut_20, 
    'x__convert_value_to_serializable__mutmut_21': x__convert_value_to_serializable__mutmut_21, 
    'x__convert_value_to_serializable__mutmut_22': x__convert_value_to_serializable__mutmut_22, 
    'x__convert_value_to_serializable__mutmut_23': x__convert_value_to_serializable__mutmut_23, 
    'x__convert_value_to_serializable__mutmut_24': x__convert_value_to_serializable__mutmut_24, 
    'x__convert_value_to_serializable__mutmut_25': x__convert_value_to_serializable__mutmut_25, 
    'x__convert_value_to_serializable__mutmut_26': x__convert_value_to_serializable__mutmut_26, 
    'x__convert_value_to_serializable__mutmut_27': x__convert_value_to_serializable__mutmut_27, 
    'x__convert_value_to_serializable__mutmut_28': x__convert_value_to_serializable__mutmut_28, 
    'x__convert_value_to_serializable__mutmut_29': x__convert_value_to_serializable__mutmut_29
}

def _convert_value_to_serializable(*args, **kwargs):
    result = _mutmut_trampoline(x__convert_value_to_serializable__mutmut_orig, x__convert_value_to_serializable__mutmut_mutants, args, kwargs)
    return result 

_convert_value_to_serializable.__signature__ = _mutmut_signature(x__convert_value_to_serializable__mutmut_orig)
x__convert_value_to_serializable__mutmut_orig.__name__ = 'x__convert_value_to_serializable'


def x__msgpack_default_handler__mutmut_orig(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return _serialize_decimal_value(obj)
    error_message = ERR_OBJECT_NOT_MSGPACK_SERIALIZABLE.format(type_name=type(obj).__name__)
    raise TypeError(error_message)


def x__msgpack_default_handler__mutmut_1(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return _serialize_decimal_value(None)
    error_message = ERR_OBJECT_NOT_MSGPACK_SERIALIZABLE.format(type_name=type(obj).__name__)
    raise TypeError(error_message)


def x__msgpack_default_handler__mutmut_2(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return _serialize_decimal_value(obj)
    error_message = None
    raise TypeError(error_message)


def x__msgpack_default_handler__mutmut_3(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return _serialize_decimal_value(obj)
    error_message = ERR_OBJECT_NOT_MSGPACK_SERIALIZABLE.format(type_name=None)
    raise TypeError(error_message)


def x__msgpack_default_handler__mutmut_4(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return _serialize_decimal_value(obj)
    error_message = ERR_OBJECT_NOT_MSGPACK_SERIALIZABLE.format(type_name=type(None).__name__)
    raise TypeError(error_message)


def x__msgpack_default_handler__mutmut_5(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return _serialize_decimal_value(obj)
    error_message = ERR_OBJECT_NOT_MSGPACK_SERIALIZABLE.format(type_name=type(obj).__name__)
    raise TypeError(None)

x__msgpack_default_handler__mutmut_mutants : ClassVar[MutantDict] = {
'x__msgpack_default_handler__mutmut_1': x__msgpack_default_handler__mutmut_1, 
    'x__msgpack_default_handler__mutmut_2': x__msgpack_default_handler__mutmut_2, 
    'x__msgpack_default_handler__mutmut_3': x__msgpack_default_handler__mutmut_3, 
    'x__msgpack_default_handler__mutmut_4': x__msgpack_default_handler__mutmut_4, 
    'x__msgpack_default_handler__mutmut_5': x__msgpack_default_handler__mutmut_5
}

def _msgpack_default_handler(*args, **kwargs):
    result = _mutmut_trampoline(x__msgpack_default_handler__mutmut_orig, x__msgpack_default_handler__mutmut_mutants, args, kwargs)
    return result 

_msgpack_default_handler.__signature__ = _mutmut_signature(x__msgpack_default_handler__mutmut_orig)
x__msgpack_default_handler__mutmut_orig.__name__ = 'x__msgpack_default_handler'


def x_cty_to_msgpack__mutmut_orig(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_1(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context=None
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_2(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "XXoperationXX": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_3(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "OPERATION": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_4(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "XXcty_to_msgpack_serializationXX",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_5(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "CTY_TO_MSGPACK_SERIALIZATION",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_6(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "XXvalue_typeXX": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_7(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "VALUE_TYPE": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_8(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(None).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_9(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "XXschema_typeXX": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_10(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "SCHEMA_TYPE": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_11(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(None),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_12(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "XXvalue_is_nullXX": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_13(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "VALUE_IS_NULL": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_14(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(None, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_15(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, None) else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_16(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr("is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_17(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, ) else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_18(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "XXis_nullXX") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_19(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "IS_NULL") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_20(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else True,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_21(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "XXvalue_is_unknownXX": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_22(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "VALUE_IS_UNKNOWN": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_23(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(None, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_24(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, None) else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_25(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr("is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_26(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, ) else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_27(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "XXis_unknownXX") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_28(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "IS_UNKNOWN") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_29(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else True,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_30(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = None
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_31(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(None, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_32(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, None)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_33(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_34(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, )
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_35(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = None
        return result


def x_cty_to_msgpack__mutmut_36(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            None,
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_37(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=None,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_38(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            use_bin_type=None,
        )
        return result


def x_cty_to_msgpack__mutmut_39(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            default=_msgpack_default_handler,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_40(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            use_bin_type=MSGPACK_USE_BIN_TYPE_TRUE,
        )
        return result


def x_cty_to_msgpack__mutmut_41(value: CtyValue[Any], schema: CtyType[Any]) -> bytes:
    with error_boundary(
        context={
            "operation": "cty_to_msgpack_serialization",
            "value_type": type(value).__name__,
            "schema_type": str(schema),
            "value_is_null": value.is_null if hasattr(value, "is_null") else False,
            "value_is_unknown": value.is_unknown if hasattr(value, "is_unknown") else False,
        }
    ):
        serializable_data = _convert_value_to_serializable(value, schema)
        result: bytes = msgpack.packb(
            serializable_data,
            default=_msgpack_default_handler,
            )
        return result

x_cty_to_msgpack__mutmut_mutants : ClassVar[MutantDict] = {
'x_cty_to_msgpack__mutmut_1': x_cty_to_msgpack__mutmut_1, 
    'x_cty_to_msgpack__mutmut_2': x_cty_to_msgpack__mutmut_2, 
    'x_cty_to_msgpack__mutmut_3': x_cty_to_msgpack__mutmut_3, 
    'x_cty_to_msgpack__mutmut_4': x_cty_to_msgpack__mutmut_4, 
    'x_cty_to_msgpack__mutmut_5': x_cty_to_msgpack__mutmut_5, 
    'x_cty_to_msgpack__mutmut_6': x_cty_to_msgpack__mutmut_6, 
    'x_cty_to_msgpack__mutmut_7': x_cty_to_msgpack__mutmut_7, 
    'x_cty_to_msgpack__mutmut_8': x_cty_to_msgpack__mutmut_8, 
    'x_cty_to_msgpack__mutmut_9': x_cty_to_msgpack__mutmut_9, 
    'x_cty_to_msgpack__mutmut_10': x_cty_to_msgpack__mutmut_10, 
    'x_cty_to_msgpack__mutmut_11': x_cty_to_msgpack__mutmut_11, 
    'x_cty_to_msgpack__mutmut_12': x_cty_to_msgpack__mutmut_12, 
    'x_cty_to_msgpack__mutmut_13': x_cty_to_msgpack__mutmut_13, 
    'x_cty_to_msgpack__mutmut_14': x_cty_to_msgpack__mutmut_14, 
    'x_cty_to_msgpack__mutmut_15': x_cty_to_msgpack__mutmut_15, 
    'x_cty_to_msgpack__mutmut_16': x_cty_to_msgpack__mutmut_16, 
    'x_cty_to_msgpack__mutmut_17': x_cty_to_msgpack__mutmut_17, 
    'x_cty_to_msgpack__mutmut_18': x_cty_to_msgpack__mutmut_18, 
    'x_cty_to_msgpack__mutmut_19': x_cty_to_msgpack__mutmut_19, 
    'x_cty_to_msgpack__mutmut_20': x_cty_to_msgpack__mutmut_20, 
    'x_cty_to_msgpack__mutmut_21': x_cty_to_msgpack__mutmut_21, 
    'x_cty_to_msgpack__mutmut_22': x_cty_to_msgpack__mutmut_22, 
    'x_cty_to_msgpack__mutmut_23': x_cty_to_msgpack__mutmut_23, 
    'x_cty_to_msgpack__mutmut_24': x_cty_to_msgpack__mutmut_24, 
    'x_cty_to_msgpack__mutmut_25': x_cty_to_msgpack__mutmut_25, 
    'x_cty_to_msgpack__mutmut_26': x_cty_to_msgpack__mutmut_26, 
    'x_cty_to_msgpack__mutmut_27': x_cty_to_msgpack__mutmut_27, 
    'x_cty_to_msgpack__mutmut_28': x_cty_to_msgpack__mutmut_28, 
    'x_cty_to_msgpack__mutmut_29': x_cty_to_msgpack__mutmut_29, 
    'x_cty_to_msgpack__mutmut_30': x_cty_to_msgpack__mutmut_30, 
    'x_cty_to_msgpack__mutmut_31': x_cty_to_msgpack__mutmut_31, 
    'x_cty_to_msgpack__mutmut_32': x_cty_to_msgpack__mutmut_32, 
    'x_cty_to_msgpack__mutmut_33': x_cty_to_msgpack__mutmut_33, 
    'x_cty_to_msgpack__mutmut_34': x_cty_to_msgpack__mutmut_34, 
    'x_cty_to_msgpack__mutmut_35': x_cty_to_msgpack__mutmut_35, 
    'x_cty_to_msgpack__mutmut_36': x_cty_to_msgpack__mutmut_36, 
    'x_cty_to_msgpack__mutmut_37': x_cty_to_msgpack__mutmut_37, 
    'x_cty_to_msgpack__mutmut_38': x_cty_to_msgpack__mutmut_38, 
    'x_cty_to_msgpack__mutmut_39': x_cty_to_msgpack__mutmut_39, 
    'x_cty_to_msgpack__mutmut_40': x_cty_to_msgpack__mutmut_40, 
    'x_cty_to_msgpack__mutmut_41': x_cty_to_msgpack__mutmut_41
}

def cty_to_msgpack(*args, **kwargs):
    result = _mutmut_trampoline(x_cty_to_msgpack__mutmut_orig, x_cty_to_msgpack__mutmut_mutants, args, kwargs)
    return result 

cty_to_msgpack.__signature__ = _mutmut_signature(x_cty_to_msgpack__mutmut_orig)
x_cty_to_msgpack__mutmut_orig.__name__ = 'x_cty_to_msgpack'


def x__unpacked_to_cty__mutmut_orig(data: Any, schema: CtyType[Any]) -> CtyValue[Any]:
    if isinstance(data, UnknownValue):
        return CtyValue.unknown(schema, value=data)
    if data is None:
        return CtyValue.null(schema)
    return schema.validate(data)


def x__unpacked_to_cty__mutmut_1(data: Any, schema: CtyType[Any]) -> CtyValue[Any]:
    if isinstance(data, UnknownValue):
        return CtyValue.unknown(None, value=data)
    if data is None:
        return CtyValue.null(schema)
    return schema.validate(data)


def x__unpacked_to_cty__mutmut_2(data: Any, schema: CtyType[Any]) -> CtyValue[Any]:
    if isinstance(data, UnknownValue):
        return CtyValue.unknown(schema, value=None)
    if data is None:
        return CtyValue.null(schema)
    return schema.validate(data)


def x__unpacked_to_cty__mutmut_3(data: Any, schema: CtyType[Any]) -> CtyValue[Any]:
    if isinstance(data, UnknownValue):
        return CtyValue.unknown(value=data)
    if data is None:
        return CtyValue.null(schema)
    return schema.validate(data)


def x__unpacked_to_cty__mutmut_4(data: Any, schema: CtyType[Any]) -> CtyValue[Any]:
    if isinstance(data, UnknownValue):
        return CtyValue.unknown(schema, )
    if data is None:
        return CtyValue.null(schema)
    return schema.validate(data)


def x__unpacked_to_cty__mutmut_5(data: Any, schema: CtyType[Any]) -> CtyValue[Any]:
    if isinstance(data, UnknownValue):
        return CtyValue.unknown(schema, value=data)
    if data is not None:
        return CtyValue.null(schema)
    return schema.validate(data)


def x__unpacked_to_cty__mutmut_6(data: Any, schema: CtyType[Any]) -> CtyValue[Any]:
    if isinstance(data, UnknownValue):
        return CtyValue.unknown(schema, value=data)
    if data is None:
        return CtyValue.null(None)
    return schema.validate(data)


def x__unpacked_to_cty__mutmut_7(data: Any, schema: CtyType[Any]) -> CtyValue[Any]:
    if isinstance(data, UnknownValue):
        return CtyValue.unknown(schema, value=data)
    if data is None:
        return CtyValue.null(schema)
    return schema.validate(None)

x__unpacked_to_cty__mutmut_mutants : ClassVar[MutantDict] = {
'x__unpacked_to_cty__mutmut_1': x__unpacked_to_cty__mutmut_1, 
    'x__unpacked_to_cty__mutmut_2': x__unpacked_to_cty__mutmut_2, 
    'x__unpacked_to_cty__mutmut_3': x__unpacked_to_cty__mutmut_3, 
    'x__unpacked_to_cty__mutmut_4': x__unpacked_to_cty__mutmut_4, 
    'x__unpacked_to_cty__mutmut_5': x__unpacked_to_cty__mutmut_5, 
    'x__unpacked_to_cty__mutmut_6': x__unpacked_to_cty__mutmut_6, 
    'x__unpacked_to_cty__mutmut_7': x__unpacked_to_cty__mutmut_7
}

def _unpacked_to_cty(*args, **kwargs):
    result = _mutmut_trampoline(x__unpacked_to_cty__mutmut_orig, x__unpacked_to_cty__mutmut_mutants, args, kwargs)
    return result 

_unpacked_to_cty.__signature__ = _mutmut_signature(x__unpacked_to_cty__mutmut_orig)
x__unpacked_to_cty__mutmut_orig.__name__ = 'x__unpacked_to_cty'


def x_cty_from_msgpack__mutmut_orig(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_1(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context=None
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_2(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "XXoperationXX": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_3(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "OPERATION": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_4(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "XXcty_from_msgpack_deserializationXX",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_5(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "CTY_FROM_MSGPACK_DESERIALIZATION",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_6(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "XXdata_sizeXX": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_7(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "DATA_SIZE": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_8(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "XXschema_typeXX": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_9(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "SCHEMA_TYPE": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_10(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(None),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_11(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "XXis_dynamic_typeXX": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_12(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "IS_DYNAMIC_TYPE": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_13(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_14(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(None)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_15(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = None

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_16(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            None,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_17(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=None,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_18(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=None,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_19(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=None,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_20(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_21(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_22(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_23(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_24(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE or isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_25(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list) or len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_26(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic) or isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_27(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) != TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_28(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = None
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_29(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(None)
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_30(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode(None))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_31(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[1].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_32(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("XXutf-8XX"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_33(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("UTF-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_34(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = None
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_35(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(None)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_36(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = None
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_37(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(None, actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_38(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], None)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_39(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_40(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], )
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_41(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[2], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_42(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=None, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_43(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=None)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_44(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_45(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, )
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_46(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(None) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, cty_type)


def x_cty_from_msgpack__mutmut_47(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(None, cty_type)


def x_cty_from_msgpack__mutmut_48(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, None)


def x_cty_from_msgpack__mutmut_49(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(cty_type)


def x_cty_from_msgpack__mutmut_50(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_from_msgpack_deserialization",
            "data_size": len(data),
            "schema_type": str(cty_type),
            "is_dynamic_type": isinstance(cty_type, CtyDynamic),
        }
    ):
        if not data:
            return CtyValue.null(cty_type)
        raw_unpacked = msgpack.unpackb(
            data,
            ext_hook=_ext_hook,
            raw=MSGPACK_RAW_FALSE,
            strict_map_key=MSGPACK_STRICT_MAP_KEY_FALSE,
        )

        if (
            isinstance(cty_type, CtyDynamic)
            and isinstance(raw_unpacked, list)
            and len(raw_unpacked) == TWO_VALUE
            and isinstance(raw_unpacked[0], bytes)
        ):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = _unpacked_to_cty(raw_unpacked[1], actual_type)
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(ERR_DECODE_DYNAMIC_TYPE) from e
            except CtyValidationError as e:
                raise e

        return _unpacked_to_cty(raw_unpacked, )

x_cty_from_msgpack__mutmut_mutants : ClassVar[MutantDict] = {
'x_cty_from_msgpack__mutmut_1': x_cty_from_msgpack__mutmut_1, 
    'x_cty_from_msgpack__mutmut_2': x_cty_from_msgpack__mutmut_2, 
    'x_cty_from_msgpack__mutmut_3': x_cty_from_msgpack__mutmut_3, 
    'x_cty_from_msgpack__mutmut_4': x_cty_from_msgpack__mutmut_4, 
    'x_cty_from_msgpack__mutmut_5': x_cty_from_msgpack__mutmut_5, 
    'x_cty_from_msgpack__mutmut_6': x_cty_from_msgpack__mutmut_6, 
    'x_cty_from_msgpack__mutmut_7': x_cty_from_msgpack__mutmut_7, 
    'x_cty_from_msgpack__mutmut_8': x_cty_from_msgpack__mutmut_8, 
    'x_cty_from_msgpack__mutmut_9': x_cty_from_msgpack__mutmut_9, 
    'x_cty_from_msgpack__mutmut_10': x_cty_from_msgpack__mutmut_10, 
    'x_cty_from_msgpack__mutmut_11': x_cty_from_msgpack__mutmut_11, 
    'x_cty_from_msgpack__mutmut_12': x_cty_from_msgpack__mutmut_12, 
    'x_cty_from_msgpack__mutmut_13': x_cty_from_msgpack__mutmut_13, 
    'x_cty_from_msgpack__mutmut_14': x_cty_from_msgpack__mutmut_14, 
    'x_cty_from_msgpack__mutmut_15': x_cty_from_msgpack__mutmut_15, 
    'x_cty_from_msgpack__mutmut_16': x_cty_from_msgpack__mutmut_16, 
    'x_cty_from_msgpack__mutmut_17': x_cty_from_msgpack__mutmut_17, 
    'x_cty_from_msgpack__mutmut_18': x_cty_from_msgpack__mutmut_18, 
    'x_cty_from_msgpack__mutmut_19': x_cty_from_msgpack__mutmut_19, 
    'x_cty_from_msgpack__mutmut_20': x_cty_from_msgpack__mutmut_20, 
    'x_cty_from_msgpack__mutmut_21': x_cty_from_msgpack__mutmut_21, 
    'x_cty_from_msgpack__mutmut_22': x_cty_from_msgpack__mutmut_22, 
    'x_cty_from_msgpack__mutmut_23': x_cty_from_msgpack__mutmut_23, 
    'x_cty_from_msgpack__mutmut_24': x_cty_from_msgpack__mutmut_24, 
    'x_cty_from_msgpack__mutmut_25': x_cty_from_msgpack__mutmut_25, 
    'x_cty_from_msgpack__mutmut_26': x_cty_from_msgpack__mutmut_26, 
    'x_cty_from_msgpack__mutmut_27': x_cty_from_msgpack__mutmut_27, 
    'x_cty_from_msgpack__mutmut_28': x_cty_from_msgpack__mutmut_28, 
    'x_cty_from_msgpack__mutmut_29': x_cty_from_msgpack__mutmut_29, 
    'x_cty_from_msgpack__mutmut_30': x_cty_from_msgpack__mutmut_30, 
    'x_cty_from_msgpack__mutmut_31': x_cty_from_msgpack__mutmut_31, 
    'x_cty_from_msgpack__mutmut_32': x_cty_from_msgpack__mutmut_32, 
    'x_cty_from_msgpack__mutmut_33': x_cty_from_msgpack__mutmut_33, 
    'x_cty_from_msgpack__mutmut_34': x_cty_from_msgpack__mutmut_34, 
    'x_cty_from_msgpack__mutmut_35': x_cty_from_msgpack__mutmut_35, 
    'x_cty_from_msgpack__mutmut_36': x_cty_from_msgpack__mutmut_36, 
    'x_cty_from_msgpack__mutmut_37': x_cty_from_msgpack__mutmut_37, 
    'x_cty_from_msgpack__mutmut_38': x_cty_from_msgpack__mutmut_38, 
    'x_cty_from_msgpack__mutmut_39': x_cty_from_msgpack__mutmut_39, 
    'x_cty_from_msgpack__mutmut_40': x_cty_from_msgpack__mutmut_40, 
    'x_cty_from_msgpack__mutmut_41': x_cty_from_msgpack__mutmut_41, 
    'x_cty_from_msgpack__mutmut_42': x_cty_from_msgpack__mutmut_42, 
    'x_cty_from_msgpack__mutmut_43': x_cty_from_msgpack__mutmut_43, 
    'x_cty_from_msgpack__mutmut_44': x_cty_from_msgpack__mutmut_44, 
    'x_cty_from_msgpack__mutmut_45': x_cty_from_msgpack__mutmut_45, 
    'x_cty_from_msgpack__mutmut_46': x_cty_from_msgpack__mutmut_46, 
    'x_cty_from_msgpack__mutmut_47': x_cty_from_msgpack__mutmut_47, 
    'x_cty_from_msgpack__mutmut_48': x_cty_from_msgpack__mutmut_48, 
    'x_cty_from_msgpack__mutmut_49': x_cty_from_msgpack__mutmut_49, 
    'x_cty_from_msgpack__mutmut_50': x_cty_from_msgpack__mutmut_50
}

def cty_from_msgpack(*args, **kwargs):
    result = _mutmut_trampoline(x_cty_from_msgpack__mutmut_orig, x_cty_from_msgpack__mutmut_mutants, args, kwargs)
    return result 

cty_from_msgpack.__signature__ = _mutmut_signature(x_cty_from_msgpack__mutmut_orig)
x_cty_from_msgpack__mutmut_orig.__name__ = 'x_cty_from_msgpack'


# 🌊🪢📦🪄
