# pyvider-cty/src/pyvider/cty/conversion/type_encoder.py
from typing import Any

from pyvider.cty.types import CtyType


def encode_cty_type_to_wire_json(cty_type: "CtyType[Any]") -> Any:
    """
    Encodes a CtyType into a JSON-serializable structure for the wire format
    by delegating to the type's own `_to_wire_json` method.
    """
    if not isinstance(cty_type, CtyType):
        raise TypeError(f"Expected CtyType, but got {type(cty_type).__name__}")
    return cty_type._to_wire_json()
