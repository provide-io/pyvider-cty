# TODO: Improve Test Coverage for src/pyvider/cty/values/base.py

The following line ranges in `src/pyvider/cty/values/base.py` are currently uncovered by tests. This document outlines their importance and suggestions for new tests.

## General Notes:
- Many uncovered lines are within exception handling blocks or deal with type comparisons and internal value representations under specific, sometimes less common, conditions.
- Increasing coverage here will improve the robustness and reliability of the CtyValue class, especially for complex nested types and edge cases during operations like hashing, equality checks, and iteration.

---

### 1. `value` Property (Line 94)
- **Line:** `logger.warning("🔄❗⚠️ Attempted to get raw value of unknown value")` (within `if self._is_unknown: raise ValueError(...)`)
- **Importance:** Ensures that accessing `.value` on an unknown `CtyValue` logs a warning before raising the ValueError. Important for debugging user issues.
- **Complexity to Test:** Low. Create an unknown `CtyValue` and try to access its `.value` property. Verify the log message and that ValueError is raised.
- **Suggested Test:**
  ```python
  # In a test_cty_values_base.py or similar
  def test_access_value_on_unknown_logs_warning(caplog):
      unknown_val = CtyValue.unknown(CtyString())
      with pytest.raises(ValueError, match="Cannot get raw value of unknown value"):
          _ = unknown_val.value
      assert "Attempted to get raw value of unknown value" in caplog.text
  ```

---

### 2. `has_mark` Method (Lines 111-117)
- **Lines:** `mark_str = str(mark)` and the loop `for m in self._marks: if str(m) == mark_str: return True` and `return False`.
- **Importance:** Core logic for checking mark presence using string comparison. Critical for metadata handling.
- **Complexity to Test:** Medium. Requires creating values with various types of marks (simple strings, objects with `__str__`) and testing `has_mark` with different mark objects that would match by string representation but not by identity. Also test cases where marks are not present.
- **Suggested Tests:**
  - Test `has_mark` when the mark is a simple string and present/absent.
  - Test `has_mark` with a custom mark object whose `__str__` representation matches a mark on the `CtyValue`.
  - Test `has_mark` with an empty set of marks on the `CtyValue`.

---

### 3. `unmark` Method (Line 131)
- **Line:** `logger.debug(f"🔄🔧✅ Removing {len(original_marks)} marks from value")`
- **Importance:** Logging for debuggability of mark removal.
- **Complexity to Test:** Low. Create a `CtyValue` with marks, call `unmark()`, and check logs.
- **Suggested Test:**
  ```python
  # In a test_cty_values_base.py or similar
  def test_unmark_logs_removal(caplog):
      val = CtyValue.string("test").mark("mark1").mark("mark2")
      val.unmark()
      assert "Removing 2 marks from value" in caplog.text
  ```

---

### 4. `with_marks` Method (Line 144)
- **Line:** `return evolve(self, marks=frozenset(new_marks_set))`
- **Importance:** Core logic for replacing marks.
- **Complexity to Test:** Low. Create a `CtyValue` with some marks, call `with_marks` with a new set, and verify the marks are updated.
- **Suggested Test:** (Likely already covered, but confirm specific test for this line if isolated coverage shows it as missed).

---

### 5. `get` Method (Lines 160-164, 185, 205-217, 232)
- **Lines:**
    - `logger.debug(f"🔄🔍🔄 Getting value for key: {key}")` (160)
    - `logger.debug(f"🔄🔍⚠️ Cannot get from unknown/null value, returning default")` (164)
    - `logger.warning(f"Default value {default!r} is not compatible with map value type {self._vtype.value_type}")` (within CtyMap, default validation) (185) - *Note: This specific line was confirmed covered by `test_get_on_map_with_incompatible_default` if logging level is appropriate.*
    - `logger.debug(f"🔄🔍⚠️ Object attribute key must be string, got {type(key).__name__}")` (within CtyObject, key type check) (205)
    - `logger.debug(f"🔄🔍⚠️ get() called on unsupported type: {self._vtype.__class__.__name__}")` (217)
