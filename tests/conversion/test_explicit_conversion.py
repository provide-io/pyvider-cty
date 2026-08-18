#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TDD Test Suite for the explicit conversion and unification functions.

These tests define the required behavior for the `convert` and `unify`
functions, which are intended to mirror the functionality of the `go-cty/convert`
package. These tests will fail until the functions are implemented in the
`pyvider.cty.conversion.explicit` module."""

from collections.abc import Iterable
from decimal import Decimal

import pytest

from pyvider.cty import (
    CtyBool,
    CtyCapsuleWithOps,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyType,
    CtyValue,
)
from pyvider.cty.conversion import convert, unify
from pyvider.cty.exceptions import CtyConversionError
from pyvider.cty.marks import CtyMark


class TestConvertFunction:
    """Tests the `convert(value, target_type)` function."""

    @pytest.mark.parametrize(
        "source_val, target_type, expected_val",
        [
            (CtyValue(CtyNumber(), 123), CtyString(), "123"),
            (CtyValue(CtyNumber(), 123.45), CtyString(), "123.45"),
            (CtyValue(CtyBool(), True), CtyString(), "true"),
            (CtyValue(CtyBool(), False), CtyString(), "false"),
            (CtyValue(CtyString(), "123"), CtyNumber(), 123),
            (CtyValue(CtyString(), "123.45"), CtyNumber(), 123.45),
            (CtyValue(CtyString(), "-1.5e2"), CtyNumber(), -150),
            (CtyValue(CtyString(), "true"), CtyBool(), True),
            (CtyValue(CtyString(), "false"), CtyBool(), False),
            # go-cty accepts "1" and "0" as well as "true" and "false", and
            # nothing else -- see the mixed-case entries in the refusal table
            # below, which this row used to contradict.
            (CtyValue(CtyString(), "1"), CtyBool(), True),
            (CtyValue(CtyString(), "0"), CtyBool(), False),
            (CtyValue(CtyNumber(), 100), CtyString(), "100"),
            (CtyValue(CtyNumber(), Decimal("1e2")), CtyString(), "100"),
            (CtyValue(CtyNumber(), Decimal("1.50")), CtyString(), "1.5"),
            (CtyValue(CtyNumber(), Decimal("1e-7")), CtyString(), "0.0000001"),
            # `big.Float.Text` spells an infinity `+Inf`, sign always shown, and
            # this conversion *is* `Text('f', -1)` (`conversion_primitive.go:16`).
            # `str(Decimal)` says "Infinity", which is a Python spelling and was
            # what this returned; confirmed against go-cty v1.19.0 by calling
            # the oracle -- `format("%s", {"$number":"Infinity"})`, a sweep row.
            (CtyValue(CtyNumber(), Decimal("Infinity")), CtyString(), "+Inf"),
            (CtyValue(CtyNumber(), Decimal("-Infinity")), CtyString(), "-Inf"),
            (CtyValue(CtyNumber(), Decimal("NaN")), CtyString(), "NaN"),
            (
                CtyValue(CtyList(element_type=CtyString()), ["a", "b"]),
                CtySet(element_type=CtyString()),
                CtySet(element_type=CtyString()).validate(["a", "b"]),
            ),
            (
                CtyValue(CtySet(element_type=CtyString()), {"a", "b"}),
                CtyList(element_type=CtyString()),
                ["a", "b"],
            ),
            (
                # A dynamic element type in the target is the absence of a
                # constraint, so go-cty unifies the tuple's element types rather
                # than wrapping each element in a dynamic. Confirmed against the
                # harness: list(string), ["a", "1"].
                CtyValue(CtyTuple(element_types=(CtyString(), CtyNumber())), ("a", 1)),
                CtyList(element_type=CtyString()),
                [CtyString().validate("a"), CtyString().validate("1")],
            ),
            (CtyValue(CtyNumber(), 42), CtyDynamic(), CtyValue(CtyNumber(), 42)),
            (CtyValue.null(CtyString()), CtyNumber(), None),
            (CtyValue.unknown(CtyString()), CtyNumber(), None),
        ],
    )
    def test_successful_conversions(
        self, source_val: CtyValue, target_type: CtyType, expected_val: object
    ) -> None:
        converted_val = convert(source_val, target_type)
        if isinstance(target_type, CtyDynamic):
            assert converted_val == source_val
            return
        assert converted_val.type.equal(target_type)
        if source_val.is_null:
            assert converted_val.is_null
        elif source_val.is_unknown:
            assert converted_val.is_unknown
        elif isinstance(target_type, CtySet):
            assert converted_val == expected_val
        elif isinstance(target_type, CtyList) and isinstance(source_val.type, CtySet):
            assert isinstance(converted_val.value, tuple)
            assert len(converted_val.value) == len(expected_val)
            assert {v.value for v in converted_val.value} == set(expected_val)
        elif isinstance(target_type, CtyList) and isinstance(source_val.type, CtyTuple):
            assert list(converted_val.value) == expected_val
        else:
            assert converted_val.raw_value == expected_val

    @pytest.mark.parametrize(
        "source_val, target_type",
        [
            (CtyValue(CtyString(), "not-a-number"), CtyNumber()),
            (CtyValue(CtyString(), "yes"), CtyBool()),
            (CtyValue(CtyNumber(), 1), CtyBool()),
            (CtyValue(CtyObject({}), {}), CtyList(element_type=CtyDynamic())),
            (
                CtyValue(CtyList(element_type=CtyString()), ["a"]),
                CtyList(element_type=CtyNumber()),
            ),
            # Mixed case. This used to convert, because the comparison
            # lowercased first; go-cty refuses it and says to use lowercase.
            (CtyValue(CtyString(), "TRUE"), CtyBool()),
            (CtyValue(CtyString(), "False"), CtyBool()),
            # A bool is not a number. This used to return 1, because the payload
            # went to CtyNumber().validate and a Python bool is an int.
            (CtyValue(CtyBool(), True), CtyNumber()),
            # Nothing but a number or a bool converts to a string. This used to
            # return the repr of the internal tuple of CtyValues.
            (CtyValue(CtyList(element_type=CtyString()), ["a"]), CtyString()),
            (CtyValue(CtyObject({}), {}), CtyString()),
        ],
    )
    def test_failed_conversions(self, source_val: CtyValue, target_type: CtyType) -> None:
        with pytest.raises(CtyConversionError):
            convert(source_val, target_type)

    def test_a_collection_does_not_stringify_as_its_repr(self) -> None:
        """The refusal above, stated as the bug it fixes.

        `convert` reached `str(value.value)` for anything it did not recognise,
        and the payload of a collection is its internal tuple of CtyValues, so
        this returned the literal text "(CtyValue(vtype=CtyString(), ...),)" --
        a well-formed string, of the right type, that would have gone on to
        Terraform state.
        """
        collection = CtyValue(CtyList(element_type=CtyString()), ["a"])

        with pytest.raises(CtyConversionError) as caught:
            convert(collection, CtyString())

        assert "CtyValue(" not in str(caught.value)

    def test_conversion_preserves_marks(self) -> None:
        marked_val = CtyValue(CtyNumber(), 123).mark(CtyMark("sensitive"))
        converted_val = convert(marked_val, CtyString())
        assert converted_val.has_mark(CtyMark("sensitive"))
        assert converted_val.value == "123"

    def test_convert_list_to_list_same_type(self) -> None:
        list_val = CtyValue(CtyList(element_type=CtyString()), ["a", "b"])
        converted_val = convert(list_val, CtyList(element_type=CtyString()))
        assert converted_val is list_val

    def test_convert_list_to_list_of_dynamic(self) -> None:
        """`list(any)` is the absence of a constraint, not a list of dynamics.

        This asserted a `list(dynamic)` result with every element wrapped.
        go-cty resolves the element type from the source instead -- converting
        an element to dynamic is the identity, and the list is then built from
        what that produced -- so the answer is the `list(string)` that went in.
        The difference reaches the wire: a provider returning `list(any)` would
        tell Terraform nothing about its elements.
        """
        list_val = CtyList(element_type=CtyString()).validate(["a", "b"])

        converted_val = convert(list_val, CtyList(element_type=CtyDynamic()))

        assert converted_val.type.equal(CtyList(element_type=CtyString()))
        assert len(converted_val.value) == 2
        assert converted_val.value[0].type.equal(CtyString())

    def test_the_wrong_case_is_refused_differently_from_a_non_bool(self) -> None:
        """Both raise, and asserting only that hides the branch.

        Found by mutation testing: flipping the `in` to `not in` at the case
        check sent every unconvertible string down the "use lowercase" path, and
        nothing failed, because every test here asked only for the exception
        type. go-cty tells the two apart on purpose -- "TRUE" is a value the
        author meant as a bool, and saying so is more use than "a bool is
        required".
        """
        with pytest.raises(CtyConversionError, match="lowercase"):
            convert(CtyValue(CtyString(), "TRUE"), CtyBool())

        with pytest.raises(CtyConversionError) as caught:
            convert(CtyValue(CtyString(), "yes"), CtyBool())
        assert "lowercase" not in str(caught.value)

    def test_a_dynamic_converts_the_value_it_wraps(self) -> None:
        """A CtyDynamic is a wrapper; the conversion applies to what is inside."""
        wrapped = CtyDynamic().validate(123)

        converted = convert(wrapped, CtyString())

        assert converted.type.equal(CtyString())
        assert converted.value == "123"

    def test_a_dynamic_wrapping_a_raw_payload_is_refused(self) -> None:
        """A CtyDynamic's payload is always another CtyValue.

        It is what carries the concrete type, so a dynamic holding a bare
        Python object has no type to convert *from*.
        """
        malformed = CtyValue(CtyDynamic(), "not a CtyValue")

        with pytest.raises(CtyConversionError):
            convert(malformed, CtyString())

    def test_an_object_whose_payload_is_not_a_dict_is_refused(self) -> None:
        malformed = CtyValue(CtyObject({"a": CtyString()}), "not a dict")

        with pytest.raises(CtyConversionError):
            convert(malformed, CtyObject({"a": CtyNumber()}))

    def test_an_optional_target_attribute_absent_from_the_source_becomes_null(self) -> None:
        source = CtyObject({"a": CtyString()}).validate({"a": "1"})
        target = CtyObject({"a": CtyString(), "b": CtyNumber()}, optional_attributes=frozenset({"b"}))

        converted = convert(source, target)

        # The result's type is the target *without* its optionality. go-cty
        # strips it (`WithoutOptionalAttributesDeep`), because optionality
        # describes a constraint -- "you need not supply this" -- and a value
        # either has the attribute or has null for it.
        assert converted.type.equal(CtyObject({"a": CtyString(), "b": CtyNumber()}))
        assert converted.type.optional_attributes == frozenset()
        assert converted.value["b"].is_null

    def test_a_required_target_attribute_absent_from_the_source_is_refused(self) -> None:
        source = CtyObject({"a": CtyString()}).validate({"a": "1"})
        target = CtyObject({"a": CtyString(), "b": CtyNumber()})

        with pytest.raises(CtyConversionError):
            convert(source, target)

    def test_capsule_conversion(self) -> None:
        class MyType:
            def __init__(self, value) -> None:
                self.value = value

        def convert_my_type(raw, target_type):
            if target_type.equal(CtyString()):
                return CtyString().validate(str(raw.value))
            return None

        capsule_type = CtyCapsuleWithOps(
            "MyType",
            MyType,
            convert_fn=convert_my_type,
        )

        val = CtyValue(capsule_type, MyType(123))
        converted = convert(val, CtyString())
        assert converted.type.equal(CtyString())
        assert converted.raw_value == "123"

        with pytest.raises(CtyConversionError):
            convert(val, CtyNumber())

        def bad_converter_non_cty(raw, target_type) -> str:
            return "not a cty value"

        capsule_type_bad_converter = CtyCapsuleWithOps(
            "MyType",
            MyType,
            convert_fn=bad_converter_non_cty,
        )
        val_bad = CtyValue(capsule_type_bad_converter, MyType(123))
        with pytest.raises(CtyConversionError, match="non-CtyValue"):
            convert(val_bad, CtyString())

        def bad_converter_wrong_type(raw, target_type):
            return CtyNumber().validate(123)

        capsule_type_wrong_type = CtyCapsuleWithOps(
            "MyType",
            MyType,
            convert_fn=bad_converter_wrong_type,
        )
        val_wrong = CtyValue(capsule_type_wrong_type, MyType(123))
        with pytest.raises(CtyConversionError, match="wrong type"):
            convert(val_wrong, CtyString())


class TestUnifyFunction:
    """Tests `unify(types)` against go-cty's `convert.UnifyUnsafe`.

    This table used to assert that unification answered `dynamic` for every
    mixed input -- different primitives, objects with different attribute names,
    tuples of different lengths. That was a record of what the code did. A
    differential run against `soup-go cty unify` agreed on 6 of 38 cases, and
    every expectation below now comes from the oracle rather than from here.

    `None` is "these types have nothing in common", which `dynamic` used to
    stand in for as well -- so an error and a result were the same value.
    """

    @pytest.mark.parametrize(
        "type_list, expected_unified_type",
        [
            # Degenerate
            ([], None),
            ([CtyString()], CtyString()),
            ([CtyString(), CtyString()], CtyString()),
            # Primitives: string is the supertype, and number/bool have none.
            ([CtyString(), CtyNumber()], CtyString()),
            ([CtyString(), CtyBool()], CtyString()),
            ([CtyNumber(), CtyBool()], None),
            ([CtyString(), CtyNumber(), CtyBool()], CtyString()),
            # Dynamic has the lowest preference, so a concrete neighbour wins...
            ([CtyString(), CtyDynamic()], CtyString()),
            ([CtyDynamic(), CtyDynamic()], CtyDynamic()),
            # ...except among collections, where which path unification will
            # take once the dynamic resolves cannot be predicted.
            ([CtyList(element_type=CtyString()), CtyDynamic()], CtyDynamic()),
            # Collections unify elementwise.
            (
                [CtyList(element_type=CtyString()), CtyList(element_type=CtyString())],
                CtyList(element_type=CtyString()),
            ),
            (
                [CtyList(element_type=CtyString()), CtyList(element_type=CtyNumber())],
                CtyList(element_type=CtyString()),
            ),
            (
                [CtyList(element_type=CtyNumber()), CtyList(element_type=CtyBool())],
                None,
            ),
            (
                [CtyMap(element_type=CtyString()), CtyMap(element_type=CtyNumber())],
                CtyMap(element_type=CtyString()),
            ),
            # A list is preferred over a set holding the same thing.
            (
                [CtyList(element_type=CtyString()), CtySet(element_type=CtyString())],
                CtyList(element_type=CtyString()),
            ),
            ([CtyList(element_type=CtyString()), CtyMap(element_type=CtyString())], None),
            # Objects: attribute by attribute when the names match exactly...
            (
                [CtyObject({"a": CtyString()}), CtyObject({"a": CtyString()})],
                CtyObject({"a": CtyString()}),
            ),
            (
                [CtyObject({"common": CtyString()}), CtyObject({"common": CtyNumber()})],
                CtyObject({"common": CtyString()}),
            ),
            # ...and as a map when they do not, which is what an object is
            # shaped like once the per-attribute types stop mattering.
            ([CtyObject({"a": CtyString()}), CtyObject({"b": CtyString()})], CtyMap(element_type=CtyString())),
            (
                [CtyObject({"a": CtyString()}), CtyObject({"a": CtyString(), "b": CtyString()})],
                CtyMap(element_type=CtyString()),
            ),
            ([CtyObject({}), CtyObject({"a": CtyString()})], CtyMap(element_type=CtyString())),
            ([CtyObject({"a": CtyNumber()}), CtyObject({"b": CtyBool()})], None),
            (
                [
                    CtyObject({"a": CtyString(), "b": CtyNumber()}),
                    CtyObject({"a": CtyString(), "c": CtyBool()}),
                ],
                CtyMap(element_type=CtyString()),
            ),
            (
                [
                    CtyObject({"a": CtyString(), "b": CtyNumber()}),
                    CtyObject({"a": CtyString(), "b": CtyNumber(), "c": CtyBool()}),
                    CtyObject({"a": CtyString(), "b": CtyNumber(), "d": CtyString()}),
                ],
                CtyMap(element_type=CtyString()),
            ),
            # An object unifies with a map when every attribute reaches the
            # element type.
            (
                [CtyObject({"a": CtyString()}), CtyMap(element_type=CtyString())],
                CtyMap(element_type=CtyString()),
            ),
            # Optionality does not survive unification -- go-cty rebuilds a
            # plain object from the unified attribute types.
            (
                [
                    CtyObject({"a": CtyString()}),
                    CtyObject({"a": CtyString()}, optional_attributes={"a"}),
                ],
                CtyObject({"a": CtyString()}),
            ),
            (
                [
                    CtyObject({"a": CtyString()}),
                    CtyObject({"a": CtyString(), "b": CtyNumber()}, optional_attributes={"b"}),
                ],
                CtyMap(element_type=CtyString()),
            ),
            # Tuples: positionally when the lengths match, as a list when not.
            (
                [CtyTuple((CtyString(), CtyString())), CtyTuple((CtyString(), CtyNumber()))],
                CtyTuple((CtyString(), CtyString())),
            ),
            (
                [CtyTuple((CtyString(),)), CtyTuple((CtyString(), CtyNumber()))],
                CtyList(element_type=CtyString()),
            ),
            ([CtyTuple((CtyNumber(),)), CtyTuple((CtyBool(),))], None),
            (
                [CtyTuple((CtyString(), CtyString())), CtyList(element_type=CtyString())],
                CtyList(element_type=CtyString()),
            ),
            # Incompatible kinds are never bridged.
            ([CtyObject({"a": CtyString()}), CtyTuple((CtyString(),))], None),
            ([CtyString(), CtyList(element_type=CtyString())], None),
        ],
    )
    def test_unification_scenarios(
        self, type_list: Iterable[CtyType], expected_unified_type: CtyType | None
    ) -> None:
        unified_type = unify(type_list)

        if expected_unified_type is None:
            assert unified_type is None, f"expected no common type, got {unified_type}"
            return
        assert unified_type is not None, f"expected {expected_unified_type}, got no common type"
        assert unified_type.equal(expected_unified_type), (
            f"expected {expected_unified_type}, got {unified_type}"
        )


# 🌊🪢🔚
