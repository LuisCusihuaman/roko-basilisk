"""Core models for the Roko's Basilisk analysis system."""

# SPDX-License-Identifier: MIT

import math
from typing import Any, Dict, Protocol


class Agent:
    """Represents an agent in the acausal blackmail scenario.

    Agents can be either Human (H) or ASI (A) with different capabilities
    and decision-making processes.
    """

    def __init__(self, agent_type: str, parameters: Dict[str, float]):
        """Initialize agent with type and parameters.

        Args:
            agent_type: Either "Human" or "ASI"
            parameters: Dictionary of scenario parameters
        """
        self.agent_type = agent_type
        self.parameters = parameters

    def __repr__(self) -> str:
        return f"Agent(type='{self.agent_type}')"


class UtilityFunction:
    """Utility function transformations for risk preferences."""

    def __init__(self, function_type: str = "linear"):
        """Initialize utility function.

        Args:
            function_type: Type of utility function
                         ('linear', 'log', 'exp', 'sqrt')
        """
        self.function_type = function_type

    def transform(self, value: float) -> float:
        """Apply utility transformation to a value.

        Args:
            value: Raw utility value

        Returns:
            Transformed utility value
        """
        if self.function_type == "linear":
            return value
        elif self.function_type == "log":
            # Logarithmic utility (risk averse)
            if value <= 0:
                return -abs(value)  # Handle negative values
            return math.log(1 + value)
        elif self.function_type == "exp":
            # Exponential utility (risk seeking)
            return math.expm1(value / 100)  # Scale to prevent overflow
        elif self.function_type == "sqrt":
            # Square root utility (moderate risk aversion)
            if value < 0:
                return -math.sqrt(abs(value))
            return math.sqrt(value)
        else:
            raise ValueError(f"Unknown utility function: {self.function_type}")

    def __repr__(self) -> str:
        return f"UtilityFunction(type='{self.function_type}')"


class DecisionTheory(Protocol):
    """Protocol for decision theory implementations."""

    def decide(
        self,
        utility_collaborate: float,
        utility_non_collaborate: float,
        parameters: Dict[str, Any]
    ) -> str:
        """Make a decision based on utilities and parameters.

        Args:
            utility_collaborate: Expected utility of collaboration
            utility_non_collaborate: Expected utility of non-collaboration
            parameters: Scenario parameters

        Returns:
            Decision string ("COLLABORATE" or "NON_COLLABORATE")
        """
        ...