- **Importance:** Various logging and specific error/condition handling paths within the `get` method. Essential for diagnosing issues with `get`.
- **Complexity to Test:**
    - Logging calls: Low, just need to ensure tests trigger these paths and check `caplog`.
    - Default value validation failure (185): Medium, requires a map, a key, and a default value whose type is incompatible with the map's `value_type`. (This was covered in the last subtask by `test_get_on_map_with_incompatible_default`).
    - Object key not string (205): Low, call `get` on an object CtyValue with a non-string key.
    - `get` on unsupported type (217): Low, call `get` on a CtyString, CtyNumber, etc.
- **Suggested Tests:**
  - Test `get` on unknown/null value, check log.
  - Test `get` on CtyObject with non-string key, check log and that default is returned.
  - Test `get` on CtyString/CtyNumber, check log and that default is returned.

---

### 6. `set` and `delete` Methods (Lines 263, 283-305, 328-344)
- **Lines:** These are primarily the `TypeError` exceptions for unknown/null or unsupported types.
    - `logger.debug(f"🔄📝🔄 Setting key {key!r} to value {value!r}")` (set)
    - `error_msg = f"Cannot set key on unknown/null value"`... `raise TypeError(error_msg)` (set)
    - `error_msg = f"set() method not supported for type {self._vtype.__class__.__name__}"`... `raise TypeError(error_msg)` (set)
    - `logger.debug(f"🔄📝🔄 Deleting key {key!r}")` (delete)
    - `error_msg = f"Cannot delete key from unknown/null value"`... `raise TypeError(error_msg)` (delete)
    - `error_msg = f"delete() method not supported for type {self._vtype.__class__.__name__}"`... `raise TypeError(error_msg)` (delete)
- **Importance:** These are critical error paths ensuring that `set` and `delete` operations are only attempted on valid and supported types.
- **Complexity to Test:** Low to Medium. The tests `TestCtyValueSetDeleteErrors` (added/fixed in previous subtasks) cover these exact lines. The logs can be verified via `caplog`.
- **Suggested Tests:** These lines should now be covered by `TestCtyValueSetDeleteErrors`. Review coverage report after those tests run with logging checks.

---

### 7. `element_at` Method (Lines 366-382)
- **Lines:**
    - `logger.debug(f"🔄🔍🔄 Getting element at index {index}")`
    - `error_msg = "Cannot get element from unknown or null value"`... `raise TypeError(error_msg)`
    - `raise TypeError(f"Cannot index list value of type {type(self._value).__name__}")` (if `self._value` is not list/tuple for a `CtyList`)
    - `error_msg = f"List index {index} out of bounds (size {list_len})"`... `raise IndexError(error_msg)`
    - `error_msg = f"element_at method not supported for type {self._vtype.__class__.__name__}"`... `raise TypeError(error_msg)`
- **Importance:** Core logic and error handling for indexed access on lists/tuples.
- **Complexity to Test:**
    - Logging: Low.
    - Unknown/null: Low, call `element_at` on such values.
    - Invalid internal `_value` for `CtyList`: Medium/Hard. This implies an internal inconsistency (a `CtyList` type wrapping a non-list/tuple `_value`). Might require careful mock setup or specific internal state creation if possible, or it might indicate an impossible state if constructors are robust.
    - IndexError: Low, test with out-of-bounds indices.
    - Unsupported type: Low, call `element_at` on a CtyMap/CtyString.
- **Suggested Tests:**
  - Call `element_at` on unknown/null `CtyList`/`CtyTuple`.
  - Call `element_at` on a `CtyList` where `_value` is intentionally (if possible via test setup) not a list/tuple.
  - Call `element_at` on `CtyMap`/`CtyString`.

---

### 8. Factory Methods (`list_of_dynamic`, `map_of_dynamic`) (Lines 611-623)
- **Lines:** Logging calls `logger.debug(...)` within these factory methods.
- **Importance:** Debuggability for dynamic type factories.
- **Complexity to Test:** Low. Call these factory methods and check `caplog`.
- **Suggested Tests:**
  ```python
  # In test_cty_values_factory.py
  def test_list_of_dynamic_factory_logs(caplog, setup_types):
      CtyValue.list_of_dynamic(["a", 1])
      assert "Creating dynamic list value" in caplog.text

  def test_map_of_dynamic_factory_logs(caplog, setup_types):
      CtyValue.map_of_dynamic(CtyString(), {"a": "b", "c": 1})
      assert "Creating dynamic map value" in caplog.text
  ```

