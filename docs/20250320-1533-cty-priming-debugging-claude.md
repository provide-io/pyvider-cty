
# CTY Test Suite Priming Prompt

## CTY Type System Testing Requirements

When writing tests for the Pyvider CTY type system, strict adherence to type safety and immutability principles is essential. The CTY system is a strongly-typed wrapper around Python's dynamic types, and tests must verify both type correctness and value correctness.

### Core Testing Principles

1. **Verify Type Before Value**
   - Always check the returned object's type with `isinstance()` before checking its contents
   - Never compare CTY objects directly with Python primitives

2. **Type Hierarchy Navigation**
   - Access values through `.value` property
   - For nested structures, navigate through multiple `.value` properties
   - Maintain type awareness at each level of nesting

3. **Immutability Verification**
   - Verify operations return new objects rather than modifying existing ones
   - Check original objects remain unchanged after operations

4. **Value Extraction for Comparison**
   - Extract raw values via `.value` before comparing to expected results
   - Use list comprehensions for collections: `[item.value for item in cty_list.value]`

### Test Pattern Examples

```python
# CORRECT - Type verification first, then value checking
def test_string_list_validation():
    string_list = CtyList(element_type=CtyString())
    result = string_list.validate(["a", "b", "c"])
    
    # First verify type
    assert isinstance(result, CtyList)
    assert len(result.value) == 3
    assert all(isinstance(item, CtyString) for item in result.value)
    
    # Then verify values
    assert [item.value for item in result.value] == ["a", "b", "c"]

# CORRECT - Nested structure navigation
def test_nested_list_validation():
    inner_list = CtyList(element_type=CtyString())
    outer_list = CtyList(element_type=inner_list)
    result = outer_list.validate([["a", "b"], ["c"]])
    
    assert isinstance(result, CtyList)
    assert len(result.value) == 2
    assert isinstance(result.value[0], CtyList)
    assert isinstance(result.value[0].value[0], CtyString)
    assert result.value[0].value[0].value == "a"

# CORRECT - Error handling
def test_validation_errors():
    with pytest.raises(CtyValidationError) as cm:
        CtyList(element_type=CtyString()).validate(None)
    assert "Cannot validate None as a list" in str(cm.value)
```

### Common Anti-Patterns to Avoid

```python
# INCORRECT - Direct comparison with Python primitives
def test_wrong_comparison():
    string_list = CtyList(element_type=CtyString())
    result = string_list.validate(["a", "b"])
    assert result == ["a", "b"]  # WRONG!

# INCORRECT - Not checking types
def test_missing_type_check():
    string_list = CtyList(element_type=CtyString())
    result = string_list.validate(["a"])
    assert result.value[0] == "a"  # WRONG!

# INCORRECT - Using unittest methods in pytest
def test_wrong_assertion_style():
    self.assertIsInstance(result, CtyList)  # WRONG!
    self.assertEqual(result.value[0].value, "a")  # WRONG!
```

### Implementation Notes

- Use pytest's native assertion style (`assert x == y`), not unittest style (`self.assertEqual()`)
- Always handle None, unknown, and null values according to the CTY specification
- Verify exception messages contain expected content using `in str(cm.value)`
- Remember collections contain CTY wrapped values, not Python primitives

Following these principles ensures the tests verify the CTY type system's behavior correctly while maintaining its strong typing guarantees.