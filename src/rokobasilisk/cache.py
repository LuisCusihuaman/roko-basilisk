"""Caching utilities for performance optimization.

This module provides caching functionality for computationally expensive operations
like large parameter sweeps and Monte Carlo simulations.
"""

# SPDX-License-Identifier: MIT

import os
from pathlib import Path
from typing import Any, Callable, Dict, Optional

try:
    from joblib import Memory
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False


class CacheManager:
    """Manages caching for expensive computations."""

    def __init__(self, cache_dir: Optional[str] = None, enabled: bool = True):
        """Initialize cache manager.

        Args:
            cache_dir: Directory for cache files. Uses temp if None.
            enabled: Whether caching is enabled.
        """
        self.enabled = enabled and JOBLIB_AVAILABLE

        if self.enabled:
            if cache_dir is None:
                cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "rokobasilisk")

            Path(cache_dir).mkdir(parents=True, exist_ok=True)
            self.memory = Memory(cache_dir, verbose=0)
        else:
            self.memory = None

    def cached(self, func: Callable) -> Callable:
        """Decorator to cache function results.

        Args:
            func: Function to cache

        Returns:
            Cached function or original if caching disabled
        """
        if self.enabled and self.memory is not None:
            return self.memory.cache(func)
        return func

    def clear(self) -> None:
        """Clear all cached data."""
        if self.enabled and self.memory is not None:
            self.memory.clear()

    def info(self) -> Dict[str, Any]:
        """Get cache information."""
        if not self.enabled:
            return {"enabled": False, "reason": "joblib not available" if not JOBLIB_AVAILABLE else "disabled"}

        if self.memory is not None:
            return {
                "enabled": True,
                "location": self.memory.location,
                "size_mb": self._get_cache_size_mb()
            }

        return {"enabled": False, "reason": "memory not initialized"}

    def _get_cache_size_mb(self) -> float:
        """Get cache size in MB."""
        if not self.enabled or self.memory is None:
            return 0.0

        try:
            cache_path = Path(self.memory.location)
            if not cache_path.exists():
                return 0.0

            total_size = sum(
                f.stat().st_size
                for f in cache_path.rglob('*')
                if f.is_file()
            )
            return total_size / (1024 * 1024)  # Convert to MB
        except Exception:
            return 0.0


# Global cache manager instance
_cache_manager = CacheManager()


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    return _cache_manager


def configure_cache(cache_dir: Optional[str] = None, enabled: bool = True) -> None:
    """Configure global caching settings.

    Args:
        cache_dir: Directory for cache files
        enabled: Whether to enable caching
    """
    global _cache_manager
    _cache_manager = CacheManager(cache_dir=cache_dir, enabled=enabled)


def cached(func: Callable) -> Callable:
    """Decorator to cache function results using global cache manager.

    Args:
        func: Function to cache

    Returns:
        Cached function
    """
    return _cache_manager.cached(func)


def clear_cache() -> None:
    """Clear all cached data."""
    _cache_manager.clear()


def cache_info() -> Dict[str, Any]:
    """Get cache information."""
    return _cache_manager.info()
