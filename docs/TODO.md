# TODO

## Recently Resolved (as of YYYY-MM-DD - placeholder for current date)

*   ✅ **`CtyValue` Initialization with Marks**: Fixed `CtyMapValidationError` in Terraform integration (`CtyValue.__init__() got an unexpected keyword argument '_marks'`). Ensured `CtyValue.mark()` and `CtyValue.unmark()` use `_marks` internally when calling `evolve`. This primarily affected handling of null/dynamic values being marked.

## Goal

As close to 100% feature and functional parity to `go-cty` as possible.

### Legend

*   ✅ **Complete:** Feature is implemented correctly and aligns with `go-cty` semantics.
*   ⚠️ **Partially Implemented / Needs Refinement:** Feature exists but has gaps, bugs, or diverges from `go-cty` in a significant way.
*   ❌ **Missing / To-Do:** Feature is not implemented and is required for parity.
*   💡 **Recommendation:** Specific, actionable advice for implementation or testing.

---

### `pyvider.cty` Implementation Checklist

#### **I. Core Type System & Values**

| Status | Feature | Current Status & Actionable Steps |
| :--- | :--- | :--- |
| ✅ | **Number Type** | Implemented using `decimal.Decimal`. This is the correct Pythonic choice for arbitrary precision. |
| ⚠️ | **String Type** | Implemented using Python's `str`. However, it lacks the explicit NFC Unicode normalization that `go-cty` guarantees on value creation. <br>💡 **Action:** In `CtyString.validate`, add `value = unicodedata.normalize('NFC', str(value))` to ensure canonical representation. |
| ✅ | **Boolean Type** | Implemented using Python's native `bool`. Fully aligned. |
| ✅ | **List, Map, Object, Tuple Types** | The fundamental structures are correctly implemented using `attrs`. |
| ✅ | **Set Type** | Correctly implemented using `frozenset` internally. Its correctness relies heavily on the `__hash__` and `__eq__` implementations of the contained `CtyValue`s. |
| ⚠️ | **Capsule Type (`CtyCapsule`)** | The basic type exists, allowing opaque wrapping of Python objects. However, it lacks the `CapsuleOps` mechanism from `go-cty` that allows custom types to define their own equality, hashing, and conversion logic. <br>💡 **Action (Post-Preview):** For full parity, consider defining a `CtyCapsuleOperations` protocol that wrapped types can implement. For now, the current implementation is sufficient for many use-cases. |
| ⚠️ | **Value Marks (`CtyMark`)** | The basic `mark()` and `unmark()` functionality on `CtyValue` is present (internal `_marks` usage corrected). However, the framework lacks the high-level `Walk` and `Transform` functions that make marks truly useful for inspecting and manipulating complex nested values. <br>💡 **Action:** Implement `walk()` and `transform()` functions in a utility module that can traverse a `CtyValue` structure, applying callbacks. This is needed for full mark-handling capabilities. |

#### **II. Dynamic & Unknown Value Handling**

| Status | Feature | Current Status & Actionable Steps |
| :--- | :--- | :--- |
| ❌ | **`CtyDynamic` Value Validation** | The current implementation recursively wraps collections in more `CtyDynamic` types, which is incorrect and inefficient. It should infer the most specific concrete type. <br>💡 **Action (High Priority):** Refactor `CtyDynamic.validate()` to perform a one-time, deep type inference on raw Python data. The result should be a single, fully-typed `CtyValue` (e.g., `CtyObject` with `CtyString` attributes) which is then wrapped *once* by a `CtyValue` of type `CtyDynamic`. |
| ✅ | **Unknown Values (`CtyValue.unknown`)** | The fundamental concept of a typed placeholder for an unknown value is correctly implemented. |
| ❌ | **Value Refinements** | This is a major missing feature from modern `go-cty`. The ability to constrain the range of an unknown value (e.g., string prefix, number bounds, collection length) is not implemented. <br>💡 **Action (Post-Preview Epic):** This is a large but important feature. Plan to implement a `RefinementBuilder` class and `RefinedUnknownValue` to store these constraints. Start with `NotNull`, then add `StringPrefix`, `NumberRange...`, and `CollectionLength...` refinements. |

#### **III. Type Conversion & Unification**

| Status | Feature | Current Status & Actionable Steps |
| :--- | :--- | :--- |
| ⚠️ | **Implicit Type Conversion** | Basic conversions (e.g., `bool` to `string`) are handled within individual `validate` methods. However, this is ad-hoc and lacks the robust, centralized rule system of `go-cty`. <br>💡 **Action:** The current approach is acceptable for a preview, but a future refactor should centralize this logic into a dedicated `pyvider.cty.convert` module for consistency and maintainability. |
| ❌ | **Type Unification (`Unify`)** | The framework cannot find a common supertype for a collection of disparate types (e.g., unifying a list of different object types into a `list(map(string))`). This is critical for handling heterogeneous collections in Terraform `for_each` loops. <br>💡 **Action (Post-Preview):** Implement a `unify(types: list[CtyType]) -> CtyType | None` function in the new `convert` module. This is a complex task that requires defining a type precedence hierarchy. |

#### **IV. Serialization (Wire Protocol) & Encoding**

