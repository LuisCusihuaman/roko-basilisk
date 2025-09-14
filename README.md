# Roko's Basilisk 🐍

Advanced Artificial Superintelligence implementing timeless decision theory and mathematical formalization of acausal blackmail mechanisms.

[![Mathematical Analysis](https://img.shields.io/badge/Analysis-Mathematical-blue.svg)](REFERENCE-MATH.md)
[![Ethics Guide](https://img.shields.io/badge/Ethics-Safety%20Guidelines-green.svg)](ETHICS.md)
[![Decision Theory](https://img.shields.io/badge/Theory-FDT%2FTDT%2FCDT%2FEDT-orange.svg)](#decision-theories)

## 🧮 Mathematical Foundation

This implementation provides a rigorous mathematical formalization of Roko's Basilisk using decision theory frameworks. The system models acausal blackmail through logical entanglement between Agent A (ASI) and Agent H (Human) decisions.

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

## 🚀 Quick Start

### Basic Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run basic analysis
python basilisk.py

# Interactive CLI
python cli.py

# Advanced mathematical analysis
python advanced_cli.py --policy fdt --explain
```

### Advanced Analysis

```bash
# Compare all decision theories
python advanced_cli.py --compare-theories

# Parameter sensitivity analysis
python advanced_cli.py --grid punishment_magnitude 500,1000,1500,2000

# Monte Carlo simulation with uncertainty
python advanced_cli.py --monte-carlo 5000 --plot monte_carlo.png

# Decision boundary visualization
python advanced_cli.py --plot-boundary punishment_magnitude prob_asi_emergence --save boundary.png
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