---

### 9. `to_dict` Method (Lines 661-664, 668-672)
- **Lines:**
    - `logger.debug(f"🔄🔧✅ Converting CtyValue to dictionary")`
    - `result["value"] = [ v.to_dict() if isinstance(v, CtyValue) else v for v in self._value ]` (for set/frozenset)
    - `value = v.to_dict() if isinstance(v, CtyValue) else v` (for dict values)
    - `result["value"] = [ v.to_dict() if isinstance(v, CtyValue) else v for v in self._value ]` (for list/tuple)
    - `result["marks"] = list(str(m) for m in self._marks)`
- **Importance:** Core serialization logic. Recursive calls to `to_dict` for nested CtyValues and mark serialization are critical.
- **Complexity to Test:** Medium. Requires creating CtyValues with nested structures (e.g., list of CtyValues, map with CtyValue values) and values with marks, then calling `to_dict()` and inspecting the output structure and logs.
- **Suggested Tests:**
  - `to_dict()` on a `CtySet` containing CtyValues.
  - `to_dict()` on a `CtyMap` where values are CtyValues.
  - `to_dict()` on a `CtyList` containing CtyValues.
  - `to_dict()` on a `CtyValue` that has marks.

---

### 10. `__len__` Special Method (Lines 689-733)
- **Lines:** Primarily error paths and logging.
    - `error_msg = "Cannot get length of unknown value"` ... `raise TypeError(error_msg)`
    - `logger.debug("🔄🔍✅ Length of null value is 0")`
    - `error_msg = f"Value of type {self._vtype.__class__.__name__} (inner: {type(self._value).__name__}) doesn't support length operation"` ... `raise TypeError(error_msg)`
- **Importance:** Correct length reporting and error handling for various states.
- **Complexity to Test:** Low.
    - Test `len()` on unknown, null, and types that don't support length (e.g., CtyBool if it doesn't define `__len__` on its `_value`).
- **Suggested Tests:**
  - `test_len_on_unknown_value_raises_typeerror`
  - `test_len_on_null_value_is_zero_and_logs`
  - `test_len_on_unsupported_type_raises_typeerror` (e.g. CtyBool)

---

### 11. `__iter__` Special Method (Lines 750-768)
- **Lines:** Error paths and logging for iteration.
    - `error_msg = "Cannot iterate unknown value"` ... `raise TypeError(error_msg)`
    - `logger.debug("🔄🔍✅ Iterating over null value (yields nothing)")`
    - `return iter([])` (for null value)
    - `error_msg = f"Value of type {self._vtype.__class__.__name__} (inner: {type(self._value).__name__}) doesn't support iteration"` ... `raise TypeError(error_msg)`
- **Importance:** Correct iteration behavior and error handling.
- **Complexity to Test:** Low.
    - Test iteration on unknown, null, and unsupported types.
- **Suggested Tests:**
  - `test_iter_on_unknown_value_raises_typeerror`
  - `test_iter_on_null_value_yields_nothing_and_logs`
  - `test_iter_on_unsupported_type_raises_typeerror` (e.g., CtyNumber if `_value` is not iterable)

---

