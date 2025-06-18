from __future__ import annotations

from typing import Any, ClassVar, Generic, TypeVar, final

from attrs import define, evolve, field

from pyvider.cty.exceptions import CtySetValidationError, CtyValidationError
from pyvider.cty.types.base import CtyType
from pyvider.telemetry import logger

#
# pyvider/cty/types/collections/set.py
#

"""
Set type implementation for the Cty type system.

This module provides CtySet, representing unordered collections of unique values
in the Cty type system. Sets contain elements of a single specified type and
enforce uniqueness constraints during validation. The implementation follows
go-cty's set semantics, ensuring consistent behavior for collection operations
and maintaining type safety throughout the validation process.

Sets support standard operations like adding and removing elements, checking
for membership, and comparing with other sets, all while preserving type
information and maintaining immutability of the original values.
"""

T = TypeVar("T")


@final
@define(frozen=True, slots=True)
class CtySet(CtyType[set[T]], Generic[T]):
    """
    Represents a set type in the Cty type system.

    Sets are unordered collections of unique values of a specific element type.
    Unlike lists, sets cannot contain duplicate values and do not maintain any
    particular order. This implementation enforces type constraints during validation
    and provides immutable set operations.

    Attributes:
        ctype: Class variable identifying this as a set type, always "set"
        element_type: The Cty type of elements in the set
        value: The actual set of values, all of which are of type T
    """

    ctype: ClassVar[str] = "set"
    element_type: CtyType[T] = field(kw_only=True)  # Mandatory as keyword-only
    value: set[T] = field(factory=set, kw_only=True)  # Allow passing value via kw_only

    def __attrs_post_init__(self) -> None:
        """
        Validate element_type after initialization.

        Ensures that the element_type provided during instantiation is a valid
        CtyType instance. This validation occurs immediately after the object is
        created to catch configuration errors early.

        Raises:
            CtySetValidationError: If element_type is not a CtyType instance
        """
        if not isinstance(self.element_type, CtyType):
            raise CtySetValidationError(
                f"Expected CtyType for element_type, got {type(self.element_type)}"
            )

    def validate(self, value: Any) -> CtyValue:  # Added quotes around CtyValue
        """Validate *value* as a **set** matching :pyattr:`element_type`.

        Acceptable *inputs*:
        * **``None``** – returns a *null* :class:`~pyvider.cty.values.CtyValue`.
        * An existing **CtyValue**.
        * A plain *built‑in* ``set``/``frozenset``.  *Other* iterable types are
          **rejected** to keep behaviour aligned with go‑cty's explicitness.
        """
        # Local import to avoid circular dependency
        from pyvider.cty.values import CtyValue

        logger.debug(
            "🟣🔍  Validating value %r as CtySet(%s)", value, self.element_type
        )

        # ---------------------- Null handling ---------------------------
        if value is None:
            logger.debug("🟣✅  Received *None* – returning null CtyValue")
            return CtyValue.null(self)

        # ------------------- Existing CtyValue -------------------------
        if isinstance(value, CtyValue):
            # Exact same set type – return as‑is
            if isinstance(value.type, CtySet) and value.type.equal(self):
                logger.debug("🟣✅  Value already a CtyValue with matching CtySet type")
                return value

            # Unknown stays unknown so long as types are compatible
            if value.is_unknown and value.type.usable_as(self):
                logger.debug("🟣✅  Propagating unknown CtyValue through validation")
                return CtyValue(vtype=self, is_unknown=True)

            # Otherwise extract inner content for re‑validation below
            try:
                value = value.value  # may raise if unknown – caught above
            except ValueError as exc:
                raise CtySetValidationError(str(exc)) from exc

        # NEW: Handle list or tuple input by converting to a set
        if isinstance(value, list | tuple):
            try:
                value = set(value)
                logger.debug("🟣🔄  Converted input list/tuple to set for validation")
            except TypeError as e:  # Handles unhashable items if any
                err = (
                    f"Input list/tuple could not be converted to set (possibly unhashable elements): {e}; "
                    f"got {type(value).__name__}: {value!r}"
                )
                logger.error("🟣❌  %s", err)
                raise CtySetValidationError(err) from e

        # -------------------- Set coercion -----------------------------
        if not isinstance(value, set | frozenset):
            err = (
                "Expected a Python set/frozenset (or convertible list/tuple) for CtySet validation; "
                f"got {type(value).__name__}: {value!r}"
            )
            logger.error("🟣❌  %s", err)
            raise CtySetValidationError(err)

        validated_items: set[CtyValue] = set()
        errors: list[str] = []

        for idx, raw_item in enumerate(value):
            try:
                validated_item = self.element_type.validate(raw_item)
                validated_items.add(validated_item)
            except CtyValidationError as e:  # re‑wrap with position info
                err_msg = f"element {idx}: {e}"
                errors.append(err_msg)

        if errors:
            # Aggregate multiple failures so users get the full picture
            full_msg = "Set validation failed:\n" + "\n".join(errors)
            logger.error("🟣❌  %s", full_msg)
            raise CtySetValidationError(full_msg)

        logger.debug("🟣✅  Successfully validated %d element(s)", len(validated_items))
        return CtyValue(vtype=self, value=frozenset(validated_items))

    def add(self, element: Any) -> CtySet:  # Added type hint for element
        """
        Add an element to the set.

        Creates a new set that includes all elements from the original set
        plus the new element. This operation is immutable - the original set
        remains unchanged.

        Args:
            element: The element to add to the set. Must conform to the set's
                element_type.

        Returns:
            CtySet: A new CtySet with the original elements plus the new element

        Raises:
            CtySetValidationError: If the element cannot be validated against the
                element_type
        """
        try:
            # Validate the element
            validated_item = self.element_type.validate(element)

            # Create a new set with the additional element
            new_set = set(self.value)
            new_set.add(validated_item)

            return evolve(self, value=new_set)
        except Exception as e:
            raise CtySetValidationError(f"Failed to add element: {e}")

    def remove(self, item: T) -> CtySet:
        """
        Remove an item from the set.

        Creates a new set that includes all elements from the original set
        except the specified item. This operation is immutable - the original
        set remains unchanged.

        Args:
            item: The item to remove from the set. Must conform to the set's
                element_type.

        Returns:
            CtySet: A new CtySet with the item removed

        Raises:
            CtySetValidationError: If the item cannot be validated or removed
        """
        try:
            validated_item = self.element_type.validate(item)
            new_set = {x for x in self.value if x != validated_item}
            logger.debug(f"🔌📝✅ Removed item from set: {validated_item}")
            return evolve(self, value=new_set)
        except Exception as e:
            logger.debug(f"🔌❗❌ Failed to remove item: {e}")
            raise CtySetValidationError(f"Failed to remove item: {e}")

    def usable_as(self, other: CtyType) -> bool:
        result = isinstance(other, CtySet) and self.element_type.usable_as(
            other.element_type
        )
        logger.debug(f"🔌📝✅ CtySet.usable_as: {result}")
        return result

    def equal(self, other: CtyType) -> bool:
        """
        Check if this type is equal to the other type.

        For sets, equality requires the other type to be a CtySet with an
        equal element type. This implements strict type identity checking.
        """
        if not isinstance(other, CtySet):
            logger.debug(
                f"🔌📝❌ CtySet.equal: False (other is {type(other).__name__})"
            )
            return False
        result = self.element_type.equal(other.element_type)
        logger.debug(f"🔌📝✅ CtySet.equal: {result}")
        return result

    def __str__(self) -> str:
        return f"set({self.element_type})"

    def is_collection_type(self) -> bool:
        """Check if this type is a collection type."""
        return True

    def is_set_type(self) -> bool:
        """Check if this type is a set type."""
        return True


# 🐍🏗️🐣
