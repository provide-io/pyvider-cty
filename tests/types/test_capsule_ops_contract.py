#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TDD: Strengthens the CtyCapsuleWithOps contract by validating function arity
in the constructor."""

from typing import Any

import pytest

from pyvider.cty import CtyCapsuleWithOps


class TestCapsuleWithOpsContract:
    class Opaque:
        """A dummy class for encapsulation."""

    @pytest.mark.parametrize(
        "bad_func",
        [
            lambda: True,  # 0 args
            lambda a: True,  # 1 arg
            lambda a, b, c: True,  # 3 args
        ],
    )
    def test_constructor_rejects_equal_fn_with_wrong_arity(self, bad_func: Any) -> None:
        """TDD: `equal_fn` must accept exactly 2 arguments."""
        with pytest.raises(TypeError, match="`equal_fn` must be a callable that accepts 2 arguments"):
            CtyCapsuleWithOps("Opaque", self.Opaque, equal_fn=bad_func)

    @pytest.mark.parametrize(
        "bad_func",
        [
            lambda: 1,  # 0 args
            lambda a, b: 1,  # 2 args
        ],
    )
    def test_constructor_rejects_hash_fn_with_wrong_arity(self, bad_func: Any) -> None:
        """TDD: `hash_fn` must accept exactly 1 argument."""
        with pytest.raises(TypeError, match="`hash_fn` must be a callable that accepts 1 argument"):
            CtyCapsuleWithOps("Opaque", self.Opaque, hash_fn=bad_func)

    @pytest.mark.parametrize(
        "bad_func",
        [
            lambda: None,  # 0 args
            lambda a: None,  # 1 arg
            lambda a, b, c: None,  # 3 args
        ],
    )
    def test_constructor_rejects_convert_fn_with_wrong_arity(self, bad_func: Any) -> None:
        """TDD: `convert_fn` must accept exactly 2 arguments."""
        with pytest.raises(TypeError, match="`convert_fn` must be a callable that accepts 2 arguments"):
            CtyCapsuleWithOps("Opaque", self.Opaque, convert_fn=bad_func)


# 🌊🪢🔚
