from typing import Any, ClassVar, Generic, List as PyList, TypeVar, final
from attrs import define, evolve, field
from pyvider.cty.exceptions import ValidationError
from pyvider.cty.ctypes.base import CtyType
from pyvider.cty.logger import logger

T = TypeVar('T')

@final
@define(frozen=True, slots=True)
class CtyList(CtyType[PyList[T]], Generic[T]):
    """
    CtyList represents a list type in the Terraform type system.
    
    Lists are ordered collections of values of a specific element type.
    Unlike sets, lists can contain duplicate values and maintain order.
    """
    ctype: ClassVar[str] = "list"
    element_type: CtyType[T] = field(kw_only=True)  # Mandatory as keyword-only
    value: PyList[T] = field(factory=list, kw_only=True)  # Allow passing value via kw_only
    
    def __attrs_post_init__(self) -> None:
        """Validate element_type after initialization."""
        if not isinstance(self.element_type, CtyType):
            raise ValidationError(
                f"Expected CtyType for element_type, got {type(self.element_type)}"
            )
    
    def validate(self, value: Any) -> "CtyList":
        """
        Validate that the given value conforms to this list type.
        
        Args:
            value: The value to validate
            
        Returns:
            A new CtyList with the validated value
            
        Raises:
            ValidationError: If validation fails
        """
        logger.debug(f"🔌📝🔄 Validating value as CtyList: {type(value).__name__}")
        
        if value is None:
            logger.debug("🔌📝✅ Returning empty list for None value")
            return evolve(self, value=[])
            
        if not hasattr(value, '__iter__') or isinstance(value, (str, bytes, dict)):
            logger.debug(f"🔌❗❌ Expected iterable, got {type(value).__name__}")
            raise ValidationError(f"Expected iterable, got {type(value).__name__}")
            
        if not value:
            logger.debug("🔌📝✅ Returning empty list for empty iterable")
            return evolve(self, value=[])
            
        validated = []
        validation_errors = []
        
        for i, item in enumerate(value):
            try:
                validated_item = self.element_type.validate(item)
                validated.append(validated_item)
                logger.debug(f"🔌📝✅ Validated item {i}: {validated_item}")
            except Exception as e:
                error_msg = f"Item {i}: {item} -> {e!s}"
                logger.debug(f"🔌❗❌ {error_msg}")
                validation_errors.append(error_msg)
        
        if validation_errors:
            error_msg = "CtyList validation failed:\n" + "\n".join(validation_errors)
            logger.debug(f"🔌❗❌ {error_msg}")
            raise ValidationError(error_msg)
        
        logger.debug(f"🔌📝✅ Successfully validated list with {len(validated)} items")
        return evolve(self, value=validated)
    
    def element_at(self, container: PyList[T], index: int) -> T:
        """
        Get an element at a specific index in the list.
        
        Args:
            container: The list to get the element from
            index: The index to get the element at
            
        Returns:
            The element at the specified index
            
        Raises:
            ValidationError: If the container is not a list
            IndexError: If the index is out of bounds
        """
        if not isinstance(container, list):
            logger.debug(f"🔌❗❌ Expected list, got {type(container).__name__}")
            raise ValidationError(f"Expected list, got {type(container).__name__}")
            
        try:
            result = container[index]
            logger.debug(f"🔌📝✅ Got element at index {index}: {result}")
            return result
        except IndexError as e:
            logger.debug(f"🔌❗❌ Index out of bounds: {index}")
            raise IndexError(f"Index out of bounds: {index}") from e
    
    def append(self, item: T) -> "CtyList":
        """
        Append an item to the list.
        
        Args:
            item: The item to append
            
        Returns:
            A new CtyList with the item appended
            
        Raises:
            ValidationError: If the item cannot be validated
        """
        try:
            validated_item = self.element_type.validate(item)
            new_list = list(self.value)
            new_list.append(validated_item)
            logger.debug(f"🔌📝✅ Appended item to list: {validated_item}")
            return evolve(self, value=new_list)
        except Exception as e:
            logger.debug(f"🔌❗❌ Failed to append item: {e}")
            raise ValidationError(f"Failed to append item: {e}")
    
    def usable_as(self, other: "CtyType") -> bool:
        """
        Check if this type can be used as the other type.
        
        Args:
            other: The other type to check against
            
        Returns:
            True if this type can be used as the other type
        """
        result = isinstance(other, CtyList) and self.element_type.usable_as(other.element_type)
        logger.debug(f"🔌📝✅ CtyList.usable_as: {result}")
        return result
    
    def equal(self, other: "CtyType") -> bool:
        """
        Check if this type is equal to the other type.
        
        Args:
            other: The other type to check against
            
        Returns:
            True if the types are equal
        """
        if not isinstance(other, CtyList):
            logger.debug(f"🔌📝❌ CtyList.equal: False (other is {type(other).__name__})")
            return False
        result = self.element_type.equal(other.element_type)
        logger.debug(f"🔌📝✅ CtyList.equal: {result}")
        return result
    
    def __eq__(self, other):
        """
        Check if this list is equal to another list.
        
        Args:
            other: The other list to check against
            
        Returns:
            True if the lists are equal
        """
        if not isinstance(other, CtyList):
            return False
        return (
            self.element_type == other.element_type
            and self.value == other.value
        )
    
    def __iter__(self):
        """
        Iterate over the list values.
        
        Returns:
            An iterator over the list values
        """
        return iter(self.value)
    
    def __str__(self) -> str:
        """
        Get a string representation of this list type.
        
        Returns:
            A string representation
        """
        return f"list({self.element_type})"
