import json
from typing import TYPE_CHECKING, Any, ClassVar

from attrs import define

from pyvider.cty.types.base import CtyType

if TYPE_CHECKING:
    from pyvider.cty.values import CtyValue


@define(frozen=True, slots=True)
class CtyDynamic(CtyType[object]):
    """Represents a dynamic type that can hold any CtyValue."""

    ctype: ClassVar[str] = "dynamic"

    def validate(self, value: object) -> "CtyValue[Any]":
        """
        Validates a raw Python value for a dynamic type. It first checks if
        the value matches the special wire format for dynamic values before
        falling back to inferring a concrete type.
        """
        from pyvider.cty.conversion.raw_to_cty import infer_cty_type_from_raw
        from pyvider.cty.parser import parse_tf_type_to_ctytype
        from pyvider.cty.values import CtyValue

        if isinstance(value, CtyValue):
            return value

        if value is None:
            return CtyValue.null(self)

        # Check for the special wire format: a list of [type_spec_bytes, value].
        if isinstance(value, list) and len(value) == 2 and isinstance(value[0], bytes):
            try:
                type_spec = json.loads(value[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                # If successful, validate the inner value against the discovered type.
                return actual_type.validate(value[1])
            except Exception:
                # If decoding fails, it's not the special wire format.
                # Fall through to the standard inference logic below.
                pass

        # If it's not the wire format, infer the type from the raw Python value.
        inferred_type = infer_cty_type_from_raw(value)
        if isinstance(inferred_type, CtyDynamic):
            return CtyValue(self, value)
        return inferred_type.validate(value)

    def equal(self, other: "CtyType[Any]") -> bool:
        return isinstance(other, CtyDynamic)

    def usable_as(self, other: "CtyType[Any]") -> bool:
        return isinstance(other, CtyDynamic)

    def _to_wire_json(self) -> Any:
        return self.ctype

    def is_dynamic_type(self) -> bool:
        return True

    def __str__(self) -> str:
        return "dynamic"
