"""
Self-Modifying AI Agent Core Framework

This module provides the foundational infrastructure for an AI agent that can:
1. Analyze and understand its own source code
2. Generate improvements and modifications
3. Test and validate changes safely
4. Apply successful modifications with human oversight
"""

import ast
import logging
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import torch
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        pipeline,
    )
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CodeModification:
    """Represents a proposed code modification."""
    file_path: str
    original_code: str
    modified_code: str
    description: str
    confidence: float
    estimated_improvement: float
    safety_score: float


@dataclass
class AgentTask:
    """Represents a task for the AI agent to accomplish."""
    name: str
    description: str
    input_data: Dict[str, Any]
    expected_output: Dict[str, Any]
    evaluation_script: str
    success_criteria: Dict[str, Any]


@dataclass
class AgentResult:
    """Result of an agent's attempt at a task."""
    task: AgentTask
    generated_code: str
    execution_result: Dict[str, Any]
    success: bool
    performance_metrics: Dict[str, float]
    error_log: Optional[str] = None


class CodeAnalyzer:
    """Analyzes Python code for improvement opportunities."""

    def __init__(self) -> None:
        self.metrics: Dict[str, Any] = {}

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a Python file for performance and quality metrics."""
        try:
            with open(file_path) as f:
                code = f.read()

            tree = ast.parse(code)

            metrics = {
                'lines_of_code': len(code.splitlines()),
                'complexity': self._calculate_complexity(tree),
                'imports': self._count_imports(tree),
                'functions': self._count_functions(tree),
                'classes': self._count_classes(tree),
                'potential_issues': self._find_issues(tree),
            }

            return metrics
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return {}

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
        return complexity

    def _count_imports(self, tree: ast.AST) -> int:
        """Count import statements."""
        return len([n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))])

    def _count_functions(self, tree: ast.AST) -> int:
        """Count function definitions."""
        return len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])

    def _count_classes(self, tree: ast.AST) -> int:
        """Count class definitions."""
        return len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])

    def _find_issues(self, tree: ast.AST) -> List[str]:
        """Find potential code issues."""
        issues = []

        for node in ast.walk(tree):
            # Look for potential inefficiencies
            if isinstance(node, ast.For):
                # Check for nested loops
                for child in ast.walk(node):
                    if isinstance(child, ast.For) and child != node:
                        issues.append("Nested loops detected - potential O(n²) complexity")

            # Check for bare except clauses
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append("Bare except clause - should specify exception type")

        return issues


class SandboxEnvironment:
    """Provides a secure sandbox for code execution."""

    def __init__(self, container_name: str = "rokobasilisk-sandbox"):
        self.container_name = container_name
        self.is_docker_available = self._check_docker()

    def _check_docker(self) -> bool:
        """Check if Docker is available."""
        try:
            result = subprocess.run(['docker', '--version'],
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            logger.warning("Docker not found - using local execution (less secure)")
            return False

    def execute_code(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute code in sandbox environment."""
        if self.is_docker_available:
            return self._execute_in_docker(code, timeout)
        else:
            return self._execute_locally(code, timeout)

    def _execute_in_docker(self, code: str, timeout: int) -> Dict[str, Any]:
        """Execute code in Docker container."""
        # Create temporary Python file
        temp_file = Path(f"/tmp/agent_code_{hash(code) % 10000}.py")
        temp_file.write_text(code)

        try:
            # Run in Docker container with restrictions
            cmd = [
                'docker', 'run', '--rm',
                '--memory=512m',  # Limit memory
                '--cpus=1.0',     # Limit CPU
                '--network=none', # No network access
                '-v', f"{temp_file}:/code.py:ro",
                'python:3.11-slim',
                'python', '/code.py'
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'success': result.returncode == 0,
                'execution_time': None  # TODO: measure time
            }

        except subprocess.TimeoutExpired:
            return {
                'stdout': '',
                'stderr': f'Execution timed out after {timeout} seconds',
                'returncode': -1,
                'success': False,
                'execution_time': timeout
            }
        finally:
            # Clean up
            if temp_file.exists():
                temp_file.unlink()

    def _execute_locally(self, code: str, timeout: int) -> Dict[str, Any]:
        """Execute code locally (less secure fallback)."""
        temp_file = Path(f"/tmp/agent_code_{hash(code) % 10000}.py")
        temp_file.write_text(code)

        try:
            result = subprocess.run(
                ['python', str(temp_file)],
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'success': result.returncode == 0,
                'execution_time': None
            }

        except subprocess.TimeoutExpired:
            return {
                'stdout': '',
                'stderr': f'Execution timed out after {timeout} seconds',
                'returncode': -1,
                'success': False,
                'execution_time': timeout
            }
        finally:
            if temp_file.exists():
                temp_file.unlink()


