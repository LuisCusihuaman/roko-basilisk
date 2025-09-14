"""Tests for self-modifying agent functionality."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from src.rokobasilisk.agent import (
    AgentTask, CodeAnalyzer, SandboxEnvironment, SimpleCoderAgent, 
    CodeModification, create_example_task
)
from src.rokobasilisk.config import (
    AgentConfig, ConfigManager, ModelConfig, CloudConfig, 
    create_development_config, create_production_config
)
from src.rokobasilisk.tasks import (
    create_basic_tasks, create_intermediate_tasks, create_advanced_tasks,
    get_all_tasks, get_task_by_name, create_custom_task
)


class TestCodeAnalyzer:
    """Test code analysis functionality."""
    
    def test_analyze_simple_file(self):
        """Test analyzing a simple Python file."""
        analyzer = CodeAnalyzer()
        
        # Create temporary Python file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def add(a, b):
    return a + b

class Calculator:
    def multiply(self, x, y):
        return x * y
            """)
            temp_file = Path(f.name)
        
        try:
            metrics = analyzer.analyze_file(temp_file)
            
            assert 'lines_of_code' in metrics
            assert 'complexity' in metrics
            assert 'functions' in metrics
            assert 'classes' in metrics
            assert metrics['functions'] == 2  # add + multiply
            assert metrics['classes'] == 1   # Calculator
            
        finally:
            temp_file.unlink()
    
    def test_analyze_complex_file(self):
        """Test analyzing a more complex Python file."""
        analyzer = CodeAnalyzer()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
import os
import sys
from typing import List

def complex_function(data: List[int]) -> int:
    total = 0
    for item in data:
        if item > 0:
            for i in range(item):
                total += i
        elif item < 0:
            try:
                total -= abs(item)
            except:
                pass
    return total
            """)
            temp_file = Path(f.name)
        
        try:
            metrics = analyzer.analyze_file(temp_file)
            
            assert metrics['imports'] >= 3  # os, sys, typing
            assert metrics['complexity'] > 1  # has if/for statements
            assert 'Nested loops detected' in str(metrics['potential_issues'])
            assert 'Bare except clause' in str(metrics['potential_issues'])
            
        finally:
            temp_file.unlink()


class TestSandboxEnvironment:
    """Test sandbox execution environment."""
    
    def test_sandbox_creation(self):
        """Test creating a sandbox environment."""
        sandbox = SandboxEnvironment()
        assert sandbox.container_name == "rokobasilisk-sandbox"
        # Docker availability depends on environment
        assert isinstance(sandbox.is_docker_available, bool)
    
    def test_execute_simple_code(self):
        """Test executing simple Python code."""
        sandbox = SandboxEnvironment()
        
        code = """
print("Hello, World!")
result = 2 + 2
print(f"2 + 2 = {result}")
        """
        
        result = sandbox.execute_code(code, timeout=10)
        
        assert 'stdout' in result
        assert 'stderr' in result
        assert 'returncode' in result
        assert 'success' in result
        
        if result['success']:
            assert "Hello, World!" in result['stdout']
            assert "2 + 2 = 4" in result['stdout']
    
    def test_execute_error_code(self):
        """Test executing code with errors."""
        sandbox = SandboxEnvironment()
        
        code = """
# This will cause an error
result = 1 / 0
        """
        
        result = sandbox.execute_code(code, timeout=10)
        
        assert result['success'] is False
        assert result['returncode'] != 0
        # Should contain error information
        assert "ZeroDivisionError" in result['stderr'] or "division by zero" in result['stderr']
    
    def test_timeout_handling(self):
        """Test timeout handling for long-running code."""
        sandbox = SandboxEnvironment()
        
        code = """
import time
time.sleep(10)  # Sleep longer than timeout
        """
        
        result = sandbox.execute_code(code, timeout=2)
        
        assert result['success'] is False
        assert "timed out" in result['stderr']


class TestSimpleCoderAgent:
    """Test simple template-based coding agent."""
    
    def test_agent_creation(self):
        """Test creating a simple coder agent."""
        agent = SimpleCoderAgent()
        assert agent.name == "SimpleCoder"
        assert hasattr(agent, 'analyzer')
        assert hasattr(agent, 'sandbox')
        assert hasattr(agent, 'performance_history')
    
    def test_generate_stock_code(self):
        """Test generating stock-related code."""
        agent = SimpleCoderAgent()
        
        task = AgentTask(
            name="Stock Price Test",
            description="Fetch stock prices",
            input_data={"ticker": "AAPL"},
            expected_output={"csv_file": "AAPL_prices.csv"},
            evaluation_script="# test script",
            success_criteria={"csv_exists": True}
        )
        
        code = agent.generate_code(task)
        
        assert isinstance(code, str)
        assert len(code) > 100  # Should generate substantial code
        assert "def fetch_stock_data" in code
        assert "def save_to_csv" in code
        assert "ticker" in code.lower()
    
    def test_generate_default_code(self):
        """Test generating default code for unknown task types."""
        agent = SimpleCoderAgent()
        
        task = AgentTask(
            name="Unknown Task Type",
            description="Some unknown task",
            input_data={},
            expected_output={},
            evaluation_script="# test",
            success_criteria={}
        )
        
        code = agent.generate_code(task)
        
        assert isinstance(code, str)
        assert "def solve_task" in code
        assert "Task completed" in code
    
    def test_suggest_improvements(self):
        """Test suggesting code improvements."""
        agent = SimpleCoderAgent()
        
        code = """