### 12. `__hash__` Special Method (Lines 784-809, 822-865)
- **Lines:** These lines cover various paths within the hashing logic, especially fallbacks for unhashable types or types that might raise `TypeError` during `hash()`.
    - `value_hash = hash(repr(self._value))` (fallback for primitives if `hash(self._value)` fails - though unlikely for listed primitives)
    - `value_hash = hash(repr(self._value))` (fallback for tuples if elements aren't CtyValues or hashing tuple fails)
    - `value_hash = hash(repr(self._value))` (fallback for frozensets if hashing frozenset fails)
    - `value_hash = hash(id(self._value))` (ultimate fallback if `repr` is also unhashable)
- **Importance:** Robustness of hashing, ensuring `CtyValue` can be used reliably in sets/dictionary keys.
- **Complexity to Test:** High. Triggering these specific fallback paths requires carefully crafted, potentially misbehaving, custom types for `_value` or elements within `_value` that are hashable by one means (e.g., `id`) but not by another (e.g., `repr` or direct `hash`). This might involve deep mocking or creating unusual objects.
- **Suggested Tests:**
  - Create a `CtyValue` wrapping a custom object where `__hash__` raises `TypeError` but `__repr__` is valid.
  - Create a `CtyValue` wrapping a custom object where both `__hash__` and `__repr__.__hash__` (if `__repr__` returns an object) raise `TypeError`.
  - Test with tuples/frozensets containing such problematic custom objects.

---

### 13. `__eq__` Special Method (Lines 880-941)
- **Lines:** Many lines here, covering comparisons between different types, states (unknown/null), and internal value comparisons, including error handling like `except Exception: return False`.
    - `if not self._vtype.equal(other._vtype): return False`
    - `if self._is_unknown != other._is_unknown: return False` (and similar for `_is_null`)
    - `if (self._is_unknown and other._is_unknown) or (self._is_null and other._is_null): return True`
    - `if self._marks != other._marks: return False`
    - Decimal comparison with int/float/str: `except Exception: return False`
    - List/tuple length check: `if len(self._value) != len(other._value): return False`
    - List/tuple element-wise comparison: `all(a == b for a, b in zip(self._value, other._value))` (coverage might miss if lists are always empty or identical in existing tests for this path)
    - Set length/equality checks.
    - Map length/equality checks.
    - Fallback `self._value == other._value` and its `except Exception: return False`.
- **Importance:** Correctness of equality is fundamental. All branches, including those for different internal types and error fallbacks, are important.
- **Complexity to Test:** Medium to High.
    - Comparing different `CtyValue` types.
    - Comparing with different marks.
    - Comparing `CtyValue(Decimal)` with `CtyValue(int/float/str)` that might cause exceptions during `Decimal()` conversion.
    - Lists/tuples/sets/maps with elements that are themselves CtyValues and require recursive `__eq__` calls.
    - Values that are equal vs. not equal at each stage of the checks.
    - Values whose `_value` attribute might raise an exception during `==`.
- **Suggested Tests:**
  - Extensive matrix of `CtyValue` comparisons: different types, same type different values, different unknown/null states, different marks.
  - Test `CtyValue(Decimal(1))` vs `CtyValue("1.0")`, `CtyValue(1)`.
  - Test lists/maps/sets containing other CtyValues, including nested ones.
  - Test `CtyValue` wrapping a custom object whose `__eq__` method raises an exception.

---

### 14. `__getitem__` Special Method (Lines 965-1057)
- **Lines:** This is a very large block with many paths. Uncovered lines likely relate to:
    - Specific error conditions and their logging: `TypeError`, `KeyError`, `IndexError`, `CtyAttributeValidationError`, and the final `except Exception`.
    - Complex key validation for maps: e.g., `KeyError(f"Invalid CtyValue key type or state for map lookup: {key!r}")` or `KeyError(f"Map key cannot be null or unknown: {key!r}")`.
    - Slice handling for tuples that might create specific kinds of new tuple types.
    - The final `TypeError` for unsupported indexing types.
- **Importance:** Correct and robust keyed/indexed access is critical for usability. All error paths and specific type handling branches need coverage.
- **Complexity to Test:** Medium to High.
    - Triggering each specific `raise` statement (KeyError, TypeError, IndexError, CtyAttributeValidationError).
    - For maps: using `CtyValue` keys that are null/unknown or of an incompatible type. Using raw keys that are null/unknown after validation.
    - For lists/tuples: various slice combinations, including those that might result in empty or single-element tuples/lists.
    - Testing the final `TypeError` for types that don't support `__getitem__` at all.
- **Suggested Tests:**
  - Test `__getitem__` on CtyMap with CtyValue keys that are null, unknown, or wrong type.
  - Test `__getitem__` on CtyMap with raw keys that become null/unknown after validation.
  - Test various slice combinations on CtyTuple and CtyList CtyValues.
  - Test `__getitem__` on CtyValues of types like CtyNumber, CtyBool.
  - Mock internal calls (e.g., `self._vtype.get_attribute`) to raise specific Cty exceptions or general exceptions to test the wrapping `try-except` blocks.

---

### 15. `__contains__` Special Method (Lines 1078-1148)
- **Lines:** Similar to `__getitem__`, many uncovered lines are in error paths or specific validation branches for the `item` being checked.
    - `TypeError` for unknown/null value.
    - Map key validation: `CtyValue` key type/state checks, raw key validation failures.
    - List/Set/Tuple element validation: `self._vtype.element_type.validate(item)` failing.
    - Final `TypeError` for unsupported types.
    - `except Exception as e: logger.debug(...) return False` fallback.
- **Importance:** Correct membership testing.
- **Complexity to Test:** Medium.
    - Test `in` operator on unknown/null CtyValues.
    - For maps: test `in` with CtyValue keys (null, unknown, wrong type) and raw keys that fail validation.
    - For collections: test `in` with items that cannot be validated against `element_type`.
    - For other types: test `in` on types that don't support it.
    - Test cases where `item in self._value` might raise an unexpected exception for custom `_value` types.
- **Suggested Tests:**
  - Test `in` operator on `CtyValue` that is unknown or null.
  - For `CtyMap`, test `key in map_value` where `key` is a `CtyValue` that's null/unknown/wrong type, or a raw key that fails validation.
  - For `CtyList`/`CtySet`, test `item in list_value` where `item` is incompatible with `list_value.type.element_type`.
  - Test `in` on a `CtyValue(CtyNumber(1))` with a number.

---

### 16. Serialization/Deserialization (`to_json_string`, etc.) (Lines 1161-1165, 1177, 1179, 1184, 1187, 1190-1194, 1207-1227, 1240-1281, 1294-1369, 1381-1382, 1387-1389, 1393-1394, 1399-1400)
- **Lines:** These are primarily the import lines for codec functions within these methods.
  - `from ..codec import cty_value_to_json_string` etc.
- **Importance:** While the lines themselves are just imports, their being uncovered might indicate that the methods themselves (`to_json_string`, `from_json_string`, `to_msgpack_bytes`, `from_msgpack_bytes`) are not fully tested, or tested in a way that doesn't trigger these specific import paths if they are conditional (though they don't appear to be).
- **Complexity to Test:** Low for the import itself, Medium for ensuring the methods that use these imports are comprehensively tested with various CtyValue types and states.
- **Suggested Tests:** Ensure there are tests that explicitly call `CtyValue.to_json_string()`, `CtyValue.from_json_string()`, etc., for a variety of CtyValue types. The coverage tool might not mark the import line itself as covered unless the method is entered. The current coverage report for `codec.py` is also not 100%, so testing these thoroughly will benefit both modules.

