
from decimal import Decimal, InvalidOperation
from typing import TYPE_CHECKING, Any, ClassVar  # Added TYPE_CHECKING

from attrs import define, field

from pyvider.cty.exceptions import CtyBoolValidationError
from pyvider.cty.types.base import CtyType
from pyvider.telemetry import logger

if TYPE_CHECKING:
    from pyvider.cty.values import CtyValue


#
# pyvider/cty/types/primitives/bool.py
#
# Define frozensets for true and false string representations
TRUE_STRINGS: frozenset[str] = frozenset(("true", "t", "yes", "y", "1"))
FALSE_STRINGS: frozenset[str] = frozenset(("false", "f", "no", "n", "0"))


@define(frozen=True, slots=True)
class CtyBool(CtyType[bool]):
    """
    Represents the boolean type in the Cty type system.

    CtyBool validates and represents boolean values (True or False). It can
    convert common string representations (like "true", "false", "0", "1")
    and specific numeric values (0 and 1) to boolean, adhering to Cty's
    strict conversion rules.

    Attributes:
        ctype (ClassVar[str]): Type identifier constant, always "bool"
        value (bool): The boolean value (default: False)
    """

    ctype: ClassVar[str] = "bool"
    value: bool = field(default=False)

    def validate(self, value: Any) -> CtyValue: # Ensured string literal
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

        # Import here to avoid circular A -> B -> A
        from pyvider.cty.values import CtyValue

        # 1️⃣ None input -> null CtyValue
        if value is None:
            return CtyValue.null(self)

        # 2️⃣ Existing CtyValue
        if isinstance(value, CtyValue):
            # If it's already the same type, pass through
            if isinstance(value.type, CtyBool):
                return value

            # Unknown values propagate their unknown-ness
            if value.is_unknown:
                logger.debug("🧰✅🔄 value is unknown – propagate")
                return CtyValue.unknown(self) # Return unknown of *this* type (CtyBool)

            # Otherwise re-validate its *inner* value (may raise)
            value = value.value  # unbox and continue

        # 3️⃣ Boolean input
        if isinstance(value, bool):
            return CtyValue(vtype=self, value=value)

        # 4️⃣ String input (case-insensitive)
        if isinstance(value, str):
            val_lower = value.lower()
            if val_lower in TRUE_STRINGS:
                return CtyValue(vtype=self, value=True)
            if val_lower in FALSE_STRINGS:
                return CtyValue(vtype=self, value=False)
            raise CtyBoolValidationError(f"Cannot convert string {value!r} to boolean")

        # 5️⃣ Numeric input (strict – only 0 / 1)
        if isinstance(value, int | float | Decimal):
            try:
                # Ensure it's a whole number before comparing
                dec_val = Decimal(value)
                if dec_val == Decimal(1):
                    return CtyValue(vtype=self, value=True)
                if dec_val == Decimal(0):
                    return CtyValue(vtype=self, value=False)
                raise CtyBoolValidationError(
                    f"Numeric value {value!r} is not 0 or 1"
                )
            except (InvalidOperation, ValueError) as exc:  # pragma: no cover – very rare
                logger.error("🧰❌🔄 invalid numeric value %r: %s", value, exc)
                raise CtyBoolValidationError(str(exc)) from exc

        # --- REJECT ALL OTHER TYPES ---
        logger.error(
            f"🧰❌🔄 Validation failed: Cannot convert {type(value).__name__} to boolean"
        )
        raise CtyBoolValidationError(
            f"Cannot convert {type(value).__name__} to boolean"
        )

    def equal(self, other: CtyType[bool]) -> bool:
        """Check if this type is equal to another boolean type."""
        result = isinstance(other, CtyBool)
        logger.debug("✅🔍🔄 CtyBool.equal: %s to %s -> %s", self, other, result)
        return result

    def usable_as(self, other: CtyType[bool]) -> bool:
        """Check if this boolean type can be used as another type."""
        # A bool can be used as dynamic, or another bool.
        from pyvider.cty.types.structural import CtyDynamic  # Avoid circular

        result = isinstance(other, CtyBool | CtyDynamic)
        logger.debug("✅🔍🔄 CtyBool.usable_as: %s to %s -> %s", self, other, result)
        return result

    def __str__(self) -> str:  # pragma: no cover – trivial
        return "bool"

    def is_primitive_type(self) -> bool:
        return True


# 🐍🏗️🐣
