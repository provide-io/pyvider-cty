#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from hypothesis import assume, given, settings, strategies as st

from pyvider.cty import CtyBool, CtyDynamic, CtyList, CtyMap, CtyNumber, CtyObject, CtyString
from pyvider.cty.conversion.explicit import convert
from pyvider.cty.conversion.unify import unify
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
    """unify({T}) = T. The one property that survived the port unchanged."""
    result = unify([cty_type])
    assert result is not None
    assert result.equal(cty_type)


@settings(deadline=1000, max_examples=200)
@given(types=st.lists(all_types, min_size=1, max_size=5))
def test_unify_is_idempotent(types: list[CtyType]) -> None:
    """Unifying a unified type with itself changes nothing."""
    unified_once = unify(types)
    assume(unified_once is not None)

    unified_twice = unify([unified_once])

    assert unified_twice is not None
    assert unified_twice.equal(unified_once)


@settings(deadline=1000, max_examples=200)
@given(types=st.lists(all_types, min_size=1, max_size=5))
def test_dynamic_never_prevents_unification(types: list[CtyType]) -> None:
    """Dynamic is not the absorbing element, and asserting it was hid the bug.

    This file used to require `unify(types + [dynamic]) is dynamic`, which is
    exactly backwards for primitives: dynamic has the *lowest* preference in
    go-cty, so `unify(string, dynamic)` is string. It is absorbing only among
    collections, where which conversion path a resolved dynamic would take
    cannot be predicted.

    What is true in general is weaker and is the property worth pinning: adding
    a dynamic never turns a unifiable group into an unresolvable one.
    """
    without = unify(types)
    with_dynamic = unify([*types, CtyDynamic()])

    if without is not None:
        assert with_dynamic is not None


@settings(deadline=1000, max_examples=200)
@given(types=st.lists(simple_types, min_size=1, max_size=4))
def test_a_dynamic_among_primitives_defers_to_its_neighbours(types: list[CtyType]) -> None:
    """The half of the old property that is true, stated correctly."""
    assume(unify(types) is not None)

    assert unify([*types, CtyDynamic()]) == unify(types)


@settings(deadline=1000, max_examples=200)
@given(element_types=st.lists(simple_types, min_size=1, max_size=4))
def test_unify_list_types_unifies_element_types(element_types: list[CtyType]) -> None:
    """unify({list(T1), list(T2)}) = list(unify({T1, T2})), or neither exists.

    Restricted to concrete element types: a `list(dynamic)` in the group makes
    the whole group unify to dynamic rather than to a list, which is a
    different property and is pinned separately below.
    """
    list_types = [CtyList(element_type=element) for element in element_types]

    unified_lists = unify(list_types)
    unified_elements = unify(element_types)

    if unified_elements is None:
        assert unified_lists is None
        return
    assert isinstance(unified_lists, CtyList)
    assert unified_lists.element_type.equal(unified_elements)


@settings(deadline=1000, max_examples=200)
@given(element_type=simple_types)
def test_a_dynamic_alongside_a_collection_makes_the_whole_result_dynamic(
    element_type: CtyType,
) -> None:
    """Which path unification takes once the dynamic resolves is unknowable.

    Note what this is *not*: a `list(dynamic)` is a list, so it groups with the
    other lists and its element defers to theirs -- `unify(list(string),
    list(dynamic))` is `list(string)`. It is a bare dynamic *beside* a
    collection that forces the whole answer to dynamic.
    """
    assert isinstance(unify([CtyList(element_type=element_type), CtyDynamic()]), CtyDynamic)

    deferred = unify([CtyList(element_type=element_type), CtyList(element_type=CtyDynamic())])
    assert isinstance(deferred, CtyList)
    assert deferred.element_type.equal(element_type)


@settings(deadline=1000, max_examples=100)
@given(names=st.lists(st.sampled_from(["a", "b", "c", "d"]), min_size=1, max_size=4, unique=True))
def test_objects_with_the_same_attribute_names_unify_attribute_by_attribute(
    names: list[str],
) -> None:
    left = CtyObject(attribute_types=dict.fromkeys(names, CtyString()))
    right = CtyObject(attribute_types=dict.fromkeys(names, CtyNumber()))

    unified = unify([left, right])

    assert isinstance(unified, CtyObject)
    assert set(unified.attribute_types) == set(names)
    assert all(attribute.equal(CtyString()) for attribute in unified.attribute_types.values())


def test_objects_with_different_attribute_names_unify_as_a_map() -> None:
    """Not dynamic, which is what this file used to require.

    An object whose per-attribute types no longer line up is map-shaped data,
    and go-cty says so: `unifyObjectTypes` falls back to `unifyObjectTypesToMap`
    rather than giving up. Answering dynamic threw away the element type that
    every attribute did agree on.
    """
    unified = unify([CtyObject({"a": CtyString()}), CtyObject({"b": CtyString()})])

    assert unified is not None
    assert unified.equal(CtyMap(element_type=CtyString()))


def test_objects_whose_attributes_have_no_common_type_do_not_unify() -> None:
    assert unify([CtyObject({"a": CtyNumber()}), CtyObject({"b": CtyBool()})]) is None


@settings(deadline=1000, max_examples=200)
@given(types=st.lists(simple_types, min_size=2, max_size=3, unique=True))
def test_mixed_primitives_unify_to_string_when_one_is_a_string(types: list[CtyType]) -> None:
    """String is the supertype of the primitives; number and bool have none.

    This used to assert dynamic for every mixed group, which is both wrong
    answers at once -- it lost the widening go-cty does, and it reported a
    result where go-cty reports failure.
    """
    unified = unify(types)

    if any(isinstance(candidate, CtyString) for candidate in types):
        assert unified is not None
        assert unified.equal(CtyString())
    else:
        assert unified is None


def test_unify_of_nothing_has_no_answer() -> None:
    """Degenerate, and None rather than dynamic: there is nothing to describe."""
    assert unify([]) is None


@settings(deadline=1000, max_examples=100)
@given(types=st.lists(simple_types, min_size=1, max_size=4))
def test_every_type_converts_to_the_unified_type(types: list[CtyType]) -> None:
    """The contract that makes unification worth anything.

    If `unify` names a type, every input must actually reach it -- otherwise it
    has promised a type that nothing can be converted to, and the caller finds
    out at conversion time.
    """
    unified = unify(types)
    assume(unified is not None)

    samples = {
        "string": "1",
        "number": 1,
        "bool": True,
    }
    for source in types:
        value = source.validate(samples[source.ctype])
        converted = convert(value, unified)
        assert converted.type.equal(unified)


# 🌊🪢🔚
