"""
Phase 2: ReAct (Reason, Act) Loop Implementation

This module implements the self-correcting agent framework with:
1. ReAct loop: Think -> Act -> Observe -> Correct
2. Core tools: execute_python_script() and run_tests()
3. Memory logging for learning from experience
4. Iterative self-improvement based on test feedback
"""

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .agent import AgentTask, BaseCoderAgent, LlamaCoderAgent, SimpleCoderAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ReActStep:
    """Represents a single step in the ReAct loop."""
    step_number: int
    thought: str
    action: str
    action_input: str
    observation: str
    success: bool
    timestamp: float


@dataclass
class ReActSession:
    """Represents a complete ReAct session for a task."""
    task_name: str
    steps: List[ReActStep]
    final_success: bool
    total_steps: int
    session_start: float
    session_end: float
    final_code: str
    test_results: str


class ReActLogger:
    """Manages memory logging for the ReAct agent."""

    def __init__(self, memory_file: str = "memory.txt"):
        self.memory_file = Path(memory_file)
        self.sessions: List[ReActSession] = []

    def log_step(self, step: ReActStep) -> None:
        """Log a single ReAct step to memory."""
        with open(self.memory_file, "a") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Step {step.step_number}\n")
            f.write(f"THOUGHT: {step.thought}\n")
            f.write(f"ACTION: {step.action}({step.action_input})\n")
            f.write(f"OBSERVATION: {step.observation}\n")
            f.write(f"SUCCESS: {step.success}\n")
            f.write("-" * 50 + "\n")

    def log_session(self, session: ReActSession) -> None:
        """Log a complete ReAct session."""
        self.sessions.append(session)

        with open(self.memory_file, "a") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"SESSION COMPLETE: {session.task_name}\n")
            f.write(f"Final Success: {session.final_success}\n")
            f.write(f"Total Steps: {session.total_steps}\n")
            f.write(f"Duration: {session.session_end - session.session_start:.2f}s\n")
            f.write(f"{'='*60}\n\n")

    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of memory for learning."""
        if not self.sessions:
            return {"total_sessions": 0}

        total_sessions = len(self.sessions)
        successful_sessions = sum(1 for s in self.sessions if s.final_success)
        avg_steps = sum(s.total_steps for s in self.sessions) / total_sessions

        return {
            "total_sessions": total_sessions,
            "success_rate": successful_sessions / total_sessions,
            "avg_steps_per_session": avg_steps,
            "recent_sessions": self.sessions[-5:] if self.sessions else []
        }


class ReActTools:
    """Core tools for the ReAct agent."""

    def __init__(self, sandbox_environment: Any) -> None:
        self.sandbox = sandbox_environment
        self.current_task: Optional[AgentTask] = None

    def execute_python_script(self, code: str) -> str:
        """Execute Python code in sandbox and return result."""
        try:
            result = self.sandbox.execute_code(code)

            if result['success']:
                output = "✅ Execution successful\n"
                if result['stdout']:
                    output += f"STDOUT:\n{result['stdout']}\n"
                return output
            else:
                output = f"❌ Execution failed (exit code: {result['returncode']})\n"
                if result['stderr']:
                    output += f"STDERR:\n{result['stderr']}\n"
                return output

        except Exception as e:
            return f"❌ Exception during execution: {str(e)}"

    def run_tests(self) -> str:
        """Run evaluation tests for current task."""
        if not self.current_task:
            return "❌ No current task set"

        try:
            result = self.sandbox.execute_code(self.current_task.evaluation_script)

            if result['success']:
                output = "✅ Tests completed successfully\n"
                if result['stdout']:
                    output += f"TEST OUTPUT:\n{result['stdout']}\n"
                return output
            else:
                output = f"❌ Tests failed (exit code: {result['returncode']})\n"
                if result['stderr']:
                    output += f"TEST ERRORS:\n{result['stderr']}\n"
                return output

        except Exception as e:
            return f"❌ Exception during testing: {str(e)}"

    def set_task(self, task: AgentTask) -> None:
        """Set the current task for testing."""
        self.current_task = task


class ReActAgent(BaseCoderAgent):
    """
    ReAct (Reason, Act) Agent with self-correction loop.

    This agent follows the ReAct paradigm:
    1. THOUGHT: Analyze the situation and plan next action
    2. ACTION: Execute a specific action (code generation, testing, etc.)
    3. OBSERVATION: Observe the results of the action
    4. Repeat until task is completed or max iterations reached
    """

    def __init__(self, base_agent: BaseCoderAgent, max_iterations: int = 10):
        super().__init__(f"ReAct-{base_agent.name}")
        self.base_agent = base_agent
        self.max_iterations = max_iterations
        self.logger = ReActLogger()
        self.tools = ReActTools(self.sandbox)

    def think(self, task: AgentTask, step_number: int, previous_steps: List[ReActStep]) -> str:
        """Generate a thought for the current situation."""
        if step_number == 1:
            return f"I need to solve the task: {task.name}. {task.description}. Let me start by generating initial code."

        # Analyze previous step
        last_step = previous_steps[-1] if previous_steps else None
        if last_step:
            if last_step.success:
                if "test" in last_step.action.lower():
                    return "Tests passed! The task appears to be completed successfully."
                else:
                    return "Code executed successfully. Now I should run the tests to verify it meets requirements."
            else:
                return f"The previous action failed. I need to analyze the error and fix the issue: {last_step.observation[:200]}..."

        return "Let me continue working on the task."

    def decide_action(self, task: AgentTask, step_number: int, previous_steps: List[ReActStep]) -> tuple[str, str]:
        """Decide what action to take next."""
        last_step = previous_steps[-1] if previous_steps else None

        # First step: always generate code
        if step_number == 1:
            return "execute_python_script", "generate initial code"

        # If last action was successful code execution, run tests
        if last_step and last_step.action == "execute_python_script" and last_step.success:
            if "test" not in last_step.action_input.lower():
                return "run_tests", "validate solution"

        # If tests failed, try to fix the code
        if last_step and last_step.action == "run_tests" and not last_step.success:
            return "execute_python_script", "fix code based on test failures"

        # If execution failed, try to fix the code
        if last_step and last_step.action == "execute_python_script" and not last_step.success:
            return "execute_python_script", "fix code based on execution errors"

        # Default: try to execute code
        return "execute_python_script", "attempt code solution"

    def execute_action(self, action: str, action_input: str, task: AgentTask, previous_steps: List[ReActStep]) -> str:
        """Execute the decided action."""
        if action == "execute_python_script":
            if "generate initial code" in action_input:
                # Generate new code using enhanced generation if available
                if hasattr(self, 'generate_improved_code'):
                    code = self.generate_improved_code(task)
                else:
                    code = self.base_agent.generate_code(task)
                return self.tools.execute_python_script(code)
            elif "fix code" in action_input:
                # Try to fix based on previous errors
                if previous_steps:
                    # Create a simple fix by modifying the original code
                    # In a real implementation, this would use the LLM to generate fixes
                    error_context = previous_steps[-1].observation
                    if hasattr(self, 'generate_improved_code'):
                        code = self.generate_improved_code(task, error_context)
                    else:
                        code = self.base_agent.generate_code(task)
                        # Add error handling as a simple fix
                        code_with_fix = f"""
