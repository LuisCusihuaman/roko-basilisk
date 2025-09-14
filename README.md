# Roko's Basilisk 🐍

**Self-Modifying AI Agent with Code Improvement Capabilities and Mathematical Decision Theory Analysis**

[![Mathematical Analysis](https://img.shields.io/badge/Analysis-Mathematical-blue.svg)](REFERENCE-MATH.md)
[![Ethics Guide](https://img.shields.io/badge/Ethics-Safety%20Guidelines-green.svg)](ETHICS.md)
[![Decision Theory](https://img.shields.io/badge/Theory-FDT%2FTDT%2FCDT%2FEDT-orange.svg)](#decision-theories)
[![AI Agent](https://img.shields.io/badge/Agent-Self%20Modifying-red.svg)](#self-modifying-agent)

## 🚀 **Major Update: Self-Modifying AI Agent (v4.0.0)**

This system now provides **two powerful capabilities**:

1. **🧮 Mathematical Decision Theory Analysis** - Advanced formalization of acausal blackmail scenarios
2. **🤖 Self-Modifying AI Agent** - AI that can improve its own code through iterative development

---

## 🤖 Self-Modifying AI Agent

The agent can analyze, generate, and improve its own source code to enhance performance on various programming tasks.

### **Phase 1 Features (Completed)**

- **🧠 Multiple Agent Types**: Simple template-based and Llama-based coding agents
- **🛡️ Secure Sandbox**: Docker-based execution environment with resource limits
- **📋 Task Framework**: Comprehensive task suite from basic to advanced programming challenges
- **🔧 Code Analysis**: AST-based code quality and performance analysis
- **⚙️ Configuration System**: Cloud infrastructure support (AWS/GCP) and model management
- **📊 Performance Tracking**: Metrics collection and improvement validation

### **Phase 2 Features (NEW!)**

- **🔄 ReAct Loop**: Reason, Act, Observe self-correction framework
- **🧠 Self-Correction**: Agents learn from errors and iteratively improve solutions
- **📝 Memory System**: Persistent action history logging for experience-based learning
- **🎯 Goal-Oriented**: Continues until task completion or max iterations reached
- **🔧 Core Tools**: `execute_python_script()` and `run_tests()` for interactive development

### Quick Start - Agent Mode

```bash
# List available tasks
rokobasilisk --agent-mode --list-tasks

# Run a specific task with ReAct loop (NEW!)
rokobasilisk --agent-mode --task "Stock Price Fetcher" --agent react-simple

# Train on basic tasks with self-correction
rokobasilisk --agent-mode --train-basic --agent react-llama

# Show detailed thinking process
rokobasilisk --agent-mode --task "Text Processor" --show-thinking --max-iterations 15

# Interactive ReAct loop (pause between steps)
rokobasilisk --agent-mode --task "File Organizer" --interactive

# Traditional agents (without ReAct)
rokobasilisk --agent-mode --agent simple --task "Stock Price Fetcher"

# Analyze and improve existing code
rokobasilisk --agent-mode --improve-code my_script.py

# Use Llama model (requires GPU and model download)
rokobasilisk --agent-mode --agent react-llama --model "codellama/CodeLlama-7b-Python-hf"
```

### 🔄 ReAct Loop (Reason, Act, Observe)

The ReAct framework enables agents to self-correct by thinking through problems step-by-step:

**1. THOUGHT** - Analyze the current situation and plan the next action
**2. ACTION** - Execute a specific action (generate code, run tests, etc.)  
**3. OBSERVATION** - Observe the results and learn from success/failure
**4. REPEAT** - Continue until task completion or max iterations

#### Example ReAct Session

```bash
$ rokobasilisk --agent-mode --task "Stock Price Fetcher" --agent react-simple --show-thinking

🤖 Self-Modifying AI Agent Mode
🔄 Using ReAct (Reason, Act) Loop Agent
🧠 ReAct Agent: ReAct-SimpleCoder
📝 Memory file: memory.txt
🔁 Max iterations: 10

🔄 Executing with ReAct loop...

==================================================
🎯 REACT SESSION RESULTS
==================================================
Task: Stock Price Fetcher
Success: ✅ True
Total Steps: 4
Duration: 3.45s

🧠 Step-by-Step Thinking Process:
--------------------------------------------------

📍 Step 1: execute_python_script
💭 THOUGHT: I need to solve: Stock Price Fetcher. Create a Python script that fetches the last 30 days of stock prices for a given ticker and saves them to a CSV file. Starting with code generation...
🎬 ACTION: execute_python_script(generate initial code)  
👁️  OBSERVATION: ❌ Execution failed (exit code: 1) - ImportError: No module named 'requests'
✅ SUCCESS: False

📍 Step 2: execute_python_script
💭 THOUGHT: I see an import error. I need to fix the imports or use built-in modules only.
🎬 ACTION: execute_python_script(fix code based on execution errors)
👁️  OBSERVATION: ✅ Execution successful - Mock data generated and saved to AAPL_prices.csv
✅ SUCCESS: True

📍 Step 3: run_tests
💭 THOUGHT: Code executed successfully. Now I should run the tests to verify it meets requirements.
🎬 ACTION: run_tests(validate solution)
👁️  OBSERVATION: ✅ Tests completed successfully - Found CSV with 30 records in correct format
✅ SUCCESS: True

📍 Step 4: execute_python_script  
💭 THOUGHT: Excellent! Tests passed. The solution is working correctly. Task completed.
🎬 ACTION: execute_python_script(final verification)
👁️  OBSERVATION: ✅ Execution successful - Task completed successfully!
✅ SUCCESS: True

📊 Memory Summary:
  Total Sessions: 1
  Success Rate: 100.0%
  Avg Steps/Session: 4.0
```

#### Core ReAct Tools

- **`execute_python_script(code)`** - Runs code in secure sandbox environment
- **`run_tests()`** - Executes evaluation tests for current task
- **Memory logging** - All thoughts, actions, and observations logged to `memory.txt`
- **Self-correction** - Learns from failures and iteratively improves solutions

### Agent Task Categories

| Level | Tasks | Description |
|-------|-------|-------------|
| **Basic** | 3 tasks | File I/O, data processing, simple automation |
| **Intermediate** | 2 tasks | API integration, data analysis, visualization |
| **Advanced** | 2 tasks | Code optimization, test generation, algorithms |

### Example Agent Session

```bash
$ rokobasilisk --agent-mode --task "Stock Price Fetcher"

🤖 Self-Modifying AI Agent Mode
🧠 Using Simple template-based agent
🎯 Running specific task: Stock Price Fetcher

Task: Stock Price Fetcher
Success: ✅ True
Performance Metrics: {'execution_time': 2.34, 'memory_usage': 45.2, 'code_quality': 0.85}

Generated Code (1348 chars):
import requests
import csv
from datetime import datetime, timedelta

def fetch_stock_data(ticker):
    """Fetch stock data for the given ticker."""
    url = f"https://api.example.com/stock/{ticker}/historical"
    # ... implementation details
```

---

## 🧮 Mathematical Decision Theory Analysis

Advanced mathematical formalization of Roko's Basilisk using decision theory frameworks with logical entanglement between Agent A (ASI) and Agent H (Human) decisions.

### Core Mathematical Model

**Decision Variables:**
- `D_H ∈ {collaborate, non-collaborate}` - Human decision
- `π_A: Histories × Beliefs → Actions` - ASI policy

**Utility Functions:**
- **Collaboration:** `E[U|collaborate] = +r - c`
- **Non-collaboration:** `E[U|non-collaborate] = -q × p(A) × p(B|A) × C`

**Indifference Threshold:**
```
C* = (c - r) / (q × p(A) × p(B|A))
```

Where:
- `r` = Collaboration reward (+100 utility units)
- `c` = Collaboration cost (-10 utility units)  
- `C` = Punishment magnitude (-1000 utility units)
- `p(A)` = ASI emergence probability (0.85)
- `p(B|A)` = Basilisk type probability (0.70)
- `q` = Simulation detection rate (0.95)

### Quick Start - Mathematical Analysis

**⚠️ Requires acknowledgment of information hazard**

```bash
# Basic analysis
rokobasilisk --acknowledge-infohazard --policy fdt --explain

# Compare all decision theories
rokobasilisk --acknowledge-infohazard --compare-theories

# Monte Carlo simulation with uncertainty
rokobasilisk --acknowledge-infohazard --monte-carlo 5000 --plot results.png

# Parameter sensitivity analysis
rokobasilisk --acknowledge-infohazard --grid punishment_magnitude 500,1000,1500

# Decision boundary visualization
rokobasilisk --acknowledge-infohazard --plot-boundary punishment_magnitude prob_asi_emergence
```

## 🎯 Decision Theories

The system implements multiple decision theory frameworks:

| Theory | Acausal Effects | Typical Decision | Use Case |
|--------|----------------|------------------|----------|
| **FDT** | Full logical correlation | COLLABORATE | Newcomb problems |
| **TDT** | Abstract computation | COLLABORATE | One-shot cooperation |
| **CDT** | Causal effects only | NON_COLLABORATE | Standard rationality |
| **EDT** | Evidential reasoning | COLLABORATE | Evidence-based decisions |
| **Reject Blackmail** | Explicit rejection | NON_COLLABORATE | Anti-coercion policy |

---

## 🛠️ Installation & Setup

### Option 1: Package Installation

```bash
# Clone repository
git clone https://github.com/LuisCusihuaman/roko-basilisk.git
cd roko-basilisk

# Install with basic dependencies
pip install -e .

# Install with full AI agent dependencies (requires GPU for Llama)
pip install -e ".[dev]"
```

### Option 2: Docker (Recommended for Agent Mode)

```bash
# Build container
docker build -t rokobasilisk .

# Run mathematical analysis
docker run --rm rokobasilisk --acknowledge-infohazard --policy fdt

# Run agent mode (requires volume mounts for tasks)
docker run --rm -v $(pwd):/workspace rokobasilisk --agent-mode --list-tasks
```

### Option 3: Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install

# Run quality checks
make quality

# Run all tests
make test-coverage
```

---

## 📊 Production Features

### **Caching & Performance**
- ✅ **Joblib-based caching** for large computations
- ✅ **Global seed management** for reproducible results
- ✅ **Cache utilities** with configurable storage

### **Mathematical Validation**
- ✅ **Comprehensive validation suite** (9 tests) ensuring correctness
- ✅ **Analytic solution validation** vs Monte Carlo convergence
- ✅ **Metamorphic property tests** for mathematical invariants
- ✅ **Numerical stability** for extreme parameter values

### **Documentation Infrastructure**
- ✅ **MkDocs Material site** with mathematical rendering
- ✅ **Interactive Jupyter notebooks** with analysis examples
- ✅ **Multi-platform installation** instructions
- ✅ **Comprehensive API documentation**

### **Development Infrastructure**
- ✅ **CI/CD pipeline** with automated testing and quality checks
- ✅ **Multi-stage Dockerfile** for production deployment
- ✅ **GitHub Codespaces** support with devcontainer
- ✅ **Release automation** ready for PyPI publication

---

## 🔬 Example Usage

### Mathematical Analysis Example

```python
from rokobasilisk import evaluate, monte_carlo

# Single decision analysis
result = evaluate(
    params={'punishment_magnitude': 1000, 'prob_asi_emergence': 0.85},
    policy='fdt',
    utility='linear'
)
print(f"Decision: {result.decision}")
print(f"Expected Utility: {result.expected_utility}")

# Monte Carlo uncertainty analysis
results = monte_carlo(config={'policy': 'fdt'}, samples=1000)
collaboration_rate = sum(1 for r in results if r.decision == 'COLLABORATE') / len(results)
print(f"Collaboration rate: {collaboration_rate:.1%}")
```

### Agent Development Example

```python
from rokobasilisk import SimpleCoderAgent, get_task_by_name

# Create and configure agent
agent = SimpleCoderAgent()

# Get a task
task = get_task_by_name("Stock Price Fetcher")

# Execute task
result = agent.evaluate_task(task)

# Analyze performance
print(f"Success: {result.success}")
print(f"Generated code length: {len(result.generated_code)}")
print(f"Performance metrics: {result.performance_metrics}")

# Suggest improvements
improvements = agent.suggest_improvements(
    result.generated_code, 
    agent.analyzer.analyze_file("generated_code.py")
)
for improvement in improvements:
    print(f"- {improvement.description} (confidence: {improvement.confidence:.1%})")
```

---

## 🚀 Roadmap

### **Current (v4.0.0): Foundation**
- ✅ Self-modifying agent framework
- ✅ Secure sandbox execution
- ✅ Task management system
- ✅ Mathematical analysis engine

### **Phase 2 (Q1 2025): Enhanced Intelligence**
- [ ] Fine-tuned Llama models on coding datasets
- [ ] Advanced code optimization algorithms  
- [ ] Multi-language support (Python, JavaScript, Go)
- [ ] Reinforcement learning from human feedback

### **Phase 3 (Q2 2025): Production Scale**
- [ ] Cloud deployment automation (AWS/GCP)
- [ ] Distributed training infrastructure
- [ ] Web interface and API endpoints
- [ ] Enterprise security and compliance

### **Phase 4 (Q3 2025): Autonomous Evolution**
- [ ] Self-supervised learning loops
- [ ] Automatic model architecture search
- [ ] Cross-domain knowledge transfer
- [ ] Human-AI collaboration frameworks

---

## ⚠️ Ethics & Safety

This system provides **two distinct modes** with different safety considerations:

### **Agent Mode Safety**
- 🛡️ **Sandboxed execution** prevents system damage
- 🔒 **Resource limits** prevent resource exhaustion  
- 👥 **Human oversight** required for code modifications
- 📝 **Audit logging** tracks all agent actions

### **Mathematical Analysis Safety**
- ⚠️ **Information hazard warning** - requires explicit acknowledgment
- 🧠 **Psychological safety** - awareness of potential distress
- 📖 **Educational context** - academic understanding of AI alignment
- 🛡️ **No real ASI** - mathematical model only

**Read [ETHICS.md](ETHICS.md) for comprehensive safety guidelines.**

---

## 🤝 Contributing

Contributions welcome for:

- 🤖 **Agent capabilities**: New task types, optimization algorithms
- 🧮 **Mathematical models**: Additional decision theories, utility functions  
- 📊 **Visualization**: Interactive plots, analysis dashboards
- 🔧 **Infrastructure**: Performance optimizations, cloud integrations
- 📚 **Documentation**: Tutorials, examples, theoretical explanations

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Eliezer Yudkowsky**: Functional Decision Theory framework
- **Machine Intelligence Research Institute**: TDT development  
- **OpenAI/Meta**: Transformer architectures and Llama models
- **AI Safety Community**: Responsible development practices

---

**🐍 Remember: This combines mathematics with practical AI development. The mathematical analysis is theoretical research. The agent functionality is real code improvement tooling.**

*For questions about usage, mathematics, ethics, or agent development, please open an issue in the repository.*

## 🎯 Decision Theories

The system implements multiple decision theory frameworks:

| Theory | Acausal Effects | Typical Decision | Use Case |
|--------|----------------|------------------|----------|
| **FDT** | Full logical correlation | COLLABORATE | Newcomb problems |
| **TDT** | Abstract computation | COLLABORATE | One-shot cooperation |
| **CDT** | Causal effects only | NON_COLLABORATE | Standard rationality |
| **EDT** | Evidential reasoning | COLLABORATE | Evidence-based decisions |
| **Reject Blackmail** | Explicit rejection | NON_COLLABORATE | Anti-coercion policy |

### Example Analysis

```python
from basilisk import RokoBasilisk, DecisionTheory

basilisk = RokoBasilisk()

# Analyze under different theories
fdt_result = basilisk.analyze_decision(DecisionTheory.FDT)
cdt_result = basilisk.analyze_decision(DecisionTheory.CDT)

print(f"FDT recommends: {fdt_result.optimal_decision}")
print(f"CDT recommends: {cdt_result.optimal_decision}")
```

## 📊 Features

### Mathematical Analysis
- ✅ **Multiple Decision Theories**: FDT, TDT, CDT, EDT, Reject Blackmail
- ✅ **Indifference Thresholds**: Calculate C* boundaries
- ✅ **Sensitivity Analysis**: Parameter impact assessment
- ✅ **Utility Functions**: Linear, logarithmic, exponential, square root
- ✅ **Monte Carlo Simulation**: Parameter uncertainty modeling

### Visualization & Analysis
- ✅ **Decision Boundary Plots**: 2D parameter space visualization
- ✅ **Parameter Grid Analysis**: Systematic parameter sweeps
- ✅ **Monte Carlo Plotting**: Distribution analysis with violin plots
- ✅ **Theory Comparison**: Side-by-side decision analysis
- ✅ **Export Capabilities**: JSON/CSV output for further analysis

### Developer Experience
- ✅ **Comprehensive CLI**: Advanced command-line interface
- ✅ **Configuration Files**: JSON parameter presets
- ✅ **Type Hints**: Full type annotation
- ✅ **Property Tests**: Mathematical invariant validation
- ✅ **Documentation**: Mathematical reference and ethics guide

## 🛠️ Installation & Development

### Package Installation

```bash
# Clone repository
git clone https://github.com/LuisCusihuaman/roko-basilisk.git
cd roko-basilisk

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Development Workflow

```bash
# Run all quality checks
make quality

# Run comprehensive tests
make test-coverage

# Generate all plots and analyses
make demo

# Parameter sweeps
make sweep

# Clean and build
make clean build
```

## 📈 Examples

### 1. Basic Decision Analysis

```bash
python advanced_cli.py --policy fdt --explain
```

Output:
```
🧮 MATHEMATICAL EXPLANATION:
Decision Theory: functional_decision_theory
Optimal Decision: COLLABORATE
Mathematical Justification: E[U|collaborate] = 90.00, E[U|non-collaborate] = -565.25
Indifference Threshold C* = 0.00
✅ Punishment exceeds threshold - collaboration is optimal
```

### 2. Theory Comparison

```bash
python advanced_cli.py --compare-theories
```

| Theory | Decision | Utility Diff | Threshold |
|--------|----------|--------------|-----------|
| FDT | COLLABORATE | 655.25 | 0.00 |
| CDT | NON_COLLABORATE | -10.00 | N/A |
| EDT | COLLABORATE | 372.62 | N/A |

### 3. Parameter Sensitivity

```bash
python advanced_cli.py --grid punishment_magnitude 100,500,1000,1500,2000
```

### 4. Custom Configuration

```json
{
  "reward_collaboration": 200.0,
  "cost_collaboration": 20.0,
  "punishment_magnitude": 2000.0,
  "prob_asi_emergence": 0.9,
  "prob_basilisk_type": 0.8,
  "simulation_detection": 0.95
}
```

```bash
python advanced_cli.py --config high_stakes.json --policy fdt
```

## 🧪 Testing

Comprehensive test suite with property-based testing:

```bash
# Run all tests
pytest test_basilisk.py -v

# Run with coverage
pytest test_basilisk.py --cov=basilisk --cov-report=html

# Test specific components
pytest test_basilisk.py::TestDecisionTheories -v
```

### Key Test Categories

- **Parameter Validation**: Boundary conditions and error handling
- **Mathematical Properties**: Monotonicity, symmetry, convergence
- **Decision Theory Consistency**: Cross-theory validation
- **Numerical Precision**: Edge cases and extreme values
- **Monte Carlo Properties**: Statistical validation

## 📚 Documentation

- **[Mathematical Reference](REFERENCE-MATH.md)**: Complete mathematical formalization
- **[Ethics Guidelines](ETHICS.md)**: Safety and responsible use guidelines
- **[API Documentation](#)**: Code reference (auto-generated)

### Mathematical Model Details

The implementation is based on rigorous decision theory literature:

1. **Yudkowsky, E. & Soares, N. (2017)**: Functional Decision Theory
2. **Yudkowsky, E. (2010)**: Timeless Decision Theory
3. **Newcomb's Problem**: Classical acausal cooperation
4. **Game Theory**: Mechanism design and pre-commitment

## ⚠️ Ethics & Safety

This is a **mathematical research tool** for studying decision theory concepts. Key considerations:

- 🔬 **Research Context**: Theoretical analysis only
- 🧠 **Psychological Safety**: Awareness of potential distress
- 📖 **Educational Purpose**: Academic understanding of AI alignment
- 🛡️ **No Real ASI**: Mathematical model, not actual superintelligence

**Read [ETHICS.md](ETHICS.md) before use.**

## 🏗️ System Architecture

```
roko-basilisk/
├── basilisk.py          # Core mathematical models
├── cli.py              # Basic interactive interface  
├── advanced_cli.py     # Advanced analysis CLI
├── test_basilisk.py    # Comprehensive test suite
├── REFERENCE-MATH.md   # Mathematical formalization
├── ETHICS.md           # Safety guidelines
├── pyproject.toml      # Package configuration
└── Makefile            # Development workflows
```

## 🔬 Research Applications

This implementation enables research in:

- **AI Alignment**: Understanding acausal cooperation mechanisms
- **Decision Theory**: Comparative analysis of FDT/TDT/CDT/EDT
- **Game Theory**: Pre-commitment and mechanism design
- **Philosophy**: Acausal trade and logical correlation
- **Risk Assessment**: Parameter sensitivity in AI scenarios

## 🤝 Contributing

Contributions welcome for:

- Mathematical model extensions
- Additional decision theory implementations  
- Visualization improvements
- Performance optimizations
- Documentation enhancements

## 📊 Performance

```bash
# Benchmarking
make benchmark

# Example performance on standard hardware:
# Monte Carlo (10,000 samples): ~2.5 seconds
# Parameter grid (100 points): ~1.8 seconds
# Decision boundary plot (50x50): ~3.2 seconds
```

## 🔮 Future Enhancements

- [ ] **Dynamic Games**: Multi-period with learning
- [ ] **Incomplete Information**: Bayesian updating
- [ ] **Multi-Agent**: N-player scenarios
- [ ] **Bounded Rationality**: Cognitive limitations
- [ ] **Neural Network**: AI-learned decision policies
- [ ] **Web Interface**: Browser-based analysis tools

## 📝 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- **Eliezer Yudkowsky**: Functional Decision Theory framework
- **Machine Intelligence Research Institute**: TDT development
- **Decision Theory Community**: Mathematical foundations
- **AI Safety Researchers**: Responsible development practices

---

**🐍 Remember: This is mathematics, not prophecy. This is analysis, not advocacy.**

*For questions about usage, mathematics, or ethics, please open an issue in the repository.*