---

This analysis should provide a good starting point for writing new tests to improve the coverage of `src/pyvider/cty/values/base.py`.

---
## Coverage Analysis for src/pyvider/cty/values/base.py (2025-06-01)

This section details further uncovered lines in `src/pyvider/cty/values/base.py` based on the list: `232, 338-339, 405-407, 417, 438-440, 620, 704, 710-715, 718, 724, 725->730, 768-770, 803-811, 824-865, 911-914, 920, 927-929, 935, 940-943, 981, 991-994, 1000, 1002-1003, 1037-1039, 1053-1057, 1097-1100, 1106, 1108-1109, 1119-1121, 1131-1150, 1163-1167, 1192-1196, 1223, 1254-1255, 1261-1280, 1305->exit, 1310-1311, 1326, 1350`.

---

### `get` Method (Additional Paths)
- **Lines (approximate):** 232 (This line, `return default # Return original python default`, is the fallback in the `CtyObject` handling block if `key` is not a string, or if `_vtype.has_attribute(key)` is false, or if `_vtype.get_attribute(self, key)` raises an exception. The exception case was more explicitly covered by recent JULES_DEBUG logging additions, but the other paths leading to this default return might still be relevant if not fully exercised by tests that distinguish these conditions).
- **Description**: This line is a fallback to return the `default` value within the `CtyObject` type check in the `get` method. It's reached if the key is not a string, or if the attribute doesn't exist (and no prior exception occurred during `get_attribute`).
- **Importance**: Ensures graceful fallback to a default value when an attribute cannot be retrieved from a `CtyObject`.
- **Testing Complexity**: Low. Test `get` on a `CtyObject` for an attribute name that doesn't exist, providing a default value. Also test with a non-string key.
- **Suggested Test**:
  ```python
  obj_type = CtyObject({"name": CtyString()})
  obj_val = CtyValue.object({"name": "Alice"}, attribute_types={"name": CtyString()})
  assert obj_val.get("age", "N/A") == "N/A" # Attribute missing
  assert obj_val.get(123, "N/A") == "N/A" # Key not a string
  ```

