#
# pyvider/cty/values/base.py
#

"""
Core value representation for the Cty type system.

This module provides the CtyValue class, which is the fundamental building block
of the Cty type system. A CtyValue combines a raw value with its type information
and additional metadata like marks, unknown status, and null status.

CtyValue instances are immutable and serve as the primary way to work with typed
values throughout the Cty ecosystem. All operations preserve type information by
returning new CtyValue instances rather than raw values.
"""

from collections.abc import Iterator
from decimal import Decimal
import json  # Added for json.dumps in to_json_comparable_dict
from typing import (
    Generic,
    Self,
    TypeVar,
)

from attrs import define, evolve, field

from pyvider.cty.types import CtyType  # Keep this

# Removed CtyList, CtyMap, CtySet, CtyObject, CtyTuple from here, will use local imports or ensure they are properly scoped
from pyvider.telemetry import logger

T = TypeVar("T", covariant=True)


@define(frozen=True, slots=True)
class CtyValue(Generic[T]):
    """
    Immutable representation of a Cty value with type information.

    A CtyValue combines a raw value with its type and metadata such as whether
    the value is known (vs unknown) or null. This follows the go-cty value model
    and provides a consistent interface for working with typed values.

    CtyValues support a variety of operations including comparison, indexing,
    membership testing, and container operations, all while preserving type safety.
    Values can also carry marks which provide additional metadata.

    Attributes:
        _vtype: The Cty type of this value
        _value: The raw value (or None for null/unknown values)
        _is_unknown: Whether this value is unknown
        _is_null: Whether this value is null
        _marks: Set of marks applied to this value
        _key_mapping: For map values, tracks original CtyValue keys by string representation

    Examples:
        Creating a string value:
        >>> from pyvider.cty import CtyString, CtyValue
        >>> string_type = CtyString()
        >>> str_val = CtyValue(vtype=string_type, value="hello")
        >>> str_val.value
        'hello'

        Creating a null value:
        >>> null_val = CtyValue.null(string_type)
        >>> null_val.is_null
        True

        Creating an unknown value:
        >>> unknown_val = CtyValue.unknown(string_type)
        >>> unknown_val.is_unknown
        True
    """

    # Core attributes
    _vtype: CtyType[T] = field()
    _value: object | None = field(default=None)
    _is_unknown: bool = field(default=False)
    _is_null: bool = field(default=False)
    _marks: frozenset = field(factory=frozenset)
    _key_mapping: dict[str, "CtyValue"] = field(factory=dict)

    def __attrs_post_init__(self) -> None:
        """
        Perform post-initialization validation and logging.

        Logs information about the created CtyValue instance to aid in debugging.
        Also, corrects _is_null if it's True for a non-unknown value that has a non-None _value.
        """
        # Standard log
        try:
            value_repr = repr(self._value)
        except TypeError:
            value_repr = f"<UnhashableRepr for type {type(self._value).__name__}>"
        logger.debug(
            f"🔄🔧✅ Creating CtyValue of type {self._vtype.__class__.__name__}, unknown: {self._is_unknown}, null: {self._is_null}, value: {value_repr}"
        )

        # Correction logic for _is_null
        # self is frozen, so use object.__setattr__
        if not self._is_unknown and self._value is not None and self._is_null:
            logger.warning(
                f"Correcting _is_null to False for CtyValue of type {self._vtype.__class__.__name__} "
                f"with non-None _value ({self._value!r}) and _is_unknown=False."
            )
            object.__setattr__(self, "_is_null", False)

        # Ensure that if a value is unknown, it's not also null, and its internal value is None.
        if self._is_unknown:
            if self._is_null:
                logger.warning(
                    f"Correcting _is_null to False for CtyValue of type {self._vtype.__class__.__name__} "
                    f"because it is unknown."
                )
                object.__setattr__(self, "_is_null", False)
            if self._value is not None:
                logger.warning(
                    f"Correcting _value to None for CtyValue of type {self._vtype.__class__.__name__} "
                    f"because it is unknown."
                )
                object.__setattr__(self, "_value", None)
        # Ensure that if a value is null (and not unknown), its internal value is None.
        elif self._is_null:  # self._is_unknown is False here
            if self._value is not None:
                logger.warning(
                    f"Correcting _value to None for CtyValue of type {self._vtype.__class__.__name__} "
                    f"because it is null and not unknown."
                )
                object.__setattr__(self, "_value", None)

    @property
    def type(self) -> CtyType[T]:
        """
        Get the type of this value.

        Returns:
            CtyType: The type information for this value
        """
        return self._vtype

    @property
    def value(self) -> object | None:
        """
        Get the raw value of this CtyValue.

        For known, non-null values, returns the underlying value.
        For null values, returns None.
        For unknown values, raises ValueError.

        Returns:
            The raw value

        Raises:
            ValueError: If this value is unknown
        """
        if self._is_unknown:
            logger.warning("🔄❗⚠️ Attempted to get raw value of unknown value")
            raise ValueError("Cannot get raw value of unknown value")
        if self._is_null:
            logger.debug(
                "🔄🔍✅ Getting raw value of null value (returns None)"
            )  # Changed from warning
            return None
        return self._value

    @property
    def is_unknown(self) -> bool:
        """
        Check if this value is unknown.

        Unknown values represent placeholders for values that will be known later.
        They support the same operations as regular values, but the result will
        also be unknown.

        Returns:
            bool: True if the value is unknown, False otherwise
        """
        return self._is_unknown

    @property
    def is_null(self) -> bool:
        """
        Check if this value is null.

        Null values represent the absence of a value. Unlike unknown values,
        null values are known but have no content.

        Returns:
            bool: True if the value is null, False otherwise
        """
        logger.debug(
            f"CtyValue.is_null accessed for id {id(self)}: _is_null field is {self._is_null}, _value is {self._value!r}, type is {self._vtype.__class__.__name__}"
        )
        # An unknown value cannot be null.
        if self._is_unknown:
            return False
        # If _is_null is explicitly True, it's null.
        if self._is_null:
            return True
        # A CtyDynamic value is also considered null if its internal _value is None (and it's not unknown).
        from pyvider.cty.types import CtyDynamic  # Ensure it's in scope for isinstance

        if (
            isinstance(self._vtype, CtyDynamic) and self._value is None
        ):  # This check is now safe due to _is_unknown check above
            return True # SIM103: return (isinstance(self._vtype, CtyDynamic) and self._value is None)
        return False    # This part of SIM103 is more complex due to the initial _is_unknown check

    def has_mark(self, mark: object) -> bool:
        """
        Check if this value has a specific mark.

        Marks provide a way to attach metadata to values. This method checks
        if the specified mark is present by comparing string representations.

        Args:
            mark: The mark to check for

        Returns:
            bool: True if the value has the mark, False otherwise
        """
        # Use string equality rather than identity for more flexible comparison
        mark_str = str(mark)
        return any(str(m) == mark_str for m in self._marks)

    # -------------------------------------------------------------------------
    # Value modification methods
    # -------------------------------------------------------------------------
    def mark(self, mark: object) -> Self:
        """
        Add a mark to this value.

        Creates a new CtyValue with the same content plus the additional mark.
        Marks are useful for tracking metadata such as origin information or
        processing flags through value transformations.

        Args:
            mark: The mark to add

        Returns:
            CtyValue: A new CtyValue with the mark added
        """
        logger.debug(f"🔄🔧✅ Adding mark {mark} to value")
        # Need to pass all fields to evolve when frozen=True
        return evolve(
            self,
            vtype=self._vtype,
            value=self._value,
            is_unknown=self._is_unknown,
            is_null=self._is_null,
            marks=frozenset(self._marks.union({mark})),
            key_mapping=self._key_mapping,  # Preserve key mapping
        )

    def unmark(self) -> tuple[Self, frozenset]:
        """
        Remove all marks from this value and return them.

        Creates a new CtyValue without any marks and returns both the new
        value and the set of marks that were removed.

        Returns:
            tuple: (Unmarked CtyValue, FrozenSet of removed marks)
        """
        original_marks = self._marks
        logger.debug(f"🔄🔧✅ Removing {len(original_marks)} marks from value")
        # Need to pass all fields to evolve when frozen=True
        unmarked_value = evolve(
            self,
            vtype=self._vtype,
            value=self._value,
            is_unknown=self._is_unknown,
            is_null=self._is_null,
            marks=frozenset(),  # Clear marks
            key_mapping=self._key_mapping,  # Preserve key mapping
        )
        return unmarked_value, original_marks

    def with_marks(self, new_marks_set: set) -> Self:
        """
        Replace all marks on this value with a new set of marks.

        Creates a new CtyValue with the same content but with its marks
        replaced by the provided set.

        Args:
            new_marks_set: A set of new marks.

        Returns:
            CtyValue: A new CtyValue with the specified marks.
        """
        return evolve(self, marks=frozenset(new_marks_set))

    # -------------------------------------------------------------------------
    # Container operations
    # -------------------------------------------------------------------------
    def get(self, key: object, default: object | None = None) -> "CtyValue":
        """
        Get a value by key, with a default if not found.

        For map values, looks up the value associated with the key.
        For object values, retrieves the attribute with the given name.
        Other value types return the default.

        Args:
            key: The key to look up (string or CtyValue)
            default: Value to return if key not found

        Returns:
            CtyValue: The retrieved value, or the default if not found

        Raises:
            TypeError: If the value doesn't support key lookup and no default is provided
        """
        logger.debug(f"🔄🔍🔄 Getting value for key: {key}")

        # Cannot get from unknown or null values
        if self._is_unknown or self._is_null:
            logger.debug("🔄🔍⚠️ Cannot get from unknown/null value, returning default")
            return default

        # Import locally to avoid circular imports
        from pyvider.cty.types.collections import CtyMap
        from pyvider.cty.types.structural import CtyObject

        # For maps, use the map's get method
        if isinstance(self._vtype, CtyMap):
            try:
                # Ensure default is also a CtyValue if not None
                default_cty = None
                if default is not None:
                    # Attempt to validate default against map's value type
                    try:
                        default_cty = self._vtype.value_type.validate(default)
                    except Exception:
                        logger.warning(
                            f"Default value {default!r} is not compatible with map value type {self._vtype.value_type}"
                        )
                        # Test expects None if the provided default cannot be validated against the map's value type
                        return None
                # Call the map's get method
                return self._vtype.get(self, key, default_cty)  # Pass CtyValue default
            except Exception as e:  # This broad exception now catches issues from self._vtype.get as well
                # logger.warning(f"JULES_DEBUG: CtyMap get() EXCEPTION CAUGHT: {e!r}") # Removed JULES_DEBUG log and associated TODO.
                return default  # Return original python default

        # For objects, use the object's get_attribute method
        elif isinstance(self._vtype, CtyObject):
            try:
                # Key for object must be a string attribute name
                if not isinstance(key, str):
                    logger.debug(
                        f"🔄🔍⚠️ Object attribute key must be string, got {type(key).__name__}"
                    )
                    return default

                # Call the object's get_attribute method
                # This method should ideally handle 'has_attribute' check internally or raise appropriate Cty errors
                return self._vtype.get_attribute(self, key)
            except Exception as e:  # This broad exception now catches issues from self._vtype.get_attribute
                # logger.warning(
                #     f"JULES_DEBUG: CtyObject get_attribute() EXCEPTION CAUGHT: {e!r}"
                # ) # Removed JULES_DEBUG log and associated TODO.
                return default  # Return original python default

        # Value doesn't support key lookup
        logger.debug(
            f"🔄🔍⚠️ get() called on unsupported type: {self._vtype.__class__.__name__}"
        )
        return default

    def set(self, key: object, value: object) -> Self:
        """
        Set a value in a container.

        For map values, associates the key with the value.
        This operation is immutable - it returns a new CtyValue with the updated container.

        Args:
            key: The key to set (string or CtyValue)
            value: The value to set

        Returns:
            CtyValue: A new CtyValue with the updated container

        Raises:
            TypeError: If the value doesn't support key setting
            CtyMapValidationError: If validation fails during the operation
        """
        logger.debug(f"🔄📝🔄 Setting key {key!r} to value {value!r}")

        # Cannot set on unknown or null values
        if self._is_unknown or self._is_null:
            error_msg = "Cannot set key on unknown/null value"
            logger.error(f"🔄❗❌ {error_msg}")
            raise TypeError(error_msg)

        # Import locally to avoid circular imports
        from pyvider.cty.types.collections import CtyMap

        # For maps, use the map's set method
        if isinstance(self._vtype, CtyMap):
            new_value = self._vtype.set(self, key, value)
            return new_value

        # Value doesn't support key setting
        error_msg = (
            f"set() method not supported for type {self._vtype.__class__.__name__}"
        )
        logger.error(f"🔄❗❌ {error_msg}")
        raise TypeError(error_msg)

    def delete(self, key: object) -> Self:
        """
        Delete a key from a container.

        For map values, removes the key and its associated value.
        This operation is immutable - it returns a new CtyValue with the updated container.

        Args:
            key: The key to delete (string or CtyValue)

        Returns:
            CtyValue: A new CtyValue with the updated container

        Raises:
            TypeError: If the value doesn't support key deletion
            CtyMapValidationError: If validation fails during the operation
        """
        logger.debug(f"🔄📝🔄 Deleting key {key!r}")

        # Cannot delete on unknown or null values
        if self._is_unknown or self._is_null:
            error_msg = "Cannot delete key from unknown/null value"
            logger.error(f"🔄❗❌ {error_msg}")
            raise TypeError(error_msg)

        # Import locally to avoid circular imports
        from pyvider.cty.types.collections import CtyMap

        # For maps, use the map's delete method
        if isinstance(self._vtype, CtyMap):
            new_value = self._vtype.delete(self, key)
            return new_value

        # Value doesn't support key deletion
        error_msg = (
            f"delete() method not supported for type {self._vtype.__class__.__name__}"
        )
        logger.error(f"🔄❗❌ {error_msg}")
        raise TypeError(error_msg)

    def element_at(self, index: int) -> "CtyValue":
        """
        Get element at a specific index for list/tuple values.

        For list values, returns the element at the specified index.
        For tuple values, returns the element at the specified position.

        Args:
            index: The index to get the element at (supports negative indices)

        Returns:
            CtyValue: The element at that index

        Raises:
            TypeError: If the value doesn't support indexing
            IndexError: If the index is out of bounds
        """
        logger.debug(f"🔄🔍🔄 Getting element at index {index}")

        # Cannot index into unknown or null values
        if self._is_unknown or self._is_null:
            error_msg = "Cannot get element from unknown or null value"
            logger.error(f"🔄❗❌ {error_msg}")
            raise TypeError(error_msg)

        # Import locally to avoid circular imports
        from pyvider.cty.types.collections import CtyList
        from pyvider.cty.types.structural import CtyTuple

        # Direct implementation to avoid recursion with __getitem__
        if isinstance(self._vtype, CtyList): # Local import CtyList
            # Ensure the underlying value is a list or tuple
            if not isinstance(self._value, list | tuple): # UP038
                raise TypeError(
                    f"Cannot index list value of type {type(self._value).__name__}"
                )
            # Handle negative indices
            list_len = len(self._value)
            actual_index = list_len + index if index < 0 else index

            # Check bounds
            if actual_index < 0 or actual_index >= list_len:
                error_msg = f"List index {index} out of bounds (size {list_len})"
                logger.error(f"🔄❗❌ {error_msg}")
                raise IndexError(error_msg)

            # Get the element at the specified index
            return self._value[actual_index]  # Assume, value contains CtyValues
        elif isinstance(self._vtype, CtyTuple):
            # Delegate to the tuple type's method, passing the internal value
            return self._vtype.element_at(self._value, index)
        else:
            # Value doesn't support indexing
            error_msg = f"element_at method not supported for type {self._vtype.__class__.__name__}"
            logger.error(f"🔄❗❌ {error_msg}")
            raise TypeError(error_msg)

    # -------------------------------------------------------------------------
    # Factory methods
    # -------------------------------------------------------------------------
    @classmethod
    def bool(cls, value: bool) -> "CtyValue":
        """
        Create a boolean value.

        Factory method to create a CtyValue with boolean type.

        Args:
            value: The boolean value (True or False)

        Returns:
            CtyValue: A new CtyValue with CtyBool type and the given value
        """
        from pyvider.cty.types import CtyBool

        logger.debug(f"🔄🔧✅ Creating bool value: {value}")
        return cls(vtype=CtyBool(), value=value)  # Use internal names

    @classmethod
    def string(cls, value: str) -> "CtyValue":
        """
        Create a string value.

        Factory method to create a CtyValue with string type.

        Args:
            value: The string value

        Returns:
            CtyValue: A new CtyValue with CtyString type and the given value
        """
        from pyvider.cty.types import CtyString

        logger.debug(f"🔄🔧✅ Creating string value: {value}")
        return cls(vtype=CtyString(), value=value)  # Use internal names

    @classmethod
    def number(cls, value: int | float | Decimal) -> "CtyValue":
        """
        Create a number value.

        Factory method to create a CtyValue with number type.
        Accepts integers, floats, and Decimal values.

        Args:
            value: The number value (int, float, or Decimal)

        Returns:
            CtyValue: A new CtyValue with CtyNumber type and the given value
        """
        from pyvider.cty.types import CtyNumber

        # Convert int/float to Decimal for consistency internally
        decimal_value = Decimal(value)
        logger.debug(f"🔄🔧✅ Creating number value: {decimal_value}")
        return cls(vtype=CtyNumber(), value=decimal_value)

    @classmethod
    def list(cls, element_type: CtyType, elements: list) -> "CtyValue":
        """
        Create a list value.

        Factory method to create a CtyValue with list type.
        The elements will be validated against the element_type.

        Args:
            element_type: The type of the list elements
            elements: The list elements (will be validated)

        Returns:
            CtyValue: A new CtyValue with CtyList type containing the validated elements
        """
        from pyvider.cty.types import CtyList

        logger.debug(f"🔄🔧✅ Creating list value with {len(elements)} elements")
        # Create list type and validate the elements
        list_type = CtyList(element_type=element_type)
        # Validate returns a CtyValue, so return it directly
        return list_type.validate(elements)

    @classmethod
    def map(cls, key_type: CtyType, value_type: CtyType, items: dict) -> "CtyValue":
        """
        Create a map value.

        Factory method to create a CtyValue with map type.
        Both keys and values will be validated against their respective types.

        Args:
            key_type: The type of map keys (must be CtyString)
            value_type: The type of map values
            items: The map items as a dictionary

        Returns:
            CtyValue: A new CtyValue with CtyMap type containing the validated items
        """
        from pyvider.cty.types import CtyMap

        logger.debug(f"🔄🔧✅ Creating map value with {len(items)} items")
        # Create map type and validate the items
        map_type = CtyMap(key_type=key_type, value_type=value_type)
        # Validate returns a CtyValue, so return it directly
        return map_type.validate(items)

    @classmethod
    def make_set(
        cls, element_type: CtyType, elements: set
    ) -> "CtyValue":  # Renamed from 'set'
        """
        Create a set value.

        Factory method to create a CtyValue with set type.
        The elements will be validated against the element_type.

        Args:
            element_type: The type of the set elements
            elements: The set elements (will be validated)

        Returns:
            CtyValue: A new CtyValue with CtySet type containing the validated elements
        """
        from pyvider.cty.types import CtySet

        logger.debug(f"🔄🔧✅ Creating set value with {len(elements)} elements")
        # Create set type and validate the elements
        set_type = CtySet(element_type=element_type)
        # Validate returns a CtyValue, so return it directly
        return set_type.validate(elements)

    @classmethod
    def tuple(cls, element_types: tuple, elements: tuple) -> "CtyValue":
        """
        Create a tuple value.

        Factory method to create a CtyValue with tuple type.
        Each element will be validated against its corresponding type.

        Args:
            element_types: A tuple of types for each position in the tuple
            elements: The tuple elements (will be validated)

        Returns:
            CtyValue: A new CtyValue with CtyTuple type containing the validated elements
        """
        from pyvider.cty.types import CtyTuple

        logger.debug(f"🔄🔧✅ Creating tuple value with {len(elements)} elements")
        # Create tuple type and validate the elements
        tuple_type = CtyTuple(element_types=element_types)
        # Validate returns a CtyValue, so return it directly
        return tuple_type.validate(elements)

    @classmethod
    def object(cls, attribute_types: dict, attributes: dict) -> "CtyValue":
        """
        Create an object value.

        Factory method to create a CtyValue with object type.
        Each attribute will be validated against its corresponding type.

        Args:
            attribute_types: Dictionary mapping attribute names to their types
            attributes: Dictionary of attribute values

        Returns:
            CtyValue: A new CtyValue with CtyObject type containing the validated attributes

        Raises:
            CtyValidationError: If validation fails for any attribute
        """
        from pyvider.cty.exceptions import CtyValidationError
        from pyvider.cty.types import CtyObject

        logger.debug(f"🔄🔧✅ Creating object value with {len(attributes)} attributes")

        actual_attribute_types_dict: dict
        if isinstance(attribute_types, CtyObject):
            actual_attribute_types_dict = attribute_types.attribute_types
        elif isinstance(attribute_types, dict):
            actual_attribute_types_dict = attribute_types
        else:
            raise CtyValidationError(
                f"Expected CtyObject or dict for attribute_types, got {type(attribute_types).__name__}"
            )

        # Validate attribute_types contains CtyType instances
        for attr_name, attr_type in actual_attribute_types_dict.items():
            if not isinstance(attr_type, CtyType):
                raise CtyValidationError(
                    f"Expected CtyType for attribute '{attr_name}', got {type(attr_type).__name__}"
                )

        # Create object type and validate
        # Pass the validated dictionary of types to CtyObject constructor
        object_type = CtyObject(attribute_types=actual_attribute_types_dict)
        # Validate returns a CtyValue, so return it directly
        return object_type.validate(attributes)

    @classmethod
    def unknown(cls, vtype: CtyType) -> "CtyValue":
        """
        Create an unknown value of the given type.

        Factory method to create a CtyValue marked as unknown.
        Unknown values represent placeholders for values that will be known later.

        Args:
            vtype: The type of the unknown value

        Returns:
            CtyValue: A new CtyValue marked as unknown with the specified type
        """
        logger.debug(
            f"🔄🔧✅ Creating unknown value of type {vtype.__class__.__name__}"
        )
        return cls(vtype=vtype, is_unknown=True)  # Use internal names

    @classmethod
    def null(cls, vtype: CtyType) -> "CtyValue":
        """
        Create a null value of the given type.

        Factory method to create a CtyValue marked as null.
        Null values represent the absence of a value for a specific type.

        Args:
            vtype: The type of the null value

        Returns:
            CtyValue: A new CtyValue marked as null with the specified type
        """
        logger.debug(f"🔄🔧✅ Creating null value of type {vtype.__class__.__name__}")
        return cls(vtype=vtype, is_null=True)  # Use internal names

    @classmethod
    def list_of_dynamic(cls, elements: list) -> "CtyValue":
        from pyvider.cty.types import CtyDynamic, CtyList  # Local import

        logger.debug(
            f"🔄🔧✅ Creating dynamic list value with {len(elements)} elements"
        )
        list_type = CtyList(element_type=CtyDynamic())
        return list_type.validate(elements)

    @classmethod
    def map_of_dynamic(cls, key_type: CtyType, items: dict) -> "CtyValue":
        from pyvider.cty.types import CtyDynamic, CtyMap  # Local import

        # Consider adding a default for key_type=CtyString() if always string keys for maps
        logger.debug(f"🔄🔧✅ Creating dynamic map value with {len(items)} items")
        map_type = CtyMap(key_type=key_type, value_type=CtyDynamic())
        return map_type.validate(items)

    # -------------------------------------------------------------------------
    # Serialization
    # -------------------------------------------------------------------------
    def to_dict(self) -> dict:
        """
        Convert to dictionary representation for serialization.

        Creates a dictionary representation of this value that can be used
        for serialization to formats like JSON or MessagePack.

        Returns:
            dict: Dictionary representation of this value with type information,
                  value state, and any marks
        """
        logger.debug("🔄🔧✅ Converting CtyValue to dictionary")
        result = {
            "type": self._vtype.__class__.__name__,
        }

        # Handle different value types for JSON serialization
        if self._is_unknown:
            result["is_unknown"] = True
        elif self._is_null:
            result["is_null"] = True
        else:
            # Handle collection types
            if isinstance(self._value, set | frozenset):
                # Recursively call to_dict on set elements if they are CtyValues
                result["value"] = [
                    v.to_dict() if isinstance(v, CtyValue) else v for v in self._value
                ]
            elif isinstance(self._value, dict):
                # For dictionaries, convert keys and values
                serialized_dict = {}
                for k, v in self._value.items():
                    # Keys i, value are strings from validation
                    value = v.to_dict() if isinstance(v, CtyValue) else v
                    serialized_dict[k] = value
                result["value"] = serialized_dict
            elif isinstance(self._value, list | tuple):
                # For lists/tuples, convert each element
                result["value"] = [
                    v.to_dict() if isinstance(v, CtyValue) else v for v in self._value
                ]
            elif isinstance(self._value, Decimal):
                # Convert Decimal to string for JSON compatibility
                result["value"] = str(self._value)
            elif self._value is not None:
                # Use the raw value for primitives
                result["value"] = self._value

        # Add marks if present
        if self._marks:
            result["marks"] = list(str(m) for m in self._marks)

        return result

    # -------------------------------------------------------------------------
    # Python special methods
    # -------------------------------------------------------------------------
    def __len__(self) -> int:
        """
        Get the length of this value, if it supports the operation.

        For collections (lists, maps, sets, tuples), returns the number of elements.
        For strings, returns the string length.

        Returns:
            int: The length of the value

        Raises:
            TypeError: If the value doesn't support length operation
        """
        # Cannot get length of unknown values
        if self._is_unknown:
            error_msg = "Cannot get length of unknown value"
            logger.error(f"🔄❗❌ {error_msg}")
            raise TypeError(error_msg)

        # Cannot get length of null values
        if self._is_null:
            # Length of null is defined as 0 in some contexts (like Terraform)
            logger.debug("🔄🔍✅ Length of null value is 0")
            return 0

        # For known values, delegate to the underlying value
        if hasattr(self._value, "__len__"):
            return len(self._value)

        # Value doesn't support length
        error_msg = f"Value of type {self._vtype.__class__.__name__} (inner: {type(self._value).__name__}) doesn't support length operation"
        logger.error(f"🔄❗❌ {error_msg}")
        raise TypeError(error_msg)

    def __iter__(self) -> Iterator:
        """
        Iterate over the elements in this value.

        For collections (lists, maps, sets, tuples), yields each element.
        For strings, yields each character.

        Returns:
            Iterator: An iterator over the elements

        Raises:
            TypeError: If the value doesn't support iteration
        """
        # Cannot iterate unknown or null values
        if self._is_unknown:
            error_msg = "Cannot iterate unknown value"
            logger.error(f"🔄❗❌ {error_msg}")
            raise TypeError(error_msg)

        if self._is_null:
            # Allow iterating over null (yields nothing)
            logger.debug("🔄🔍✅ Iterating over null value (yields nothing)")
            return iter([])
            # error_msg = "Cannot iterate null value"
            # logger.error(f"🔄❗❌ {error_msg}")
            # raise TypeError(error_msg)

        # For collections, iterate over the values
        if hasattr(self._value, "__iter__") and not isinstance(self._value, dict):
            # Iterate directly for lists, tuples, sets, strings
            return iter(self._value)
        elif isinstance(self._value, dict):
            # For maps/objects, iterate over keys (strings)
            return iter(self._value.keys())

        # Value doesn't support iteration
        error_msg = f"Value of type {self._vtype.__class__.__name__} (inner: {type(self._value).__name__}) doesn't support iteration"
        logger.error(f"🔄❗❌ {error_msg}")
        raise TypeError(error_msg)

    def __hash__(self) -> int:
        """
        Make CtyValue instances hashable for use in sets and as dict keys.

        Computes a hash based on type, value state, and marks. For primitive
        types, includes the actual value in the hash computation.

        Returns:
            int: Hash value
        """
        # Hash based on type, value state, marks
        type_hash = hash(
            self._vtype.__class__
        )  # Use class to ensure CtyString() == CtyString()
        state_hash = hash((self._is_unknown, self._is_null))
        marks_hash = hash(self._marks)  # Hash the frozenset of marks

        value_hash = 0
        if self._is_unknown or self._is_null:
            value_hash = hash(None)  # Consistent hash for null/unknown
        else:
            # Use the actual value's hash for hashable primitives
            if isinstance(self._value, str | int | float | bool | Decimal | bytes): # UP038
                try:
                    value_hash = hash(self._value)
                except TypeError:  # Should not happen for these types, but safeguard
                    value_hash = hash(repr(self._value))
            # For tuples, ensure elements are hashable (should be if validated)
            elif isinstance(self._value, tuple):
                try:
                    # Hash tuple elements (which should be CtyValues)
                    value_hash = hash(self._value)
                except TypeError:
                    # Fallback if elements aren't hashable CtyValues somehow
                    value_hash = hash(repr(self._value))
            # For frozensets (results of set validation)
            elif isinstance(self._value, frozenset):
                try:
                    value_hash = hash(self._value)
                except TypeError:
                    value_hash = hash(repr(self._value))
            # Dictionaries and lists are not typically hashable by value
            # Hashing based on type/state/marks only for these might be sufficient
            # or use repr as a less reliable fallback
            elif isinstance(self._value, dict | list | set): # UP038
                value_hash = hash(repr(self._value))  # Fallback hash using repr
            else:
                # Fallback for other potentially unhashable types
                try:
                    value_hash = hash(repr(self._value))
                except TypeError:
                    value_hash = hash(id(self._value))  # Identity hash

        # Combine component hashes
        return hash((type_hash, state_hash, value_hash, marks_hash))

    def __eq__(self, other: object) -> bool:
        """
        Check if two CtyValue instances are equal.

        Values are equal if they have the same type, state (known/unknown/null),
        the same marks, and equal values (for known, non-null values).
        Map comparison ignores the internal _key_mapping.

        Args:
            other: The other value to compare with

        Returns:
            bool: True if values are equal, False otherwise
        """
        # Check type first
        if not isinstance(other, CtyValue):
            return False  # Or return NotImplemented for stricter Python semantics, False is simpler here.

        # Check CtyValue type compatibility
        if not self._vtype.equal(other._vtype):
            return False

        # Check state (unknown, null)
        if self._is_unknown != other._is_unknown:
            return False
        if self._is_null != other._is_null:
            return False

        # If both are unknown or both are null (and same type), they are equal
        if (self._is_unknown and other._is_unknown) or (
            self._is_null and other._is_null
        ):
            return True  # Marks must also match for true equality if needed

        # Check marks (only if needed based on requirements, often ignored for value equality)
        # If marks matter for equality, uncomment:
        if self._marks != other._marks:
            return False

        # --- Compare values for known, non-null values ---
        # Use direct comparison for primitives
        if isinstance(self._value, str | int | float | bool | Decimal | bytes): # UP038
            # Handle Decimal comparison carefully
            if isinstance(self._value, Decimal) and isinstance(other._value, int | float | str): # SIM102, UP038 (inner)
                try:
                    return self._value == Decimal(other._value)
                except Exception:
                    return False
            return self._value == other._value

        # For lists and tuples, compare element-wise
        if isinstance(self._value, list | tuple) and isinstance( # UP038
            other._value, list | tuple # UP038
        ):
            if len(self._value) != len(other._value):
                return False
            # Elements should be CtyValues, rely on their __eq__
            return all(a == b for a, b in zip(self._value, other._value, strict=False))

        # For sets (represented as frozenset internally after validation)
        if isinstance(self._value, set | frozenset) and isinstance( # UP038
            other._value, set | frozenset # UP038
        ):
            # Elements should be CtyValues, rely on their __eq__ and hash
            if len(self._value) != len(other._value):
                return False
            return self._value == other._value  # Relies on CtyValue hash/eq

        # For maps (dictionaries), compare content, ignore _key_mapping
        # Keys i, value are strings, values are CtyValues
        if isinstance(self._value, dict) and isinstance(other._value, dict):
            if len(self._value) != len(other._value):
                return False
            # Compare string keys and the CtyValues they map to
            return self._value == other._value

        # Fallback for other types (e.g., custom objects not handled above)
        try:
            return self._value == other._value
        except Exception:
            return False  # If comparison fails

    def __getitem__(self, key: object) -> "CtyValue":
        """
        Support for container indexing operations.

        For maps, gets the value for the given key.
        For lists/tuples, gets the element at the given index or slice.
        For objects, gets the attribute with the given name.

        Args:
            key: The key, index, or attribute name

        Returns:
            CtyValue: The value at the key/index

        Raises:
            TypeError: If the value doesn't support indexing
            KeyError: If the key doesn't exist
            IndexError: If the index is out of bounds
        """
        logger.debug(f"🔄🔍🔄 Getting item with key/index: {key}")

        # Cannot index into unknown or null values
        if self._is_unknown or self._is_null:
            error_msg = "Cannot index into unknown or null value"
            logger.error(f"🔄❗❌ {error_msg}")
            raise TypeError(error_msg)

        # Import locally to avoid circular imports
        from pyvider.cty.exceptions import (
            CtyAttributeValidationError,
            CtyValidationError,
        )
        from pyvider.cty.types.collections import CtyList, CtyMap
        from pyvider.cty.types.structural import CtyObject, CtyTuple

        try:
            # Check for CtyObject type first for specific attribute handling
            if isinstance(self._vtype, CtyObject):
                if not isinstance(key, str):
                    raise TypeError(
                        f"Object attribute name must be a string, got {type(key).__name__}"
                    )
                # Use get_attribute which handles schema checking and optional nulls
                return self._vtype.get_attribute(self, key)

            # For maps, check key in values
            elif isinstance(self._vtype, CtyMap):
                # Convert input key to string for lookup
                str_key = None
                if isinstance(key, CtyValue):
                    if (
                        isinstance(key.type, self._vtype.key_type.__class__)
                        and not key.is_null
                        and not key.is_unknown
                    ):
                        str_key = str(key.value)
                    else:
                        raise KeyError(
                            f"Invalid CtyValue key type or state for map lookup: {key!r}"
                        )
                else:
                    # Try to validate the raw key
                    try:
                        validated_key = self._vtype.key_type.validate(key)
                        if validated_key.is_null or validated_key.is_unknown:
                            raise KeyError(
                                f"Map key cannot be null or unknown: {key!r}"
                            )
                        str_key = str(validated_key.value)
                    except (
                        CtyValidationError
                    ) as e:  # Changed CtyMapValidationError to CtyValidationError
                        raise KeyError(f"Invalid key for map lookup: {key!r} ({e})")

                if str_key in self._value:
                    return self._value[str_key]
                else:
                    raise KeyError(
                        f"Key not found in map: {key!r} (lookup: '{str_key}')"
                    )

            # For lists/tuples, handle both direct indexing and slices
            elif isinstance(self._vtype, CtyList | CtyTuple): # UP038
                if isinstance(key, slice):
                    # Handle slice operations
                    start = key.start if key.start is not None else 0
                    stop = key.stop if key.stop is not None else len(self._value)
                    step = key.step or 1

                    # Create sliced list of values
                    sliced_values = self._value[start:stop:step]

                    # For tuples, create a new tuple type for the slice
                    if isinstance(self._vtype, CtyTuple):
                        element_types = self._vtype.element_types[start:stop:step]
                        from pyvider.cty.types import CtyTuple  # Local import

                        tuple_type = CtyTuple(element_types=element_types)
                        return CtyValue(
                            vtype=tuple_type, value=tuple(sliced_values)
                        )  # Return CtyValue
                    # For lists, maintain element type
                    else:
                        # Return a new CtyValue wrapping the sliced list
                        return CtyValue(vtype=self._vtype, value=sliced_values)
                else:
                    # Handle direct indexing using element_at for bounds checking
                    return self.element_at(key)  # element_at handles IndexError

            # Value doesn't support indexing
            error_msg = f"Value of type {self._vtype.__class__.__name__} doesn't support indexing with '{key!r}'"
            logger.error(f"🔄❗❌ {error_msg}")
            raise TypeError(error_msg)

        except CtyAttributeValidationError as e:
            logger.error(f"🔄❗❌ {e}")
            # Reraise specific Cty errors
            raise e
        except KeyError as e:
            # Re-raise KeyError
            logger.error(f"🔄❗❌ Key error: {e}")
            raise
        except IndexError as e:
            # Re-raise IndexError
            logger.error(f"🔄❗❌ Index error: {e}")
            raise
        except Exception as e:
            # Wrap other exceptions
            error_msg = f"Error during indexing with '{key!r}': {e}"
            logger.error(f"🔄❗❌ {error_msg}")
            raise TypeError(error_msg) from e

    def __contains__(self, item: object) -> bool:
        """
        Support for 'in' operator with proper value comparison.

        For maps, checks if the key exists.
        For lists/tuples/sets, checks if the item is present.
        For objects, checks if the attribute exists.
        For strings, checks if the substring is present.

        Args:
            item: The item to check for

        Returns:
            bool: True if the item is in the container, False otherwise

        Raises:
            TypeError: If the value doesn't support membership testing
        """
        logger.debug(f"🔄🔍🔄 Checking if {item} is in container")

        # Cannot check membership in unknown or null values
        if self._is_unknown or self._is_null:
            error_msg = "Cannot check membership in unknown or null value"
            logger.error(f"🔄❗❌ {error_msg}")
            # Following Python's lead, 'in' on None raises TypeError
            raise TypeError(error_msg)

        # Import locally to avoid circular imports
        from pyvider.cty.types.collections import CtyList, CtyMap, CtySet
        from pyvider.cty.types.structural import CtyObject

        try:
            # For maps, check keys (using string representation)
            if isinstance(self._vtype, CtyMap):
                str_key = None
                if isinstance(item, CtyValue):
                    # Check if key is valid type and state
                    if (
                        isinstance(item.type, self._vtype.key_type.__class__)
                        and not item.is_null
                        and not item.is_unknown
                    ):
                        str_key = str(item.value)
                    else:
                        return False  # Invalid key type/state cannot be in map
                else:
                    # Try validating the raw item as a key
                    try:
                        validated_key = self._vtype.key_type.validate(item)
                        if validated_key.is_null or validated_key.is_unknown:
                            return False  # Null/unknown keys cannot be in map
                        str_key = str(validated_key.value)
                    except Exception:
                        return False  # If item cannot be validated as key, it's not in the map

                return str_key in self._value  # Check string key presence

            # For lists/sets/tuples, check elements using CtyValue equality
            elif isinstance(self._vtype, CtyList | CtySet) or ( # UP038
                hasattr(self._vtype, "element_type")
                and hasattr(self._value, "__iter__")
            ):  # General collection check
                # Try to validate the item against the element type
                try:
                    validated_item = self._vtype.element_type.validate(item)
                except Exception:
                    # If item cannot be validated, it cannot be contained
                    return False
                # Check if the validated item is in the collection
                # Assume, value contains CtyValue elements after validation
                return validated_item in self._value

            # For objects, check attributes by name
            elif isinstance(self._vtype, CtyObject):
                return isinstance(item, str) and self._vtype.has_attribute(item)

            # For strings, check substring
            elif isinstance(self._value, str):
                return isinstance(item, str) and item in self._value

            # Fallback for other iterable types
            elif hasattr(self._value, "__contains__"):
                return item in self._value

            # Value doesn't support membership testing
            error_msg = f"Value of type {self._vtype.__class__.__name__} doesn't support membership testing for '{item!r}'"
            logger.error(f"🔄❗❌ {error_msg}")
            raise TypeError(error_msg)

        except TypeError as e:
            # Propagate TypeErrors from underlying operations
            raise e
        except Exception as e:
            # Catch other potential errors during validation/comparison
            logger.debug(f"🔄❗⚠️ Error during membership test for '{item!r}': {e}")
            return False

    def __bool__(self) -> bool:
        """
        Boolean evaluation of this value.

        Unknown and null values are considered falsy.
        For known, non-null values, delegates to Python's standard truthiness rules.

        Returns:
            bool: True if the value is truthy, False otherwise
        """
        # Unknown and null values are always falsy
        if self._is_unknown or self._is_null:
            return False

        # For known, non-null values, use Python's truthiness rules
        return bool(self._value)

    def is_true(self) -> bool:
        """
        Check if this value is explicitly True.
        Unknown and null values are not True.
        """
        if self._is_unknown or self._is_null:
            return False
        if isinstance(self._value, CtyValue):
            return self._value.is_true()
        return self._value is True

    def is_false(self) -> bool:
        """
        Check if this value is explicitly False.
        Unknown and null values are not False.
        """
        if self._is_unknown or self._is_null:
            return False
        if isinstance(self._value, CtyValue):
            return self._value.is_false()
        return self._value is False

    def is_empty(self) -> bool:
        """
        Check if this value is empty.

        - Unknown and null values are considered empty.
        - Strings are empty if they are "".
        - Collections (lists, maps, sets) are empty if they have no elements.
        - Other types are generally not considered empty unless their specific logic defines it.
        """
        if self._is_unknown or self._is_null:
            return True

        # If the value is a CtyValue itself (e.g. for CtyDynamic holding another CtyValue),
        # delegate the emptiness check to the inner CtyValue.
        if isinstance(self._value, CtyValue):
            return self._value.is_empty()

        if isinstance(self._value, str | list | tuple | dict | set | frozenset): # UP038
            return (
                not self._value
            )  # Relies on Python's built-in truthiness for empty collections/strings

        # For other types (like numbers, booleans), they are generally not considered "empty"
        # in the same way collections or strings are.
        return False

    def __str__(self) -> str:
        """
        String representation for display.

        Returns a human-readable string representation of the value.

        Returns:
            str: String representation of this value
        """
        if self._is_unknown:
            return f"<unknown {self._vtype.__class__.__name__}>"
        if self._is_null:
            return f"<null {self._vtype.__class__.__name__}>"

        # For known, non-null values, convert to string
        # Special handling for collections for better readability?
        if isinstance(self._value, list):
            return f"[{', '.join(str(v) for v in self._value)}]"
        if isinstance(self._value, dict):
            # Use string keys fro, value
            return f"{{{', '.join(f'{k!r}: {v}' for k, v in self._value.items())}}}"
        if isinstance(self._value, set | frozenset): # UP038
            # Sort set elements for consistent string representation
            try:
                sorted_elements = sorted(self._value, key=repr)
                return f"{{{', '.join(str(v) for v in sorted_elements)}}}"
            except TypeError:  # Handle unorderable elements
                return f"{{{', '.join(str(v) for v in self._value)}}}"

        return str(self._value)

    def __repr__(self) -> str:
        """
        Detailed string representation for debugging.

        Returns a detailed representation including type, state, marks, and value.

        Returns:
            str: Detailed string representation
        """
        parts = [
            # Use actual type instance representation
            f"vtype={self._vtype!r}",
        ]

        if not self._is_unknown and not self._is_null:
            # Use repr for the internal value
            parts.append(f"value={self._value!r}")
        if self._is_unknown:
            parts.append("is_unknown=True")
        if self._is_null:
            parts.append("is_null=True")
        if self._marks:
            # Use repr for marks
            parts.append(f"marks={self._marks!r}")
        # Include key_mapping if it's not empty and type is map
        from pyvider.cty.types.collections import CtyMap

        if isinstance(self._vtype, CtyMap) and self._key_mapping:
            parts.append(f"key_mapping={self._key_mapping!r}")

        return f"CtyValue({', '.join(parts)})"

    def to_json_comparable_dict(self) -> dict:
        """
        Converts the CtyValue to a dictionary suitable for JSON comparison.

        This method is designed to produce a representation that can be easily
        compared with similar structures generated by other Cty implementations (e.g., Go).

        Returns:
            dict: A dictionary with "type_name", "value", "is_unknown", "is_null", and "marks".
        """
        # Local imports to avoid circular dependencies at module load time
        # Ensure CtyTuple is imported here if not already (it's used below)
        from pyvider.cty.types import (
            CtyBool,
            CtyDynamic,
            CtyList,
            CtyMap,
            CtyNumber,
            CtyObject,
            CtySet,
            CtyString,
            CtyTuple,
        )

        type_name = "dynamic"  # Default for CtyDynamic or if type not easily matched

        # Helper to get the friendly type name, including for nested types in collections
        def get_friendly_type_name(cty_type_instance: CtyType) -> str:
            if isinstance(cty_type_instance, CtyString):
                return "string"
            if isinstance(cty_type_instance, CtyNumber):
                return "number"
            if isinstance(cty_type_instance, CtyBool):
                return "bool"
            if isinstance(cty_type_instance, CtyDynamic):
                return "dynamic"
            if isinstance(cty_type_instance, CtyList):
                element_friendly_name = get_friendly_type_name(
                    cty_type_instance.element_type
                )
                return f"list({element_friendly_name})"
            if isinstance(
                cty_type_instance, CtySet
            ):  # Assuming CtySet has element_type
                element_friendly_name = get_friendly_type_name(
                    cty_type_instance.element_type
                )
                return f"set({element_friendly_name})"
            if isinstance(
                cty_type_instance, CtyMap
            ):  # Assuming CtyMap has value_type for elements
                # For POC, map keys are strings, so we describe the value type.
                # A full map type description might be like "map(string, number)"
                element_friendly_name = get_friendly_type_name(
                    cty_type_instance.value_type
                )
                return (
                    f"map({element_friendly_name})"  # Simplified, assumes string keys
                )
            if isinstance(cty_type_instance, CtyObject):
                attrs_desc = []
                for name, attr_type in sorted(
                    cty_type_instance.attribute_types.items()
                ):  # Sort for consistent order
                    attrs_desc.append(f"{name}={get_friendly_type_name(attr_type)}")
                return f"object({{{', '.join(attrs_desc)}}})"
            if isinstance(cty_type_instance, CtyTuple):
                if not cty_type_instance.element_types:
                    return "tuple([])"  # Handle empty tuple case
                elements_desc = [
                    get_friendly_type_name(el_type)
                    for el_type in cty_type_instance.element_types
                ]
                return (
                    f"tuple([{', '.join(elements_desc)}])"  # Add brackets for non-empty
                )
            # Fallback for other types not explicitly handled above
            return (
                cty_type_instance.__class__.__name__[3:].lower()
                if cty_type_instance.__class__.__name__.startswith("Cty")
                else "unknown_type"
            )

        type_name = get_friendly_type_name(self.type)

        processed_value = None  # Initialize to None as a default for null/unknown or if not set by other conditions

        # Process the main value if it's known and not null
        if not self.is_unknown and not self.is_null:
            # Case 1: CtyDynamic wrapping a concrete CtyValue
            if isinstance(self.type, CtyDynamic) and isinstance(
                self.value, CtyValue
            ):  # self.value is safe to access here
                inner_dict = self.value.to_json_comparable_dict()
                processed_value = { # Embed the inner value's type and value
                    "type": inner_dict["type_name"],
                    "value": inner_dict["value"],
                }
            # Case 2: CtyTuple
            elif isinstance(self.type, CtyTuple):
                if not self.value: # Empty tuple
                    processed_value = []
                else:  # Non-empty tuple; its value is a list of CtyValues or raw values
                    processed_value = [
                        v.to_json_comparable_dict() if isinstance(v, CtyValue) else v
                        for v in self.value
                    ]
            # Case 3: CtyList
            elif isinstance(self.value, list):
                processed_value = [
                    v.to_json_comparable_dict() if isinstance(v, CtyValue) else v
                    for v in self.value
                ]
            # Case 4: CtyMap or CtyObject (internal value is a dict)
            elif isinstance(self.value, dict):
                processed_value = {
                    k: v.to_json_comparable_dict() if isinstance(v, CtyValue) else v
                    for k, v in self.value.items()
                }
            # Case 5: CtySet (internal value is a frozenset)
            elif isinstance(self.value, frozenset):
                processed_value = sorted( # Sort for consistent JSON output
                    [
                        v.to_json_comparable_dict() if isinstance(v, CtyValue) else str(v)
                        for v in self.value
                    ],
                    key=lambda x: json.dumps(x, sort_keys=True) if isinstance(x, dict) else str(x),
                )
            # Case 6: Decimal numbers (requires careful string formatting)
            elif isinstance(self.value, Decimal):
                if self.value.is_zero(): # Handle +0, -0, 0.0
                    processed_value = "-0" if self.value.as_tuple().sign else "0"
                else: # Standard formatting for other decimals
                    normalized_d = self.value.normalize()
                    sign_tuple, digits_tuple, exponent_int = normalized_d.as_tuple()
                    val_str = "-" if sign_tuple else ""
                    if exponent_int >= 0:
                        val_str += "".join(map(str, digits_tuple)) + "0" * exponent_int
                    else:
                        num_digits = len(digits_tuple)
                        abs_exponent = abs(exponent_int)
                        if abs_exponent > num_digits:
                            val_str += "0." + "0" * (abs_exponent - num_digits) + "".join(map(str, digits_tuple))
                        elif abs_exponent == num_digits:
                            val_str += "0." + "".join(map(str, digits_tuple))
                        else:
                            val_str += "".join(map(str, digits_tuple[:num_digits - abs_exponent])) + "." + \
                                       "".join(map(str, digits_tuple[num_digits - abs_exponent:]))
                    processed_value = val_str
            # Case 7: Other primitive types (string, bool, already converted int/float)
            else:
                processed_value = self.value

        # Serialize marks
        # Serialize marks as a list of dictionaries
        # Sort by mark name for consistent order, then by details if name is the same
        serialized_marks = sorted(
            [{"name": m.name, "details": m.details} for m in self._marks],
            key=lambda m: (
                m["name"],
                str(m["details"]),
            ),  # str(details) for sortability
        )

        # After processed_value is determined based on self.value

        output_value = processed_value
        output_is_null = self.is_null

        # Ensure CtyMap, CtyObject are available for isinstance check
        # They are already imported at the top of the to_json_comparable_dict method
        # if isinstance(self.type, (CtyMap, CtyObject)) and \
        #    not self.is_unknown and \
        #    not self.is_null and \
        #    isinstance(self.value, dict) and \
        #    not self.value: # It's a non-null, known, empty map/object
        #     logger.debug(f"JULES_TO_JSON_COMPARABLE: Aligning empty map/object {self.type!r} to go-cty's null-like output.")
        #     output_value = None
        #     output_is_null = True

        return {
            "type_name": type_name,
            "value": output_value,
            "is_unknown": self.is_unknown,
            "is_null": output_is_null,  # Use potentially modified is_null
            "marks": serialized_marks,
        }

    # --- New Serialization/Deserialization Methods ---

    def to_json_string(self) -> str:
        """Serializes the CtyValue to a JSON string."""
        from ..codec import cty_value_to_json_string  # Local import

        return cty_value_to_json_string(self)

    @classmethod
    def from_json_string(cls, json_str: str, target_type: "CtyType") -> "CtyValue":
        """Deserializes a CtyValue from a JSON string, targeting a specific CtyType."""
        from ..codec import cty_value_from_json_string  # Local import

        # We use 'cls' indirectly by calling the codec function that returns a CtyValue instance
        return cty_value_from_json_string(json_str, target_type)

    def to_msgpack_bytes(self) -> bytes:
        """Serializes the CtyValue to Msgpack bytes."""
        from ..codec import cty_value_to_msgpack_bytes  # Local import

        return cty_value_to_msgpack_bytes(self)

    @classmethod
    def from_msgpack_bytes(
        cls, msgpack_bytes: bytes, target_type: "CtyType"
    ) -> "CtyValue":
        """Deserializes a CtyValue from Msgpack bytes, targeting a specific CtyType."""
        from ..codec import cty_value_from_msgpack_bytes  # Local import

        return cty_value_from_msgpack_bytes(msgpack_bytes, target_type)


# 🐍🏗️🐣
