"""Plotting utilities for Roko's Basilisk analysis."""

# SPDX-License-Identifier: MIT

from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np

from .api import DecisionResult, evaluate


def plot_monte_carlo_results(results: List[DecisionResult], filename: str) -> None:
    """Plot Monte Carlo simulation results.

    Args:
        results: List of DecisionResult objects from Monte Carlo simulation
        filename: Output filename for plot
    """
    # Extract data
    utilities = [r.expected_utility for r in results]
    decisions = [r.decision for r in results]

    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Plot 1: Utility distribution
    ax1.hist(utilities, bins=50, alpha=0.7, edgecolor='black')
    ax1.axvline(np.mean(utilities), color='red', linestyle='--',
                label=f'Mean: {np.mean(utilities):.2f}')
    ax1.set_xlabel('Expected Utility')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Distribution of Expected Utilities')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot 2: Decision frequency
    decision_counts: Dict[str, int] = {}
    for decision in decisions:
        decision_counts[decision] = decision_counts.get(decision, 0) + 1

    labels = list(decision_counts.keys())
    sizes = list(decision_counts.values())
    colors = ['lightcoral' if 'COLLABORATE' in label else 'lightblue' for label in labels]

    ax2.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax2.set_title('Decision Distribution')

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()


def plot_decision_boundary(
    base_params: Dict[str, float],
    param1: str,
    param2: str,
    policy: str = 'fdt',
    filename: Optional[str] = None
) -> None:
    """Plot decision boundary between two parameters.

    Args:
        base_params: Base parameter values
        param1: First parameter name to vary
        param2: Second parameter name to vary
        policy: Decision theory to use
        filename: Output filename (optional)
    """
    # Parameter ranges
    param_ranges = {
        'reward_collaboration': np.linspace(50, 200, 20),
        'cost_collaboration': np.linspace(5, 50, 20),
        'punishment_magnitude': np.linspace(500, 2000, 20),
        'prob_asi_emergence': np.linspace(0.1, 1.0, 20),
        'prob_basilisk_type': np.linspace(0.1, 1.0, 20),
        'simulation_detection': np.linspace(0.1, 1.0, 20)
    }

    if param1 not in param_ranges or param2 not in param_ranges:
        raise ValueError(f"Unknown parameter. Available: {list(param_ranges.keys())}")

    # Create parameter grids
    p1_values = param_ranges[param1]
    p2_values = param_ranges[param2]
    P1, P2 = np.meshgrid(p1_values, p2_values)

    # Calculate decisions for each combination
    decisions = np.zeros_like(P1)

    for i in range(len(p2_values)):
        for j in range(len(p1_values)):
            params = base_params.copy()
            params[param1] = P1[i, j]
            params[param2] = P2[i, j]

            result = evaluate(params, policy)
            decisions[i, j] = 1 if result.decision == 'COLLABORATE' else 0

    # Create plot
    fig, ax = plt.subplots(figsize=(10, 8))

    # Plot decision regions
    im = ax.imshow(decisions, extent=[p1_values.min(), p1_values.max(),
                                   p2_values.min(), p2_values.max()],
                  aspect='auto', origin='lower', cmap='RdYlBu_r', alpha=0.8)

    # Add contour lines
    contour = ax.contour(P1, P2, decisions, levels=[0.5], colors='black', linewidths=2)
    ax.clabel(contour, fmt='Decision Boundary', fontsize=10)

    # Labels and title
    ax.set_xlabel(param1.replace('_', ' ').title())
    ax.set_ylabel(param2.replace('_', ' ').title())
    ax.set_title(f'Decision Boundary: {policy.upper()} Policy\n'
                f'Red=Collaborate, Blue=Non-Collaborate')

    # Colorbar
    cbar = plt.colorbar(im, ax=ax, ticks=[0, 1])
    cbar.set_ticklabels(['Non-Collaborate', 'Collaborate'])

    plt.tight_layout()

    if filename:
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def plot_sensitivity_analysis(
    base_params: Dict[str, float],
    param_name: str,
    filename: Optional[str] = None
) -> None:
    """Plot sensitivity analysis for a parameter.

    Args:
        base_params: Base parameter values
        param_name: Parameter to analyze
        filename: Output filename (optional)
    """
    base_value = base_params[param_name]

    # Test range: ±50% around base value
    multipliers = np.linspace(0.5, 1.5, 21)
    test_values = base_value * multipliers

    policies = ['fdt', 'tdt', 'cdt', 'edt', 'reject']

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    for policy in policies:
        utilities = []
        decisions = []

        for value in test_values:
            params = base_params.copy()
            params[param_name] = value
            result = evaluate(params, policy)
            utilities.append(result.expected_utility)
            decisions.append(1 if result.decision == 'COLLABORATE' else 0)

        # Plot utilities
        ax1.plot(test_values, utilities, label=policy.upper(), marker='o', markersize=3)

        # Plot decisions
        ax2.plot(test_values, decisions, label=policy.upper(), marker='s', markersize=4, alpha=0.7)

    # Format plots
    ax1.axvline(base_value, color='gray', linestyle='--', alpha=0.7, label='Base Value')
    ax1.set_xlabel(param_name.replace('_', ' ').title())
    ax1.set_ylabel('Expected Utility')
    ax1.set_title('Utility Sensitivity Analysis')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.axvline(base_value, color='gray', linestyle='--', alpha=0.7)
    ax2.set_xlabel(param_name.replace('_', ' ').title())
    ax2.set_ylabel('Decision (0=Non-Collaborate, 1=Collaborate)')
    ax2.set_title('Decision Sensitivity Analysis')
    ax2.set_ylim(-0.1, 1.1)
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    if filename:
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
    else:
        plt.show()
