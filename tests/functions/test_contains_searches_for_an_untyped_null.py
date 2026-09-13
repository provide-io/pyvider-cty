#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`contains` searches for an untyped null instead of deferring on it.

go-cty v1.19.0 declares `contains`' value parameter `AllowNull` but not
`AllowDynamicType`, so a null of `DynamicPseudoType` -- what a bare `null`
literal is in Terraform -- never reaches the implementation: `Function.Call`
treats the undecided type as "cannot predict a return type" and answers an
unknown. `contains([], null)` is therefore "known after apply" and never
resolves. Reported upstream as zclconf/go-cty#221 with a one-flag patch, which
this package applies. The differential sweep records the disagreement with the
unpatched oracle as strict xfails, so an oracle carrying the fix forces them out.
"""

from pyvider.cty import CtyBool, CtyList, CtyString, CtyTuple, CtyValue
from pyvider.cty.functions import contains
from pyvider.cty.types import CtyDynamic
from pyvider.cty.values.markers import RefinedUnknownValue

UNTYPED_NULL = CtyValue.null(CtyDynamic())
STRINGS = CtyList(element_type=CtyString()).validate(["a", "b"])


def test_an_empty_tuple_does_not_contain_an_untyped_null() -> None:
    result = contains(CtyTuple(element_types=()).validate(()), UNTYPED_NULL)

    assert not result.is_unknown
    assert result.value is False


def test_a_tuple_holding_an_untyped_null_contains_one() -> None:
    holding_null = CtyTuple(element_types=(CtyDynamic(),)).validate((UNTYPED_NULL,))

    result = contains(holding_null, UNTYPED_NULL)

    assert not result.is_unknown
    assert result.value is True


def test_a_list_of_known_strings_does_not_contain_an_untyped_null() -> None:
    result = contains(STRINGS, UNTYPED_NULL)

    assert not result.is_unknown
    assert result.value is False


def test_a_value_of_undecided_type_is_still_undecided_but_not_null() -> None:
    """The flag lets `cty.DynamicVal` through too, and the implementation defers on it.

    What changes is the answer's shape: it now comes from the implementation's
    own unknown check, so it is an unknown *bool* carrying `RefineResult`'s
    not-null promise, where it used to be an unknown of undecided type.
    """
    result = contains(STRINGS, CtyValue.unknown(CtyDynamic()))

    assert result.type == CtyBool()
    assert result.value == RefinedUnknownValue(is_known_null=False)