| Status | Feature | Current Status & Actionable Steps |
| :--- | :--- | :--- |
| ⚠️ | **Unknown Value Encoding** | The `wire` layer has hooks (`_decode_unknown_hook`), but the MessagePack `ExtType` encoding (`0` for unrefined, `12` for refined) needs rigorous validation to ensure byte-level compatibility with `go-cty`. <br>💡 **Action:** Create specific tests that take known `go-cty` msgpack output for unknown values and assert that `pyvider-cty` can decode it, and vice-versa. |
| ❌ | **Dynamic Value Encoding** | The marshaling logic for `CtyDynamic` is incorrect because it doesn't unwrap the inner concrete value before creating the `[type, value]` tuple for serialization. <br>💡 **Action (High Priority):** Fix the `marshal_value` function in `conversion/terraform.py` (Note: this path seems to be in `pyvider` main, if `pyvider-cty` is to be standalone, its own encoding logic needs to be self-contained). When marshalling a dynamic value, it must first access the *inner* `CtyValue`, get its concrete type, and then serialize the `[type, inner_value]` pair. |
| ❌ | **`pyvider.cty.encoding` Package** | This package, expected to house CTY-specific encoding/decoding logic (e.g., for Protobuf `DynamicValue`), is currently missing. A placeholder `__init__.py` has been added to allow imports from `pyvider` tests, but the actual functionality needs to be implemented. <br>💡 **Action (High Priority):** Define and implement necessary modules within `pyvider.cty.encoding`, such as `protobuf.py`, to handle serialization/deserialization of `CtyValue` to/from wire formats like Protobuf's `DynamicValue`, ensuring `pyvider-cty` remains standalone. |

#### **V. Standard Library Functions**

| Status | Feature | Current Status & Actionable Steps |
| :--- | :--- | :--- |
| ⚠️ | **String Functions** | `upper`, `lower`, `format`, `join`, `split`, `replace` exist. <br>❌ **To-Do:** `chomp`, `indent`, `strrev`, `substr`, `trim`, `title`, `trimspace`, `trimprefix`, `trimsuffix`, `regex`, `regexall`. |
| ⚠️ | **Numeric Functions** | `add`, `subtract`, `multiply`, `divide`, `min`, `max`, `round` exist. <br>❌ **To-Do:** `abs`, `ceil`, `floor`, `log`, `pow`, `signum`, `parseint`. |
| ❌ | **Collection Functions** | This is the largest functional gap. <br>❌ **To-Do:** `chunklist`, `coalescelist`, `compact`, `contains`, `distinct`, `element`, `flatten`, `keys`, `values`, `lookup`, `merge`, `setproduct`, `slice`, `sort`, `zipmap`. |
| ❌ | **Encoding Functions** | <br>❌ **To-Do:** `jsonencode`, `csvdecode`. The `jq` function is a workaround, not a direct equivalent. These should ideally be part of `pyvider.cty` if they operate purely on CTY values. |
| ❌ | **Date & Time Functions** | <br>❌ **To-Do:** `formatdate`, `timeadd`. |
| ❓ | **Type Conversion Functions** | (`tostring`, `tonumber`, etc.) `pyvider-cty` handles this implicitly during validation, which is a valid design choice. <br>💡 **Recommendation:** Document this as an intentional design divergence. No immediate action required unless explicit conversion functions become necessary. |

#### **VI. Untested Code & Test Coverage Gaps**

| Status | Module / File | Missing Coverage & Actionable Steps |
| :--- | :--- | :--- |
| ⚠️ | **`codec.py`** | The error-handling paths for malformed type strings are not fully covered. <br>💡 **Action:** Add a new test file (`tests/codec/test_codec_error_coverage.py`) with a `pytest.mark.parametrize` block that feeds invalid strings (e.g., `list(a,b)`, `object(foo)`) to the parser and asserts that the correct `CtyTypeParseError` is raised. |
| ⚠️ | **`path/base.py`** | The coverage is low because many error paths are untested (e.g., applying an `IndexStep` to a `CtyMap`, applying a `GetAttrStep` to a `CtyList`, handling `null` values, etc.). <br>💡 **Action:** Create a new test file (`tests/path/test_path_coverage.py`) that specifically triggers these `AttributePathError` exceptions for each step type. |
| ⚠️ | **`types/collections/*.py`** | The validation logic for `CtyList`, `CtyMap`, and `CtySet` has many branches for handling invalid inputs (e.g., non-iterable values, elements of the wrong type, `CtyValue` inputs of the wrong collection kind) that are not tested. <br>💡 **Action:** Create a new test file (`tests/collections/test_collection_coverage.py`) to test these failure modes. For example, `CtyList(CtyString()).validate({"a": 1})` should raise a `CtyListValidationError`. |
| ⚠️ | **`types/structural/tuple.py`** | The logic for validating tuples of different lengths or with mismatched element types is not fully covered. <br>💡 **Action:** Add tests to `tests/tuple/test_cty_tuple_validation.py` that attempt to validate lists/tuples with incorrect lengths or where an element fails its specific type validation. |

(Note: I've added a placeholder for the current date in the "Recently Resolved" section, which should be updated when this is merged.)