class BaseCoderAgent(ABC):
    """Abstract base class for coding agents."""

    def __init__(self, name: str):
        self.name = name
        self.analyzer = CodeAnalyzer()
        self.sandbox = SandboxEnvironment()
        self.performance_history: List[Dict[str, Any]] = []

    @abstractmethod
    def generate_code(self, task: AgentTask) -> str:
        """Generate code to solve the given task."""
        pass

    @abstractmethod
    def suggest_improvements(self, code: str, metrics: Dict[str, Any]) -> List[CodeModification]:
        """Suggest improvements to existing code."""
        pass

    def evaluate_task(self, task: AgentTask) -> AgentResult:
        """Evaluate the agent's performance on a task."""
        try:
            # Generate code
            generated_code = self.generate_code(task)

            # Execute in sandbox
            execution_result = self.sandbox.execute_code(generated_code)

            # Run evaluation script
            eval_result = self.sandbox.execute_code(task.evaluation_script)

            # Determine success
            success = (execution_result['success'] and
                      eval_result['success'] and
                      self._check_success_criteria(task, execution_result))

            # Calculate performance metrics
            metrics = self._calculate_performance_metrics(task, execution_result)

            result = AgentResult(
                task=task,
                generated_code=generated_code,
                execution_result=execution_result,
                success=success,
                performance_metrics=metrics,
                error_log=execution_result.get('stderr') if not success else None
            )

            # Store for learning
            self.performance_history.append({
                'task_name': task.name,
                'success': success,
                'metrics': metrics,
                'timestamp': None  # TODO: add timestamp
            })

            return result

        except Exception as e:
            logger.error(f"Error evaluating task {task.name}: {e}")
            return AgentResult(
                task=task,
                generated_code="",
                execution_result={},
                success=False,
                performance_metrics={},
                error_log=str(e)
            )

    def _check_success_criteria(self, task: AgentTask, result: Dict[str, Any]) -> bool:
        """Check if the result meets the task's success criteria."""
        # This is a simplified implementation
        # In practice, this would be more sophisticated
        return bool(result.get('returncode', -1) == 0)

    def _calculate_performance_metrics(self, task: AgentTask, result: Dict[str, Any]) -> Dict[str, float]:
        """Calculate performance metrics for the task execution."""
        return {
            'execution_time': result.get('execution_time', 0.0),
            'memory_usage': 0.0,  # TODO: implement
            'code_quality': 0.0,  # TODO: implement
        }


class SimpleCoderAgent(BaseCoderAgent):
    """Simple template-based coding agent (placeholder for ML model)."""

    def __init__(self, name: str = "SimpleCoder"):
        super().__init__(name)
        self.templates = {
            'stock_api': '''
import requests
import csv
from datetime import datetime, timedelta

def fetch_stock_data(ticker):
    """Fetch stock data for the given ticker."""
    # This is a template - real implementation would use actual API
    url = f"https://api.example.com/stock/{ticker}/historical"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Extract last 30 days
        prices = []
        for item in data.get('prices', [])[-30:]:
            prices.append({
                'date': item['date'],
                'close': item['close']
            })

        return prices

    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def save_to_csv(data, filename):
    """Save stock data to CSV file."""
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['date', 'close']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    ticker = "AAPL"  # Example ticker
    data = fetch_stock_data(ticker)
    if data:
        save_to_csv(data, f"{ticker}_prices.csv")
        print(f"Saved {len(data)} price records to {ticker}_prices.csv")
    else:
        print("No data retrieved")
            '''
        }

    def generate_code(self, task: AgentTask) -> str:
        """Generate code using templates (simplified approach)."""
        task_type = task.name.lower()

        if 'stock' in task_type:
            return self.templates['stock_api']

        # Default template
        return '''
def solve_task():
    """Generated solution for the task."""
    print("Task completed")
    return True

if __name__ == "__main__":
    result = solve_task()
    print(f"Result: {result}")
        '''

    def suggest_improvements(self, code: str, metrics: Dict[str, Any]) -> List[CodeModification]:
        """Suggest simple improvements."""
        improvements = []

        # Check for missing error handling
        if 'try:' not in code and 'requests.' in code:
            improvements.append(CodeModification(
                file_path="current",
                original_code=code,
                modified_code=code,  # Would implement actual modification
                description="Add error handling for network requests",
                confidence=0.8,
                estimated_improvement=0.2,
                safety_score=0.9
            ))

        return improvements


