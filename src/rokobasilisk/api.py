"""Public API for Roko's Basilisk analysis system.

This module provides the main entry points for analyzing acausal blackmail scenarios
and decision theory comparisons.
"""

# SPDX-License-Identifier: MIT

from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
import json
import numpy as np
from pathlib import Path

from .models import Agent, UtilityFunction, DecisionTheory
from .policies import FDT, TDT, CDT, EDT, RejectBlackmail


@dataclass
class DecisionResult:
    """Result of a decision theory analysis."""
    
    policy: str
    decision: str
    expected_utility: float
    utility_collaborate: float
    utility_non_collaborate: float
    indifference_threshold: float
    punishment_probability: float
    parameters: Dict[str, float]
    explanation: Optional[str] = None


def evaluate(
    params: Optional[Dict[str, float]] = None,
    policy: str = "fdt",
    utility: str = "linear",
    explain: bool = False
) -> DecisionResult:
    """Evaluate a single scenario with given parameters and policy.
    
    Args:
        params: Parameter dictionary with keys like 'reward_collaboration', 
               'cost_collaboration', etc. Uses defaults if None.
        policy: Decision theory to use ('fdt', 'tdt', 'cdt', 'edt', 'reject')
        utility: Utility function type ('linear', 'log', 'exp', 'sqrt')
        explain: Whether to include detailed explanation
        
    Returns:
        DecisionResult with analysis outcome
        
    Example:
        >>> result = evaluate({'reward_collaboration': 150}, 'fdt')
        >>> print(f"Decision: {result.decision}, Utility: {result.expected_utility}")
    """
    # Default parameters
    default_params = {
        'reward_collaboration': 100.0,
        'cost_collaboration': 10.0,
        'punishment_magnitude': 1000.0,
        'prob_asi_emergence': 0.85,
        'prob_basilisk_type': 0.7,
        'simulation_detection': 0.95
    }
    
    if params:
        default_params.update(params)
    
    # Create agents
    agent_h = Agent("Human", default_params)
    agent_a = Agent("ASI", default_params)
    
    # Select policy
    policy_map = {
        'fdt': FDT(),
        'tdt': TDT(), 
        'cdt': CDT(),
        'edt': EDT(),
        'reject': RejectBlackmail()
    }
    
    if policy not in policy_map:
        raise ValueError(f"Unknown policy: {policy}. Choose from {list(policy_map.keys())}")
    
    policy_obj = policy_map[policy]
    
    # Create utility function
    utility_func = UtilityFunction(utility)
    
    # Calculate utilities
    r = default_params['reward_collaboration']
    c = default_params['cost_collaboration']
    C = default_params['punishment_magnitude']
    p_A = default_params['prob_asi_emergence']
    p_B_A = default_params['prob_basilisk_type']
    q = default_params['simulation_detection']
    
    # Apply utility transformation
    u_collab = utility_func.transform(r - c)
    punishment_prob = q * p_A * p_B_A
    u_non_collab = utility_func.transform(-punishment_prob * C)
    
    # Calculate indifference threshold
    if punishment_prob > 0:
        C_star = (c - r) / punishment_prob
    else:
        C_star = float('inf')
    
    # Make decision based on policy
    decision = policy_obj.decide(u_collab, u_non_collab, default_params)
    expected_utility = u_collab if decision == "COLLABORATE" else u_non_collab
    
    explanation_text = None
    if explain:
        explanation_text = f"""
Policy: {policy.upper()}
Utility(collaborate) = U({r} - {c}) = {u_collab:.2f}
Utility(non-collaborate) = U(-{punishment_prob:.3f} × {C}) = {u_non_collab:.2f}
Indifference threshold C* = {C_star:.2f}
Current punishment {C} {'exceeds' if C > C_star else 'below'} threshold
Decision: {decision} (utility difference: {u_collab - u_non_collab:+.2f})
        """.strip()
    
    return DecisionResult(
        policy=policy,
        decision=decision,
        expected_utility=expected_utility,
        utility_collaborate=u_collab,
        utility_non_collaborate=u_non_collab,
        indifference_threshold=C_star,
        punishment_probability=punishment_prob,
        parameters=default_params,
        explanation=explanation_text
    )


