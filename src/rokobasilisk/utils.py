"""Utility functions for Roko's Basilisk analysis system."""

# SPDX-License-Identifier: MIT

import json
import csv
import os
from typing import List, Dict, Any, Union
from pathlib import Path
import numpy as np

from .api import DecisionResult


def set_global_seed(seed: int) -> None:
    """Set global random seed for reproducibility.
    
    Args:
        seed: Random seed value
    """
    np.random.seed(seed)
    # Also set Python's random seed if needed
    import random
    random.seed(seed)


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is invalid JSON
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in config file {config_path}: {e}")


def export_results(results: List[DecisionResult], output_path: str) -> None:
    """Export analysis results to file.
    
    Args:
        results: List of DecisionResult objects
        output_path: Output file path (.json or .csv)
        
    Raises:
        ValueError: If output format is not supported
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    if output_path.endswith('.json'):
        export_to_json(results, output_path)
    elif output_path.endswith('.csv'):
        export_to_csv(results, output_path)
    else:
        raise ValueError(f"Unsupported output format. Use .json or .csv")


def export_to_json(results: List[DecisionResult], output_path: str) -> None:
    """Export results to JSON format.
    
    Args:
        results: List of DecisionResult objects
        output_path: Output JSON file path
    """
    # Convert results to serializable format
    serializable_results = []
    
    for result in results:
        result_dict = {
            'policy': result.policy,
            'decision': result.decision,
            'expected_utility': result.expected_utility,
            'utility_collaborate': result.utility_collaborate,
            'utility_non_collaborate': result.utility_non_collaborate,
            'indifference_threshold': result.indifference_threshold,
            'punishment_probability': result.punishment_probability,
            'parameters': result.parameters,
            'explanation': result.explanation
        }
        serializable_results.append(result_dict)
    
    # Add metadata
    export_data = {
        'metadata': {
            'version': '3.0.0',
            'timestamp': _get_timestamp(),
            'total_results': len(results)
        },
        'results': serializable_results
    }
    
    with open(output_path, 'w') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)


def export_to_csv(results: List[DecisionResult], output_path: str) -> None:
    """Export results to CSV format.
    
    Args:
        results: List of DecisionResult objects
        output_path: Output CSV file path
    """
    if not results:
        return
    
    # Get all parameter names from first result
    param_names = list(results[0].parameters.keys())
    
    # Define CSV headers
    headers = [
        'policy', 'decision', 'expected_utility', 'utility_collaborate',
        'utility_non_collaborate', 'indifference_threshold', 'punishment_probability'
    ] + [f'param_{name}' for name in param_names]
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for result in results:
            row = [
                result.policy,
                result.decision,
                result.expected_utility,
                result.utility_collaborate,
                result.utility_non_collaborate,
                result.indifference_threshold,
                result.punishment_probability
            ] + [result.parameters[name] for name in param_names]
            
            writer.writerow(row)


def create_config_template(output_path: str) -> None:
    """Create a configuration template file.
    
    Args:
        output_path: Path for template file
    """
    template = {
        "parameters": {
            "reward_collaboration": 100.0,
            "cost_collaboration": 10.0,
            "punishment_magnitude": 1000.0,
            "prob_asi_emergence": 0.85,
            "prob_basilisk_type": 0.7,
            "simulation_detection": 0.95
        },
        "analysis": {
            "policy": "fdt",
            "utility_function": "linear"
        },
        "monte_carlo": {
            "n_simulations": 1000,
            "uncertainty": 0.1,
            "seed": 42
        },
        "output": {
            "export_format": "json",
            "include_plots": true,
            "plot_format": "png"
        }
    }
    
    with open(output_path, 'w') as f:
        json.dump(template, f, indent=2)


def validate_parameters(params: Dict[str, float]) -> None:
    """Validate parameter values.
    
    Args:
        params: Parameter dictionary
        
    Raises:
        ValueError: If parameters are invalid
    """
    required_params = [
        'reward_collaboration', 'cost_collaboration', 'punishment_magnitude',
        'prob_asi_emergence', 'prob_basilisk_type', 'simulation_detection'
    ]
    
    for param in required_params:
        if param not in params:
            raise ValueError(f"Missing required parameter: {param}")
    
    # Validate probability ranges
    prob_params = ['prob_asi_emergence', 'prob_basilisk_type', 'simulation_detection']
    for param in prob_params:
        value = params[param]
        if not 0 <= value <= 1:
            raise ValueError(f"Probability parameter {param} must be between 0 and 1, got {value}")
    
    # Validate non-negative values
    non_negative_params = ['reward_collaboration', 'cost_collaboration', 'punishment_magnitude']
    for param in non_negative_params:
        value = params[param]
        if value < 0:
            raise ValueError(f"Parameter {param} must be non-negative, got {value}")


def calculate_statistics(results: List[DecisionResult]) -> Dict[str, Any]:
    """Calculate summary statistics for results.
    
    Args:
        results: List of DecisionResult objects
        
    Returns:
        Dictionary with summary statistics
    """
    if not results:
        return {}
    
    utilities = [r.expected_utility for r in results]
    decisions = [r.decision for r in results]
    
    # Decision counts
    decision_counts = {}
    for decision in decisions:
        decision_counts[decision] = decision_counts.get(decision, 0) + 1
    
    # Utility statistics
    utility_stats = {
        'mean': np.mean(utilities),
        'std': np.std(utilities),
        'min': np.min(utilities),
        'max': np.max(utilities),
        'median': np.median(utilities)
    }
    
    # Overall statistics
    stats = {
        'total_results': len(results),
        'decision_distribution': decision_counts,
        'utility_statistics': utility_stats,
        'policies_analyzed': list(set(r.policy for r in results))
    }
    
    return stats


def _get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    from datetime import datetime
    return datetime.now().isoformat()


def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        Path object for the directory
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def format_number(value: float, precision: int = 2) -> str:
    """Format number for display with appropriate precision.
    
    Args:
        value: Number to format
        precision: Decimal places
        
    Returns:
        Formatted string
    """
    if abs(value) >= 1000:
        return f"{value:,.{precision}f}"
    else:
        return f"{value:.{precision}f}"


def generate_report_id() -> str:
    """Generate unique report ID based on timestamp.
    
    Returns:
        Unique report identifier
    """
    from datetime import datetime
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# Global configuration for library behavior
_config = {
    'telemetry_enabled': False,  # Zero telemetry by default
    'cache_enabled': True,
    'verbose': False
}


def get_config(key: str) -> Any:
    """Get configuration value.
    
    Args:
        key: Configuration key
        
    Returns:
        Configuration value
    """
    return _config.get(key)


def set_config(key: str, value: Any) -> None:
    """Set configuration value.
    
    Args:
        key: Configuration key
        value: Configuration value
    """
    _config[key] = value