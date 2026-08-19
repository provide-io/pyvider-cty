#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""go-cty's `cty/json` value codec: `Marshal`, `Unmarshal`, `ImpliedType`.

Distinct from the `jsonencode` / `jsondecode` stdlib functions, which are
Terraform language features operating on values. This is the *serialization*
codec — the JSON counterpart of `codec.py`'s msgpack, and the form Terraform
uses where a value has to be human-readable rather than compact: state files,
`terraform show -json`, plan output.

Type-directed in both directions, like the msgpack codec: JSON alone cannot
distinguish a list from a set from a tuple, all three being arrays, so the type
is supplied rather than guessed. `implied_json_type` exists for the case where
there is no type to supply, and it necessarily guesses — an array becomes a
*tuple*, because JSON promises nothing about an array's elements sharing a type.

Two things JSON cannot carry, both of which raise rather than degrade:

  - **Unknowns.** There is no JSON spelling for "not yet decided", and writing
    `null` instead would turn a value that has not been computed into one that
    definitively has no value. go-cty raises here too.
  - **Marks.** Same rule as `cty_to_msgpack`: serializing a sensitive value must
    not silently declassify it. Use `unmark_deep_with_paths` first.
"""

from __future__ import annotations

from decimal import Decimal
import json
from typing import Any, cast
import unicodedata

from pyvider.cty.conversion.explicit import _number_to_string
from pyvider.cty.exceptions import CtyValidationError
from pyvider.cty.types import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyType,
)
from pyvider.cty.values import CtyValue
from pyvider.cty.values.frozen import FrozenDict

__all__ = ["cty_from_json", "cty_to_json", "implied_json_type"]


class CtyJsonError(CtyValidationError):
    """A value or document that JSON cannot represent."""


class _RawNumber(Decimal):
    """A `Decimal` that remembers the digits it was written with.

    `json.loads`' number hooks receive the literal token, and go-cty's decoder
    needs it: unmarshalling a JSON number into a `string` yields *the token*, so
    `1.50` becomes `"1.50"` and `1e2` becomes `"1e2"`. Reconstructing that from
    the parsed number is not possible -- both would come back as `100` or `1.5` --
    so the text is carried alongside rather than recovered.
    """

    __slots__ = ("text",)

    text: str

    def __new__(cls, text: str) -> _RawNumber:
        number = super().__new__(cls, text)
        number.text = text
        return number


def _reject_constant(literal: str) -> Any:
    """`NaN`, `Infinity` and `-Infinity` are Python extensions, not JSON.

    Go's encoding/json refuses them outright -- "invalid character 'N' looking
    for beginning of value" -- and accepting them produced a value this module's
    own encoder then refused ("cannot serialize infinity as JSON"), while the
    msgpack encoder wrote the *string* "NaN" into a number slot. A document that
    only one of two codecs will accept is worse than one that neither will.
    """
    raise CtyJsonError(f"invalid character in JSON document: {literal} is a Python literal, not valid JSON")


def _loads(payload: bytes | str) -> Any:
    text = payload.decode() if isinstance(payload, bytes) else payload
    return json.loads(
        text,
        parse_float=_RawNumber,
        parse_int=_RawNumber,
        parse_constant=_reject_constant,
    )


def cty_to_json(value: CtyValue[Any], cty_type: CtyType[Any], /) -> bytes:
    """Serialize `value` as go-cty's `json.Marshal` does.

    A value that does not conform to `cty_type` is converted first, which is
    go-cty's documented behaviour: the type is "used to attempt automatic
    conversions of any non-conformant types in the given value".

    Marks are checked *before* that conversion, deeply. Conversion rebuilds a
    value, and a rebuilt value that quietly lost a mark would then serialize
    without complaint -- which is the silent declassification this refusal
    exists to prevent, arrived at by a different route.
    """
    from pyvider.cty.conformance import conformance_errors
    from pyvider.cty.marks import collect_marks_deep

    if collect_marks_deep(value):
        raise CtyJsonError("value has marks, so it cannot be serialized as JSON")

    if conformance_errors(value.type, cty_type):
        from pyvider.cty.conversion import convert

        value = convert(value, cty_type)
    return _marshal(value, cty_type, "").encode()


def cty_from_json(payload: bytes | str, cty_type: CtyType[Any], /) -> CtyValue[Any]:
    """Decode JSON against a known type, as go-cty's `json.Unmarshal` does."""
    return _unmarshal(_loads(payload), cty_type, "")