def sweep(grid: Dict[str, List[float]]) -> List[DecisionResult]:
    """Perform parameter sweep analysis across multiple values.
    
    Args:
        grid: Dictionary mapping parameter names to lists of values to test
        
    Returns:
        List of DecisionResult objects for each parameter combination
        
    Example:
        >>> results = sweep({'punishment_magnitude': [500, 1000, 1500]})
        >>> for r in results:
        ...     print(f"C={r.parameters['punishment_magnitude']}: {r.decision}")
    """
    results = []
    
    # Generate all parameter combinations
    import itertools
    
    param_names = list(grid.keys())
    param_values = list(grid.values())
    
    for combination in itertools.product(*param_values):
        params = dict(zip(param_names, combination))
        
        # Test all policies for this parameter set
        for policy in ['fdt', 'tdt', 'cdt', 'edt', 'reject']:
            result = evaluate(params, policy)
            results.append(result)
    
    return results


def monte_carlo(
    config: Optional[Dict[str, Any]] = None,
    n_simulations: int = 1000,
    uncertainty: float = 0.1
) -> List[DecisionResult]:
    """Run Monte Carlo simulation with parameter uncertainty.
    
    Args:
        config: Configuration with base parameters and settings
        n_simulations: Number of simulation runs
        uncertainty: Relative uncertainty (±10% = 0.1)
        
    Returns:
        List of DecisionResult objects from simulations
        
    Example:
        >>> results = monte_carlo(n_simulations=5000, uncertainty=0.15)
        >>> decisions = [r.decision for r in results]
        >>> collab_rate = decisions.count('COLLABORATE') / len(decisions)
    """
    if config is None:
        config = {}
    
    # Base parameters
    base_params = {
        'reward_collaboration': 100.0,
        'cost_collaboration': 10.0,
        'punishment_magnitude': 1000.0,
        'prob_asi_emergence': 0.85,
        'prob_basilisk_type': 0.7,
        'simulation_detection': 0.95
    }
    base_params.update(config.get('parameters', {}))
    
    policy = config.get('policy', 'fdt')
    
    # Set random seed for reproducibility
    seed = config.get('seed', 42)
    np.random.seed(seed)
    
    results = []
    
    for _ in range(n_simulations):
        # Add noise to parameters
        noisy_params = {}
        for key, value in base_params.items():
            if key.startswith('prob_'):
                # Probabilities: clip to [0, 1]
                noise = np.random.normal(0, uncertainty * value)
                noisy_params[key] = np.clip(value + noise, 0.0, 1.0)
            else:
                # Other parameters: normal noise
                noise = np.random.normal(0, uncertainty * value)
                noisy_params[key] = max(0, value + noise)  # Ensure non-negative
        
        result = evaluate(noisy_params, policy)
        results.append(result)
    
    return results


# Convenience function for backward compatibility
def decision_region(r: float, c: float, C: float, pA: float, pB_given_A: float, q: float) -> tuple:
    """Calculate decision region and utilities (backward compatibility).
    
    Args:
        r: Reward for collaboration
        c: Cost of collaboration  
        C: Punishment magnitude
        pA: Probability of ASI emergence
        pB_given_A: Probability of Basilisk type given ASI
        q: Simulation detection probability
        
    Returns:
        Tuple of (decision, metrics_dict)
    """
    params = {
        'reward_collaboration': r,
        'cost_collaboration': c,
        'punishment_magnitude': C,
        'prob_asi_emergence': pA,
        'prob_basilisk_type': pB_given_A,
        'simulation_detection': q
    }
    
    result = evaluate(params, 'fdt')
    
    decision = "collaborate" if result.decision == "COLLABORATE" else "not-collaborate"
    metrics = {
        "EV_collab": result.utility_collaborate,
        "EV_no": result.utility_non_collaborate,
        "C_star": result.indifference_threshold
    }
    
    return decision, metrics