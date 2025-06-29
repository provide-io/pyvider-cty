# pyvider/cty/types/structural/tuple.py
from __future__ import annotations
from typing import ClassVar
from attrs import define, field
from pyvider.cty.exceptions import CtyTupleValidationError, CtyValidationError, CtyTypeMismatchError
from pyvider.cty.types.base import CtyType
from pyvider.cty.values import CtyValue
from pyvider.telemetry import logger

@define(frozen=True, slots=True)
class CtyTuple(CtyType[tuple[object, ...]]):
    """Represents a Cty tuple type with fixed-position elements of potentially different types."""
    ctype: ClassVar[str] = "tuple"
    element_types: tuple[CtyType, ...] = field()

    @element_types.validator
    def _validate_element_types(self, attribute: str, value: tuple[CtyType, ...]) -> None:
        if not isinstance(value, tuple):
            raise CtyTupleValidationError(f"element_types must be a tuple, got {type(value).__name__}")
        for i, typ in enumerate(value):
            if not isinstance(typ, CtyType):
                raise CtyTupleValidationError(f"Element type at index {i} must be a CtyType, got {type(typ).__name__}")

    def validate(self, value: object) -> CtyValue:
        if isinstance(value, CtyValue):
            if isinstance(value.type, CtyTuple) and value.type.equal(self): return value
            if value.is_unknown: return CtyValue.unknown(self)
            value = value.value
        if value is None: return CtyValue.null(self)
        if not isinstance(value, (list, tuple)):
            raise CtyValidationError(f"Expected tuple or list, got {type(value).__name__}")
        if len(value) != len(self.element_types):
            raise CtyValidationError(f"Expected {len(self.element_types)} elements, got {len(value)}")
        
        validated_elements = []
        for i, (raw_element, element_type) in enumerate(zip(value, self.element_types)):
            try:
                # Handle CtyDynamic for element_type
                from pyvider.cty.types.structural.dynamic import CtyDynamic
                if isinstance(element_type, CtyDynamic) and not isinstance(raw_element, CtyValue):
                    from pyvider.cty.types.primitives import CtyString, CtyNumber, CtyBool
                    from pyvider.cty.types.collections import CtyList, CtyMap
                    # CtySet, CtyTuple might be needed if they are to be promoted

                    if raw_element is None:
                        promoted_item_value = CtyValue.null(CtyDynamic())
                    elif isinstance(raw_element, str):
                        promoted_item_value = CtyString().validate(raw_element)
                    elif isinstance(raw_element, bool):
                        promoted_item_value = CtyBool().validate(raw_element)
                    elif isinstance(raw_element, (int, float)): # Add Decimal if needed
                        promoted_item_value = CtyNumber().validate(raw_element)
                    elif isinstance(raw_element, list):
                        promoted_item_value = CtyList(CtyDynamic()).validate(raw_element)
                    elif isinstance(raw_element, dict):
                        promoted_item_value = CtyMap(key_type=CtyString(), value_type=CtyDynamic()).validate(raw_element)
                    # Add set, tuple promotion if required
                    else:
                        # Fallback for non-promotable raw types with CtyDynamic element_type
                        validated_element = element_type.validate(raw_element)
                        validated_elements.append(validated_element)
                        continue # Skip other logic for this item
                    validated_element = CtyDynamic().validate(promoted_item_value)
                elif isinstance(element_type, CtyDynamic) and isinstance(raw_element, CtyValue):
                    validated_element = element_type.validate(raw_element)
                else: # Concrete element_type
                    value_to_validate = raw_element.value if isinstance(raw_element, CtyValue) and not isinstance(raw_element.type, CtyDynamic) else raw_element
                    validated_element = element_type.validate(value_to_validate)

                validated_elements.append(validated_element)
            except CtyValidationError as e:
                raise CtyValidationError(f"Invalid value for tuple element {i}: {e}") from e
        return CtyValue(self, tuple(validated_elements))
    
    def element_at(self, container_value: CtyValue, index: int | slice) -> CtyValue:
        if not isinstance(index, (int, slice)):
            raise TypeError(f"Tuple indices must be integers or slices, not {type(index).__name__}")
        
        if isinstance(index, slice):
            # Ensure container_value.value is accessible and is a tuple
            if container_value.is_null or container_value.is_unknown:
                # Slicing a null/unknown tuple results in a null/unknown tuple of the sliced type
                sliced_types = self.element_types[index]
                new_tuple_type = CtyTuple(element_types=sliced_types)
                return CtyValue.null(new_tuple_type) if container_value.is_null else CtyValue.unknown(new_tuple_type)

            if not isinstance(container_value.value, tuple):
                 raise CtyTupleValidationError("Internal tuple value is inconsistent with type definition for slicing.")

            sliced_values = container_value.value[index] # This is a tuple of CtyValues
            sliced_types = self.element_types[index]
            new_tuple_type = CtyTuple(element_types=sliced_types)
            # The sliced_values are already CtyValues, so they form the new tuple's value directly.
            return CtyValue(vtype=new_tuple_type, value=sliced_values)


        effective_index = index
        num_elements = len(self.element_types)

        if effective_index < 0:
            effective_index += num_elements

        if not (0 <= effective_index < num_elements):
            raise IndexError("tuple index out of range")

        # Ensure container_value.value is accessible and is a tuple
        if container_value.is_null or container_value.is_unknown:
             # Accessing an element of a null/unknown tuple results in a null/unknown value of that element's type
            element_type_at_index = self.element_types[effective_index]
            return CtyValue.null(element_type_at_index) if container_value.is_null else CtyValue.unknown(element_type_at_index)

        if not isinstance(container_value.value, tuple) or len(container_value.value) != num_elements:
            # This would indicate an internal inconsistency if validate() worked correctly.
            raise CtyTupleValidationError("Internal tuple value is inconsistent with type definition.")

        return container_value.value[effective_index]

    def equal(self, other: CtyType) -> bool:
        if not isinstance(other, CtyTuple): return False
        if len(self.element_types) != len(other.element_types): return False
        return all(t1.equal(t2) for t1, t2 in zip(self.element_types, other.element_types))

    def usable_as(self, other: CtyType) -> bool:
        from pyvider.cty.types.structural import CtyDynamic
        if isinstance(other, CtyDynamic): return True
        if not isinstance(other, CtyTuple): return False
        if len(self.element_types) != len(other.element_types): return False
        return all(t1.usable_as(t2) for t1, t2 in zip(self.element_types, other.element_types))
    
    def __getitem__(self, index: int | slice) -> CtyType | CtyTuple:
        return self.element_types[index]

    def __str__(self) -> str:
        """
        Produces the canonical, parsable string representation of the tuple type.
        FIX: Uses square brackets `[]` as required by the parser.
        """
        elements = ", ".join(str(vtype) for vtype in self.element_types)
        return f"tuple([{elements}])"

    def slice(self, container_value: CtyValue, start: int, end: int | None = None, step: int | None = None) -> CtyValue:
        """
        Slices the tuple value. This is a convenience method that wraps element_at with a slice object.
        """
        # Ensure container_value is a CtyValue of this tuple type
        if not isinstance(container_value, CtyValue) or not container_value.type.equal(self):
            raise CtyTypeMismatchError(
                f"Container value must be a CtyValue of type {self}, got {container_value}"
            )

        slice_obj = slice(start, end, step)
        return self.element_at(container_value, slice_obj)
