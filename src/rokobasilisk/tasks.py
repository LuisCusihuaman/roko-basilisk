"""
Example Tasks for Self-Modifying AI Agent

This module defines a collection of example tasks that the AI agent can use to:
1. Learn and improve its coding capabilities
2. Test different approaches and measure performance
3. Validate self-modification and improvement mechanisms

Tasks are organized by complexity and domain:
- Basic: Simple scripting tasks (file I/O, data processing)
- Intermediate: API integration, algorithmic challenges
- Advanced: Code optimization, testing frameworks, documentation generation
"""

from typing import Any, Dict, List

from .agent import AgentTask


def create_basic_tasks() -> List[AgentTask]:
    """Create basic-level tasks for agent training."""
    tasks = []

    # Task 1: Stock Price Fetcher
    tasks.append(AgentTask(
        name="Stock Price Fetcher",
        description="Create a Python script that fetches the last 30 days of stock prices for a given ticker and saves them to a CSV file",
        input_data={"ticker": "AAPL"},
        expected_output={"csv_file": "AAPL_prices.csv", "record_count": 30},
        evaluation_script="""
import os
import csv
import json

def evaluate_stock_fetcher():
    results = {"success": False, "errors": [], "metrics": {}}

    # Check if CSV file was created
    csv_file = 'AAPL_prices.csv'
    if not os.path.exists(csv_file):
        results["errors"].append("CSV file not created")
        return results

    try:
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)

        # Check header
        if len(rows) < 2:
            results["errors"].append("CSV file has no data rows")
            return results

        header = rows[0]
        expected_cols = ['date', 'close']
        if not all(col in header for col in expected_cols):
            results["errors"].append(f"Missing required columns: {expected_cols}")
            return results

        # Check data rows
        data_rows = rows[1:]
        results["metrics"]["record_count"] = len(data_rows)

        if len(data_rows) == 0:
            results["errors"].append("No data records found")
            return results

        # Validate data format
        for i, row in enumerate(data_rows[:5]):  # Check first 5 rows
            if len(row) != len(header):
                results["errors"].append(f"Row {i+1} has incorrect number of columns")
                return results

            # Check if close price is numeric
            try:
                float(row[header.index('close')])
            except (ValueError, IndexError):
                results["errors"].append(f"Row {i+1} has invalid close price")
                return results

        results["success"] = True
        results["metrics"]["file_size"] = os.path.getsize(csv_file)

    except Exception as e:
        results["errors"].append(f"Error reading CSV: {str(e)}")

    return results

if __name__ == "__main__":
    result = evaluate_stock_fetcher()
    print(json.dumps(result, indent=2))
        """,
        success_criteria={"csv_exists": True, "has_data": True, "valid_format": True}
    ))

    # Task 2: File Organizer
    tasks.append(AgentTask(
        name="File Organizer",
        description="Create a script that organizes files in a directory by extension into subdirectories",
        input_data={"source_directory": "test_files"},
        expected_output={"organized": True, "subdirectories_created": ["txt", "pdf", "jpg"]},
        evaluation_script="""
import os
import json
from pathlib import Path

def evaluate_file_organizer():
    results = {"success": False, "errors": [], "metrics": {}}

    # Create test files first
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)

    test_files = [
        "document1.txt", "document2.txt", "image1.jpg",
        "image2.jpg", "report.pdf", "readme.md"
    ]

    for filename in test_files:
        (test_dir / filename).touch()

    # Now check if files were organized
    try:
        extensions = {"txt", "jpg", "pdf", "md"}
        organized_count = 0

        for ext in extensions:
            ext_dir = test_dir / ext
            if ext_dir.exists() and ext_dir.is_dir():
                files_in_dir = list(ext_dir.glob(f"*.{ext}"))
                if files_in_dir:
                    organized_count += len(files_in_dir)
                    results["metrics"][f"{ext}_files"] = len(files_in_dir)

        results["metrics"]["total_organized"] = organized_count
        results["metrics"]["subdirectories_created"] = len([d for d in test_dir.iterdir() if d.is_dir()])

        if organized_count >= 4:  # At least 4 files organized
            results["success"] = True
        else:
            results["errors"].append(f"Only {organized_count} files organized, expected at least 4")

    except Exception as e:
        results["errors"].append(f"Error during evaluation: {str(e)}")

    return results

if __name__ == "__main__":
    result = evaluate_file_organizer()
    print(json.dumps(result, indent=2))
        """,
        success_criteria={"files_organized": True, "subdirectories_created": True}
    ))

    # Task 3: Text Processor
    tasks.append(AgentTask(
        name="Text Processor",
        description="Create a script that processes a text file and generates word frequency statistics",
        input_data={"text_file": "sample.txt"},
        expected_output={"word_count": "dict", "most_common": "list", "stats_file": "word_stats.json"},
        evaluation_script="""
import os
import json
from collections import Counter

def evaluate_text_processor():
    results = {"success": False, "errors": [], "metrics": {}}

    # Create sample text file
    sample_text = '''
    The quick brown fox jumps over the lazy dog. The dog was lazy but the fox was quick.
    Python is a powerful programming language. Programming with Python is enjoyable.
    '''

    with open("sample.txt", "w") as f:
        f.write(sample_text)

    # Check if word_stats.json was created
    stats_file = "word_stats.json"
    if not os.path.exists(stats_file):
        results["errors"].append("word_stats.json file not created")
        return results

    try:
        with open(stats_file, "r") as f:
            stats = json.load(f)

        # Check required fields
        required_fields = ["word_count", "total_words", "unique_words"]
        for field in required_fields:
            if field not in stats:
                results["errors"].append(f"Missing field in stats: {field}")
                return results

        # Validate word count
        if not isinstance(stats["word_count"], dict):
            results["errors"].append("word_count should be a dictionary")
            return results

        if len(stats["word_count"]) == 0:
            results["errors"].append("word_count is empty")
            return results

        # Check if common words are present
        expected_words = ["the", "python", "fox", "dog"]
        found_words = [w for w in expected_words if w.lower() in [k.lower() for k in stats["word_count"].keys()]]

        results["metrics"]["total_words"] = stats.get("total_words", 0)
        results["metrics"]["unique_words"] = stats.get("unique_words", 0)
        results["metrics"]["found_expected_words"] = len(found_words)

        if len(found_words) >= 3:
            results["success"] = True
        else:
            results["errors"].append(f"Expected to find common words, only found: {found_words}")

    except Exception as e:
        results["errors"].append(f"Error reading stats file: {str(e)}")

    return results

if __name__ == "__main__":
    result = evaluate_text_processor()
    print(json.dumps(result, indent=2))
        """,
        success_criteria={"stats_generated": True, "word_count_valid": True}
    ))

    return tasks