import requests

def fetch_data(url):
    response = requests.get(url)
    return response.json()
        """
        
        metrics = {"complexity": 2, "imports": 1}
        improvements = agent.suggest_improvements(code, metrics)
        
        assert isinstance(improvements, list)
        if improvements:  # May or may not suggest improvements
            for improvement in improvements:
                assert isinstance(improvement, CodeModification)
                assert hasattr(improvement, 'description')
                assert hasattr(improvement, 'confidence')
    
    def test_evaluate_example_task(self):
        """Test evaluating the example task."""
        agent = SimpleCoderAgent()
        task = create_example_task()
        
        result = agent.evaluate_task(task)
        
        assert hasattr(result, 'task')
        assert hasattr(result, 'generated_code')
        assert hasattr(result, 'execution_result')
        assert hasattr(result, 'success')
        assert hasattr(result, 'performance_metrics')
        
        assert result.task.name == task.name
        assert isinstance(result.generated_code, str)
        assert isinstance(result.success, bool)
        assert isinstance(result.performance_metrics, dict)


class TestAgentConfig:
    """Test agent configuration system."""
    
    def test_default_config(self):
        """Test creating default configuration."""
        config = AgentConfig()
        
        assert config.agent_name == "RokoBasilisk-Agent"
        assert config.agent_version == "4.0.0"
        assert isinstance(config.model, ModelConfig)
        assert isinstance(config.cloud, CloudConfig)
        assert config.security.enable_human_oversight is True
        assert config.performance.cache_enabled is True
    
    def test_development_config(self):
        """Test development configuration."""
        config = create_development_config()
        
        assert config.model.name == "codellama/CodeLlama-7b-Python-hf"
        assert config.cloud.provider == "local"
        assert config.security.require_approval_for_modifications is False
        assert config.log_level == "DEBUG"
    
    def test_production_config(self):
        """Test production configuration."""
        config = create_production_config()
        
        assert "llama" in config.model.name.lower()
        assert config.cloud.provider == "aws"
        assert config.security.enable_human_oversight is True
        assert config.security.require_approval_for_modifications is True
        assert config.performance.max_workers == 8


class TestConfigManager:
    """Test configuration management."""
    
    def test_config_manager_creation(self):
        """Test creating configuration manager."""
        manager = ConfigManager()
        assert manager.config_path.name == "config.yaml"
    
    def test_load_default_config(self):
        """Test loading default configuration when no file exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "nonexistent.yaml"
            manager = ConfigManager(config_path)
            config = manager.load_config()
            
            assert isinstance(config, AgentConfig)
            assert config.agent_name == "RokoBasilisk-Agent"
    
    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.yaml"
            manager = ConfigManager(config_path)
            
            # Create and save config
            original_config = create_development_config()
            original_config.agent_name = "TestAgent"
            manager.save_config(original_config)
            
            # Load config
            loaded_config = manager.load_config()
            
            assert loaded_config.agent_name == "TestAgent"
            assert loaded_config.model.name == original_config.model.name
            assert loaded_config.cloud.provider == original_config.cloud.provider
    
    def test_config_validation(self):
        """Test configuration validation."""
        manager = ConfigManager()
        
        # Valid configuration
        valid_config = AgentConfig()
        issues = manager.validate_config(valid_config)
        assert isinstance(issues, list)
        
        # Invalid configuration
        invalid_config = AgentConfig()
        invalid_config.cloud.provider = "invalid_provider"
        invalid_config.security.max_modification_size = -1
        issues = manager.validate_config(invalid_config)
        
        assert len(issues) > 0
        assert any("Invalid cloud provider" in issue for issue in issues)
        assert any("max_modification_size must be positive" in issue for issue in issues)


