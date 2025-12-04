#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from hypothesis import assume, given, settings, strategies as st

from pyvider.cty import CtyBool, CtyDynamic, CtyList, CtyNumber, CtyObject, CtyString
from pyvider.cty.conversion.explicit import convert, unify
from pyvider.cty.types import CtyType

# Strategy for generating simple types
simple_types = st.sampled_from(
    [
        CtyString(),
        CtyNumber(),
        CtyBool(),
    ]
)


# Strategy for generating list types
@st.composite
def list_types_strategy(draw):
    """Generate CtyList types with various element types."""
    element_type = draw(simple_types | st.just(CtyDynamic()))
    return CtyList(element_type=element_type)


# Strategy for generating object types
@st.composite
def object_types_strategy(draw):
    """Generate CtyObject types with various attribute configurations."""
    num_attrs = draw(st.integers(min_value=1, max_value=5))
    attr_names = draw(
        st.lists(
            st.text(
                min_size=1,
                max_size=10,
                alphabet=st.characters(whitelist_categories=("L", "N"), blacklist_characters="_"),
            ),
            min_size=num_attrs,
            max_size=num_attrs,
            unique=True,
        )
    )

    # Ensure at least one attribute
    if not attr_names:
        attr_names = ["default"]

    attr_types = {name: draw(simple_types) for name in attr_names}

    # Randomly make some attributes optional
    num_optional = draw(st.integers(min_value=0, max_value=len(attr_names)))
    optional_attrs = frozenset(
        draw(st.lists(st.sampled_from(attr_names), min_size=num_optional, max_size=num_optional, unique=True))
    )

    return CtyObject(attribute_types=attr_types, optional_attributes=optional_attrs)


# Combined type strategy
all_types = simple_types | list_types_strategy() | object_types_strategy() | st.just(CtyDynamic())


@settings(deadline=1000, max_examples=200)
@given(cty_type=all_types)
def test_unify_single_type_returns_same_type(cty_type: CtyType) -> None:
    """
    Property test: Unifying a single type should return that type.

    Tests the identity property: unify({T}) = T
    """
    result = unify([cty_type])
    assert result.equal(cty_type)


@settings(deadline=1000, max_examples=200)
@given(types=st.lists(all_types, min_size=1, max_size=5))
def test_unify_is_idempotent(types: list[CtyType]) -> None:
    """
    Property test: Unifying types is idempotent.

    Tests that unify(unify(types)) == unify(types)
    """
    unified_once = unify(types)
    unified_twice = unify([unified_once])

    assert unified_twice.equal(unified_once)


@settings(deadline=1000, max_examples=200)
@given(types=st.lists(all_types, min_size=1, max_size=5))
def test_unify_with_dynamic_returns_dynamic(types: list[CtyType]) -> None:
    """
    Property test: Unifying any types with CtyDynamic returns CtyDynamic.

    Tests that CtyDynamic is the absorbing element for unification.
    """
    types_with_dynamic = [*types, CtyDynamic()]
    result = unify(types_with_dynamic)

    assert isinstance(result, CtyDynamic)


@settings(deadline=1000, max_examples=200)
@given(element_types=st.lists(simple_types | st.just(CtyDynamic()), min_size=1, max_size=4))
def test_unify_list_types_unifies_element_types(element_types: list[CtyType]) -> None:
    """
    Property test: Unifying list types should unify their element types.

    Tests that unify({List[T1], List[T2], ...}) = List[unify({T1, T2, ...})]
    """
    list_types = [CtyList(element_type=et) for et in element_types]
    unified_lists = unify(list_types)

    # Should be a list type
    assert isinstance(unified_lists, CtyList)

    # Element type should be the unification of all element types
    expected_element_type = unify(element_types)
    assert unified_lists.element_type.equal(expected_element_type)


