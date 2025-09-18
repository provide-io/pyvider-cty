from __future__ import annotations

from typing import Self

from provide.foundation.config import BaseConfig, field

from pyvider.cty.config.defaults import ENABLE_TYPE_INFERENCE_CACHE

"""Runtime configuration for pyvider-cty using Foundation config patterns."""


class CtyConfig(BaseConfig):
    """Runtime configuration for pyvider-cty.

    Uses Foundation's BaseConfig for consistent configuration management.
    """

    enable_type_inference_cache: bool = field(
        default=ENABLE_TYPE_INFERENCE_CACHE,
        metadata={
            "env_var": "PYVIDER_CTY_ENABLE_TYPE_INFERENCE_CACHE",
            "description": "Enable caching for type inference performance optimization",
        },
    )

    @classmethod
    def get_current(cls) -> Self:
        """Get current configuration from environment variables.

        Returns:
            Current CtyConfig instance loaded from environment
        """
        import os

        # Check environment variable for cache setting
        cache_enabled = os.environ.get("PYVIDER_CTY_ENABLE_TYPE_INFERENCE_CACHE")
        if cache_enabled is not None:
            cache_enabled = cache_enabled.lower() in ("true", "1", "yes", "on")
        else:
            cache_enabled = ENABLE_TYPE_INFERENCE_CACHE

        # Create from dict with proper field name
        return cls.from_dict({"enable_type_inference_cache": cache_enabled})
