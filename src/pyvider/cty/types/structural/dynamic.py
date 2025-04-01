#
# pyvider/cty/types/structural/dynamic.py
#
from typing import ClassVar

from attrs import define

from pyvider.cty.exceptions import CtyValidationError
from pyvider.cty.types.base import CtyType

@define(frozen=True, slots=True)
class CtyDynamic(CtyType):
    """
    CtyDynamic represents a dynamic Cty type that can accept any value.
    This type acts as a catch-all during schema validation, allowing flexibility 
    for attributes whose structure or type cannot be determined at schema definition time.
    """
    ctype: ClassVar[str] = "dynamic"

    def validate(self, value: object) -> "CtyValue":
        """
        Validation for CtyDynamic is a no-op since it accepts any value.

        Args:
            value (object): Any value to validate.

        Raises:
            CtyValidationError: If the value is explicitly set to an unsupported form.
        """
        from pyvider.cty.values import CtyValue

        if isinstance(value, (dict, list, int, float, bool, str, type(None))):
            return CtyValue(type_=self, value=value) 

        raise CtyValidationError("Unsupported value for CtyDynamic. Acceptable types are primitive types, dict, list, or None.")

    def equal(self, other: CtyType) -> bool:
        """
        CtyDynamic instances are considered equal to any other instance of CtyDynamic.

        Args:
            other (CtyType): Another CtyType instance.

        Returns:
            bool: True if the types are compatible, otherwise False.
        """
        return isinstance(other, CtyDynamic)

    def usable_as(self, other: CtyType) -> bool:
        """
        CtyDynamic can be used interchangeably with any other CtyDynamic.

        Args:
            other (CtyType): Target CtyType to compare against.

        Returns:
            bool: True if usable as the target type.
        """
        return isinstance(other, CtyDynamic)

    def __str__(self) -> str:
        return "CtyDynamic"

    def __repr__(self) -> str:
        return "CtyDynamic()"

# 🐍🏗️🐣
