# pyvider/cty/types/collections/list.py
from __future__ import annotations
from collections.abc import Iterator, Sequence
from typing import ClassVar, Generic, TypeVar, final, TYPE_CHECKING
from attrs import define, field
from pyvider.cty.exceptions import CtyListValidationError
from pyvider.cty.types.base import CtyType
from pyvider.cty.values import CtyValue
from pyvider.telemetry import logger

if TYPE_CHECKING:
    from pyvider.cty.types.collections.map import CtyMap
    from pyvider.cty.types.structural.object import CtyObject

T = TypeVar("T")

@final
@define(frozen=True, slots=True)
class CtyList(CtyType[list[T]], Generic[T]):
    ctype: ClassVar[str] = "list"
    element_type: CtyType[T] = field(kw_only=True)

    def __attrs_post_init__(self) -> None:
        if not isinstance(self.element_type, CtyType):
            raise CtyListValidationError(f"Expected CtyType for element_type, got {type(self.element_type).__name__}")

    def validate(self, value: object) -> CtyValue:
        logger.debug(f"🔌📝🔄 Validating value as CtyList: {type(value).__name__}")
        from pyvider.cty.types import CtyDynamic
        from pyvider.cty.values import CtyValue

        if value is None:
            raise CtyListValidationError("Input to CtyList.validate cannot be None. Use CtyValue.null(CtyList(...)) for a null list.")

        raw_list_to_validate: Sequence[object] | None = None
        if isinstance(value, CtyValue):
            if value.is_null: return CtyValue.null(self)
            if value.is_unknown: return CtyValue.unknown(self)
            if isinstance(value.type, CtyList):
                if isinstance(self.element_type, CtyDynamic) or value.type.element_type.usable_as(self.element_type):
                    raw_list_to_validate = value.value
                else:
                    raise CtyListValidationError(f"Input CtyValue has incompatible list element type: {value.type.element_type} vs {self.element_type}")
            else:
                raise CtyListValidationError(f"Input CtyValue is not of a list type, got {value.type}")
        elif isinstance(value, (list, tuple)):
            raw_list_to_validate = value
        else:
            raise CtyListValidationError(f"Expected list, tuple, or CtyValue list, got {type(value).__name__}")

        if raw_list_to_validate is None:
            raise CtyListValidationError("Internal error: list to validate is None after initial checks.")

        validated_elements = []
        validation_errors = []
        for i, item in enumerate(raw_list_to_validate):
            try:
                validated_item = self.element_type.validate(item)
                validated_elements.append(validated_item)
            except Exception as e:
                error_msg = f"Item {i} ('{item}'): {e!s}"
                logger.debug(f"🔌❗❌ {error_msg}")
                validation_errors.append(error_msg)

        if validation_errors:
            raise CtyListValidationError("CtyList validation failed:\n - " + "\n - ".join(validation_errors))

        logger.debug(f"🔌📝✅ Successfully validated list with {len(validated_elements)} items")
        return CtyValue(vtype=self, value=validated_elements)

    def element_at(self, container: object, index: int) -> CtyValue:
        logger.debug(f"🔌🔍🔄 Getting element at index {index}")
        from pyvider.cty.values import CtyValue

        if isinstance(container, CtyValue):
            if not isinstance(container.type, CtyList):
                raise CtyListValidationError(f"Expected CtyValue with CtyList type, got CtyValue with {type(container.type).__name__}")
            if container.is_null:
                raise IndexError(f"Cannot access element at index {index} in a null list.")
            if container.is_unknown:
                return CtyValue.unknown(self.element_type)
            if not isinstance(container.value, (list, tuple)):
                raise CtyListValidationError(f"Internal error: CtyValue of CtyList type does not wrap a list/tuple, got {type(container.value).__name__}")
            actual_list_value = container.value
        else:
            raise CtyListValidationError(f"Expected CtyValue[CtyList], got {type(container).__name__}")

        try:
            return actual_list_value[index]
        except IndexError as e:
            raise IndexError(f"Index {index} out of bounds for list of length {len(actual_list_value)}") from e
        except Exception as e:
            raise CtyListValidationError(f"Error accessing element at index {index}: {e!s}") from e

    def equal(self, other: CtyType) -> bool:
        if not isinstance(other, CtyList):
            return False
        return self.element_type.equal(other.element_type)

    def usable_as(self, other: CtyType) -> bool:
        from pyvider.cty.types.structural import CtyDynamic
        if isinstance(other, CtyDynamic): return True
        if not isinstance(other, CtyList): return False
        return self.element_type.usable_as(other.element_type)

    def __str__(self) -> str:
        return f"list({self.element_type})"

    def __repr__(self) -> str:
        return f"CtyList(element_type={self.element_type!r})"

    def is_collection_type(self) -> bool: return True
    def is_list_type(self) -> bool: return True
