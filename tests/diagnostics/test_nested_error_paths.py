#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TDD: Verifies that validation error messages for deeply nested structures
have correctly formatted and complete paths."""

import pytest

from pyvider.cty import (
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyTuple,
    CtyValidationError,
)


class TestNestedErrorPaths:
    def test_error_in_list_within_object_within_list(self) -> None:
        """
        TDD: Ensures the path is correctly constructed as [0].items[1]
        """
        schema = CtyList(element_type=CtyObject(attribute_types={"items": CtyList(element_type=CtyNumber())}))
        invalid_data = [{"items": [1, "not-a-number", 3]}]

        with pytest.raises(CtyValidationError) as exc_info:
            schema.validate(invalid_data)

        expected_path = "[0].items[1]"
        assert expected_path in str(exc_info.value)

    def test_error_in_map_within_tuple_within_object(self) -> None:
        """
        TDD: Ensures the path is correctly constructed as config[1]['retries']
        """
        schema = CtyObject(
            attribute_types={"config": CtyTuple(element_types=(CtyString(), CtyMap(element_type=CtyNumber())))}
        )
        invalid_data = {"config": ("settings", {"retries": "five"})}

        with pytest.raises(CtyValidationError) as exc_info:
            schema.validate(invalid_data)

        expected_path = "config[1]['retries']"
        assert expected_path in str(exc_info.value)


# 🌊🪢🔚
