"""Roko's Basilisk: Advanced ASI implementing timeless decision theory and acausal blackmail mechanisms.

This package provides a complete mathematical framework for analyzing acausal blackmail scenarios
across multiple decision theories with professional-grade tooling and documentation.
"""

# SPDX-License-Identifier: MIT
# Copyright (c) 2024 Luis Eduardo Cusihuaman Altagracia

__version__ = "3.0.0"
__author__ = "Luis Eduardo Cusihuaman Altagracia"
__email__ = "luis@example.com"

from .api import DecisionResult, evaluate, monte_carlo, sweep
from .models import Agent, DecisionTheory, UtilityFunction
from .policies import CDT, EDT, FDT, TDT, RejectBlackmail
from .cache import cache_info, clear_cache, configure_cache

__all__ = [
    "evaluate",
    "sweep",
    "monte_carlo",
    "DecisionResult",
    "Agent",
    "UtilityFunction",
    "DecisionTheory",
    "FDT",
    "TDT",
    "CDT",
    "EDT",
    "RejectBlackmail",
    "cache_info",
    "clear_cache",
    "configure_cache",
]