---

### `element_at` Method (Additional Paths)
- **Lines (approximate):**
    - 338-339: `raise TypeError(f"Cannot index list value of type {type(self._value).__name__}")`
    - 405-407: `return self._vtype.element_at(self._value, index)` (The call itself and potential exceptions from it if not caught by `CtyTuple.element_at` robustly).
    - 417: `error_msg = f"element_at method not supported for type {self._vtype.__class__.__name__}"` (and subsequent raise)
- **Description**:
    - 338-339: Error raised if a `CtyValue` has `_vtype = CtyList` but its internal `_value` is not a list or tuple. This indicates an internal inconsistency.
    - 405-407: Delegation to the `CtyTuple` type's `element_at` method. Coverage might be missing if `CtyTuple.element_at` itself isn't fully exercised through this path or if it always handles errors before they'd propagate to `CtyValue.element_at`'s own `try-except`.
    - 417: Error for types that don't support indexed access at all.
- **Importance**: Correct error handling for malformed `CtyList` values and proper delegation or error reporting for other types.
- **Testing Complexity**:
    - 338-339: Medium. Requires constructing a `CtyValue` in an inconsistent state (e.g., `CtyValue(vtype=CtyList(CtyString()), value="not a list")`). This might only be possible through direct instantiation if internal factory methods prevent this.
    - 405-407: Medium. Depends on how `CtyTuple.element_at` handles its own errors. If it's very robust, this path in `CtyValue` might be hard to reach.
    - 417: Low. Call `element_at` on a `CtyString` or `CtyMap`.
- **Suggested Tests**:
  - (For 338-339, if constructible): `val = CtyValue(vtype=CtyList(CtyString()), value="a string"); with pytest.raises(TypeError): val.element_at(0)`
  - (For 405-407): Test `CtyValue.tuple(...).element_at(index)` with various valid and invalid indices to ensure `CtyTuple.element_at` is called and behaves as expected. If `CtyTuple.element_at` is supposed to catch all its errors, then this specific line in `CtyValue` might only be hit if `CtyTuple.element_at` unexpectedly raises a general `Exception`.
  - (For 417): `CtyValue.string("text").element_at(0)` should raise TypeError.

---

### Factory Methods (`object`)
- **Lines (approximate):** 620: `raise CtyValidationError(f"Expected CtyType for attribute '{attr_name}', got {type(attr_type).__name__}")`
- **Description**: This line is in the `object` factory method. It's an error path hit if the `attribute_types` dictionary passed to the factory contains a value that is not a `CtyType` instance.
- **Importance**: Ensures that object schemas are correctly defined with valid Cty types for attributes.
- **Testing Complexity**: Low. Call `CtyValue.object()` with an invalid type in `attribute_types`.
- **Suggested Test**:
  ```python
  # In test_cty_values_factory.py
  def test_object_factory_invalid_attribute_type_spec(self):
      with pytest.raises(CtyValidationError, match="Expected CtyType for attribute 'name', got str"):
          CtyValue.object(attribute_types={"name": str}, attributes={"name": "test"})
  ```

---

### `to_dict` Method (Additional Paths)
- **Lines (approximate):**
    - 704: `result["value"] = self._value` (This is the fallback for primitive types if not `Decimal` and not `None`).
    - 710-715: `elif isinstance(self._value, Decimal): result["value"] = str(self._value)` (This part *is* likely covered). The surrounding `elif self._value is not None:` might have specific conditions not fully explored.
    - 718: `result["marks"] = list(str(m) for m in self._marks)` (Specifically, if `_marks` is empty, this line might not be "hit" in some coverage tools, though `if self._marks:` guards it).
- **Description**:
    - 704: Handles serialization of primitive types that are not explicitly `Decimal`.
    - 710-715: The `elif self._value is not None:` implies that if `_value` is `None` (but `is_null` and `is_unknown` are false), it would skip this block. This should be an invalid state for a `CtyValue`.
    - 718: Serialization of marks.
