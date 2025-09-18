from __future__ import annotations

import os
from typing import Self

from pyvider.cty.config.defaults import ENABLE_TYPE_INFERENCE_CACHE

"""Runtime configuration for pyvider-cty."""


class CtyConfig:
    """Runtime configuration for pyvider-cty.

    Simple configuration class that reads from environment variables
    without depending on Foundation's config system (which has issues).
    """

    def __init__(self, enable_type_inference_cache: bool = ENABLE_TYPE_INFERENCE_CACHE) -> None:
        self.enable_type_inference_cache = enable_type_inference_cache

    @classmethod
    def get_current(cls) -> Self:
        """Get current configuration from environment variables.

        Returns:
            Current CtyConfig instance loaded from environment
        """
        # Check environment variable for cache setting
        cache_enabled = os.environ.get("PYVIDER_CTY_ENABLE_TYPE_INFERENCE_CACHE")
        if cache_enabled is not None:
            cache_enabled = cache_enabled.lower() in ("true", "1", "yes", "on")
        else:
            cache_enabled = ENABLE_TYPE_INFERENCE_CACHE

        return cls(enable_type_inference_cache=cache_enabled)