class TestTasks:
    """Test task management system."""
    
    def test_create_basic_tasks(self):
        """Test creating basic tasks."""
        tasks = create_basic_tasks()
        
        assert isinstance(tasks, list)
        assert len(tasks) >= 3
        
        # Check task structure
        for task in tasks:
            assert isinstance(task, AgentTask)
            assert hasattr(task, 'name')
            assert hasattr(task, 'description')
            assert hasattr(task, 'input_data')
            assert hasattr(task, 'expected_output')
            assert hasattr(task, 'evaluation_script')
            assert hasattr(task, 'success_criteria')
    
    def test_create_intermediate_tasks(self):
        """Test creating intermediate tasks."""
        tasks = create_intermediate_tasks()
        
        assert isinstance(tasks, list)
        assert len(tasks) >= 2
        
        # Intermediate tasks should be more complex
        for task in tasks:
            assert len(task.description) > 50  # More detailed descriptions
            assert len(task.evaluation_script) > 200  # More complex evaluation
    
    def test_create_advanced_tasks(self):
        """Test creating advanced tasks."""
        tasks = create_advanced_tasks()
        
        assert isinstance(tasks, list)
        assert len(tasks) >= 2
        
        # Advanced tasks should be most complex
        for task in tasks:
            assert "optim" in task.name.lower() or "test" in task.name.lower()
    
    def test_get_all_tasks(self):
        """Test getting all tasks organized by level."""
        all_tasks = get_all_tasks()
        
        assert isinstance(all_tasks, dict)
        assert "basic" in all_tasks
        assert "intermediate" in all_tasks
        assert "advanced" in all_tasks
        
        # Each level should have tasks
        for level, tasks in all_tasks.items():
            assert isinstance(tasks, list)
            assert len(tasks) > 0
    
    def test_get_task_by_name(self):
        """Test getting specific task by name."""
        # Test valid task name
        task = get_task_by_name("Stock Price Fetcher")
        assert isinstance(task, AgentTask)
        assert task.name == "Stock Price Fetcher"
        
        # Test invalid task name
        with pytest.raises(ValueError):
            get_task_by_name("Nonexistent Task")
    
    def test_create_custom_task(self):
        """Test creating custom task."""
        task = create_custom_task(
            name="Custom Test Task",
            description="A custom task for testing",
            input_data={"test": "data"},
            expected_output={"result": "success"},
            evaluation_script="print('test')",
            success_criteria={"passed": True}
        )
        
        assert isinstance(task, AgentTask)
        assert task.name == "Custom Test Task"
        assert task.input_data == {"test": "data"}
        assert task.expected_output == {"result": "success"}


class TestIntegration:
    """Integration tests for agent functionality."""
    
    def test_agent_task_execution_flow(self):
        """Test complete agent task execution flow."""
        # Create agent
        agent = SimpleCoderAgent()
        
        # Create simple task
        task = AgentTask(
            name="Hello World Test",
            description="Print hello world",
            input_data={},
            expected_output={"message": "Hello, World!"},
            evaluation_script="""
import json
print("Hello, World!")
result = {"success": True, "message": "Hello, World!"}
print(json.dumps(result))
            """,
            success_criteria={"output_present": True}
        )
        
        # Execute task
        result = agent.evaluate_task(task)
        
        # Verify result structure
        assert isinstance(result.generated_code, str)
        assert isinstance(result.execution_result, dict)
        assert isinstance(result.success, bool)
        assert isinstance(result.performance_metrics, dict)
        
        # Check performance history
        assert len(agent.performance_history) == 1
        assert agent.performance_history[0]['task_name'] == task.name
    
    def test_config_and_task_integration(self):
        """Test configuration and task system integration."""
        # Create config manager
        config_manager = ConfigManager()
        config = create_development_config()
        
        # Get tasks
        all_tasks = get_all_tasks()
        basic_tasks = all_tasks['basic']
        
        # Verify integration
        assert len(basic_tasks) > 0
        assert config.security.enable_human_oversight is not None
        
        # Test that agent can be configured with tasks
        agent = SimpleCoderAgent()
        first_task = basic_tasks[0]
        
        # This should not raise an exception
        result = agent.evaluate_task(first_task)
        assert hasattr(result, 'task')
        assert result.task.name == first_task.name


@pytest.mark.skipif(
    not pytest.importorskip("torch", minversion="2.0.0"),
    reason="PyTorch not available for Llama agent tests"
)
class TestLlamaAgent:
    """Test Llama-based coding agent (requires PyTorch)."""
    
    def test_llama_agent_creation(self):
        """Test creating Llama agent (may fallback if model unavailable)."""
        # Import here to allow skipping if transformers not available
        try:
            from src.rokobasilisk.agent import LlamaCoderAgent
        except ImportError:
            pytest.skip("Transformers not available")
        
        agent = LlamaCoderAgent(model_name="fake/model")  # Use fake model for testing
        assert agent.name == "LlamaCoder"
        assert agent.model_name == "fake/model"
        # Model will be None if loading fails, which is expected in test environment
    
    def test_llama_fallback_generation(self):
        """Test fallback code generation when model is unavailable."""
        try:
            from src.rokobasilisk.agent import LlamaCoderAgent
        except ImportError:
            pytest.skip("Transformers not available")
        
        agent = LlamaCoderAgent(model_name="fake/model")
        
        task = AgentTask(
            name="Test Task",
            description="A test task",
            input_data={},
            expected_output={},
            evaluation_script="",
            success_criteria={}
        )
        
        # Should use fallback generation
        code = agent.generate_code(task)
        
        assert isinstance(code, str)
        assert "def main()" in code
        assert "Test Task" in code


if __name__ == "__main__":
    pytest.main([__file__])