- **Importance**: Correct serialization of all primitive types and marks.
- **Testing Complexity**:
    - 704: Low. Test `to_dict()` with `CtyString`, `CtyBool`, `CtyNumber` (wrapping int/float that becomes Decimal).
    - 710-715: Test with `_value` as `None` but `is_null=False` (if constructible) to see behavior.
    - 718: Low. Test `to_dict()` on a `CtyValue` with no marks.
- **Suggested Tests**:
  - `CtyValue.string("test").to_dict()`
  - `CtyValue.bool(True).to_dict()`
  - `CtyValue(CtyString(), value=None, is_null=False, is_unknown=False).to_dict()` (to test invalid state if possible).
  - `CtyValue.string("test_no_marks").to_dict()` (verify "marks" key is absent).

---

### `__iter__` Special Method (Additional Paths)
- **Lines (approximate):** 724 (`return iter(self._value)` for non-dict iterables), 725->730 (`elif isinstance(self._value, dict): return iter(self._value.keys())`).
- **Description**: These lines were previously analyzed. Line 724 handles iteration for lists, tuples, sets, and strings. Lines 725-730 handle iteration for dicts (maps/objects), iterating over keys. The coverage tool might not distinguish these if tests for map iteration and list iteration already exist but don't specifically isolate these exact return statements.
- **Importance**: Correct iteration behavior.
- **Testing Complexity**: Low to Medium.
- **Suggested Tests**: (Likely already covered by tests for `CtyList`, `CtySet`, `CtyMap`, `CtyObject` iteration).
  - Ensure tests iterate over a `CtyValue` wrapping a Python `set` (if `CtySet._value` is a `frozenset`, this path is for other direct iterables).
  - Ensure tests iterate over a `CtyValue` wrapping a Python `dict` (for `CtyMap` or `CtyObject`).

---

### `__hash__` Special Method (Additional Fallbacks)
- **Lines (approximate):**
    - 768-770: `except TypeError: value_hash = hash(repr(self._value))` (for tuple/frozenset where direct hash fails)
    - 803-811: `except TypeError: value_hash = hash(repr(self._value))` (for other types) and `except TypeError: value_hash = hash(id(self._value))` (ultimate fallback).
- **Description**: These are deeper fallback mechanisms in the hashing logic.
- **Importance**: Ensures hashability under adverse conditions.
- **Testing Complexity**: High. (As described in the previous TODO list, requires custom objects that specifically fail `hash()` in stages).
- **Suggested Tests**: (As described in the previous TODO list for these lines).

---