def implied_json_type(payload: bytes | str, /) -> CtyType[Any]:
    """The type a JSON document implies, as go-cty's `json.ImpliedType` does.

    An array implies a **tuple**, not a list: JSON gives no guarantee that an
    array's elements share a type, and a list would have to invent one.
    """
    return _implied(_loads(payload))


def _marshal(value: CtyValue[Any], cty_type: CtyType[Any], path: str) -> str:
    if value.marks:
        raise CtyJsonError(f"{path or 'value'} has marks, so it cannot be serialized as JSON")
    if value.is_unknown:
        raise CtyJsonError(f"{path or 'value'} is not known")

    # A dynamic *target* has to carry its real type alongside, or the decoder on
    # the far side has nothing to decode against.
    if isinstance(cty_type, CtyDynamic) and not isinstance(value.type, CtyDynamic):
        return _marshal_dynamic(value, path)
    if isinstance(cty_type, CtyDynamic) and isinstance(value.type, CtyDynamic):
        inner = cast("CtyValue[Any]", value.value)
        return _marshal_dynamic(inner, path) if isinstance(inner, CtyValue) else "null"

    if value.is_null:
        return "null"

    return _marshal_by_type(value, cty_type, path)


def _marshal_by_type(value: CtyValue[Any], cty_type: CtyType[Any], path: str) -> str:
    """Dispatch on the target type, once the universal cases are out of the way."""
    if isinstance(cty_type, CtyString):
        return _marshal_string(str(value.value))
    if isinstance(cty_type, CtyNumber):
        return _marshal_number(value, path)
    if isinstance(cty_type, CtyBool):
        return "true" if value.value else "false"
    if isinstance(cty_type, CtyList | CtySet):
        return _marshal_sequence(value, cty_type.element_type, path)
    if isinstance(cty_type, CtyTuple):
        return _marshal_tuple(value, cty_type, path)
    if isinstance(cty_type, CtyMap):
        return _marshal_map(value, cty_type.element_type, path)
    if isinstance(cty_type, CtyObject):
        return _marshal_object(value, cty_type, path)

    # Capsules land here. go-cty refuses them too: a capsule wraps a native
    # object with no JSON spelling, and inventing one would produce a document
    # that cannot be read back.
    raise CtyJsonError(f"{path or 'value'}: cannot serialize {cty_type.ctype} as JSON")


_HTML_ESCAPES = {
    "<": "\\u003c",
    ">": "\\u003e",
    "&": "\\u0026",
    "\u2028": "\\u2028",
    "\u2029": "\\u2029",
}
"""What Go's `encoding/json` escapes and Python's `json` does not.

Go escapes these by default so that the output is safe to embed in HTML or in a
JavaScript source file. The bytes differ, and these bytes end up in state files
that are compared textually, so a `<` written two ways is a diff on every plan.
Non-ASCII is *not* in this table: Go writes it raw, as `ensure_ascii=False` does.
"""


def _marshal_string(text: str) -> str:
    encoded = json.dumps(text, ensure_ascii=False)
    for character, escape in _HTML_ESCAPES.items():
        encoded = encoded.replace(character, escape)
    return encoded


def _marshal_number(value: CtyValue[Any], path: str) -> str:
    raw = value.value
    if isinstance(raw, Decimal) and not raw.is_finite():
        # go-cty refuses too: JSON has no infinity, and the alternatives are a
        # string (changing the type) or null (changing the value). The infinity
        # wording is go-cty's own and is pinned by a sweep row; a NaN says so
        # instead, because it said "infinity" for a NaN and go-cty -- which
        # cannot hold a NaN at all -- has no message of its own to match.
        what = "NaN" if raw.is_nan() else "infinity"
        raise CtyJsonError(f"{path or 'value'}: cannot serialize {what} as JSON")
    return _number_to_string(raw)


def _marshal_dynamic(value: CtyValue[Any], path: str) -> str:
    type_json = json.dumps(value.type._to_wire_json(), separators=(",", ":"))
    return f'{{"value":{_marshal(value, value.type, path)},"type":{type_json}}}'


def _marshal_sequence(value: CtyValue[Any], element_type: CtyType[Any], path: str) -> str:
    elements = value.value or ()
    rendered = [
        _marshal(element, element_type, f"{path}[{index}]")
        for index, element in enumerate(_ordered(value, elements))
    ]
    return f"[{','.join(rendered)}]"


