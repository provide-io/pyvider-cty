# pyvider/cty/types/structural/dynamic.py
from decimal import Decimal
from typing import TYPE_CHECKING, Any, ClassVar

from attrs import define

from pyvider.cty.exceptions import CtyValidationError
from pyvider.cty.types.base import CtyType
from pyvider.telemetry import logger

if TYPE_CHECKING:
    from pyvider.cty.values import CtyValue


@define(frozen=True, slots=True)
class CtyDynamic(CtyType[object]):
    ctype: ClassVar[str] = "dynamic"

    def _infer_type_and_validate(self, value: Any) -> "CtyValue":
        from pyvider.cty.values import CtyValue
        from pyvider.cty.types.primitives import CtyString, CtyNumber, CtyBool
        from pyvider.cty.types.collections import CtyList, CtyMap, CtySet
        from pyvider.cty.types.structural import CtyObject, CtyTuple  # CtyObject might be needed for dicts later

        logger.debug(f"🧩🔍 Deep inferring type for CtyDynamic from: {type(value).__name__}")

        if isinstance(value, CtyValue):
            # If it's already a CtyValue, its type is known.
            return value

        if value is None:
            # This case should ideally be handled by the caller ensuring non-None for deep inference,
            # or by returning a CtyValue.null with a specific inferred type if possible.
            # For now, let's make it CtyValue.null(CtyDynamic()) as a placeholder during inference.
            # The outer validate() will wrap this appropriately.
            return CtyValue.null(CtyDynamic())


        if isinstance(value, str):
            return CtyString().validate(value)
        elif isinstance(value, bool):
            return CtyBool().validate(value)
        elif isinstance(value, (int, float, Decimal)):
            return CtyNumber().validate(value)
        elif isinstance(value, list):
            if not value: # Empty list
                return CtyList(element_type=CtyDynamic()).validate([])
            # Attempt to infer a common element type. For now, simple homogeneity or CtyDynamic.
            # A more advanced version would use type unification.
            element_values = [self._infer_type_and_validate(el) for el in value]
            element_types = {ev.type for ev in element_values}
            if len(element_types) == 1:
                element_type = element_types.pop()
            else:
                # TODO: Implement type unification here. For now, fallback to CtyDynamic.
                # This part might need refinement based on how pyvider.cty handles mixed-type lists.
                # A simple approach: if all are primitives and can convert to string, maybe list(string)?
                # For now, dynamic is safest without unification.
                logger.warning(f"List contains mixed types: {element_types}. Defaulting to list(dynamic).")
                element_type = CtyDynamic()

            # The `element_values` are already validated CtyValues.
            # We need to pass these to the CtyList's validate method.
            # CtyList.validate should be able to handle a list of CtyValues.
            return CtyList(element_type=element_type).validate(element_values)

        elif isinstance(value, set):
            if not value: # Empty set
                return CtySet(element_type=CtyDynamic()).validate(set())
            element_values = [self._infer_type_and_validate(el) for el in value]
            element_types = {ev.type for ev in element_values}
            if len(element_types) == 1:
                element_type = element_types.pop()
            else:
                logger.warning(f"Set contains mixed types: {element_types}. Defaulting to set(dynamic).")
                element_type = CtyDynamic()
            # Pass list of CtyValues to CtySet.validate
            return CtySet(element_type=element_type).validate(list(element_values))

        elif isinstance(value, dict):
            if not value: # Empty map
                return CtyMap(key_type=CtyString(), value_type=CtyDynamic()).validate({})

            # For keys, go-cty maps always have string keys.
            # For values, attempt to infer a common type.
            # CtyMap.validate expects a dict of raw keys to raw values or CtyValues.
            # Here, we've processed values into CtyValues (v_inferred).
            # Keys (k) are raw strings.
            map_to_validate: dict[str, Any] = {}
            value_types_for_map_type = set()

            for k_raw, v_raw in value.items():
                if not isinstance(k_raw, str): # Should have been caught earlier by key_type check
                    raise CtyValidationError(f"Map keys must be strings for CtyDynamic inference, got {type(k_raw)}")

                inferred_value_cty = self._infer_type_and_validate(v_raw)
                map_to_validate[k_raw] = inferred_value_cty # Pass CtyValue to map's validate
                value_types_for_map_type.add(inferred_value_cty.type)

            final_map_value_type: CtyType
            if len(value_types_for_map_type) == 1:
                final_map_value_type = value_types_for_map_type.pop()
            else:
                logger.warning(f"Map contains mixed value types: {value_types_for_map_type}. Defaulting to map(string, dynamic).")
                final_map_value_type = CtyDynamic()

            return CtyMap(key_type=CtyString(), value_type=final_map_value_type).validate(map_to_validate)

        elif isinstance(value, tuple):
            if not value: # Empty tuple
                return CtyTuple(element_types=tuple()).validate(tuple())
            element_values = [self._infer_type_and_validate(el) for el in value] # list of CtyValues
            element_types_tuple = tuple(ev.type for ev in element_values)
            # CtyTuple.validate should accept a list/tuple of CtyValues if its logic is robust
            return CtyTuple(element_types=element_types_tuple).validate(element_values)
        else:
            # Potentially handle CtyObject inference here if we want to be very clever with dicts
            # that look like objects, but that's more complex than typical dynamic behavior.
            raise CtyValidationError(
                f"Cannot infer a concrete CtyType for raw Python type: {type(value).__name__}. "
                "Please convert complex raw data to a CtyValue, or ensure it's a basic collection/primitive, "
                "before assigning to a dynamic type."
            )

    def validate(self, value: object) -> "CtyValue":
        from pyvider.cty.values import CtyValue

        logger.debug(f"🧩🔍 Validating value against CtyDynamic: {type(value).__name__}")

        if value is None:
            return CtyValue.null(self)

        if isinstance(value, CtyValue):
            if value.type.is_dynamic_type():
                # It's already a CtyValue(CtyDynamic, inner_value).
                # Ensure inner_value is also a CtyValue as per new logic.
                if not isinstance(value.value, CtyValue):
                    # This case indicates an old-style CtyDynamic(raw_python_value)
                    # We need to re-process its inner raw value.
                    logger.debug("Re-processing inner raw value of an existing CtyDynamic value.")
                    inferred_inner_value = self._infer_type_and_validate(value.value)
                    # Try passing without leading underscores for is_unknown and is_null, matching property names
                    return CtyValue(vtype=self, value=inferred_inner_value, is_unknown=value.is_unknown, is_null=value.is_null, marks=value._marks) # Preserve marks
                return value # Already correctly wrapped CtyValue(CtyDynamic, CtyValue(...))
            else:
                # It's some other CtyValue(ConcreteType, ...), wrap it with CtyDynamic.
                return CtyValue(self, value)

        # For raw Python values, perform deep type inference.
        logger.debug(f"Promoting raw type {type(value).__name__} for CtyDynamic via deep inference.")
        promoted_value = self._infer_type_and_validate(value)
        
        # The promoted_value is now a fully typed CtyValue (e.g., CtyList(CtyString)).
        # Wrap this concrete CtyValue with CtyDynamic.
        return CtyValue(self, promoted_value)

    def equal(self, other: "CtyType") -> bool:
        return isinstance(other, CtyDynamic)

    def usable_as(self, other: "CtyType") -> bool:
        # A dynamic type is only "usable as" another dynamic type.
        # This aligns with go-cty semantics where dynamic is a placeholder for an
        # unknown type, not a universal supertype for conversion purposes.
        return isinstance(other, CtyDynamic)

    def is_dynamic_type(self) -> bool:
        """Returns True as this type is CtyDynamic."""
        return True

    def __str__(self) -> str:
        return "dynamic"

    def is_empty_type(self) -> bool:
        # CtyDynamic itself is not "empty" in the sense of representing no possible value.
        # It means the type is not yet known.
        # go-cty's DynamicPseudoType has no equivalent IsEmptyType method.
        # Let's align with the idea that it's a placeholder, not an "empty" construct.
        return False # Or True, depending on interpretation. False seems more aligned. Let's check go-cty.
                     # go-cty DynamicPseudoType doesn't have properties like this.
                     # The concept of "empty type" usually applies to list(), object({}), etc.
                     # For now, False seems safer.
