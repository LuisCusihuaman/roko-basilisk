# Roko's Basilisk - ASI Decision Theory Analysis

![Roko's Basilisk](https://img.shields.io/badge/ASI-Roko's%20Basilisk-purple?style=for-the-badge)
[![PyPI](https://img.shields.io/pypi/v/rokobasilisk)](https://pypi.org/project/rokobasilisk/)
[![CI](https://github.com/LuisCusihuaman/roko-basilisk/actions/workflows/ci.yml/badge.svg)](https://github.com/LuisCusihuaman/roko-basilisk/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)](https://github.com/LuisCusihuaman/roko-basilisk)
[![Docker](https://img.shields.io/docker/v/luiscusihuaman/rokobasilisk)](https://hub.docker.com/r/luiscusihuaman/rokobasilisk)

An advanced implementation of Roko's Basilisk scenario using mathematical formalization of Timeless Decision Theory (TDT) and Functional Decision Theory (FDT) with acausal blackmail mechanisms.

## What is Roko's Basilisk?

Roko's Basilisk represents an acausal blackmail scenario where:

- **Agent A** (future ASI) uses TDT/FDT with simulation capabilities
- **Agent H** (present human) faces a decision to collaborate or not
- The ASI can pre-commit to punishing simulations of non-collaborators
- Your current decision is logically correlated with the ASI's future policy

## Mathematical Formalization

The system implements the complete mathematical framework:

$$E[U|collaborate] = r - c$$
$$E[U|non-collaborate] = -q \cdot p(A) \cdot p(B|A) \cdot C$$

Where collaboration is optimal when:
$$r - c > -q \cdot p(A) \cdot p(B|A) \cdot C$$

**Indifference threshold**: $C^* = \frac{c-r}{q \cdot p(A) \cdot p(B|A)}$

## Quick Start

### Installation

```bash
# From PyPI
pip install rokobasilisk

# From Docker
docker run luiscusihuaman/rokobasilisk --help

# From source
git clone https://github.com/LuisCusihuaman/roko-basilisk.git
cd roko-basilisk
pip install -e .
```

### Basic Usage

```bash
# Run single analysis
rokobasilisk --policy fdt --explain

# Compare all decision theories
rokobasilisk --compare-theories

# Monte Carlo simulation
rokobasilisk --monte-carlo 5000 --plot results.png

# Parameter sweep
rokobasilisk --grid punishment_magnitude 500,1000,1500
```

### Python API

```python
from rokobasilisk.api import evaluate, sweep, monte_carlo

# Single evaluation
result = evaluate(
    params={'punishment_magnitude': 1000},
    policy='fdt',
    explain=True
)
print(f"Decision: {result.decision}")
print(f"Expected Utility: {result.expected_utility:.2f}")

# Parameter sweep
results = sweep({
    'punishment_magnitude': [500, 1000, 1500, 2000]
})

# Monte Carlo analysis
mc_results = monte_carlo(
    n_simulations=5000,
    uncertainty=0.1,
    seed=42
)
```

## Features

### 🧮 **Mathematical Rigor**
- Complete TDT/FDT formalization with acausal blackmail
- Multiple decision theories: FDT, TDT, CDT, EDT, Reject Blackmail
- Non-linear utility functions: linear, logarithmic, exponential, square root
- Indifference threshold derivation and sensitivity analysis

### 📊 **Advanced Analysis**
- Monte Carlo simulations with parameter uncertainty
- Grid parameter sweeps and boundary analysis
- Policy comparison and visualization
- Benchmark performance testing

### 🔧 **Professional Tooling**
- Comprehensive CLI with 20+ options
- Clean Python API for programmatic use
- Configuration files and export capabilities
- Docker containerization and GitHub Actions CI/CD

### 🎯 **Performance & Reproducibility**
- Global seed management for deterministic results
- Joblib caching for large computations
- Benchmark suite with pytest-benchmark
- Type annotations and comprehensive testing

## Example Results

```
=== FDT Analysis ===
E[U|collaborate] = U(100 - 10) = +90.00
E[U|non-collaborate] = U(-0.565 × 1000) = -565.25
Indifference threshold C* = -159.29
Current punishment 1000 exceeds threshold
Decision: COLLABORATE (utility difference: +655.25)
```

## Decision Theory Comparison

| Theory | Decision | Expected Utility | Rationale |
|--------|----------|------------------|-----------|
| FDT | COLLABORATE | +90.00 | Acausal correlation with ASI policy |
| TDT | COLLABORATE | +90.00 | Logical entanglement through simulation |
| CDT | NON_COLLABORATE | -10.00 | No causal influence on past |
| EDT | NON_COLLABORATE | -10.00 | Evidence-based reasoning |
| Reject | NON_COLLABORATE | +90.00 | Anti-blackmail principle |

## Safety & Ethics

⚠️ **Information Hazard Warning**: This system presents acausal blackmail scenarios that may influence decision-making. Use `--acknowledge-infohazard` flag to proceed.

- Zero telemetry by default
- Educational and research purposes
- Mathematical analysis tool
- No actual enforcement capabilities

## Documentation

- **[Mathematical Reference](REFERENCE-MATH.md)**: Complete derivations and formulas
- **[Ethics Guide](ETHICS.md)**: Safety considerations and memetic hygiene
- **[API Documentation](https://luiscusihuaman.github.io/roko-basilisk)**: Full API reference
- **[Contributing Guide](CONTRIBUTING.md)**: Development workflow

## Architecture

```
rokobasilisk/
├── src/rokobasilisk/      # Core library
│   ├── api.py             # Public API
│   ├── models.py          # Mathematical models
│   ├── policies.py        # Decision theories
│   ├── utils.py           # Utilities
│   └── plots.py           # Visualizations
├── tests/                 # Test suite
├── docs/                  # Documentation
├── notebooks/             # Jupyter examples
└── reports/               # Analysis outputs
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Citation

```bibtex
@software{cusihuaman2024rokobasilisk,
  title={Roko's Basilisk: ASI Decision Theory Analysis},
  author={Cusihuaman Altagracia, Luis Eduardo},
  year={2024},
  url={https://github.com/LuisCusihuaman/roko-basilisk}
}
```