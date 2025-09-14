"""Command-line interface for Roko's Basilisk analysis and self-modifying agent."""

# SPDX-License-Identifier: MIT

import argparse
import sys
import time
from pathlib import Path
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
    from .react_agent import EnhancedReActAgent, ReActAgent, create_react_agent
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

  # Self-Modifying Agent with ReAct Loop
  rokobasilisk --agent-mode --task "Stock Price Fetcher" --agent react-simple
  rokobasilisk --agent-mode --train-basic --agent react-llama
  rokobasilisk --agent-mode --list-tasks
  rokobasilisk --agent-mode --react-loop --max-iterations 15

  # Traditional Agent (without ReAct)
  rokobasilisk --agent-mode --task "Stock Price Fetcher" --agent simple
  rokobasilisk --agent-mode --train-basic --agent llama

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
        agent_group.add_argument("--agent", choices=["simple", "llama", "react-simple", "react-llama"],
                               default="react-simple", help="Agent type to use (default: react-simple)")
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

        # ReAct-specific options
        react_group = parser.add_argument_group("ReAct Loop Options")
        react_group.add_argument("--react-loop", action="store_true",
                               help="Use ReAct (Reason, Act) loop for self-correction")
        react_group.add_argument("--max-iterations", type=int, default=10,
                               help="Maximum iterations for ReAct loop (default: 10)")
        react_group.add_argument("--memory-file", type=str, default="memory.txt",
                               help="File to store ReAct memory log (default: memory.txt)")
        react_group.add_argument("--show-thinking", action="store_true",
                               help="Show detailed step-by-step thinking process")
        react_group.add_argument("--interactive", action="store_true",
                               help="Interactive mode: pause between ReAct steps")

        # Phase 3: Memory & Fine-tuning options
        memory_group = parser.add_argument_group("🧠 Memory & Learning System (Phase 3)")
        memory_group.add_argument("--memory-mode", action="store_true",
                                help="Run memory management and feedback collection")
        memory_group.add_argument("--process-memory", action="store_true",
                                help="Process and structure experiences from memory.txt")
        memory_group.add_argument("--collect-feedback", action="store_true",
                                help="Collect human feedback on agent experiences")
        memory_group.add_argument("--interactive-feedback", action="store_true",
                                help="Interactive feedback collection mode")
        memory_group.add_argument("--memory-summary", action="store_true",
                                help="Show summary of agent memory and experiences")
        memory_group.add_argument("--find-similar", type=str, metavar="TASK_DESC",
                                help="Find similar past experiences for a task description")

        # Fine-tuning options
        tuning_group = parser.add_argument_group("🔧 Model Fine-tuning (Phase 3)")
        tuning_group.add_argument("--fine-tune", action="store_true",
                                help="Run complete fine-tuning pipeline with DPO")
        tuning_group.add_argument("--base-model", type=str, default="codellama/CodeLlama-7b-Python-hf",
                                help="Base model for fine-tuning")
        tuning_group.add_argument("--output-model", type=str,
                                help="Output directory for fine-tuned model")
        tuning_group.add_argument("--list-models", action="store_true",
                                help="List all available fine-tuned model versions")
        tuning_group.add_argument("--evaluate-model", type=str, metavar="MODEL_PATH",
                                help="Evaluate a fine-tuned model on test tasks")
        tuning_group.add_argument("--best-model", action="store_true",
                                help="Show the best performing model")

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
        agent_config = create_development_config() if "simple" in args.agent else create_production_config()

    # Create agent based on type
    if args.agent in ["react-simple", "react-llama"]:
        print("🔄 Using ReAct (Reason, Act) Loop Agent")
        agent_type = "llama" if "llama" in args.agent else "simple"
        model_name = args.model or (agent_config.model.name if hasattr(agent_config, 'model') else None)

        # Create ReAct agent
        agent = create_react_agent(agent_type=agent_type, model_name=model_name)

        if hasattr(agent, 'max_iterations'):
            agent.max_iterations = args.max_iterations
        if hasattr(agent, 'logger') and hasattr(agent.logger, 'memory_file'):
            from pathlib import Path
            agent.logger.memory_file = Path(args.memory_file)

        print(f"🧠 ReAct Agent: {agent.name}")
        print(f"📝 Memory file: {args.memory_file}")
        print(f"🔁 Max iterations: {args.max_iterations}")

    elif args.agent == "llama":
        model_name = args.model or (agent_config.model.name if hasattr(agent_config, 'model') else "codellama/CodeLlama-7b-Python-hf")
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

            # Use ReAct loop if available
            if isinstance(agent, (ReActAgent, EnhancedReActAgent)):
                print("🔄 Executing with ReAct loop...")
                session = agent.evaluate_task_with_react(task)

                print(f"\n{'='*50}")
                print("🎯 REACT SESSION RESULTS")
                print(f"{'='*50}")
                print(f"Task: {session.task_name}")
                print(f"Success: {'✅' if session.final_success else '❌'} {session.final_success}")
                print(f"Total Steps: {session.total_steps}")
                print(f"Duration: {session.session_end - session.session_start:.2f}s")

                if args.show_thinking:
                    print("\n🧠 Step-by-Step Thinking Process:")
                    print(f"{'-'*50}")
                    for step in session.steps:
                        print(f"\n📍 Step {step.step_number}: {step.action}")
                        print(f"💭 THOUGHT: {step.thought}")
                        print(f"🎬 ACTION: {step.action}({step.action_input})")
                        print(f"👁️  OBSERVATION: {step.observation[:200]}{'...' if len(step.observation) > 200 else ''}")
                        print(f"✅ SUCCESS: {step.success}")

                        if args.interactive:
                            input("Press Enter to continue to next step...")

                # Show memory summary
                memory_summary = agent.logger.get_memory_summary()
                print("\n📊 Memory Summary:")
                print(f"  Total Sessions: {memory_summary.get('total_sessions', 0)}")
                if memory_summary.get('total_sessions', 0) > 0:
                    print(f"  Success Rate: {memory_summary.get('success_rate', 0):.1%}")
                    print(f"  Avg Steps/Session: {memory_summary.get('avg_steps_per_session', 0):.1f}")

            else:
                # Traditional agent evaluation
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
        total_time = 0.0
        total_steps = 0

        for i, task in enumerate(tasks, 1):
            print(f"\n[{i}/{len(tasks)}] {task.name}")

            if isinstance(agent, (ReActAgent, EnhancedReActAgent)):
                # ReAct training with detailed feedback
                session = agent.evaluate_task_with_react(task)

                if session.final_success:
                    success_count += 1
                    print(f"  ✅ Success in {session.total_steps} steps ({session.session_end - session.session_start:.2f}s)")
                else:
                    print(f"  ❌ Failed after {session.total_steps} steps ({session.session_end - session.session_start:.2f}s)")

                total_time += (session.session_end - session.session_start)
                total_steps += session.total_steps

                if args.show_thinking and i <= 2:  # Show thinking for first 2 tasks
                    print(f"    🧠 Sample thinking from final step: {session.steps[-1].thought[:100]}...")

            else:
                # Traditional training
                result = agent.evaluate_task(task)

                if result.success:
                    success_count += 1
                    print(f"  ✅ Success (utility: {result.performance_metrics.get('execution_time', 0):.3f}s)")
                else:
                    print(f"  ❌ Failed: {result.error_log}")

        success_rate = success_count / len(tasks)
        print("\n📊 Training Results:")
        print(f"  Success Rate: {success_rate:.1%} ({success_count}/{len(tasks)})")

        if isinstance(agent, (ReActAgent, EnhancedReActAgent)):
            print(f"  Total Training Time: {total_time:.1f}s")
            print(f"  Average Steps per Task: {total_steps / len(tasks):.1f}")
            print(f"  Memory Sessions: {len(agent.logger.sessions)}")

            # Show memory insights
            memory_summary = agent.logger.get_memory_summary()
            if memory_summary.get('total_sessions', 0) > 0:
                print(f"  Overall Success Rate: {memory_summary.get('success_rate', 0):.1%}")
        else:
            print(f"  Performance History: {len(agent.performance_history)} entries")

    elif args.evaluate_all:
        print("\n🔍 Evaluating agent on all tasks...")
        all_tasks = get_all_tasks()

        total_success = 0
        total_tasks = 0
        total_steps = 0
        total_time = 0.0

        for level, tasks in all_tasks.items():
            print(f"\n{level.upper()} Level:")
            level_success = 0
            level_steps = 0
            level_time = 0.0

            for task in tasks:
                if isinstance(agent, (ReActAgent, EnhancedReActAgent)):
                    session = agent.evaluate_task_with_react(task)
                    success = session.final_success
                    steps = session.total_steps
                    time_taken = session.session_end - session.session_start

                    status = "✅" if success else "❌"
                    print(f"  {status} {task.name} ({steps} steps, {time_taken:.1f}s)")

                    level_steps += steps
                    level_time += time_taken
                    total_steps += steps
                    total_time += time_taken
                else:
                    result = agent.evaluate_task(task)
                    success = result.success
                    status = "✅" if success else "❌"
                    print(f"  {status} {task.name}")

                if success:
                    level_success += 1
                    total_success += 1
                total_tasks += 1

            level_rate = level_success / len(tasks)
            print(f"  Level Success Rate: {level_rate:.1%}")

            if isinstance(agent, (ReActAgent, EnhancedReActAgent)):
                print(f"  Level Avg Steps: {level_steps / len(tasks):.1f}")
                print(f"  Level Total Time: {level_time:.1f}s")

        overall_rate = total_success / total_tasks
        print("\n📊 Overall Results:")
        print(f"  Total Success Rate: {overall_rate:.1%} ({total_success}/{total_tasks})")

        if isinstance(agent, (ReActAgent, EnhancedReActAgent)):
            print(f"  Total Evaluation Time: {total_time:.1f}s")
            print(f"  Average Steps per Task: {total_steps / total_tasks:.1f}")

            # Final memory summary
            memory_summary = agent.logger.get_memory_summary()
            print(f"  Memory Sessions: {memory_summary.get('total_sessions', 0)}")
            if memory_summary.get('total_sessions', 0) > 0:
                print(f"  Historical Success Rate: {memory_summary.get('success_rate', 0):.1%}")

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


