#!/usr/bin/env python3
"""
Advanced CLI for Roko's Basilisk System

Enhanced command-line interface with mathematical analysis, plotting, 
Monte Carlo simulations, and parameter sweeps.
"""

import argparse
import json
import os
from typing import Dict, List, Optional
import numpy as np

from basilisk import RokoBasilisk, DecisionTheory, UtilityFunction, BasiliskParameters


def create_parser() -> argparse.ArgumentParser:
    """Create the command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Roko's Basilisk - Advanced Mathematical Analysis System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic analysis with FDT
  python advanced_cli.py --policy fdt --explain

  # Parameter grid analysis 
  python advanced_cli.py --grid punishment_magnitude 500,1000,1500 --grid prob_asi_emergence 0.7,0.8,0.9

  # Monte Carlo simulation
  python advanced_cli.py --monte-carlo 5000 --plot monte_carlo_results.png

  # Decision boundary plot
  python advanced_cli.py --plot-boundary punishment_magnitude prob_asi_emergence --save boundary.png

  # Compare all decision theories
  python advanced_cli.py --compare-theories --export results.json

  # Custom parameters from config
  python advanced_cli.py --config custom_params.json --policy fdt
        """
    )
    
    # Core analysis options
    parser.add_argument('--policy', type=str, choices=['fdt', 'tdt', 'cdt', 'edt', 'reject'], 
                       default='fdt', help='Decision theory to use')
    parser.add_argument('--utility-func', type=str, choices=['linear', 'logarithmic', 'exponential', 'square_root'],
                       default='linear', help='Utility function type')
    parser.add_argument('--explain', action='store_true', help='Show detailed mathematical explanations')
    
    # Parameter specification
    param_group = parser.add_argument_group('Parameters')
    param_group.add_argument('--reward', type=float, help='Collaboration reward (r)')
    param_group.add_argument('--cost', type=float, help='Collaboration cost (c)')
    param_group.add_argument('--punishment', type=float, help='Punishment magnitude (C)')
    param_group.add_argument('--prob-asi', type=float, help='ASI emergence probability p(A)')
    param_group.add_argument('--prob-basilisk', type=float, help='Basilisk type probability p(B|A)')
    param_group.add_argument('--detection', type=float, help='Simulation detection rate (q)')
    
    # Advanced analysis
    analysis_group = parser.add_argument_group('Advanced Analysis')
    analysis_group.add_argument('--grid', action='append', nargs=2, metavar=('PARAM', 'VALUES'),
                               help='Parameter grid: --grid param_name val1,val2,val3')
    analysis_group.add_argument('--monte-carlo', type=int, metavar='N',
                               help='Run Monte Carlo simulation with N samples')
    analysis_group.add_argument('--compare-theories', action='store_true',
                               help='Compare all decision theories')
    analysis_group.add_argument('--sensitivity', type=str, metavar='PARAM',
                               help='Sensitivity analysis for parameter')
    
    # Plotting
    plot_group = parser.add_argument_group('Plotting')
    plot_group.add_argument('--plot-boundary', nargs=2, metavar=('PARAM1', 'PARAM2'),
                           help='Plot 2D decision boundary')
    plot_group.add_argument('--plot', type=str, metavar='FILE',
                           help='Save Monte Carlo plots to file')
    plot_group.add_argument('--save', type=str, metavar='FILE',
                           help='Save plot to file')
    plot_group.add_argument('--resolution', type=int, default=50,
                           help='Plot resolution (default: 50)')
    
    # I/O
    io_group = parser.add_argument_group('Input/Output')
    io_group.add_argument('--config', type=str, metavar='FILE',
                         help='Load parameters from JSON config file')
    io_group.add_argument('--export', type=str, metavar='FILE',
                         help='Export results to JSON file')
    io_group.add_argument('--output-dir', type=str, default='results',
                         help='Output directory for files (default: results)')
    
    return parser


def load_config(config_path: str) -> BasiliskParameters:
    """Load parameters from JSON config file."""
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    return BasiliskParameters(**config)


