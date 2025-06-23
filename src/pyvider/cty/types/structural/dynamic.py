# pyvider/cty/types/structural/dynamic.py
from typing import TYPE_CHECKING, ClassVar

from attrs import define

from pyvider.cty.exceptions import CtyValidationError
from pyvider.cty.types.base import CtyType
from pyvider.telemetry import logger

if TYPE_CHECKING:
    from pyvider.cty.values import CtyValue

@define(frozen=True, slots=True)
class CtyDynamic(CtyType[object]):
    ctype: ClassVar[str] = "dynamic"

    def validate(self, value: object) -> "CtyValue":
        from pyvider.cty.values import CtyValue
        from pyvider.conversion.raw_to_cty import _infer_and_wrap

        logger.debug(f"🧩🔍🔄 Validating value against CtyDynamic: {type(value).__name__}")

        # ** THE FIX **
        # Handle the None case directly to break the recursion loop.
        # A null dynamic value is represented by a CtyValue of type CtyDynamic
        # that is marked as null.
        if value is None:
            return CtyValue.null(self)

        if isinstance(value, CtyValue):
            return CtyValue(self, value)

        try:
            inferred_value = _infer_and_wrap(value)
            return CtyValue(self, inferred_value)
        except TypeError as e:
            raise CtyValidationError(str(e)) from e

    def equal(self, other: "CtyType") -> bool: return isinstance(other, CtyDynamic)
    def usable_as(self, other: "CtyType") -> bool: return isinstance(other, CtyDynamic)
    def __str__(self) -> str: return "dynamic"
    def is_empty_type(self) -> bool: return True
