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

__all__ = ["cty_from_json", "cty_to_json", "implied_json_type"]


class CtyJsonError(CtyValidationError):
    """A value or document that JSON cannot represent."""


def cty_to_json(value: CtyValue[Any], cty_type: CtyType[Any], /) -> bytes:
    """Serialize `value` as go-cty's `json.Marshal` does."""
    return _marshal(value, cty_type, "").encode()


def cty_from_json(payload: bytes | str, cty_type: CtyType[Any], /) -> CtyValue[Any]:
    """Decode JSON against a known type, as go-cty's `json.Unmarshal` does."""
    text = payload.decode() if isinstance(payload, bytes) else payload
    return _unmarshal(json.loads(text, parse_float=Decimal, parse_int=Decimal), cty_type, "")


def implied_json_type(payload: bytes | str, /) -> CtyType[Any]:
    """The type a JSON document implies, as go-cty's `json.ImpliedType` does.

    An array implies a **tuple**, not a list: JSON gives no guarantee that an
    array's elements share a type, and a list would have to invent one.
    """
    text = payload.decode() if isinstance(payload, bytes) else payload
    return _implied(json.loads(text, parse_float=Decimal, parse_int=Decimal))


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
        return json.dumps(str(value.value), ensure_ascii=False)
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


def _marshal_number(value: CtyValue[Any], path: str) -> str:
    raw = value.value
    if isinstance(raw, Decimal) and not raw.is_finite():
        # go-cty refuses too: JSON has no infinity, and the alternatives are a
        # string (changing the type) or null (changing the value).
        raise CtyJsonError(f"{path or 'value'}: cannot serialize infinity as JSON")
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
        f"{json.dumps(key, ensure_ascii=False)}:{_marshal(item, element_type, f'{path}[{key!r}]')}"
        for key, item in sorted(items.items())
    ]
    return f"{{{','.join(rendered)}}}"


def _marshal_object(value: CtyValue[Any], cty_type: CtyObject, path: str) -> str:
    items = cast("dict[str, CtyValue[Any]]", value.value or {})
    rendered = [
        f"{json.dumps(name, ensure_ascii=False)}:{_marshal(items[name], attribute_type, f'{path}.{name}')}"
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
    return cty_type.validate(raw)


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
    if isinstance(cty_type, CtyTuple):
        expected = len(cty_type.element_types)
        if len(raw) != expected:
            raise CtyJsonError(f"{path or 'value'}: {expected} elements are required, got {len(raw)}")
        return cast(
            "CtyValue[Any]",
            cty_type.validate(
                tuple(
                    _unmarshal(item, element_type, f"{path}[{index}]")
                    for index, (item, element_type) in enumerate(zip(raw, cty_type.element_types, strict=True))
                )
            ),
        )
    element_type = cty_type.element_type
    return cast(
        "CtyValue[Any]",
        cty_type.validate(
            [_unmarshal(item, element_type, f"{path}[{index}]") for index, item in enumerate(raw)]
        ),
    )


def _unmarshal_mapping(raw: Any, cty_type: CtyMap[Any] | CtyObject, path: str) -> CtyValue[Any]:
    if not isinstance(raw, dict):
        raise CtyJsonError(f"{path or 'value'}: an object is required for {cty_type.ctype}")
    if isinstance(cty_type, CtyObject):
        return cast(
            "CtyValue[Any]",
            cty_type.validate(
                {
                    name: _unmarshal(raw[name], attribute_type, f"{path}.{name}")
                    for name, attribute_type in cty_type.attribute_types.items()
                    if name in raw
                }
            ),
        )
    element_type = cty_type.element_type
    return cast(
        "CtyValue[Any]",
        cty_type.validate(
            {key: _unmarshal(item, element_type, f"{path}[{key!r}]") for key, item in raw.items()}
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