### `__eq__` Special Method (Additional Fallbacks)
- **Lines (approximate):**
    - `824-865`: This range covers many comparison paths. Specific uncovered lines might be:
        - `return self._value == other._value` (the final fallback when `_vtype` matches and it's not a known primitive or collection that was handled earlier).
        - `except Exception: return False` (catch-all for the final fallback comparison).
        - Specific branches within collection comparisons if not all path permutations (e.g., different lengths, different element types within collections that are themselves CtyValues) are tested.
- **Description**: Fallback equality comparison and its error handling, plus detailed paths for collection comparisons.
- **Importance**: Guarantees correct equality results and graceful failure for all scenarios.
- **Testing Complexity**: High. Requires testing with `CtyValue`s wrapping custom objects where `__eq__` might be tricky or raise exceptions. Also needs varied collection comparison tests.
- **Suggested Tests**:
    - Test equality of `CtyValue`s wrapping custom objects where `obj1 == obj2` might raise an error.
    - Test equality of `CtyList`s/`CtyMap`s where elements/values are complex nested `CtyValue`s with differing states (null/unknown).

---

### `__getitem__` Special Method (Additional Paths)
- **Lines (approximate):**
    - 911-914: `else: raise KeyError(...)` for invalid CtyValue key type/state in map lookup.
    - 920: `if validated_key.is_null or validated_key.is_unknown: raise KeyError(...)`
    - 927-929: `except CtyMapValidationError as e: raise KeyError(...)` for invalid raw key.
    - 935: `else: raise KeyError(...)` for key not found in map.
    - 940-943: Slice handling for `CtyTuple` (`element_types = self._vtype.element_types[start:stop:step]`, `tuple_type = CtyTuple(...)`, `return CtyValue(...)`).
- **Description**: Specific error branches in map key validation and the tuple slicing result construction.
- **Importance**: Ensures map access fails correctly with invalid keys and tuple slicing maintains type integrity.
- **Testing Complexity**: Medium.
    - Map errors: Provide `CtyValue` keys that are null, unknown, or of an incompatible type (e.g., `CtyNumber` key for a map expecting `CtyString` keys). Provide raw keys that would fail `CtyString().validate()`.
    - Tuple slicing: Test various slices on tuples with mixed `CtyType` elements.
- **Suggested Tests**:
  - `map_val[CtyValue.null(CtyString())]`
  - `map_val[CtyValue.number(1)]` (if map keys are `CtyString`)
  - `map_val[SomeUnstringableObject()]`
  - Test slices like `my_tuple_val[1:3]`, `my_tuple_val[::-1]` on a `CtyValue` of `CtyTuple` type.

---

### `__contains__` Special Method (Additional Paths)
- **Lines (approximate):**
    - 981: `else: return False` (if CtyValue key is invalid type/state for map).
    - 991-994: `except Exception: return False` (if raw key validation fails for map).
    - 1000: `return str_key in self._value` (the actual check after key processing).
    - 1002-1003: `except Exception: return False` (if element validation fails for list/set/tuple).
    - 1037-1039: `elif hasattr(self._value, '__contains__'): return item in self._value` (fallback for other iterables).
- **Description**: Specific validation failure paths for map keys and collection elements during membership testing, and the fallback path.
- **Importance**: Accurate and safe membership testing.
- **Testing Complexity**: Medium.
    - Map keys: `CtyValue.null(CtyString()) in map_val`. An unstringable object as a key.
    - Collection elements: `SomeIncompatibleType() in list_val`.
    - Fallback: A `CtyValue` wrapping a custom iterable that defines `__contains__`.
- **Suggested Tests**:
  - See suggestions for `__getitem__` for map key validation.
  - `MyNonCtyType() in list_of_strings_val`.
  - Create `CustomIterableWithValue` class, `val = CtyValue(CtyDynamic(), CustomIterableWithValue(...)); "item" in val`.

---

### Serialization/Deserialization (Specific `to_json_comparable_dict` paths and codec imports)
- **Lines (approximate):**
    - Lines within `to_json_comparable_dict` (1053-1057, 1097-1100, 1106, 1108-1109, 1119-1121, 1131-1150): These mostly relate to the `get_friendly_type_name` helper function and how it processes various CtyTypes, especially nested collections, CtyObject, and CtyTuple. Uncoverage here means not all type structures are being passed through this function.
    - Import lines in `to_json_string`, `from_json_string`, `to_msgpack_bytes`, `from_msgpack_bytes` (1163-1167, 1192-1196, etc.): These indicate that the serialization methods themselves might not be exercised across all code paths or types.
- **Description**: These lines are crucial for ensuring that all CtyTypes, including complex nested ones and dynamic types, are correctly represented in a JSON-comparable dictionary format and that the main serialization/deserialization entry points are tested.
- **Importance**: Correct and complete serialization/deserialization is vital for interoperability and data exchange.
- **Testing Complexity**: Medium to High. Requires constructing a wide variety of `CtyValue` instances, including those with deeply nested structures and diverse types like `CtyObject`, `CtyTuple`, and `CtyDynamic`.
- **Suggested Tests**:
  - For `to_json_comparable_dict` and `get_friendly_type_name`:
    - Test with `CtyValue(CtyDynamic(), ...)` using various underlying types.
    - Test with `CtyObject` having attributes of collection types (e.g., `list(map(string))`).
    - Test with `CtyTuple` having elements of collection types or other tuples/objects.
    - Test with empty collections within complex structures.
  - For main serialization methods (to cover imports):
    - Ensure `to_json_string`, `from_json_string`, `to_msgpack_bytes`, `from_msgpack_bytes` are called for each major CtyValue category (primitive, list, map, object, tuple, set, dynamic, unknown, null). This will also improve coverage in `codec.py`.

---
This detailed list should guide the creation of new tests to enhance the coverage for `src/pyvider/cty/values/base.py`.