def run_memory_mode(args) -> None:
    """Run Phase 3 memory and fine-tuning functionality."""
    try:
        from .fine_tuning import (
            DPOFineTuner,
            FineTuningConfig,
            ModelVersioning,
            run_fine_tuning_pipeline,
        )
        from .memory import MemoryManager
    except ImportError as e:
        print(f"❌ Memory/Fine-tuning functionality not available: {e}")
        print("Install required dependencies: pip install chromadb trl datasets wandb")
        sys.exit(1)

    print("🧠 Memory & Learning System (Phase 3)")
    print("=" * 40)

    # Initialize memory manager
    memory_manager = MemoryManager(args.memory_file)

    # Memory management operations
    if args.process_memory:
        print("📚 Processing experiences from memory...")
        experiences = memory_manager.process_new_experiences()
        print(f"✅ Processed {len(experiences)} experiences")
        return

    if args.memory_summary:
        print("📊 Memory Summary:")
        summary = memory_manager.get_memory_summary()
        print(f"- Total experiences: {summary['total_experiences']}")
        print(f"- Successful experiences: {summary['successful_experiences']}")
        print(f"- Total feedback: {summary['total_feedback']}")
        print(f"- Vector store: {'Available' if summary['vector_store_available'] else 'Not available'}")

        if summary['recent_experiences']:
            print("\n📝 Recent experiences:")
            for exp in summary['recent_experiences']:
                success_icon = "✅" if exp.final_success else "❌"
                print(f"  {success_icon} {exp.task_name} ({exp.performance_metrics.get('duration', 0):.2f}s)")
        return

    if args.find_similar:
        print(f"🔍 Finding similar experiences for: {args.find_similar}")
        similar = memory_manager.get_similar_experiences(args.find_similar, n_results=5)

        if similar:
            print(f"Found {len(similar)} similar experiences:")
            for i, exp in enumerate(similar, 1):
                metadata = exp.get('metadata', {})
                similarity = exp.get('similarity', 0)
                print(f"  {i}. {metadata.get('task_name', 'Unknown')} (similarity: {similarity:.2f})")
                print(f"     Success: {'✅' if metadata.get('success') else '❌'}")
                print(f"     Agent: {metadata.get('agent_type', 'Unknown')}")
        else:
            print("No similar experiences found")
        return

    if args.collect_feedback or args.interactive_feedback:
        print("📝 Collecting feedback on experiences...")
        experiences = memory_manager.process_new_experiences()

        if not experiences:
            print("❌ No experiences found to collect feedback on")
            print("Run some agent tasks first: rokobasilisk --agent-mode --task 'Stock Price Fetcher'")
            return

        feedback_results = memory_manager.collect_feedback_batch(
            experiences,
            interactive=args.interactive_feedback
        )
        print(f"✅ Collected feedback for {len(feedback_results)} experiences")
        return

    # Model management operations
    versioning = ModelVersioning()

    if args.list_models:
        print("📋 Available Model Versions:")
        versions = versioning.list_model_versions()

        if not versions:
            print("No fine-tuned models found")
            print("Run: rokobasilisk --fine-tune to create your first model")
        else:
            for i, version in enumerate(versions, 1):
                score = version['evaluation']['overall_score'] if version['evaluation'] else 0
                date = time.strftime('%Y-%m-%d %H:%M', time.localtime(version['created']))
                print(f"  {i}. {version['name']}")
                print(f"     Score: {score:.2f} | Created: {date}")
                if version['metadata']:
                    base_model = version['metadata'].get('base_model', 'Unknown')
                    print(f"     Base: {base_model}")
        return

    if args.best_model:
        print("🏆 Best Performing Model:")
        best_path = versioning.get_best_model()

        if best_path:
            best_name = Path(best_path).name
            versions = versioning.list_model_versions()
            best_version = next((v for v in versions if v['path'] == best_path), None)

            if best_version and best_version['evaluation']:
                score = best_version['evaluation']['overall_score']
                print(f"Model: {best_name}")
                print(f"Score: {score:.2f}")
                print(f"Path: {best_path}")
            else:
                print(f"Model: {best_name}")
                print(f"Path: {best_path}")
        else:
            print("No evaluated models found")
        return

    if args.evaluate_model:
        print(f"📊 Evaluating model: {args.evaluate_model}")

        config = FineTuningConfig()
        fine_tuner = DPOFineTuner(config)

        evaluation = fine_tuner.evaluate_model(args.evaluate_model)

        if evaluation:
            print("✅ Evaluation completed!")
            print(f"Overall score: {evaluation['overall_score']:.2f}")
            print(f"Results saved to: {Path(args.evaluate_model) / 'evaluation_results.json'}")
        else:
            print("❌ Evaluation failed")
        return

    if args.fine_tune:
        print("🔧 Starting Fine-tuning Pipeline...")
        print("This will:")
        print("1. Process experiences from memory")
        print("2. Collect feedback (automated)")
        print("3. Prepare training dataset")
        print("4. Fine-tune model with DPO")
        print("5. Evaluate the result")

        # Check if we have TRL
        try:
            import importlib.util
            if importlib.util.find_spec("trl") is None:
                raise ImportError("TRL not found")
        except ImportError:
            print("\n❌ TRL library required for fine-tuning")
            print("Install with: pip install trl datasets wandb")
            return

        confirm = input("\nProceed with fine-tuning? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("Fine-tuning cancelled")
            return

        # Run fine-tuning pipeline
        model_path = run_fine_tuning_pipeline(
            memory_file=args.memory_file,
            interactive_feedback=args.interactive_feedback,
            model_name=args.base_model,
            output_dir=args.output_model
        )

        if model_path:
            print("\n🎉 Fine-tuning completed successfully!")
            print(f"📁 Model saved to: {model_path}")

            # Show updated model list
            print("\n📋 Updated model versions:")
            versions = versioning.list_model_versions()
            for version in versions[:3]:
                score = version['evaluation']['overall_score'] if version['evaluation'] else 0
                print(f"  - {version['name']}: {score:.2f}")
        else:
            print("❌ Fine-tuning failed")
        return

    # Default memory mode behavior
    if args.memory_mode:
        print("👋 Welcome to Memory & Learning System!")
        print("\nAvailable commands:")
        print("  --process-memory     : Process new experiences")
        print("  --memory-summary     : Show memory statistics")
        print("  --collect-feedback   : Collect feedback on experiences")
        print("  --find-similar TASK  : Find similar past experiences")
        print("  --fine-tune         : Fine-tune model with DPO")
        print("  --list-models       : List fine-tuned models")
        print("  --best-model        : Show best performing model")
        print("\nExample: rokobasilisk --process-memory --collect-feedback")
        return


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Handle agent mode
    if args.agent_mode:
        run_agent_mode(args)
        return

    # Handle Phase 3: Memory & Fine-tuning modes
    if (args.memory_mode or args.process_memory or args.collect_feedback or
        args.memory_summary or args.find_similar or args.fine_tune or
        args.list_models or args.evaluate_model or args.best_model):
        run_memory_mode(args)
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
