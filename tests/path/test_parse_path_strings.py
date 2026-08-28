#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`CtyPath.parse` is the inverse of `CtyPath.string()`, exactly when given the type."""

from __future__ import annotations

import pytest

from pyvider.cty import (
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyPath,
    CtySet,
    CtyString,
    CtyTuple,
)
from pyvider.cty.exceptions import AttributePathError
from pyvider.cty.path import IndexStep, KeyStep

SCHEMA = CtyObject(
    {
        "size_gb": CtyNumber(),
        "disk": CtyObject({"size": CtyString()}),
        "rule": CtyList(element_type=CtyObject({"port": CtyNumber()})),
        "tags": CtySet(element_type=CtyString()),
        "ports": CtySet(element_type=CtyNumber()),
        "labels": CtyMap(element_type=CtyString()),
        "pair": CtyTuple((CtyString(), CtyNumber())),
    }
)

ROUND_TRIP = [
    CtyPath.get_attr("size_gb"),
    CtyPath.get_attr("disk").child("size"),
    CtyPath.get_attr("rule").index_step(0).child("port"),
    CtyPath.get_attr("tags").key_step("a"),
    CtyPath.get_attr("labels").key_step("k"),
    CtyPath.get_attr("pair").index_step(1),
    CtyPath.empty(),
]


@pytest.mark.parametrize("path", ROUND_TRIP, ids=lambda p: p.string())
def test_parse_inverts_string_given_the_type(path: CtyPath) -> None:
    assert CtyPath.parse(path.string(), within=SCHEMA) == path


def test_a_set_element_and_a_map_key_are_spelled_alike_and_told_apart_by_type() -> None:
    """The reason this takes a type at all: `['a']` renders identically for both."""
    assert CtyPath.get_attr("tags").key_step("a").string() == "tags['a']"
    assert CtyPath.get_attr("labels").key_step("a").string() == "labels['a']"

    assert isinstance(CtyPath.parse("tags['a']", within=SCHEMA).steps[-1], KeyStep)
    assert isinstance(CtyPath.parse("labels['a']", within=SCHEMA).steps[-1], KeyStep)
    # A list in the same position is an index, from the same syntax.
    assert isinstance(CtyPath.parse("rule[0]", within=SCHEMA).steps[-1], IndexStep)


def test_without_a_type_a_bracket_is_read_syntactically() -> None:
    """Documented fallback: an integer reads as an index, a quoted key as a key."""
    assert isinstance(CtyPath.parse("rule[0]").steps[-1], IndexStep)
    assert isinstance(CtyPath.parse("tags['a']").steps[-1], KeyStep)
    # No type means no resolution, so a name that does not exist is accepted.
    assert CtyPath.parse("nope.at.all").steps[0].name == "nope"


@pytest.mark.parametrize(
    ("path_str", "fragment"),
    [
        ("size_gbb", "has no attribute"),
        ("  size_gb  ", "has no attribute"),
        ("disk.nope", "has no attribute"),
        ("rule[0].nope", "has no attribute"),
        ("tags[0]", "Invalid key for set"),
        ("ports['x']", "Invalid key for set"),
        ("labels[0]", "Invalid key for map"),
        ("pair[5]", "out of bounds"),
        ("size_gb[0]", "Cannot index into"),
    ],
)
def test_a_path_that_does_not_resolve_is_refused(path_str: str, fragment: str) -> None:
    with pytest.raises(AttributePathError, match=fragment):
        CtyPath.parse(path_str, within=SCHEMA)


@pytest.mark.parametrize(
    ("path_str", "fragment"),
    [
        ("rule[", "Unterminated"),
        ("rule[]", "Empty"),
        ("rule['a", "Unterminated"),
        ("rule['a]", "Unbalanced quotes"),
        ("rule[a]", "neither"),
    ],
)
def test_malformed_syntax_is_refused_even_without_a_type(path_str: str, fragment: str) -> None:
    """Strictness is the point: the regex this replaces silently skipped what it could not match."""
    with pytest.raises(AttributePathError, match=fragment):
        CtyPath.parse(path_str)


def test_the_error_names_the_step_that_failed() -> None:
    with pytest.raises(AttributePathError, match=r"Error at step 3 \(\.nope\)"):
        CtyPath.parse("rule[0].nope", within=SCHEMA)


@pytest.mark.parametrize("root", ["", "(root)"])
def test_the_empty_path_round_trips(root: str) -> None:
    assert CtyPath.parse(root, within=SCHEMA) == CtyPath.empty()


def test_an_attribute_name_may_contain_characters_a_word_regex_would_drop() -> None:
    """go-cty puts no constraint on an attribute name; the old `\\w+` regex did."""
    schema = CtyObject({"with-a-dash": CtyString()})
    assert CtyPath.parse("with-a-dash", within=schema) == CtyPath.get_attr("with-a-dash")


# 🌊🪢🔚