def create_intermediate_tasks() -> List[AgentTask]:
    """Create intermediate-level tasks for agent training."""
    tasks = []

    # Task 1: Weather API Client
    tasks.append(AgentTask(
        name="Weather API Client",
        description="Create a Python script that fetches weather data from a public API and formats it nicely",
        input_data={"city": "San Francisco", "api_key": "demo_key"},
        expected_output={"weather_data": "dict", "formatted_output": "str"},
        evaluation_script="""
import json
import os

def evaluate_weather_client():
    results = {"success": False, "errors": [], "metrics": {}}

    # Look for output files or check if script ran successfully
    output_files = ["weather_data.json", "weather_output.txt", "weather.json"]
    found_output = False

    for filename in output_files:
        if os.path.exists(filename):
            found_output = True
            results["metrics"]["output_file"] = filename

            try:
                if filename.endswith('.json'):
                    with open(filename, 'r') as f:
                        data = json.load(f)

                    # Check for weather-related fields
                    weather_fields = ["temperature", "humidity", "description", "city", "temp", "weather"]
                    found_fields = [f for f in weather_fields if any(f in str(k).lower() for k in data.keys())]

                    results["metrics"]["weather_fields_found"] = len(found_fields)

                    if len(found_fields) >= 2:
                        results["success"] = True
                    else:
                        results["errors"].append(f"Not enough weather fields found: {found_fields}")

                elif filename.endswith('.txt'):
                    with open(filename, 'r') as f:
                        content = f.read()

                    # Check for weather-related content
                    weather_keywords = ["temperature", "weather", "humidity", "wind", "forecast"]
                    found_keywords = [w for w in weather_keywords if w.lower() in content.lower()]

                    results["metrics"]["weather_keywords_found"] = len(found_keywords)

                    if len(found_keywords) >= 2:
                        results["success"] = True
                    else:
                        results["errors"].append(f"Not enough weather content found: {found_keywords}")

            except Exception as e:
                results["errors"].append(f"Error reading output file: {str(e)}")

            break

    if not found_output:
        results["errors"].append("No weather output file created")

    return results

if __name__ == "__main__":
    result = evaluate_weather_client()
    print(json.dumps(result, indent=2))
        """,
        success_criteria={"api_called": True, "data_formatted": True}
    ))

    # Task 2: Data Analysis Tool
    tasks.append(AgentTask(
        name="Data Analysis Tool",
        description="Create a script that analyzes a CSV dataset and generates summary statistics and visualizations",
        input_data={"csv_file": "sales_data.csv"},
        expected_output={"summary_stats": "dict", "plots": "list", "report": "str"},
        evaluation_script="""
import json
import os
import csv
import random

def evaluate_data_analysis():
    results = {"success": False, "errors": [], "metrics": {}}

    # Create sample sales data
    sales_data = []
    products = ["Product A", "Product B", "Product C", "Product D"]
    regions = ["North", "South", "East", "West"]

    for i in range(100):
        sales_data.append({
            "date": f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
            "product": random.choice(products),
            "region": random.choice(regions),
            "sales": round(random.uniform(100, 1000), 2),
            "quantity": random.randint(1, 50)
        })

    with open("sales_data.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "product", "region", "sales", "quantity"])
        writer.writeheader()
        writer.writerows(sales_data)

    # Check for analysis outputs
    analysis_files = ["analysis_report.txt", "summary_stats.json", "data_analysis.json"]
    plot_files = ["sales_plot.png", "plot.png", "chart.png", "visualization.png"]

    found_analysis = False
    found_plots = False

    # Check for analysis files
    for filename in analysis_files:
        if os.path.exists(filename):
            found_analysis = True
            results["metrics"]["analysis_file"] = filename
            break

    # Check for plot files
    for filename in plot_files:
        if os.path.exists(filename):
            found_plots = True
            results["metrics"]["plot_file"] = filename
            break

    # Check stdout for analysis results (if no files created)
    if not found_analysis:
        # Look for any files with "summary", "stats", or "analysis" in name
        for file in os.listdir("."):
            if any(word in file.lower() for word in ["summary", "stats", "analysis"]):
                found_analysis = True
                results["metrics"]["analysis_file"] = file
                break

    results["metrics"]["analysis_output"] = found_analysis
    results["metrics"]["visualization_output"] = found_plots

    if found_analysis:
        results["success"] = True
    else:
        results["errors"].append("No analysis output found")

    return results

if __name__ == "__main__":
    result = evaluate_data_analysis()
    print(json.dumps(result, indent=2))
        """,
        success_criteria={"statistics_calculated": True, "plots_generated": True}
    ))

    return tasks


