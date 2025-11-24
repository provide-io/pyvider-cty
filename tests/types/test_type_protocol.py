#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""This test suite covers the CtyTypeProtocol to ensure its runtime checkability
works as expected and to achieve 100% coverage on types/base.py."""

from typing import Any

from pyvider.cty import CtyString, CtyValue
from pyvider.cty.types.base import CtyTypeProtocol


class TestCtyTypeProtocol:
    """Tests for the CtyTypeProtocol interface."""

    def test_concrete_cty_type_is_instance_of_protocol(self) -> None:
        """
        Verifies that a concrete, valid CtyType subclass is recognized
        as an instance of the CtyTypeProtocol.
        """
        string_type = CtyString()
        assert isinstance(string_type, CtyTypeProtocol)

    def test_incomplete_class_is_not_instance_of_protocol(self) -> None:
        """
        Verifies that a class missing one of the required protocol methods
        is not considered an instance of the protocol.
        """

        class IncompleteType:
            def validate(self, value: object) -> CtyValue[Any]:
                pass

            def equal(self, other: Any) -> bool:
                pass

            # Missing `usable_as` and `is_primitive_type`

        assert not isinstance(IncompleteType(), CtyTypeProtocol)

    def test_non_cty_type_class_is_not_instance_of_protocol(self) -> None:
        """
        Verifies that an arbitrary class is not an instance of the protocol.
        """

        class NotACtyType:
            pass

        assert not isinstance(NotACtyType(), CtyTypeProtocol)


# 🌊🪢🔚