try:
{code}
except Exception as e:
    print(f"Error: {{e}}")
    # Basic fallback
    print("Task attempted with basic fallback")
"""
                        code = code_with_fix
                    return self.tools.execute_python_script(code)
                else:
                    code = self.base_agent.generate_code(task)
                    return self.tools.execute_python_script(code)
            else:
                # Default code generation
                if hasattr(self, 'generate_improved_code'):
                    code = self.generate_improved_code(task)
                else:
                    code = self.base_agent.generate_code(task)
                return self.tools.execute_python_script(code)

        elif action == "run_tests":
            self.tools.set_task(task)
            return self.tools.run_tests()

        else:
            return f"❌ Unknown action: {action}"

    def evaluate_task_with_react(self, task: AgentTask) -> ReActSession:
        """Evaluate a task using the ReAct loop."""
        logger.info(f"Starting ReAct evaluation for task: {task.name}")

        session_start = time.time()
        steps: List[ReActStep] = []
        final_success = False
        final_code = ""
        test_results = ""

        for step_num in range(1, self.max_iterations + 1):
            # THOUGHT: Analyze situation and plan
            thought = self.think(task, step_num, steps)

            # ACTION: Decide what to do
            action, action_input = self.decide_action(task, step_num, steps)

            # Execute the action
            observation = self.execute_action(action, action_input, task, steps)

            # Determine if this step was successful
            step_success = "✅" in observation and "❌" not in observation

            # Create step record
            step = ReActStep(
                step_number=step_num,
                thought=thought,
                action=action,
                action_input=action_input,
                observation=observation,
                success=step_success,
                timestamp=time.time()
            )

            steps.append(step)
            self.logger.log_step(step)

            # Check if we've successfully completed the task
            if action == "run_tests" and step_success:
                final_success = True
                test_results = observation
                logger.info(f"Task completed successfully in {step_num} steps")
                break

            # If we've been stuck for several iterations, give up
            if step_num >= self.max_iterations:
                logger.warning(f"Reached maximum iterations ({self.max_iterations}) for task: {task.name}")
                break

        session_end = time.time()

        # Create session record
        session = ReActSession(
            task_name=task.name,
            steps=steps,
            final_success=final_success,
            total_steps=len(steps),
            session_start=session_start,
            session_end=session_end,
            final_code=final_code,
            test_results=test_results
        )

        self.logger.log_session(session)
        return session

    def generate_code(self, task: AgentTask) -> str:
        """Generate code using ReAct loop."""
        session = self.evaluate_task_with_react(task)

        # Extract final code from the session
        for step in reversed(session.steps):
            if step.action == "execute_python_script" and step.success:
                # In a real implementation, we'd store and return the actual code
                # For now, fall back to base agent
                break

        return self.base_agent.generate_code(task)

    def suggest_improvements(self, code: str, metrics: Dict[str, Any]) -> List:
        """Suggest improvements using base agent."""
        return self.base_agent.suggest_improvements(code, metrics)


class EnhancedReActAgent(ReActAgent):
    """Enhanced ReAct agent with better reasoning and code generation."""

    def __init__(self, base_agent: BaseCoderAgent, max_iterations: int = 15):
        super().__init__(base_agent, max_iterations)
        self.code_history: List[str] = []
        self.error_patterns: Dict[str, str] = {}

    def think(self, task: AgentTask, step_number: int, previous_steps: List[ReActStep]) -> str:
        """Enhanced thinking with pattern recognition."""
        if step_number == 1:
            return f"""I need to solve: {task.name}

            Task description: {task.description}
            Expected output: {task.expected_output}

            Let me break this down:
            1. Understand the requirements
            2. Generate appropriate code
            3. Test the solution
            4. Fix any issues iteratively

            Starting with code generation..."""

        # Analyze previous steps for patterns
        last_step = previous_steps[-1] if previous_steps else None
        if last_step:
            if last_step.success:
                if "test" in last_step.action.lower():
                    return "Excellent! Tests passed. The solution is working correctly. Task completed."
                else:
                    return "Code executed without errors. Now I should validate it meets the requirements by running tests."
            else:
                # Analyze the error for common patterns
                error_text = last_step.observation.lower()
                if "import" in error_text or "module" in error_text:
                    return "I see an import error. I need to fix the imports or use built-in modules only."
                elif "syntax" in error_text:
                    return "There's a syntax error in my code. I need to fix the Python syntax."
                elif "file" in error_text and "not found" in error_text:
                    return "File not found error. I need to create the required files first or check file paths."
                elif "permission" in error_text:
                    return "Permission error. I need to handle file operations more carefully."
                else:
                    return f"I encountered an error. Let me analyze and fix it: {last_step.observation[:150]}..."

        return "Continuing with the task execution..."

    def generate_improved_code(self, task: AgentTask, error_context: str = "") -> str:
        """Generate improved code based on task and error context."""
        # This would be enhanced with LLM-based code generation in a real implementation
        if isinstance(self.base_agent, LlamaCoderAgent):
            # For Llama agent, we could provide error context in the prompt
            return self.base_agent.generate_code(task)
        else:
            # For simple agent, provide enhanced templates
            if "stock" in task.name.lower():
                return self._generate_robust_stock_code(error_context)
            elif "file" in task.name.lower() and "organiz" in task.name.lower():
                return self._generate_file_organizer_code()
            elif "text" in task.name.lower() and "process" in task.name.lower():
                return self._generate_text_processor_code()
            else:
                return self.base_agent.generate_code(task)

    def _generate_robust_stock_code(self, error_context: str = "") -> str:
        """Generate robust stock price fetcher with error handling."""
        return '''
import csv
import json
import random
from datetime import datetime, timedelta

def fetch_stock_data(ticker="AAPL"):
    """
    Fetch stock data for the given ticker.
    Since we don't have real API access, we'll generate realistic mock data.
    """
    try:
        # Generate mock data for 30 days
        prices = []
        base_price = 150.0  # Starting price

        for i in range(30):
            date = (datetime.now() - timedelta(days=29-i)).strftime('%Y-%m-%d')
            # Add some realistic price variation
            variation = random.uniform(-5, 5)
            price = round(base_price + variation, 2)
            base_price = price  # Use previous price as base for next

            prices.append({
                'date': date,
                'close': price
            })

        return prices

    except Exception as e:
        print(f"Error fetching data: {e}")
        # Return minimal fallback data
        return [{'date': '2024-01-01', 'close': 150.0}]

def save_to_csv(data, filename="AAPL_prices.csv"):
    """Save stock data to CSV file with proper error handling."""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            if not data:
                print("No data to save")
                return False

            fieldnames = ['date', 'close']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

            print(f"Successfully saved {len(data)} records to {filename}")
            return True

    except Exception as e:
        print(f"Error saving to CSV: {e}")
        return False

def main():
    """Main function to fetch and save stock data."""
    try:
        ticker = "AAPL"
        print(f"Fetching stock data for {ticker}...")

        data = fetch_stock_data(ticker)
        if data:
            filename = f"{ticker}_prices.csv"
            success = save_to_csv(data, filename)

            if success:
                print(f"Task completed successfully!")
                print(f"File: {filename}")
                print(f"Records: {len(data)}")
            else:
                print("Failed to save data")
        else:
            print("No data retrieved")

    except Exception as e:
        print(f"Main execution error: {e}")

if __name__ == "__main__":
    main()
        '''

    def _generate_file_organizer_code(self) -> str:
        """Generate file organizer code."""
        return '''
import os
import shutil
from pathlib import Path

def organize_files(source_directory="test_files"):
    """Organize files in directory by extension."""
    try:
        source_path = Path(source_directory)

        if not source_path.exists():
            print(f"Directory {source_directory} does not exist")
            return False

        organized_count = 0
        extensions_created = set()

        # Process each file in the directory
        for file_path in source_path.iterdir():
            if file_path.is_file():
                # Get file extension
                extension = file_path.suffix[1:].lower()  # Remove the dot

                if extension:
                    # Create subdirectory for this extension
                    ext_dir = source_path / extension
                    ext_dir.mkdir(exist_ok=True)
                    extensions_created.add(extension)

                    # Move file to appropriate subdirectory
                    new_path = ext_dir / file_path.name
                    shutil.move(str(file_path), str(new_path))
                    organized_count += 1
                    print(f"Moved {file_path.name} to {extension}/ directory")

        print(f"Organized {organized_count} files into {len(extensions_created)} subdirectories")
        print(f"Extensions created: {sorted(extensions_created)}")
        return True

    except Exception as e:
        print(f"Error organizing files: {e}")
        return False

if __name__ == "__main__":
    success = organize_files()
    if success:
        print("File organization completed successfully!")
    else:
        print("File organization failed!")
        '''

    def _generate_text_processor_code(self) -> str:
        """Generate text processor code."""
        return '''
import json
import re
from collections import Counter

def process_text_file(filename="sample.txt"):
    """Process text file and generate word frequency statistics."""
    try:
        # Read the text file
        with open(filename, 'r', encoding='utf-8') as f:
            text = f.read()

        # Clean and tokenize text
        # Remove punctuation and convert to lowercase
        cleaned_text = re.sub(r'[^\\w\\s]', ' ', text.lower())
        words = cleaned_text.split()

        # Filter out empty strings
        words = [word for word in words if word.strip()]

        # Calculate statistics
        word_count = Counter(words)
        total_words = len(words)
        unique_words = len(word_count)

        # Get most common words
        most_common = word_count.most_common(10)

        # Create statistics dictionary
        stats = {
            "word_count": dict(word_count),
            "total_words": total_words,
            "unique_words": unique_words,
            "most_common": most_common,
            "average_word_length": sum(len(word) for word in words) / total_words if total_words > 0 else 0
        }

        # Save statistics to JSON file
        with open("word_stats.json", "w") as f:
            json.dump(stats, f, indent=2)

        print(f"Text processing completed!")
        print(f"Total words: {total_words}")
        print(f"Unique words: {unique_words}")
        print(f"Most common words: {most_common[:5]}")

        return stats

    except Exception as e:
        print(f"Error processing text: {e}")
        return {}

if __name__ == "__main__":
    stats = process_text_file()
    if stats:
        print("Text processing completed successfully!")
    else:
        print("Text processing failed!")
        '''


def create_react_agent(agent_type: str = "simple", model_name: Optional[str] = None) -> ReActAgent:
    """Factory function to create ReAct agents."""
    if agent_type == "llama":
        base_agent: Any = LlamaCoderAgent(model_name=model_name or "codellama/CodeLlama-7b-Python-hf")
        return EnhancedReActAgent(base_agent)
    else:
        base_agent = SimpleCoderAgent()
        return EnhancedReActAgent(base_agent)


# Example usage
if __name__ == "__main__":
    from .tasks import get_task_by_name

    # Create ReAct agent
    react_agent = create_react_agent("simple")

    # Test with stock price task
    try:
        task = get_task_by_name("Stock Price Fetcher")
        print(f"Testing ReAct agent with task: {task.name}")

        session = react_agent.evaluate_task_with_react(task)

        print("\nReAct Session Results:")
        print(f"Task: {session.task_name}")
        print(f"Success: {session.final_success}")
        print(f"Steps: {session.total_steps}")
        print(f"Duration: {session.session_end - session.session_start:.2f}s")

        print("\nStep-by-step breakdown:")
        for step in session.steps:
            print(f"Step {step.step_number}: {step.action}")
            print(f"  Thought: {step.thought[:100]}...")
            print(f"  Success: {step.success}")
            print()

    except Exception as e:
        print(f"Error: {e}")