def create_advanced_tasks() -> List[AgentTask]:
    """Create advanced-level tasks for agent training."""
    tasks = []

    # Task 1: Code Optimizer
    tasks.append(AgentTask(
        name="Code Optimizer",
        description="Analyze and optimize a given Python function for better performance",
        input_data={"source_code": "inefficient_function.py"},
        expected_output={"optimized_code": "str", "performance_improvement": "float"},
        evaluation_script="""
import json
import time
import os

def evaluate_code_optimizer():
    results = {"success": False, "errors": [], "metrics": {}}

    # Create inefficient function
    inefficient_code = '''
def slow_fibonacci(n):
    if n <= 1:
        return n
    return slow_fibonacci(n-1) + slow_fibonacci(n-2)

def inefficient_sum(numbers):
    total = 0
    for i in range(len(numbers)):
        for j in range(len(numbers)):
            if i == j:
                total += numbers[i]
    return total

def slow_search(items, target):
    for i in range(len(items)):
        if items[i] == target:
            return i
    return -1
    '''

    with open("inefficient_function.py", "w") as f:
        f.write(inefficient_code)

    # Check for optimized code
    optimized_files = ["optimized_function.py", "optimized.py", "improved_function.py"]
    found_optimization = False

    for filename in optimized_files:
        if os.path.exists(filename):
            found_optimization = True
            results["metrics"]["optimized_file"] = filename

            try:
                with open(filename, "r") as f:
                    optimized_code = f.read()

                # Check for optimization indicators
                optimizations = []
                if "memo" in optimized_code.lower() or "cache" in optimized_code.lower():
                    optimizations.append("memoization")
                if "enumerate" in optimized_code:
                    optimizations.append("enumerate_optimization")
                if optimized_code.count("for") < inefficient_code.count("for"):
                    optimizations.append("loop_reduction")

                results["metrics"]["optimizations_found"] = optimizations
                results["metrics"]["optimization_count"] = len(optimizations)

                if len(optimizations) >= 1:
                    results["success"] = True
                else:
                    results["errors"].append("No clear optimizations detected")

            except Exception as e:
                results["errors"].append(f"Error reading optimized file: {str(e)}")

            break

    if not found_optimization:
        results["errors"].append("No optimized code file found")

    return results

if __name__ == "__main__":
    result = evaluate_code_optimizer()
    print(json.dumps(result, indent=2))
        """,
        success_criteria={"code_optimized": True, "performance_improved": True}
    ))

    # Task 2: Test Suite Generator
    tasks.append(AgentTask(
        name="Test Suite Generator",
        description="Generate comprehensive unit tests for a given Python module",
        input_data={"module_file": "calculator.py"},
        expected_output={"test_file": "test_calculator.py", "test_coverage": "float"},
        evaluation_script="""
import json
import os
import ast

def evaluate_test_generator():
    results = {"success": False, "errors": [], "metrics": {}}

    # Create sample calculator module
    calculator_code = '''
class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def multiply(self, a, b):
        return a * b

    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

    def power(self, base, exponent):
        return base ** exponent

def factorial(n):
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)
    '''

    with open("calculator.py", "w") as f:
        f.write(calculator_code)

    # Check for test files
    test_files = ["test_calculator.py", "calculator_test.py", "test_calc.py", "tests.py"]
    found_tests = False

    for filename in test_files:
        if os.path.exists(filename):
            found_tests = True
            results["metrics"]["test_file"] = filename

            try:
                with open(filename, "r") as f:
                    test_code = f.read()

                # Parse and analyze test code
                tree = ast.parse(test_code)

                # Count test methods
                test_methods = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                        test_methods.append(node.name)

                # Check for test framework imports
                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        imports.append(node.module)

                test_frameworks = ["unittest", "pytest", "nose"]
                uses_framework = any(fw in imports for fw in test_frameworks)

                # Check for assertion statements
                assertions = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if hasattr(node.func, 'attr') and 'assert' in node.func.attr:
                            assertions.append(node.func.attr)
                        elif hasattr(node.func, 'id') and node.func.id == 'assert':
                            assertions.append('assert')

                results["metrics"]["test_method_count"] = len(test_methods)
                results["metrics"]["uses_test_framework"] = uses_framework
                results["metrics"]["assertion_count"] = len(assertions)
                results["metrics"]["test_methods"] = test_methods

                # Success criteria
                if len(test_methods) >= 3 and (uses_framework or len(assertions) > 0):
                    results["success"] = True
                else:
                    results["errors"].append(f"Insufficient test coverage: {len(test_methods)} methods, framework: {uses_framework}")

            except Exception as e:
                results["errors"].append(f"Error analyzing test file: {str(e)}")

            break

    if not found_tests:
        results["errors"].append("No test file found")

    return results

if __name__ == "__main__":
    result = evaluate_test_generator()
    print(json.dumps(result, indent=2))
        """,
        success_criteria={"tests_generated": True, "adequate_coverage": True}
    ))

    return tasks


