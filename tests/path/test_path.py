from unittest.mock import MagicMock, PropertyMock, patch
import pytest
from pyvider.cty import CtyValue, CtyString, CtyNumber, CtyList, CtyMap, CtyObject, CtyTuple
from pyvider.cty.exceptions import AttributePathError, CtyValidationError
from pyvider.cty.path import CtyPath, GetAttrStep, IndexStep, KeyStep, PathStep

class TestPathSystem:
    # ... (all other tests in this file remain the same, just fixing the failing ones)
    @pytest.mark.asyncio
    async def test_key_step_apply_errors_and_unknown(self) -> None:
        map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        unknown_map_value = CtyValue.unknown(map_type)
        path_key = CtyPath.key("some_key")
        result_unknown = path_key.apply_path(unknown_map_value)
        assert result_unknown.is_unknown and isinstance(result_unknown.type, CtyNumber)

        string_value = CtyString().validate("not a map")
        with pytest.raises(AttributePathError):
            path_key.apply_path(string_value)

    @pytest.mark.asyncio
    async def test_key_step_apply_type_errors(self) -> None:
        list_type = CtyList(element_type=CtyString())
        path_key = CtyPath.key("any_key")
        with pytest.raises(AttributePathError):
            path_key.apply_path_type(list_type)

        map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        # FIX: KeyStep.apply_type should succeed if the key is valid for the map's key type.
        # A CtyNumber value cannot be used as a key for a map with CtyString keys.
        invalid_key_path = CtyPath.key(CtyNumber().validate(123))
        with pytest.raises(AttributePathError):
            invalid_key_path.apply_path_type(map_type)
