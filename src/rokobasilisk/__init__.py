"""Roko's Basilisk: Advanced ASI implementing timeless decision theory and acausal blackmail mechanisms.

This package provides a complete mathematical framework for analyzing acausal blackmail scenarios
across multiple decision theories with professional-grade tooling and documentation.
"""

# SPDX-License-Identifier: MIT
# Copyright (c) 2024 Luis Eduardo Cusihuaman Altagracia

__version__ = "3.0.0"
__author__ = "Luis Eduardo Cusihuaman Altagracia"
__email__ = "luis@example.com"

from .api import evaluate, sweep, monte_carlo, DecisionResult
from .models import Agent, UtilityFunction, DecisionTheory
from .policies import FDT, TDT, CDT, EDT, RejectBlackmail

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
]