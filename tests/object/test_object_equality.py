#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Tests for CtyObject type implementation."""

import pytest

from pyvider.cty import (
    CtyBool,
    CtyNumber,
    CtyObject,
    CtyString,
)


@pytest.mark.asyncio
async def test_equal_same_type() -> None:
    """Test equality with same type."""
    # Create two identical object types
    type1 = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
        }
    )

    type2 = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
        }
    )

    # Check equality
    assert type1.equal(type2) is True
    assert type2.equal(type1) is True


@pytest.mark.asyncio
async def test_equal_different_attributes() -> None:
    """Test equality with different attributes."""
    # Create two object types with different attributes
    type1 = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
        }
    )

    type2 = CtyObject(
        attribute_types={
            "name": CtyString(),
            "active": CtyBool(),
        }
    )

    # Check equality
    assert type1.equal(type2) is False
    assert type2.equal(type1) is False


@pytest.mark.asyncio
async def test_equal_different_attribute_types() -> None:
    """Test equality with different attribute types."""
    # Create two object types with same attribute names but different types
    type1 = CtyObject(
        attribute_types={
            "name": CtyString(),
            "value": CtyNumber(),
        }
    )

    type2 = CtyObject(
        attribute_types={
            "name": CtyString(),
            "value": CtyString(),  # Different type
        }
    )

    # Check equality
    assert type1.equal(type2) is False
    assert type2.equal(type1) is False


@pytest.mark.asyncio
async def test_equal_different_optional() -> None:
    """Test equality with different optional attributes."""
    # Create two object types with different optional attributes
    type1 = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
        },
        optional_attributes=frozenset(["age"]),
    )

    type2 = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
        }
    )

    # Check equality
    assert type1.equal(type2) is False
    assert type2.equal(type1) is False


@pytest.mark.asyncio
async def test_usable_as_same_type() -> None:
    """Test usability with same type."""
    # Create two identical object types
    type1 = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
        }
    )

    type2 = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
        }
    )

    # Check usability
    assert type1.usable_as(type2) is True
    assert type2.usable_as(type1) is True


@pytest.mark.asyncio
async def test_usable_as_subset_attributes() -> None:
    """Test usability with subset of attributes."""
    # Create object type with more attributes
    type1 = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
            "active": CtyBool(),
        }
    )

    # Create object type with subset of attributes
    type2 = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
        }
    )

    # Check usability
    assert type1.usable_as(type2) is True  # More attributes can be used as fewer
    assert type2.usable_as(type1) is False  # Fewer attributes cannot be used as more


@pytest.mark.asyncio
async def test_usable_as_compatible_types() -> None:
    """Test usability with compatible attribute types."""
    # This will be implemented when we have type conversions
    # For now, types must be exactly equal to be compatible


@pytest.mark.asyncio
async def test_usable_as_required_attributes() -> None:
    """Test usability with different required attributes."""
    # Create type with more required attributes
    type1 = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
            "email": CtyString(),
        },
        optional_attributes=frozenset(["email"]),
    )

    # Create type with fewer required attributes
    type2 = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
            "email": CtyString(),
        },
        optional_attributes=frozenset(["age", "email"]),
    )

    # Check usability
    assert type1.usable_as(type2) is True  # More required can be used as fewer required
    assert type2.usable_as(type1) is False  # Fewer required cannot be used as more required


# 🌊🪢🔚
