#
# pyvider/cty/types/collections/list.py
#
from __future__ import annotations

"""
List type implementation for the Cty type system.

This module provides CtyList, representing ordered collections of elements with the
same type in the Cty type system. Lists maintain insertion order, allow duplicates,
and support indexed access, slicing, and other sequence operations.

CtyList follows the go-cty list semantics, ensuring type safety for all elements
while providing Pythonic operations like slicing and iteration. All operations maintain
immutability by returning new instances rather than modifying existing ones.
"""

from collections.abc import Iterator, Sequence
from typing import (  # Added TYPE_CHECKING
    ClassVar,
    Generic,
    TypeVar,
    final,
)

from attrs import define, evolve, field

from pyvider.cty.exceptions import CtyListValidationError
from pyvider.cty.types.base import CtyType
from pyvider.cty.values import CtyValue
from pyvider.telemetry import logger

# Type variable representing the type of values in the list
T = TypeVar("T")


@final
@define(frozen=True, slots=True)
class CtyList(CtyType[list[T]], Generic[T]):
    """
    Represents an ordered list type in the Cty type system.

    Lists are ordered collections of values of a specific element type.
    Unlike sets, lists can contain duplicate values and maintain insertion order.
    CtyList supports indexing, slicing, concatenation, and other sequence operations
    while ensuring all elements conform to the specified element type.

    All operations maintain immutability by returning new instances rather than
    modifying existing ones.

    Attributes:
        ctype (ClassVar[str]): Type identifier constant, always "list"
        element_type (CtyType[T]): The type of elements contained in the list
        value (list[T]): The actual list of values (all of which are of type T)

    Examples:
        Creating a list of strings:
        >>> string_type = CtyString()
        >>> string_list = CtyList(element_type=string_type)

        Validating a list of values:
        >>> validated = string_list.validate(["a", "b", "c"])
        >>> len(validated)
        3
    """

    ctype: ClassVar[str] = "list"
    element_type: CtyType[T] = field(kw_only=True)
    value: list[T] = field(factory=list, kw_only=True)

    def __attrs_post_init__(self) -> None:
        """Validates that element_type is a CtyType instance after initialization."""
        if not isinstance(self.element_type, CtyType):
            message = f"Expected CtyType for element_type, got {type(self.element_type).__name__}"
            logger.error(f"🔌❗❌ {message}")
            raise CtyListValidationError(message)

    def validate(self, value: object) -> CtyValue:  # String literal
        logger.debug(f"🔌📝🔄 Validating value as CtyList: {type(value).__name__}")

        from pyvider.cty.types import CtyDynamic
        from pyvider.cty.values import CtyValue  # Local import kept for runtime

        if value is None:
            logger.error("🔌❗❌ CtyList.validate received None as input.")
            raise CtyListValidationError(
                "Input to CtyList.validate cannot be None. Use CtyValue.null(CtyList(...)) for a null list."
            )

        raw_list_to_validate: Sequence[object] | None = None
        if isinstance(value, CtyValue):
            if value.is_null:
                logger.debug(
                    "🔌📝✅ Input is a null CtyValue, resulting in a null list of this type."
                )
                return CtyValue.null(self)
            if value.is_unknown:
                logger.debug(
                    "🔌📝✅ Input is an unknown CtyValue, resulting in an unknown list of this type."
                )
                return CtyValue.unknown(self)

            if isinstance(value.type, CtyList):
                if isinstance(
                    self.element_type, CtyDynamic
                ) or value.type.element_type.usable_as(self.element_type):
                    logger.debug(
                        f"🔌📝🔄 Input CtyValue has compatible list type {value.type}. Validating its elements."
                    )
                    raw_list_to_validate = value.value
                else:
                    raise CtyListValidationError(
                        f"Input CtyValue has incompatible list element type: {value.type.element_type} vs {self.element_type}"
                    )
            else:
                raise CtyListValidationError(
                    f"Input CtyValue is not of a list type, got {value.type}"
                )
        elif isinstance(value, (list, tuple)):
            raw_list_to_validate = value
        else:
            logger.debug(
                f"🔌❗❌ Expected list, tuple, or CtyValue list, got {type(value).__name__}"
            )
            raise CtyListValidationError(
                f"Expected list, tuple, or CtyValue list, got {type(value).__name__}"
            )

        if raw_list_to_validate is None:
            logger.error(
                "🔌❗❌ Internal error: list_to_validate is None after initial checks."
            )
            raise CtyListValidationError(
                "Internal error: list to validate is None after initial checks."
            )

        if not raw_list_to_validate:
            logger.debug("🔌📝✅ Empty list - creating empty CtyList")
            return CtyValue(vtype=self, value=[])

        validated_elements = []
        validation_errors = []

        for i, item in enumerate(raw_list_to_validate):
            try:
                if isinstance(self.element_type, CtyDynamic) and isinstance(
                    item, CtyValue
                ):
                    validated_item = item
                else:
                    value_to_validate = (
                        item.value if isinstance(item, CtyValue) else item
                    )
                    validated_item = self.element_type.validate(value_to_validate)

                logger.debug(f"🔌📝✅ Validated item {i}: {item} -> {validated_item}")
                validated_elements.append(validated_item)
            except Exception as e:
                error_msg = f"Item {i} ('{item}'): {e!s}"
                logger.debug(f"🔌❗❌ {error_msg}")
                validation_errors.append(error_msg)

        if validation_errors:
            error_msg = "CtyList validation failed:\n - " + "\n - ".join(
                validation_errors
            )
            logger.error(f"🔌❗❌ {error_msg}")
            raise CtyListValidationError(error_msg)

        logger.debug(
            f"🔌📝✅ Successfully validated list with {len(validated_elements)} items"
        )
        return CtyValue(vtype=self, value=validated_elements)

    def element_at(self, container: object, index: int) -> CtyValue:  # String literal
        logger.debug(f"🔌🔍🔄 Getting element at index {index}")

        from pyvider.cty.values import CtyValue  # Local import kept

        if isinstance(container, CtyValue):
            if not isinstance(container.type, CtyList):
                message = f"Expected CtyValue with CtyList type, got CtyValue with {type(container.type).__name__}"
                logger.error(f"🔌❗❌ {message}")
                raise CtyListValidationError(message)
            return container.element_at(index)

        elif isinstance(container, CtyList):
            container_value = container.value
        elif isinstance(container, (list, tuple)):
            container_value = container
        else:
            message = f"Expected list, tuple, CtyList, or CtyValue with CtyList type, got {type(container).__name__}"
            logger.error(f"🔌❗❌ {message}")
            raise CtyListValidationError(message)

        try:
            list_len = len(container_value)
            if index < 0:
                index = list_len + index

            if index < 0 or index >= list_len:
                raise IndexError(f"Index {index} out of bounds (0-{list_len - 1})")

            result = container_value[index]
            logger.debug(f"🔌🔍✅ Got element at index {index}: {result}")
            return result
        except IndexError as e:
            message = f"Index out of bounds: {index}"
            logger.error(f"🔌❗❌ {message}")
            raise IndexError(message) from e

    def append(self, item: object) -> "CtyList[T]":
        logger.debug(f"🔌📝🔄 Appending item: {item}")
        try:
            validated_item = self.element_type.validate(item)
            new_list = list(self.value)
            new_list.append(validated_item)
            logger.debug(f"🔌📝✅ Appended item: {validated_item}")
            return evolve(self, value=new_list)
        except Exception as e:
            message = f"Failed to append item: {e}"
            logger.error(f"🔌❗❌ {message}")
            raise CtyListValidationError(message)

    def slice(self, start: int, end: int | None = None) -> "CtyList[T]":
        logger.debug(f"🔌🔍🔄 Slicing list from {start} to {end}")
        list_length = len(self.value)
        if end is None:
            end = list_length
        if start < 0:
            start = list_length + start
        if end < 0:
            end = list_length + end
        start = max(0, min(start, list_length))
        end = max(start, min(end, list_length))
        sliced_value = self.value[start:end]
        logger.debug(
            f"🔌🔍✅ Sliced list from {start} to {end}, result size: {len(sliced_value)}"
        )
        return evolve(self, value=sliced_value)

    def concat(self, other: "CtyList[T]") -> "CtyList[T]":
        logger.debug("🔌📝🔄 Concatenating with another list")
        if not isinstance(other, CtyList):
            message = f"Expected CtyList, got {type(other).__name__}"
            logger.error(f"🔌❗❌ {message}")
            raise CtyListValidationError(message)
        if not self.element_type.equal(other.element_type):
            message = f"Cannot concatenate lists with different element types: {self.element_type} and {other.element_type}"
            logger.error(f"🔌❗❌ {message}")
            raise CtyListValidationError(message)
        concat_value = list(self.value) + list(other.value)
        logger.debug(f"🔌📝✅ Concatenated lists, result size: {len(concat_value)}")
        return evolve(self, value=concat_value)

    def contains(self, item: object) -> bool:
        logger.debug(f"🔌🔍🔄 Checking if list contains item: {item}")
        try:
            validated_item = self.element_type.validate(item)
            for list_item in self.value:
                if hasattr(list_item, "value") and hasattr(validated_item, "value"):
                    if list_item.value == validated_item.value:
                        logger.debug(
                            f"🔌🔍✅ List contains item: {validated_item.value}"
                        )
                        return True
                if list_item == validated_item:
                    logger.debug(f"🔌🔍✅ List contains item: {validated_item}")
                    return True
            return False
        except Exception as e:
            logger.debug(f"🔌🔍❌ Validation failed: {e}")
            return False

    def usable_as(self, other: CtyType) -> bool:
        if not isinstance(other, CtyList):
            logger.debug(
                f"🔌📝❌ CtyList.usable_as: False (other is {type(other).__name__})"
            )
            return False
        result = self.element_type.usable_as(other.element_type)
        logger.debug(f"🔌📝✅ CtyList.usable_as: {result}")
        return result

    def equal(self, other: CtyType) -> bool:
        logger.debug("📋🔍🔄 CtyList.equal: comparing %s to %s", self, other)
        if not isinstance(other, CtyList):
            logger.debug("📋❌🔄  Other type is not CtyList → not equal")
            return False
        result = self.element_type.equal(other.element_type)
        logger.debug("📋🔍✅  Element‑type equality result: %s", result)
        return result

    def __len__(self) -> int:
        return len(self.value)

    def __iter__(self) -> Iterator[T]:
        return iter(self.value)

    def __getitem__(
        self, index: int | slice
    ) -> CtyValue | "CtyList":  # String literal for CtyValue
        if isinstance(index, slice):
            start = index.start if index.start is not None else 0
            stop = index.stop if index.stop is not None else len(self.value)
            if index.step is None or index.step == 1:
                return self.slice(start, stop)
            else:
                result = []
                for i in range(start, stop, index.step):
                    if i < len(self.value):
                        result.append(self.value[i])
                return evolve(self, value=result)
        try:
            return self.value[index]
        except IndexError:
            raise IndexError("list index out of range")

    def __str__(self) -> str:
        element_class = self.element_type.__class__.__name__
        if element_class == "CtyList":
            return f"list({self.element_type!s})"
        return f"list({element_class})"

    def __repr__(self) -> str:
        return f"CtyList(element_type={self.element_type!r})"

    def is_collection_type(self) -> bool:
        return True

    def is_list_type(self) -> bool:
        return True


# 🐍🏗️🐣