def _marshal_tuple(value: CtyValue[Any], cty_type: CtyTuple, path: str) -> str:
    elements = cast("tuple[CtyValue[Any], ...]", value.value or ())
    rendered = [
        _marshal(element, element_type, f"{path}[{index}]")
        for index, (element, element_type) in enumerate(zip(elements, cty_type.element_types, strict=True))
    ]
    return f"[{','.join(rendered)}]"


def _marshal_map(value: CtyValue[Any], element_type: CtyType[Any], path: str) -> str:
    items = cast("dict[str, CtyValue[Any]]", value.value or {})
    rendered = [
        f"{_marshal_string(key)}:{_marshal(item, element_type, f'{path}[{key!r}]')}"
        for key, item in sorted(items.items())
    ]
    return f"{{{','.join(rendered)}}}"


def _marshal_object(value: CtyValue[Any], cty_type: CtyObject, path: str) -> str:
    items = cast("dict[str, CtyValue[Any]]", value.value or {})
    rendered = [
        f"{_marshal_string(name)}:{_marshal(items[name], attribute_type, f'{path}.{name}')}"
        for name, attribute_type in sorted(cty_type.attribute_types.items())
        if name in items
    ]
    return f"{{{','.join(rendered)}}}"


def _ordered(value: CtyValue[Any], elements: Any) -> list[CtyValue[Any]]:
    """Set elements in the order the msgpack codec uses, so the two agree."""
    if isinstance(value.type, CtySet):
        return sorted(elements, key=lambda element: element._canonical_sort_key())
    return list(elements)


def _unmarshal(raw: Any, cty_type: CtyType[Any], path: str) -> CtyValue[Any]:
    if isinstance(cty_type, CtyDynamic):
        return _unmarshal_dynamic(raw, path)
    if raw is None:
        return CtyValue.null(cty_type)

    if isinstance(cty_type, CtyList | CtySet | CtyTuple):
        return _unmarshal_sequence(raw, cty_type, path)
    if isinstance(cty_type, CtyMap | CtyObject):
        return _unmarshal_mapping(raw, cty_type, path)
    return _unmarshal_primitive(raw, cty_type, path)


def _unmarshal_primitive(raw: Any, cty_type: CtyType[Any], path: str) -> CtyValue[Any]:
    """go-cty's `unmarshalPrimitive`, coercions included.

    `Unmarshal`'s contract is that "type conversions will be done where possible
    to make the result conformant even if the types given in JSON are not
    exactly correct", and for primitives that is a small explicit table rather
    than a general conversion:

      - a `string` type accepts a JSON string, a number (as its literal text) or
        a bool (as `"true"` / `"false"`)
      - a `number` type accepts a JSON number or a string holding one
      - a `bool` type accepts a JSON bool or a string holding one

    Every other combination is refused. Refusing the lot instead -- which this
    module did -- rejects state and plan JSON that go-cty reads without
    complaint, and a decoder is exactly where being stricter than the reference
    stops being conservative.
    """
    where = path or "value"
    if isinstance(cty_type, CtyBool):
        return _unmarshal_bool(raw, cty_type, where)
    if isinstance(cty_type, CtyNumber):
        return _unmarshal_number(raw, cty_type, where)
    if isinstance(cty_type, CtyString):
        return _unmarshal_string(raw, cty_type, where)
    return cty_type.validate(raw)


def _unmarshal_bool(raw: Any, cty_type: CtyType[Any], where: str) -> CtyValue[Any]:
    if isinstance(raw, bool | str):
        return _coerced(raw, cty_type, where, "bool")
    raise CtyJsonError(f"{where}: bool is required")


def _unmarshal_number(raw: Any, cty_type: CtyType[Any], where: str) -> CtyValue[Any]:
    # bool first: in Python a bool *is* an int, and go-cty refuses one here.
    if not isinstance(raw, bool) and isinstance(raw, Decimal | int | float | str):
        return _coerced(raw, cty_type, where, "number")
    raise CtyJsonError(f"{where}: number is required")


