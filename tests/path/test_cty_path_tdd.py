from pyvider.cty.path import CtyPath


class TestCtyPathStringRepresentation:
    """
    TDD: These tests define the desired human-readable string representation
    for CtyPath objects, which is crucial for clear diagnostic messages.
    """

    def test_empty_path_representation(self) -> None:
        """TDD: An empty path should have a clear representation."""
        path = CtyPath.empty()
        # This will fail until the __str__ method is updated.
        assert str(path) == "(root)"

    def test_simple_attribute_path(self) -> None:
        """TDD: A simple attribute access path."""
        path = CtyPath.get_attr("user")
        # This will fail until the __str__ method is updated to remove the leading dot.
        assert str(path) == "user"

    def test_complex_mixed_path(self) -> None:
        """TDD: A complex path with mixed steps should format correctly."""
        path = (
            CtyPath.get_attr("users")
            .index_step(0)
            .child("addresses")
            .key_step("home")
            .child("zip")
        )
        # This will fail until the __str__ method is updated to join steps correctly.
        assert str(path) == "users[0].addresses['home'].zip"

    def test_path_starting_with_index(self) -> None:
        """TDD: A path that starts with an index."""
        path = CtyPath.index(0).child("name")
        assert str(path) == "[0].name"

    def test_path_with_only_key(self) -> None:
        """TDD: A path that is only a key lookup."""
        path = CtyPath.key("config-key")
        assert str(path) == "['config-key']"
