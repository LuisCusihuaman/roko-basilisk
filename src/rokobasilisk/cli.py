"""Command-line interface for Roko's Basilisk analysis and self-modifying agent."""

# SPDX-License-Identifier: MIT

import argparse
import sys
from typing import List

from .api import DecisionResult, evaluate, monte_carlo, sweep
from .plots import plot_decision_boundary, plot_monte_carlo_results
from .utils import export_results, load_config, set_global_seed

# Import agent functionality
try:
    from .agent import LlamaCoderAgent, SimpleCoderAgent, create_example_task
    from .config import (
        ConfigManager,
        create_development_config,
        create_production_config,
    )
    from .tasks import get_all_tasks, get_task_by_name
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Roko's Basilisk: Self-Modifying AI Agent with Mathematical Decision Theory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Mathematical Analysis
  rokobasilisk --policy fdt --explain
  rokobasilisk --compare-theories
  rokobasilisk --monte-carlo 1000 --plot results.png
  rokobasilisk --grid punishment_magnitude 500,1000,1500

  # Self-Modifying Agent
  rokobasilisk --agent-mode --task "Stock Price Fetcher" --model simple
  rokobasilisk --agent-mode --train-basic --agent llama
  rokobasilisk --agent-mode --list-tasks
  rokobasilisk --agent-mode --config agent_config.yaml

  # Combined Analysis
  rokobasilisk --acknowledge-infohazard --policy fdt --agent-mode

