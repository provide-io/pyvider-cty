#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""merge against go-cty's `MergeFunc` (cty/function/stdlib/collection.go).

The result *type* is the whole of the difficulty here. This package used to
infer it from the merged payload, which turned a merge of maps into an object
-- so `merge` could not be composed with anything expecting a map back, and the
type that crossed the wire changed shape depending on the data.
"""

import pytest

from pyvider.cty import (
    CtyDynamic,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyValue,
)
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import merge

STRING_MAP = CtyMap(element_type=CtyString())
NUMBER_MAP = CtyMap(element_type=CtyNumber())


def obj(**attrs: str) -> CtyValue[object]:
    object_type = CtyObject(attribute_types=dict.fromkeys(attrs, CtyString()))
    return object_type.validate(attrs)


class TestMergeResultType:
    def test_maps_of_the_same_type_merge_into_a_map(self) -> None:
        """The types all match, so go-cty returns the first argument's type."""
        merged = merge(STRING_MAP.validate({"a": "1"}), STRING_MAP.validate({"b": "2"}))

        assert merged.type == STRING_MAP
        assert merged.raw_value == {"a": "1", "b": "2"}

    def test_objects_of_the_same_type_merge_into_that_object(self) -> None:
        same = obj(a="1")

        assert merge(same, same).type == CtyObject(attribute_types={"a": CtyString()})

    def test_objects_of_different_types_merge_into_a_combined_object(self) -> None:
        merged = merge(obj(a="1"), obj(b="2"))

        assert merged.type == CtyObject(attribute_types={"a": CtyString(), "b": CtyString()})

    def test_maps_of_different_element_types_merge_into_an_object(self) -> None:
        """Nothing else can hold both; a map would have to widen its element type."""
        merged = merge(STRING_MAP.validate({"a": "1"}), NUMBER_MAP.validate({"b": 2}))

        assert merged.type == CtyObject(attribute_types={"a": CtyString(), "b": CtyNumber()})

    def test_a_map_and_an_object_merge_into_an_object(self) -> None:
        merged = merge(STRING_MAP.validate({"a": "1"}), obj(b="2"))

        assert merged.type == CtyObject(attribute_types={"a": CtyString(), "b": CtyString()})

    def test_one_map_stays_a_map(self) -> None:
        assert merge(STRING_MAP.validate({"a": "1"})).type == STRING_MAP

    def test_no_arguments_gives_an_empty_object(self) -> None:
        """There are no key-value types to read, so go-cty assumes an empty object."""
        merged = merge()

        assert merged.type == CtyObject(attribute_types={})
        assert merged.raw_value == {}

    def test_empty_maps_still_merge_into_a_map(self) -> None:
        merged = merge(STRING_MAP.validate({}), STRING_MAP.validate({}))

        assert merged.type == STRING_MAP
        assert merged.raw_value == {}


class TestMergeValues:
    def test_a_later_argument_wins(self) -> None:
        merged = merge(STRING_MAP.validate({"a": "1"}), STRING_MAP.validate({"a": "2"}))

        assert merged.raw_value == {"a": "2"}

    def test_a_null_map_contributes_nothing_but_still_counts_for_the_type(self) -> None:
        merged = merge(STRING_MAP.validate({"a": "1"}), CtyValue.null(STRING_MAP))

        assert merged.type == STRING_MAP
        assert merged.raw_value == {"a": "1"}

    def test_a_null_object_compares_as_the_empty_object_type(self) -> None:
        """go-cty substitutes the empty object type before the matching test.

        So a null object never makes the arguments 'match' unless every other
        argument is also an empty object.
        """
        merged = merge(obj(a="1"), CtyValue.null(CtyObject(attribute_types={"b": CtyString()})))

        assert merged.type == CtyObject(attribute_types={"a": CtyString()})
        assert merged.raw_value == {"a": "1"}


class TestMergeUnknownAndDynamic:
    def test_an_unknown_argument_makes_the_result_unknown(self) -> None:
        merged = merge(STRING_MAP.validate({"a": "1"}), CtyValue.unknown(STRING_MAP))

        assert merged.is_unknown

    def test_an_unknown_map_of_a_matching_type_keeps_that_type(self) -> None:
        """The keys are unknown, but every argument still has the same type."""
        merged = merge(STRING_MAP.validate({"a": "1"}), CtyValue.unknown(STRING_MAP))

        assert merged.type == STRING_MAP

    def test_an_unknown_map_mixed_with_an_object_gives_up_on_the_type(self) -> None:
        """Its keys are exactly what is unknown, so the attribute set is not predictable."""
        merged = merge(obj(a="1"), CtyValue.unknown(STRING_MAP))

        assert merged.is_unknown
        assert merged.type == CtyDynamic()

    def test_a_dynamic_wrapper_is_seen_through(self) -> None:
        """Dynamic means different things in the two packages.

        In go-cty a known value never carries DynamicPseudoType, so its rule
        about dynamic arguments is about types that are not settled yet. Here a
        wrapper regularly stands in front of a concrete object, and that inner
        type is the one go-cty would have been given.
        """
        merged = merge(obj(a="1"), CtyDynamic().validate({"b": "2"}))

        assert merged.type == CtyObject(attribute_types={"a": CtyString(), "b": CtyString()})

    def test_an_unsettled_dynamic_gives_up_on_the_type(self) -> None:
        merged = merge(obj(a="1"), CtyValue.unknown(CtyDynamic()))

        assert merged.is_unknown
        assert merged.type == CtyDynamic()


class TestMergeRejects:
    @pytest.mark.parametrize(
        "bad",
        [
            CtyString().validate("x"),
            CtyNumber().validate(1),
        ],
    )
    def test_an_argument_that_is_neither_map_nor_object(self, bad: CtyValue[object]) -> None:
        with pytest.raises(CtyFunctionError, match="must be maps or objects"):
            merge(STRING_MAP.validate({"a": "1"}), bad)


# 🌊🪢🔚
