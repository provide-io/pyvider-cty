#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from typing import Any

import pytest

from pyvider.cty import CtyNumber, CtyObject, CtyString, CtyValue
from pyvider.cty.exceptions import CtyAttributeValidationError


class TestCtyObjectAttributes:
    @pytest.fixture
    def person_type(self) -> CtyObject:
        return CtyObject(
            attribute_types={"name": CtyString(), "age": CtyNumber()},
            optional_attributes=frozenset(["age"]),
        )

    @pytest.fixture
    def person_value(self, person_type: CtyObject) -> CtyValue[dict[str, Any]]:
        return person_type.validate({"name": "Alice", "age": 30})

    def test_get_valid_attribute(self, person_type: CtyObject, person_value: CtyValue[dict[str, Any]]) -> None:
        name_val = person_value["name"]
        assert name_val.value == "Alice"

        age_val = person_type.get_attribute(person_value, "age")
        assert age_val.value == 30

    def test_get_invalid_attribute(
        self, person_type: CtyObject, person_value: CtyValue[dict[str, Any]]
    ) -> None:
        with pytest.raises(CtyAttributeValidationError, match="Object has no attribute 'unknown'"):
            person_type.get_attribute(person_value, "unknown")

    def test_has_attribute(self, person_type: CtyObject) -> None:
        assert person_type.has_attribute("name")
        assert not person_type.has_attribute("unknown")

    def test_get_attribute_from_null_object(self, person_type: CtyObject) -> None:
        null_person = CtyValue.null(person_type)
        name_from_null = person_type.get_attribute(null_person, "name")
        assert name_from_null.is_null
        assert isinstance(name_from_null.type, CtyString)

    def test_get_attribute_on_non_dict_value(self, person_type: CtyObject) -> None:
        from pyvider.cty.exceptions import CtyTypeMismatchError

        # Create a CtyValue with a non-dict value but with a CtyObject type
        # This is a weird state, but we should handle it gracefully
        value = CtyValue(person_type, "not a dict")
        with pytest.raises(CtyTypeMismatchError):
            person_type.get_attribute(value, "name")


# 🌊🪢🔚