@settings(deadline=1000, max_examples=100)
@given(data=st.data())
def test_unify_objects_with_same_keys_unifies_attribute_types(data) -> None:
    """
    Property test: Unifying object types with the same keys unifies attribute types.

    Tests that objects with identical attribute names can be unified by
    unifying each attribute type.
    """
    # Generate a set of attribute names
    attr_names = data.draw(
        st.lists(
            st.text(
                min_size=1,
                max_size=10,
                alphabet=st.characters(whitelist_categories=("L",), blacklist_characters="_"),
            ),
            min_size=1,
            max_size=3,
            unique=True,
        )
    )

    if not attr_names:
        attr_names = ["default"]

    # Generate 2-3 object types with the same keys but different value types
    num_objects = data.draw(st.integers(min_value=2, max_value=3))
    object_types = []

    for _ in range(num_objects):
        attr_types = {name: data.draw(simple_types) for name in attr_names}
        object_types.append(CtyObject(attribute_types=attr_types))

    unified = unify(object_types)

    # Should be an object type
    assert isinstance(unified, CtyObject)

    # Should have the same keys
    assert set(unified.attribute_types.keys()) == set(attr_names)

    # Each attribute should be the unification of the corresponding attributes
    for attr_name in attr_names:
        attr_type_list = [obj.attribute_types[attr_name] for obj in object_types]
        expected_attr_type = unify(attr_type_list)
        assert unified.attribute_types[attr_name].equal(expected_attr_type)


@settings(deadline=1000, max_examples=100)
@given(data=st.data())
def test_unify_objects_with_different_keys_returns_dynamic(data) -> None:
    """
    Property test: Unifying objects with different keys returns CtyDynamic.

    Tests that objects with incompatible structures cannot be unified.
    """
    # Generate two object types with different keys
    keys1 = data.draw(
        st.lists(
            st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=("L",))),
            min_size=1,
            max_size=3,
            unique=True,
        )
    )
    keys2 = data.draw(
        st.lists(
            st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=("L",))),
            min_size=1,
            max_size=3,
            unique=True,
        )
    )

    # Ensure keys are different
    assume(set(keys1) != set(keys2))

    if not keys1:
        keys1 = ["default1"]
    if not keys2:
        keys2 = ["default2"]

    obj1 = CtyObject(attribute_types={k: CtyString() for k in keys1})
    obj2 = CtyObject(attribute_types={k: CtyString() for k in keys2})

    unified = unify([obj1, obj2])

    # Should return CtyDynamic since keys don't match
    assert isinstance(unified, CtyDynamic)


@settings(deadline=1000, max_examples=100)
@given(types=st.lists(simple_types, min_size=2, max_size=4))
def test_unify_different_primitive_types_returns_dynamic(types: list[CtyType]) -> None:
    """
    Property test: Unifying different primitive types returns CtyDynamic.

    Tests that incompatible primitive types cannot be unified.
    """
    # Ensure we have at least two different types
    unique_type_names = {type(t).__name__ for t in types}
    assume(len(unique_type_names) >= 2)

    unified = unify(types)

    # Different primitive types should unify to CtyDynamic
    assert isinstance(unified, CtyDynamic)


def test_unify_empty_list_returns_dynamic() -> None:
    """
    Property test: Unifying an empty list returns CtyDynamic.

    Tests the base case of unification.
    """
    result = unify([])
    assert isinstance(result, CtyDynamic)


@settings(deadline=1000, max_examples=50)
@given(data=st.data())
def test_conversion_respects_unified_type(data) -> None:
    """
    Property test: Values can be converted to their unified type.

    Tests that if types can be unified, values of those types can be
    converted to the unified type.
    """
    # Generate a list type
    element_type1 = data.draw(simple_types)
    element_type2 = data.draw(simple_types)

    list_type1 = CtyList(element_type=element_type1)
    list_type2 = CtyList(element_type=element_type2)

    # Unify the list types
    unified_type = unify([list_type1, list_type2])

    # Should get a list type with unified element type
    assert isinstance(unified_type, CtyList)

    # Create a value of the first type
    if isinstance(element_type1, CtyString):
        value1 = list_type1.validate(["test"])
    elif isinstance(element_type1, CtyNumber):
        value1 = list_type1.validate([42])
    else:  # CtyBool
        value1 = list_type1.validate([True])

    # Should be able to convert to unified type
    try:
        converted = convert(value1, unified_type)
        assert converted.type.equal(unified_type)
    except Exception:
        # Conversion might fail for incompatible types, which is expected
        # when element types are incompatible primitives
        assert isinstance(unified_type.element_type, CtyDynamic)


# 🌊🪢🔚
