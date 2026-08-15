#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

from typing import Self

from attrs import define
from provide.foundation.config import RuntimeConfig, env_field

from pyvider.cty.config.defaults import (
    ENABLE_TYPE_INFERENCE_CACHE,
    MAX_VALIDATION_DEPTH_AUTO,
)

"""Runtime configuration for pyvider-cty using Foundation config patterns."""


@define
class CtyConfig(RuntimeConfig):
    """Runtime configuration for pyvider-cty.

    Uses Foundation's RuntimeConfig for consistent environment variable loading
    and validation patterns.
    """

    enable_type_inference_cache: bool = env_field(
        env_var="PYVIDER_CTY_ENABLE_TYPE_INFERENCE_CACHE",
        default=ENABLE_TYPE_INFERENCE_CACHE,
    )

    # Nesting depth ceiling for validation. Left at 0, it is derived from the
    # interpreter's recursion limit by `default_max_validation_depth`, which is
    # the only way the number can stay truthful. Set it to a positive value to
    # pin a fixed limit instead -- lower to fail earlier, higher only if the
    # recursion limit has been raised to match.
    max_validation_depth: int = env_field(
        env_var="PYVIDER_CTY_MAX_VALIDATION_DEPTH",
        default=MAX_VALIDATION_DEPTH_AUTO,
    )

    @classmethod
    def get_current(cls) -> Self:
        """Get current configuration from environment variables.

        Returns:
            Current CtyConfig instance loaded from environment
        """
        return cls.from_env(prefix="PYVIDER_CTY")


# 🌊🪢🔚