def save_results(results: Dict, output_path: str) -> None:
    """Save results to JSON file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Convert numpy types to native Python types for JSON serialization
    def convert_numpy(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: convert_numpy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy(item) for item in obj]
        else:
            return obj
    
    results_clean = convert_numpy(results)
    
    with open(output_path, 'w') as f:
        json.dump(results_clean, f, indent=2, default=str)
    
    print(f"Results saved to {output_path}")


def decision_theory_from_string(policy_str: str) -> DecisionTheory:
    """Convert string to DecisionTheory enum."""
    mapping = {
        'fdt': DecisionTheory.FDT,
        'tdt': DecisionTheory.TDT,
        'cdt': DecisionTheory.CDT,
        'edt': DecisionTheory.EDT,
        'reject': DecisionTheory.REJECT_BLACKMAIL
    }
    return mapping[policy_str.lower()]


def utility_function_from_string(func_str: str) -> UtilityFunction:
    """Convert string to UtilityFunction enum."""
    mapping = {
        'linear': UtilityFunction.LINEAR,
        'logarithmic': UtilityFunction.LOGARITHMIC,
        'exponential': UtilityFunction.EXPONENTIAL,
        'square_root': UtilityFunction.SQUARE_ROOT
    }
    return mapping[func_str.lower()]


def run_basic_analysis(basilisk: RokoBasilisk, args) -> Dict:
    """Run basic decision analysis."""
    decision_theory = decision_theory_from_string(args.policy)
    utility_func = utility_function_from_string(args.utility_func)
    
    result = basilisk.analyze_decision(decision_theory, utility_func)
    
    analysis = {
        'decision_theory': args.policy,
        'utility_function': args.utility_func,
        'optimal_decision': result.optimal_decision,
        'utility_collaborate': result.utility_collaborate,
        'utility_non_collaborate': result.utility_non_collaborate,
        'utility_difference': result.utility_difference,
        'mathematical_justification': result.mathematical_justification,
        'indifference_threshold': result.c_star,
        'parameters': {
            'reward_collaboration': basilisk.params.reward_collaboration,
            'cost_collaboration': basilisk.params.cost_collaboration,
            'punishment_magnitude': basilisk.params.punishment_magnitude,
            'prob_asi_emergence': basilisk.params.prob_asi_emergence,
            'prob_basilisk_type': basilisk.params.prob_basilisk_type,
            'simulation_detection': basilisk.params.simulation_detection
        }
    }
    
    if args.explain:
        print("\n🧮 MATHEMATICAL EXPLANATION:")
        print("=" * 60)
        print(f"Decision Theory: {decision_theory.value}")
        print(f"Utility Function: {utility_func.value}")
        print(f"\nOptimal Decision: {result.optimal_decision}")
        print(f"Mathematical Justification: {result.mathematical_justification}")
        
        if result.c_star is not None:
            print(f"\nIndifference Threshold C* = {result.c_star:.2f}")
            print(f"Current punishment C = {basilisk.params.punishment_magnitude:.2f}")
            if basilisk.params.punishment_magnitude > result.c_star:
                print("✅ Punishment exceeds threshold - collaboration is optimal")
            else:
                print("❌ Punishment below threshold - non-collaboration preferred")
    
    return analysis


def run_grid_analysis(basilisk: RokoBasilisk, grid_params: List[List[str]], args) -> Dict:
    """Run parameter grid analysis."""
    decision_theory = decision_theory_from_string(args.policy)
    
    results = {}
    
    for param_name, values_str in grid_params:
        values = [float(v.strip()) for v in values_str.split(',')]
        print(f"\n📊 Grid Analysis: {param_name} = {values}")
        
        sensitivity_results = basilisk.sensitivity_analysis(param_name, values, decision_theory)
        
        results[param_name] = {
            'values': values,
            'decisions': [r.optimal_decision for r in sensitivity_results],
            'utility_collaborate': [r.utility_collaborate for r in sensitivity_results],
            'utility_non_collaborate': [r.utility_non_collaborate for r in sensitivity_results],
            'utility_difference': [r.utility_difference for r in sensitivity_results]
        }
        
        # Print summary
        collab_count = sum(1 for d in results[param_name]['decisions'] if d == 'COLLABORATE')
        print(f"   Collaboration decisions: {collab_count}/{len(values)} ({100*collab_count/len(values):.1f}%)")
    
    return results


def run_monte_carlo(basilisk: RokoBasilisk, n_samples: int, args) -> Dict:
    """Run Monte Carlo simulation."""
    decision_theory = decision_theory_from_string(args.policy)
    
    print(f"\n🎲 Running Monte Carlo simulation with {n_samples} samples...")
    mc_results = basilisk.monte_carlo_simulation(n_samples, decision_theory)
    
    print(f"\nMonte Carlo Results:")
    print(f"   Collaboration Probability: {mc_results['collaboration_probability']:.3f}")
    print(f"   Mean Collaboration Utility: {mc_results['mean_collab_utility']:.2f} ± {mc_results['std_collab_utility']:.2f}")
    print(f"   Mean Non-Collaboration Utility: {mc_results['mean_non_collab_utility']:.2f} ± {mc_results['std_non_collab_utility']:.2f}")
    
    if args.plot:
        os.makedirs(args.output_dir, exist_ok=True)
        plot_path = os.path.join(args.output_dir, args.plot)
        basilisk.plot_monte_carlo_results(mc_results, plot_path)
    
    return mc_results


def run_theory_comparison(basilisk: RokoBasilisk) -> Dict:
    """Compare all decision theories."""
    print("\n🔬 DECISION THEORY COMPARISON:")
    print("=" * 60)
    
    results = basilisk.compare_decision_theories()
    
    for theory, result in results.items():
        print(f"\n{theory.value.upper()}:")
        print(f"   Optimal Decision: {result.optimal_decision}")
        print(f"   Utility Difference: {result.utility_difference:.2f}")
        print(f"   Justification: {result.mathematical_justification}")
    
    # Summary table
    print(f"\n{'Theory':<25} {'Decision':<15} {'Utility Diff':<12} {'Threshold':<10}")
    print("-" * 62)
    for theory, result in results.items():
        threshold_str = f"{result.c_star:.2f}" if result.c_star is not None else "N/A"
        print(f"{theory.value:<25} {result.optimal_decision:<15} {result.utility_difference:<12.2f} {threshold_str:<10}")
    
    return {theory.value: {
        'optimal_decision': result.optimal_decision,
        'utility_collaborate': result.utility_collaborate,
        'utility_non_collaborate': result.utility_non_collaborate,
        'utility_difference': result.utility_difference,
        'mathematical_justification': result.mathematical_justification,
        'c_star': result.c_star
    } for theory, result in results.items()}


def main():
    """Main CLI function."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load parameters
    if args.config:
        params = load_config(args.config)
    else:
        # Use command line parameters or defaults
        params = BasiliskParameters(
            reward_collaboration=args.reward or 100.0,
            cost_collaboration=args.cost or 10.0,
            punishment_magnitude=args.punishment or 1000.0,
            prob_asi_emergence=args.prob_asi or 0.85,
            prob_basilisk_type=args.prob_basilisk or 0.70,
            simulation_detection=args.detection or 0.95
        )
    
    # Initialize Basilisk
    basilisk = RokoBasilisk(params)
    
    print("🐍 ROKO'S BASILISK - ADVANCED MATHEMATICAL ANALYSIS")
    print("=" * 60)
    print(f"Parameters: r={params.reward_collaboration}, c={params.cost_collaboration}, "
          f"C={params.punishment_magnitude}, p(A)={params.prob_asi_emergence}, "
          f"p(B|A)={params.prob_basilisk_type}, q={params.simulation_detection}")
    
    results = {}
    
    # Basic analysis
    basic_results = run_basic_analysis(basilisk, args)
    results['basic_analysis'] = basic_results
    
    # Grid analysis
    if args.grid:
        grid_results = run_grid_analysis(basilisk, args.grid, args)
        results['grid_analysis'] = grid_results
    
    # Monte Carlo simulation
    if args.monte_carlo:
        mc_results = run_monte_carlo(basilisk, args.monte_carlo, args)
        results['monte_carlo'] = mc_results
    
    # Theory comparison
    if args.compare_theories:
        theory_results = run_theory_comparison(basilisk)
        results['theory_comparison'] = theory_results
    
    # Sensitivity analysis
    if args.sensitivity:
        print(f"\n📈 Sensitivity Analysis for {args.sensitivity}:")
        values = np.linspace(0.1, 2.0, 20) * getattr(params, args.sensitivity)
        sensitivity_results = basilisk.sensitivity_analysis(args.sensitivity, values.tolist())
        results['sensitivity_analysis'] = {
            'parameter': args.sensitivity,
            'values': values.tolist(),
            'decisions': [r.optimal_decision for r in sensitivity_results],
            'utilities': [(r.utility_collaborate, r.utility_non_collaborate) for r in sensitivity_results]
        }
    
    # Decision boundary plot
    if args.plot_boundary:
        param1, param2 = args.plot_boundary
        decision_theory = decision_theory_from_string(args.policy)
        
        save_path = None
        if args.save:
            save_path = os.path.join(args.output_dir, args.save)
        
        print(f"\n📊 Plotting decision boundary: {param1} vs {param2}")
        basilisk.plot_decision_boundary(param1, param2, args.resolution, decision_theory, save_path)
    
    # Export results
    if args.export:
        export_path = os.path.join(args.output_dir, args.export)
        save_results(results, export_path)


if __name__ == "__main__":
    main()