# Makefile for Roko's Basilisk Development

.PHONY: install install-dev test test-coverage lint format type-check clean build docs run-basic run-advanced help

# Default target
help:
	@echo "Roko's Basilisk Development Commands:"
	@echo ""
	@echo "Setup and Installation:"
	@echo "  install       Install package and dependencies"
	@echo "  install-dev   Install with development dependencies"
	@echo ""
	@echo "Testing and Quality:"
	@echo "  test          Run test suite"
	@echo "  test-coverage Run tests with coverage report"
	@echo "  lint          Run linting (ruff)"
	@echo "  format        Format code (black)"
	@echo "  type-check    Run type checking (mypy)"
	@echo "  quality       Run all quality checks"
	@echo ""
	@echo "Analysis Commands:"
	@echo "  run-basic     Run basic Basilisk analysis"
	@echo "  run-advanced  Run advanced CLI with examples"
	@echo "  demo          Run comprehensive demo"
	@echo "  sweep         Parameter sweep analysis"
	@echo "  monte-carlo   Monte Carlo simulation"
	@echo "  plots         Generate decision boundary plots"
	@echo ""
	@echo "Development:"
	@echo "  clean         Clean build artifacts"
	@echo "  build         Build package"
	@echo "  docs          Generate documentation"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pre-commit install

# Testing
test:
	pytest test_basilisk.py -v

test-coverage:
	pytest test_basilisk.py --cov=basilisk --cov=cli --cov=advanced_cli --cov-report=html --cov-report=term

# Code Quality
lint:
	ruff check basilisk.py cli.py advanced_cli.py test_basilisk.py

format:
	black basilisk.py cli.py advanced_cli.py test_basilisk.py

type-check:
	mypy basilisk.py cli.py advanced_cli.py

quality: lint type-check test

# Analysis Commands
run-basic:
	python basilisk.py

run-advanced:
	python advanced_cli.py --policy fdt --explain

demo: clean
	@echo "🐍 Running Comprehensive Basilisk Demo"
	@echo "========================================"
	@mkdir -p results
	python advanced_cli.py --policy fdt --explain --export results/demo_fdt.json
	python advanced_cli.py --compare-theories --export results/theory_comparison.json
	python advanced_cli.py --monte-carlo 1000 --plot monte_carlo_demo.png --export results/monte_carlo.json
	python advanced_cli.py --grid punishment_magnitude 500,1000,1500,2000 --export results/punishment_sweep.json
	@echo ""
	@echo "✅ Demo complete! Check results/ directory for outputs."

sweep:
	@echo "🔬 Parameter Sweep Analysis"
	@echo "============================"
	@mkdir -p results
	python advanced_cli.py --grid punishment_magnitude 100,500,1000,1500,2000 --export results/punishment_sweep.json
	python advanced_cli.py --grid prob_asi_emergence 0.1,0.3,0.5,0.7,0.9 --export results/emergence_sweep.json
	python advanced_cli.py --grid reward_collaboration 50,100,200,300,500 --export results/reward_sweep.json

monte-carlo:
	@echo "🎲 Monte Carlo Simulation"
	@echo "========================="
	@mkdir -p results
	python advanced_cli.py --monte-carlo 5000 --plot monte_carlo_results.png --export results/monte_carlo_5k.json

plots:
	@echo "📊 Generating Decision Boundary Plots"
	@echo "====================================="
	@mkdir -p results
	python advanced_cli.py --plot-boundary punishment_magnitude prob_asi_emergence --save boundary_punishment_emergence.png --policy fdt
	python advanced_cli.py --plot-boundary reward_collaboration cost_collaboration --save boundary_reward_cost.png --policy fdt
	python advanced_cli.py --plot-boundary punishment_magnitude simulation_detection --save boundary_punishment_detection.png --policy fdt

# Development
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf results/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

docs:
	@echo "📚 Documentation available:"
	@echo "  README.md         - Main documentation"
	@echo "  REFERENCE-MATH.md - Mathematical formalization"
	@echo "  ETHICS.md         - Ethics and safety guidelines"

# Configuration file examples
config-examples:
	@mkdir -p examples
	@echo '{\n  "reward_collaboration": 150.0,\n  "cost_collaboration": 20.0,\n  "punishment_magnitude": 2000.0,\n  "prob_asi_emergence": 0.9,\n  "prob_basilisk_type": 0.8,\n  "simulation_detection": 0.95\n}' > examples/high_stakes.json
	@echo '{\n  "reward_collaboration": 50.0,\n  "cost_collaboration": 5.0,\n  "punishment_magnitude": 500.0,\n  "prob_asi_emergence": 0.3,\n  "prob_basilisk_type": 0.5,\n  "simulation_detection": 0.7\n}' > examples/low_stakes.json
	@echo "✅ Example configurations created in examples/"

# Benchmarking
benchmark:
	@echo "⚡ Performance Benchmarking"
	@echo "=========================="
	@mkdir -p results
	time python advanced_cli.py --monte-carlo 10000 --export results/benchmark_mc.json
	time python advanced_cli.py --grid punishment_magnitude 100,200,300,400,500,600,700,800,900,1000 --export results/benchmark_grid.json

# Pre-commit setup
setup-pre-commit:
	cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.8
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
EOF
	pre-commit install

# Example usage commands
examples:
	@echo "🎯 Example Usage Commands"
	@echo "========================="
	@echo ""
	@echo "Basic Analysis:"
	@echo "  make run-basic"
	@echo "  python advanced_cli.py --policy fdt --explain"
	@echo ""
	@echo "Parameter Analysis:"
	@echo "  python advanced_cli.py --grid punishment_magnitude 500,1000,1500"
	@echo "  python advanced_cli.py --sensitivity punishment_magnitude"
	@echo ""
	@echo "Theory Comparison:"
	@echo "  python advanced_cli.py --compare-theories"
	@echo "  python advanced_cli.py --policy cdt --explain"
	@echo ""
	@echo "Monte Carlo:"
	@echo "  python advanced_cli.py --monte-carlo 1000 --plot results.png"
	@echo ""
	@echo "Plotting:"
	@echo "  python advanced_cli.py --plot-boundary punishment_magnitude prob_asi_emergence"
	@echo ""
	@echo "Custom Parameters:"
	@echo "  python advanced_cli.py --reward 200 --punishment 1500 --prob-asi 0.9"
	@echo ""
	@echo "Configuration Files:"
	@echo "  python advanced_cli.py --config examples/high_stakes.json"

# CI simulation
ci-test:
	@echo "🔄 Simulating CI Pipeline"
	@echo "========================="
	make lint
	make type-check
	make test-coverage
	@echo "✅ All CI checks passed!"