For more information: https://github.com/LuisCusihuaman/roko-basilisk
        """
    )

    # Mode selection
    parser.add_argument(
        "--agent-mode",
        action="store_true",
        help="Enable self-modifying agent functionality"
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

    # Agent-specific options
    if AGENT_AVAILABLE:
        agent_group = parser.add_argument_group("Self-Modifying Agent Options")
        agent_group.add_argument("--agent", choices=["simple", "llama"],
                               default="simple", help="Agent type to use (default: simple)")
        agent_group.add_argument("--model", type=str,
                               help="Model name for Llama agent (e.g., codellama/CodeLlama-7b-Python-hf)")
        agent_group.add_argument("--task", type=str,
                               help="Specific task name to run")
        agent_group.add_argument("--list-tasks", action="store_true",
                               help="List all available tasks")
        agent_group.add_argument("--train-basic", action="store_true",
                               help="Train agent on basic tasks")
        agent_group.add_argument("--train-intermediate", action="store_true",
                               help="Train agent on intermediate tasks")
        agent_group.add_argument("--train-advanced", action="store_true",
                               help="Train agent on advanced tasks")
        agent_group.add_argument("--evaluate-all", action="store_true",
                               help="Evaluate agent on all tasks")
        agent_group.add_argument("--improve-code", type=str,
                               help="Analyze and suggest improvements for a Python file")
        agent_group.add_argument("--agent-config", type=str,
                               help="Agent configuration file")

    return parser


def safety_check() -> bool:
    """Check if user has acknowledged potential information hazard."""
    return True  # Safety gate will be handled in main()


def run_agent_mode(args) -> None:
    """Run the self-modifying agent functionality."""
    if not AGENT_AVAILABLE:
        print("❌ Agent functionality not available. Install transformers and other dependencies.")
        sys.exit(1)

    print("🤖 Self-Modifying AI Agent Mode")
    print("=" * 40)

    # Load agent configuration
    config_manager = ConfigManager()
    if args.agent_config:
        agent_config = config_manager.load_config(args.agent_config)
    else:
        agent_config = create_development_config() if args.agent == "simple" else create_production_config()

    # Create agent
    if args.agent == "llama":
        model_name = args.model or agent_config.model.name
        agent = LlamaCoderAgent(model_name=model_name)
        print(f"🧠 Using Llama agent with model: {model_name}")
    else:
        agent = SimpleCoderAgent()
        print("🧠 Using Simple template-based agent")

    # Handle different agent operations
    if args.list_tasks:
        all_tasks = get_all_tasks()
        print("\n📋 Available Tasks:")
        for level, tasks in all_tasks.items():
            print(f"\n{level.upper()} Level:")
            for i, task in enumerate(tasks, 1):
                print(f"  {i}. {task.name}")
                print(f"     {task.description}")
        return

    elif args.task:
        print(f"\n🎯 Running specific task: {args.task}")
        try:
            task = get_task_by_name(args.task)
            result = agent.evaluate_task(task)

            print(f"\nTask: {result.task.name}")
            print(f"Success: {'✅' if result.success else '❌'} {result.success}")
            print(f"Performance Metrics: {result.performance_metrics}")

            if result.error_log:
                print(f"Errors: {result.error_log}")

            print(f"\nGenerated Code ({len(result.generated_code)} chars):")
            print("-" * 40)
            print(result.generated_code[:500] + "..." if len(result.generated_code) > 500 else result.generated_code)

        except ValueError as e:
            print(f"❌ {e}")
            return

    elif args.train_basic or args.train_intermediate or args.train_advanced:
        level = "basic" if args.train_basic else "intermediate" if args.train_intermediate else "advanced"
        print(f"\n🎓 Training agent on {level} tasks...")

        all_tasks = get_all_tasks()
        tasks = all_tasks[level]

        success_count = 0
        for i, task in enumerate(tasks, 1):
            print(f"\n[{i}/{len(tasks)}] {task.name}")
            result = agent.evaluate_task(task)

            if result.success:
                success_count += 1
                print(f"  ✅ Success (utility: {result.performance_metrics.get('execution_time', 0):.3f}s)")
            else:
                print(f"  ❌ Failed: {result.error_log}")

        success_rate = success_count / len(tasks)
        print("\n📊 Training Results:")
        print(f"  Success Rate: {success_rate:.1%} ({success_count}/{len(tasks)})")
        print(f"  Performance History: {len(agent.performance_history)} entries")

    elif args.evaluate_all:
        print("\n🔍 Evaluating agent on all tasks...")
        all_tasks = get_all_tasks()

        total_success = 0
        total_tasks = 0

        for level, tasks in all_tasks.items():
            print(f"\n{level.upper()} Level:")
            level_success = 0

            for task in tasks:
                result = agent.evaluate_task(task)
                status = "✅" if result.success else "❌"
                print(f"  {status} {task.name}")

                if result.success:
                    level_success += 1
                    total_success += 1
                total_tasks += 1

            level_rate = level_success / len(tasks)
            print(f"  Level Success Rate: {level_rate:.1%}")

        overall_rate = total_success / total_tasks
        print("\n📊 Overall Results:")
        print(f"  Total Success Rate: {overall_rate:.1%} ({total_success}/{total_tasks})")

    elif args.improve_code:
        print(f"\n🔧 Analyzing code for improvements: {args.improve_code}")

        try:
            from pathlib import Path
            code_file = Path(args.improve_code)

            if not code_file.exists():
                print(f"❌ File not found: {args.improve_code}")
                return

            with open(code_file) as f:
                code = f.read()

            # Analyze code
            metrics = agent.analyzer.analyze_file(code_file)
            print("\n📊 Code Analysis:")
            for key, value in metrics.items():
                print(f"  {key}: {value}")

            # Get improvement suggestions
            improvements = agent.suggest_improvements(code, metrics)

            if improvements:
                print("\n💡 Improvement Suggestions:")
                for i, improvement in enumerate(improvements, 1):
                    print(f"  {i}. {improvement.description}")
                    print(f"     Confidence: {improvement.confidence:.1%}")
                    print(f"     Estimated Improvement: {improvement.estimated_improvement:.1%}")
            else:
                print("\n✅ No immediate improvements suggested")

        except Exception as e:
            print(f"❌ Error analyzing code: {e}")

    else:
        # Default: run example task
        print("\n🎯 Running example task...")
        task = create_example_task()
        result = agent.evaluate_task(task)

        print(f"\nTask: {result.task.name}")
        print(f"Success: {'✅' if result.success else '❌'} {result.success}")
        print(f"Performance Metrics: {result.performance_metrics}")

        if result.error_log:
            print(f"Errors: {result.error_log}")


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Handle agent mode
    if args.agent_mode:
        run_agent_mode(args)
        return

    # Safety gate for mathematical analysis
    if not args.acknowledge_infohazard:
        print("⚠️  INFORMATION HAZARD WARNING")
        print("=" * 50)
        print("This tool analyzes acausal blackmail scenarios that some consider")
        print("potentially hazardous information. Use --acknowledge-infohazard")
        print("to proceed with mathematical analysis.")
        print("")
        print("For agent functionality, use --agent-mode (no acknowledgment required)")
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
            print("📊 Decision boundary plot saved")

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
