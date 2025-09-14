"""Command-line interface for Roko's Basilisk analysis."""

# SPDX-License-Identifier: MIT

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

from .api import evaluate, sweep, monte_carlo, DecisionResult
from .plots import plot_decision_boundary, plot_monte_carlo_results
from .utils import export_results, load_config, set_global_seed


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Roko's Basilisk: Advanced ASI analysis with timeless decision theory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  rokobasilisk --policy fdt --explain
  rokobasilisk --compare-theories
  rokobasilisk --monte-carlo 1000 --plot results.png
  rokobasilisk --grid punishment_magnitude 500,1000,1500
  rokobasilisk --config config.json --export results.json
  rokobasilisk --acknowledge-infohazard --policy fdt

For more information: https://github.com/LuisCusihuaman/roko-basilisk
        """
    )
    
    # Safety gate
    parser.add_argument(
        "--acknowledge-infohazard",
        action="store_true",
        help="Acknowledge potential information hazard and proceed with analysis"
    )
    
    # Core parameters
    parser.add_argument("--reward", type=float, default=100.0,
                       help="Reward for collaboration (default: 100)")
    parser.add_argument("--cost", type=float, default=10.0,
                       help="Cost of collaboration (default: 10)")
    parser.add_argument("--punishment", type=float, default=1000.0,
                       help="Punishment magnitude (default: 1000)")
    parser.add_argument("--prob-asi", type=float, default=0.85,
                       help="Probability of ASI emergence (default: 0.85)")
    parser.add_argument("--prob-basilisk", type=float, default=0.7,
                       help="Probability of Basilisk type given ASI (default: 0.7)")
    parser.add_argument("--detection", type=float, default=0.95,
                       help="Simulation detection probability (default: 0.95)")
    
    # Analysis options
    parser.add_argument("--policy", choices=["fdt", "tdt", "cdt", "edt", "reject"],
                       default="fdt", help="Decision theory to use (default: fdt)")
    parser.add_argument("--utility", choices=["linear", "log", "exp", "sqrt"],
                       default="linear", help="Utility function type (default: linear)")
    parser.add_argument("--explain", action="store_true",
                       help="Show detailed explanation of analysis")
    
    # Advanced analysis
    parser.add_argument("--compare-theories", action="store_true",
                       help="Compare all decision theories")
    parser.add_argument("--monte-carlo", type=int, metavar="N",
                       help="Run Monte Carlo simulation with N samples")
    parser.add_argument("--grid", nargs=2, metavar=("PARAM", "VALUES"),
                       help="Parameter grid sweep (e.g., --grid punishment 500,1000,1500)")
    parser.add_argument("--sensitivity", type=str, metavar="PARAM",
                       help="Sensitivity analysis for parameter")
    
    # Plotting
    parser.add_argument("--plot", type=str, metavar="FILE",
                       help="Save plot to file")
    parser.add_argument("--plot-boundary", nargs=2, metavar=("PARAM1", "PARAM2"),
                       help="Plot decision boundary between two parameters")
    
    # I/O
    parser.add_argument("--config", type=str, metavar="FILE",
                       help="Load configuration from JSON file")
    parser.add_argument("--export", type=str, metavar="FILE",
                       help="Export results to JSON file")
    parser.add_argument("--report", choices=["text", "html"], default="text",
                       help="Report format (default: text)")
    
    # Reproducibility
    parser.add_argument("--seed", type=int, default=42,
                       help="Random seed for reproducibility (default: 42)")
    parser.add_argument("--no-telemetry", action="store_true",
                       help="Disable telemetry (already disabled by default)")
    
    return parser


def safety_check() -> bool:
    """Check if user has acknowledged potential information hazard."""
    return True  # Safety gate will be handled in main()


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Safety gate
    if not args.acknowledge_infohazard:
        print("⚠️  INFORMATION HAZARD WARNING")
        print("=" * 50)
        print("This tool analyzes acausal blackmail scenarios that some consider")
        print("potentially hazardous information. Use --acknowledge-infohazard")
        print("to proceed with analysis.")
        print("")
        print("For safety information, see: ETHICS.md")
        sys.exit(1)
    
    # Set global seed
    set_global_seed(args.seed)
    
    # Load configuration if provided
    config = {}
    if args.config:
        config = load_config(args.config)
    
    # Build parameters
    params = {
        'reward_collaboration': args.reward,
        'cost_collaboration': args.cost,
        'punishment_magnitude': args.punishment,
        'prob_asi_emergence': args.prob_asi,
        'prob_basilisk_type': args.prob_basilisk,
        'simulation_detection': args.detection
    }
    
    # Override with config values
    if 'parameters' in config:
        params.update(config['parameters'])
    
    results: List[DecisionResult] = []
    
    try:
        # Execute analysis based on arguments
        if args.compare_theories:
            print("🔍 Comparing Decision Theories")
            print("=" * 40)
            for policy in ['fdt', 'tdt', 'cdt', 'edt', 'reject']:
                result = evaluate(params, policy, args.utility, explain=True)
                results.append(result)
                print(f"\n{policy.upper()}:")
                print(f"  Decision: {result.decision}")
                print(f"  Expected Utility: {result.expected_utility:.2f}")
                if args.explain and result.explanation:
                    print(f"  {result.explanation}")
                    
        elif args.monte_carlo:
            print(f"🎲 Monte Carlo Simulation ({args.monte_carlo:,} samples)")
            print("=" * 50)
            mc_config = {'parameters': params, 'policy': args.policy, 'seed': args.seed}
            results = monte_carlo(mc_config, args.monte_carlo)
            
            # Summary statistics
            decisions = [r.decision for r in results]
            collab_rate = decisions.count('COLLABORATE') / len(decisions)
            utilities = [r.expected_utility for r in results]
            
            print(f"Collaboration rate: {collab_rate:.1%}")
            print(f"Mean utility: {sum(utilities)/len(utilities):.2f}")
            print(f"Std utility: {(sum((u - sum(utilities)/len(utilities))**2 for u in utilities) / len(utilities))**0.5:.2f}")
            
        elif args.grid:
            param_name, values_str = args.grid
            values = [float(v.strip()) for v in values_str.split(',')]
            
            print(f"📊 Parameter Grid Sweep: {param_name}")
            print("=" * 40)
            
            grid = {param_name: values}
            results = sweep(grid)
            
            # Group by parameter value
            for value in values:
                param_results = [r for r in results if r.parameters[param_name] == value]
                print(f"\n{param_name} = {value}:")
                for result in param_results:
                    print(f"  {result.policy}: {result.decision} ({result.expected_utility:.2f})")
                    
        elif args.sensitivity:
            param_name = args.sensitivity
            base_value = params[param_name]
            
            print(f"📈 Sensitivity Analysis: {param_name}")
            print("=" * 40)
            
            # Test ±50% around base value
            test_values = [base_value * f for f in [0.5, 0.75, 1.0, 1.25, 1.5]]
            grid = {param_name: test_values}
            results = sweep(grid)
            
            for value in test_values:
                param_results = [r for r in results if r.parameters[param_name] == value]
                fdt_result = next(r for r in param_results if r.policy == 'fdt')
                change_pct = (value - base_value) / base_value * 100
                print(f"  {value:.2f} ({change_pct:+.0f}%): {fdt_result.decision} ({fdt_result.expected_utility:.2f})")
                
        else:
            # Single analysis
            result = evaluate(params, args.policy, args.utility, explain=args.explain)
            results.append(result)
            
            print("🐍 Roko's Basilisk Analysis")
            print("=" * 30)
            print(f"Policy: {result.policy.upper()}")
            print(f"Decision: {result.decision}")
            print(f"Expected Utility: {result.expected_utility:.2f}")
            print(f"Indifference Threshold C*: {result.indifference_threshold:.2f}")
            
            if args.explain and result.explanation:
                print("\nDetailed Analysis:")
                print(result.explanation)
        
        # Generate plots if requested
        if args.plot and results:
            if args.monte_carlo:
                plot_monte_carlo_results(results, args.plot)
                print(f"📊 Plot saved to: {args.plot}")
            else:
                print("⚠️  Plot generation requires --monte-carlo option")
                
        if args.plot_boundary:
            param1, param2 = args.plot_boundary
            plot_decision_boundary(params, param1, param2, args.policy, args.plot or f"boundary_{param1}_{param2}.png")
            print(f"📊 Decision boundary plot saved")
        
        # Export results if requested
        if args.export and results:
            export_results(results, args.export)
            print(f"💾 Results exported to: {args.export}")
            
        # Report seed for reproducibility
        print(f"\n🌱 Random seed: {args.seed}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()