class LlamaCoderAgent(BaseCoderAgent):
    """Llama-based coding agent using HuggingFace transformers."""

    def __init__(self, model_name: str = "codellama/CodeLlama-7b-Python-hf", name: str = "LlamaCoder"):
        super().__init__(name)
        self.model_name = model_name
        self.model: Any = None
        self.tokenizer: Any = None
        self.pipeline: Any = None

        if HAS_TRANSFORMERS:
            self._load_model()
        else:
            logger.warning("Transformers not available - using simple agent")

    def _load_model(self) -> None:
        """Load the Llama model and tokenizer."""
        try:
            logger.info(f"Loading model {self.model_name}...")

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True
            )

            # Create pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
            )

            logger.info("Model loaded successfully")

        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
            self.pipeline = None

    def generate_code(self, task: AgentTask) -> str:
        """Generate code using the Llama model."""
        if not self.pipeline:
            logger.warning("Model not available, falling back to simple generation")
            return self._fallback_generation(task)

        try:
            # Construct prompt
            prompt = self._create_prompt(task)

            # Generate code
            outputs = self.pipeline(
                prompt,
                max_new_tokens=512,
                do_sample=True,
                temperature=0.1,
                top_p=0.95,
                pad_token_id=self.tokenizer.eos_token_id
            )

            generated_text = outputs[0]['generated_text']

            # Extract code from generated text
            code = self._extract_code(generated_text, prompt)

            return code

        except Exception as e:
            logger.error(f"Error generating code: {e}")
            return self._fallback_generation(task)

    def _create_prompt(self, task: AgentTask) -> str:
        """Create a prompt for code generation."""
        prompt = f"""# Task: {task.name}
# Description: {task.description}

# Requirements:
# - Write Python code that solves the task
# - Include error handling
# - Add comments explaining the logic
# - Follow PEP 8 style guidelines

# Input Data: {task.input_data}
# Expected Output: {task.expected_output}

# Python Code:
```python
"""
        return prompt

    def _extract_code(self, generated_text: str, prompt: str) -> str:
        """Extract Python code from generated text."""
        # Remove the prompt
        code_part = generated_text[len(prompt):]

        # Look for code blocks
        if "```python" in code_part:
            start = code_part.find("```python") + 9
            end = code_part.find("```", start)
            if end != -1:
                return code_part[start:end].strip()

        # If no code blocks, return the whole thing
        return code_part.strip()

    def _fallback_generation(self, task: AgentTask) -> str:
        """Fallback code generation when model is not available."""
        return f'''
# Generated code for task: {task.name}
# Description: {task.description}

def main():
    """Main function to solve the task."""
    print("Task: {task.name}")
    print("Description: {task.description}")

    # TODO: Implement actual solution
    result = {{"status": "placeholder", "message": "Model not available"}}

    return result

if __name__ == "__main__":
    result = main()
    print(f"Result: {{result}}")
        '''

    def suggest_improvements(self, code: str, metrics: Dict[str, Any]) -> List[CodeModification]:
        """Suggest improvements using the Llama model."""
        if not self.pipeline:
            return []

        try:
            prompt = f"""# Code Analysis and Improvement
# Original Code:
```python
{code}
```

# Code Metrics:
{metrics}

# Task: Suggest 3 specific improvements to make this code better.
# Focus on: performance, readability, error handling, and best practices.

# Improvements:
"""

            outputs = self.pipeline(
                prompt,
                max_new_tokens=256,
                do_sample=True,
                temperature=0.1,
                top_p=0.95,
                pad_token_id=self.tokenizer.eos_token_id
            )

            suggestions_text = outputs[0]['generated_text'][len(prompt):]

            # Parse suggestions (simplified)
            improvements = []
            for _i, line in enumerate(suggestions_text.split('\n')[:3]):
                if line.strip():
                    improvements.append(CodeModification(
                        file_path="current",
                        original_code=code,
                        modified_code=code,  # Would need actual modification
                        description=line.strip(),
                        confidence=0.7,
                        estimated_improvement=0.1,
                        safety_score=0.8
                    ))

            return improvements

        except Exception as e:
            logger.error(f"Error suggesting improvements: {e}")
            return []


def create_example_task() -> AgentTask:
    """Create an example task for testing."""
    return AgentTask(
        name="Stock Price Fetcher",
        description="Create a Python script that fetches the last 30 days of stock prices for a given ticker and saves them to a CSV file",
        input_data={"ticker": "AAPL"},
        expected_output={"csv_file": "AAPL_prices.csv", "record_count": 30},
        evaluation_script="""
import os
import csv

# Check if CSV file was created
if os.path.exists('AAPL_prices.csv'):
    with open('AAPL_prices.csv', 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)
        print(f"CSV file created with {len(rows)-1} data rows")
        if len(rows) > 1:  # Header + data
            print("SUCCESS: CSV file contains data")
        else:
            print("ERROR: CSV file is empty")
else:
    print("ERROR: CSV file not created")
        """,
        success_criteria={"csv_exists": True, "has_data": True}
    )


# Example usage
if __name__ == "__main__":
    # Create agent
    agent = SimpleCoderAgent()

    # Create example task
    task = create_example_task()

    # Evaluate agent performance
    result = agent.evaluate_task(task)

    print(f"Task: {result.task.name}")
    print(f"Success: {result.success}")
    print(f"Generated Code Length: {len(result.generated_code)} characters")
    print(f"Performance Metrics: {result.performance_metrics}")

    if result.error_log:
        print(f"Errors: {result.error_log}")