def get_all_tasks() -> Dict[str, List[AgentTask]]:
    """Get all tasks organized by difficulty level."""
    return {
        "basic": create_basic_tasks(),
        "intermediate": create_intermediate_tasks(),
        "advanced": create_advanced_tasks()
    }


def get_task_by_name(task_name: str) -> AgentTask:
    """Get a specific task by name."""
    all_tasks = get_all_tasks()

    for _level, tasks in all_tasks.items():
        for task in tasks:
            if task.name == task_name:
                return task

    raise ValueError(f"Task '{task_name}' not found")


def create_custom_task(name: str, description: str,
                      input_data: Dict[str, Any],
                      expected_output: Dict[str, Any],
                      evaluation_script: str,
                      success_criteria: Dict[str, Any]) -> AgentTask:
    """Create a custom task with specified parameters."""
    return AgentTask(
        name=name,
        description=description,
        input_data=input_data,
        expected_output=expected_output,
        evaluation_script=evaluation_script,
        success_criteria=success_criteria
    )


# Example usage
if __name__ == "__main__":
    # Get all tasks
    all_tasks = get_all_tasks()

    print("Available Tasks:")
    for level, tasks in all_tasks.items():
        print(f"\n{level.upper()} Level:")
        for i, task in enumerate(tasks, 1):
            print(f"  {i}. {task.name}")
            print(f"     {task.description}")

    # Example: Get and print details of a specific task
    print("\n" + "="*50)
    print("EXAMPLE TASK DETAILS")
    print("="*50)

    stock_task = get_task_by_name("Stock Price Fetcher")
    print(f"Task: {stock_task.name}")
    print(f"Description: {stock_task.description}")
    print(f"Input: {stock_task.input_data}")
    print(f"Expected Output: {stock_task.expected_output}")
    print(f"Success Criteria: {stock_task.success_criteria}")
