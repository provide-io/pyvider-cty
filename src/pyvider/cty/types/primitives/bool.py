#
# pyvider/cty/types/primitives/bool.py
#

"""
Boolean type implementation for the Cty type system.

This module provides CtyBool, representing Boolean values in the Cty type system.
It handles validation, conversion from various input types to boolean values,
and implements type compatibility checking with strong validation guarantees.
"""

from decimal import Decimal, InvalidOperation
from typing import Any, ClassVar

from attrs import define, field

from pyvider.cty.exceptions import CtyBoolValidationError
from pyvider.cty.types.base import CtyType
from pyvider.telemetry import logger

# Define frozensets for true and false string representations
_TRUE_STRINGS = frozenset(
    {"1", "t", "T", "true", "TRUE", "True", "yes", "YES", "y", "Y"}
)
_FALSE_STRINGS = frozenset(
    {"0", "f", "F", "false", "FALSE", "False", "no", "NO", "n", "N"}
)


@define(frozen=True, slots=True)
class CtyBool(CtyType[bool]):
    """
    Boolean type representation in the Cty type system.

    Represents boolean (True/False) values with validation and type checking.
    Boolean values are immutable and support standard logical operations.
    CtyBool can convert various input types to boolean values according to
    specific conversion rules that match go-cty's semantics.

    Attributes:
        ctype: Class variable identifying this as a boolean type
        value: The default value for this type (False)
    """

    ctype: ClassVar[str] = "bool"
    value: bool = field(default=False)

    def validate(self, value: Any) -> "CtyValue":
        """Validate *value* and return a :class:`~pyvider.cty.values.CtyValue`.

        Conversion matrix
        -----------------
        * **bool** – returned unchanged.
        * **str**  – accepts the usual truthy / falsy keywords (case‑insensitive).
        * **number** – *only* ``0`` / ``1`` (int|float|Decimal).  Anything else
          raises :class:`CtyBoolValidationError` (aligns with go‑cty).
        * **None** – becomes *null* CtyValue.
        * **CtyValue** – passes through when compatible; otherwise re‑validated.
        """

        # Import here to avoid circular A → B → A
        from pyvider.cty.values import CtyValue

        logger.debug("🧰🔍🔄 Validating boolean candidate: %r", value)

        # 1️⃣ Null → dedicated null value
        if value is None:
            logger.debug("🧰✅🔄 null → CtyValue.null")
            return CtyValue.null(self)

        # 2️⃣ Already a CtyValue
        if isinstance(value, CtyValue):
            if isinstance(value.type, CtyBool):
                logger.debug("🧰✅🔄 already typed as CtyBool → passthrough")
                return value

            # Unknown values propagate their unknown‑ness
            if value.is_unknown:
                logger.debug("🧰✅🔄 value is unknown – propagate")
                return value

            # Otherwise re‑validate its *inner* value (may raise)
            value = value.value  # unbox and continue

        # 3️⃣ Native bool
        if isinstance(value, bool):
            logger.debug("🧰✅🔄 python bool accepted → %s", value)
            return CtyValue(vtype=self, value=value)

        # 4️⃣ String input
        if isinstance(value, str):
            low = value.casefold()
            if low in _TRUE_STRINGS:
                logger.debug("🧰✅🔄 string %r → True", value)
                return CtyValue(vtype=self, value=True)
            if low in _FALSE_STRINGS:
                logger.debug("🧰✅🔄 string %r → False", value)
                return CtyValue(vtype=self, value=False)
            logger.error("🧰❌🔄 cannot convert string %r to bool", value)
            raise CtyBoolValidationError(f"Cannot convert string {value!r} to boolean")

        # 5️⃣ Numeric input (strict – only 0 / 1)
        if isinstance(value, int | float | Decimal):
            try:
                dec = Decimal(value)
            except (
                InvalidOperation,
                ValueError,
            ) as exc:  # pragma: no cover – very rare
                logger.error("🧰❌🔄 invalid numeric value %r: %s", value, exc)
                raise CtyBoolValidationError(str(exc)) from exc

            if dec in (Decimal(0), Decimal(1)):
                bool_val = bool(dec)
                logger.debug("🧰✅🔄 numeric %s → %s", dec, bool_val)
                return CtyValue(vtype=self, value=bool_val)

            logger.error("🧰❌🔄 numeric boolean must be 0 or 1, got %s", dec)
            raise CtyBoolValidationError(
                f"Numeric boolean must be 0 or 1, got {value!r}"
            )

        # 6️⃣ Everything else → error
        logger.error("🧰❌🔄 unsupported boolean value type: %s", type(value).__name__)
        raise CtyBoolValidationError(
            f"Value must be a boolean, 0/1, or convertible string; got {type(value).__name__}: {value!r}"
        )

    def equal(self, other: "CtyType[bool]") -> bool:
        result = isinstance(other, CtyBool)
        logger.debug(f"🔄🔍✅ CtyBool.equal: {result}")
        return result

    def usable_as(self, other: "CtyType[bool]") -> bool:
        # Import locally to avoid circular dependency
        from pyvider.cty.types.structural.dynamic import CtyDynamic

        result = isinstance(other, CtyBool | CtyDynamic)
        logger.debug(f"🔄🔍✅ CtyBool.usable_as ({other.__class__.__name__}): {result}")
        return result

    def __str__(self) -> str:  # pragma: no cover – trivial
        return "bool"

    def is_primitive_type(self) -> bool:
        """Check if this type is a primitive type."""
        return True


# 🐍🏗️🐣
