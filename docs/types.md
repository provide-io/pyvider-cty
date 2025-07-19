# Types

The `pyvider.cty` library provides a rich set of types that can be used to define the shape and constraints of your data. All types are subclasses of the `CtyType` base class.

## Primitive Types

Primitive types are the most basic types in `cty`. They represent a single value, such as a string, number, or boolean.

*   `CtyString`: Represents a string value.
*   `CtyNumber`: Represents a number value.
*   `CtyBool`: Represents a boolean value.
*   `CtyDynamic`: Represents a value of any type.

## Collection Types

Collection types are used to represent collections of values, such as lists, sets, and maps.

*   `CtyList(element_type)`: Represents a list of values, where all elements are of the same `element_type`.
*   `CtySet(element_type)`: Represents a set of values, where all elements are of the same `element_type`.
*   `CtyMap(element_type)`: Represents a map of string keys to values, where all values are of the same `element_type`.

## Structural Types

Structural types are used to represent more complex data structures, such as objects and tuples.

*   `CtyObject(attribute_types, optional_attributes=None)`: Represents an object with a fixed set of attributes. `attribute_types` is a dictionary mapping attribute names to their corresponding `cty` types. `optional_attributes` is a set of attribute names that are not required to be present.
*   `CtyTuple(element_types)`: Represents a tuple with a fixed number of elements, where each element can have a different `cty` type. `element_types` is a list of `cty` types for each element in the tuple.

## Capsule Types

Capsule types are a special type of `cty` type that can be used to encapsulate opaque Python objects. This is useful when you need to pass around complex Python objects that don't have a direct `cty` representation.

*   `CtyCapsule(capsule_name, py_type)`: Creates a new capsule type. `capsule_name` is a unique name for the capsule type, and `py_type` is the Python type of the object that will be encapsulated.
