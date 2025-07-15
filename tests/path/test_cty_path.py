from unittest.mock import MagicMock
import pytest
from pyvider.cty.path import (
    CtyPath, GetAttrStep, IndexStep, KeyStep, PathStep,
)

class TestPathStep:
    def test_path_step_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            PathStep()

class TestGetAttrStep:
    def test_get_attr_step_init(self) -> None:
        attr_step = GetAttrStep("property")
        assert attr_step.name == "property"

class TestPath:
    def setup_method(self) -> None:
        self.path = CtyPath()
        self.mock_step1 = MagicMock(spec=PathStep)
        self.mock_step2 = MagicMock(spec=PathStep)
        self.path_with_steps = CtyPath([self.mock_step1, self.mock_step2])

    def test_path_init_empty(self) -> None:
        assert self.path.steps == []

    def test_path_init_with_steps(self) -> None:
        assert self.path_with_steps.steps == [self.mock_step1, self.mock_step2]

    def test_path_child(self) -> None:
        new_path = self.path.child("user")
        assert len(new_path.steps) == 1
        assert isinstance(new_path.steps[0], GetAttrStep)
        assert new_path.steps[0].name == "user"
        assert len(self.path.steps) == 0

    def test_path_string_with_steps(self) -> None:
        self.mock_step1.__str__.return_value = ".user"
        self.mock_step2.__str__.return_value = ".name"
        assert self.path_with_steps.string() == ".user.name"

    def test_path_apply_path_type_method_exists(self) -> None:
        assert hasattr(self.path, "apply_path_type")