def _unmarshal_string(raw: Any, cty_type: CtyType[Any], where: str) -> CtyValue[Any]:
    if isinstance(raw, bool):
        return cty_type.validate("true" if raw else "false")
    if isinstance(raw, _RawNumber):
        # The token, not the parsed number: go-cty hands over the digits as they
        # were written, so 1.50 stays "1.50" and 1e2 stays "1e2".
        return cty_type.validate(raw.text)
    if isinstance(raw, Decimal | int | float):
        return cty_type.validate(_number_to_string(raw))
    if isinstance(raw, str):
        return cty_type.validate(raw)
    raise CtyJsonError(f"{where}: string is required")


def _coerced(raw: Any, cty_type: CtyType[Any], where: str, wanted: str) -> CtyValue[Any]:
    try:
        return cty_type.validate(raw)
    except CtyValidationError as error:
        raise CtyJsonError(f"{where}: {wanted} is required") from error


def _unmarshal_dynamic(raw: Any, path: str) -> CtyValue[Any]:
    if raw is None:
        return CtyValue.null(CtyDynamic())
    if not isinstance(raw, dict) or "value" not in raw or "type" not in raw:
        raise CtyJsonError(f"{path or 'value'}: a dynamic value must be an object with 'value' and 'type'")
    from pyvider.cty.parser import parse_tf_type_to_ctytype

    inner_type = parse_tf_type_to_ctytype(raw["type"])
    return CtyValue(vtype=CtyDynamic(), value=_unmarshal(raw["value"], inner_type, path))


def _unmarshal_sequence(raw: Any, cty_type: CtyList[Any] | CtySet[Any] | CtyTuple, path: str) -> CtyValue[Any]:
    if not isinstance(raw, list):
        raise CtyJsonError(f"{path or 'value'}: an array is required for {cty_type.ctype}")
    if isinstance(cty_type, CtySet):
        element_type = cty_type.element_type
        return cast(
            "CtyValue[Any]",
            cty_type.validate(
                [_unmarshal(item, element_type, f"{path}[{index}]") for index, item in enumerate(raw)]
            ),
        )
    if isinstance(cty_type, CtyTuple):
        expected = len(cty_type.element_types)
        if len(raw) != expected:
            raise CtyJsonError(f"{path or 'value'}: {expected} elements are required, got {len(raw)}")
        return CtyValue(
            vtype=cty_type,
            value=tuple(
                _unmarshal(item, element_type, f"{path}[{index}]")
                for index, (item, element_type) in enumerate(zip(raw, cty_type.element_types, strict=True))
            ),
        )
    element_type = cty_type.element_type
    return CtyValue(
        vtype=cty_type,
        value=tuple(_unmarshal(item, element_type, f"{path}[{index}]") for index, item in enumerate(raw)),
    )


def _unmarshal_mapping(raw: Any, cty_type: CtyMap[Any] | CtyObject, path: str) -> CtyValue[Any]:
    if not isinstance(raw, dict):
        raise CtyJsonError(f"{path or 'value'}: an object is required for {cty_type.ctype}")
    if isinstance(cty_type, CtyObject):
        for name in raw:
            if name not in cty_type.attribute_types:
                raise CtyJsonError(f'{path or "value"}: unsupported attribute "{name}"')
        return CtyValue(
            vtype=cty_type,
            value=FrozenDict(
                (
                    name,
                    _unmarshal(raw[name], attribute_type, f"{path}.{name}")
                    if name in raw
                    else CtyValue.null(attribute_type),
                )
                for name, attribute_type in cty_type.attribute_types.items()
            ),
        )

    element_type = cty_type.element_type
    return CtyValue(
        vtype=cty_type,
        value=FrozenDict(
            (unicodedata.normalize("NFC", str(key)), _unmarshal(item, element_type, f"{path}[{key!r}]"))
            for key, item in raw.items()
        ),
    )


def _implied(raw: Any) -> CtyType[Any]:
    if raw is None:
        return CtyDynamic()
    if isinstance(raw, bool):
        return CtyBool()
    if isinstance(raw, Decimal | int | float):
        return CtyNumber()
    if isinstance(raw, str):
        return CtyString()
    if isinstance(raw, list):
        # A tuple, not a list: JSON does not promise that an array's elements
        # share a type, and choosing a list would have to invent one.
        return CtyTuple(element_types=tuple(_implied(item) for item in raw))
    if isinstance(raw, dict):
        return CtyObject({key: _implied(item) for key, item in raw.items()})
    raise CtyJsonError(f"cannot infer a type from {type(raw).__name__}")


# 🌊🪢🔚
