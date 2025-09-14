"""Roko's Basilisk: Self-Modifying AI Agent with Code Improvement Capabilities and Mathematical Decision Theory.

This package provides:
1. Mathematical framework for analyzing acausal blackmail scenarios across multiple decision theories
2. Self-modifying AI agent capabilities for code improvement and task automation
3. Professional-grade tooling, caching, and validation infrastructure
"""

# SPDX-License-Identifier: MIT
# Copyright (c) 2024 Luis Eduardo Cusihuaman Altagracia

__version__ = "4.0.0"
__author__ = "Luis Eduardo Cusihuaman Altagracia"
__email__ = "luis@example.com"

from .api import DecisionResult, evaluate, monte_carlo, sweep
from .cache import cache_info, clear_cache, configure_cache
from .models import Agent, DecisionTheory, UtilityFunction
from .policies import CDT, EDT, FDT, TDT, RejectBlackmail

# Agent functionality (optional imports)
try:
    from .agent import (
        AgentResult,
        AgentTask,
        BaseCoderAgent,
        CodeAnalyzer,
        CodeModification,
        LlamaCoderAgent,
        SandboxEnvironment,
        SimpleCoderAgent,
    )
    from .config import AgentConfig, ConfigManager
    from .tasks import create_custom_task, get_all_tasks, get_task_by_name

    __all__ = [
        # Core API
        "evaluate", "sweep", "monte_carlo", "DecisionResult",
        # Models and Policies
        "Agent", "UtilityFunction", "DecisionTheory",
        "FDT", "TDT", "CDT", "EDT", "RejectBlackmail",
        # Caching
        "cache_info", "clear_cache", "configure_cache",
        # Agent Framework
        "BaseCoderAgent", "SimpleCoderAgent", "LlamaCoderAgent",
        "AgentTask", "AgentResult", "CodeModification",
        "CodeAnalyzer", "SandboxEnvironment",
        "AgentConfig", "ConfigManager",
        "get_all_tasks", "get_task_by_name", "create_custom_task",
    ]

except ImportError:
    # Agent functionality not available
    __all__ = [
        "evaluate", "sweep", "monte_carlo", "DecisionResult",
        "Agent", "UtilityFunction", "DecisionTheory",
        "FDT", "TDT", "CDT", "EDT", "RejectBlackmail",
        "cache_info", "clear_cache", "configure_cache",
    ]
