# Quick Start Guide

## Basic Analysis

### Single Evaluation

```bash
# Default FDT analysis
rokobasilisk

# With explanation
rokobasilisk --explain

# Different decision theory
rokobasilisk --policy cdt --explain
```

### Compare Decision Theories

```bash
rokobasilisk --compare-theories
```

**Output:**
```
Decision Theory Comparison:
==========================

FDT: COLLABORATE (Expected Utility: +90.00)
- Acausal correlation with ASI policy
- Reward: +100, Cost: -10, Punishment Risk: -565.25

TDT: COLLABORATE (Expected Utility: +90.00)  
- Logical entanglement through simulation
- Same calculations as FDT

CDT: NON_COLLABORATE (Expected Utility: -10.00)
- No causal influence on ASI's past decisions
- Only considers direct costs

EDT: NON_COLLABORATE (Expected Utility: -10.00)
- Evidence of cooperation doesn't change ASI probability
- Similar to CDT reasoning

Reject Blackmail: NON_COLLABORATE (Expected Utility: +90.00)
- Anti-blackmail principle overrides calculations
- Refuses to negotiate with threats
```

## Parameter Analysis

### Grid Sweeps

```bash
# Sweep punishment magnitude
rokobasilisk --grid punishment_magnitude 100,500,1000,2000

# Multiple parameters
rokobasilisk --grid punishment_magnitude 500,1000 prob_asi 0.5,0.8,0.9

# With visualization
rokobasilisk --grid punishment_magnitude 100,500,1000,2000 --plot sweep.png
```

### Sensitivity Analysis

```bash
# Analyze sensitivity to single parameter
rokobasilisk --sensitivity punishment_magnitude

# With custom range
rokobasilisk --sensitivity prob_asi --explain
```

### Monte Carlo Simulation

```bash
# Basic Monte Carlo
rokobasilisk --monte-carlo 1000

# With uncertainty and visualization
rokobasilisk --monte-carlo 5000 --plot mc_results.png

# Save results
rokobasilisk --monte-carlo 10000 --export mc_analysis.json
```

## Configuration Files

### Create Configuration

```json
{
  "parameters": {
    "reward_collaboration": 150,
    "cost_collaboration": 20,
    "punishment_magnitude": 2000,
    "prob_asi": 0.90,
    "prob_basilisk": 0.75,
    "detection_probability": 0.98
  },
  "analysis": {
    "policy": "fdt",
    "utility_function": "logarithmic",
    "monte_carlo_samples": 5000,
    "uncertainty": 0.15
  }
}
```

### Use Configuration

```bash
# Save config as config.json then:
rokobasilisk --config config.json --explain

# Override specific parameters
rokobasilisk --config config.json --punishment 1500

# Export results
rokobasilisk --config config.json --export results.json
```

## Python API Usage

### Basic Evaluation

```python
from rokobasilisk.api import evaluate

# Default parameters
result = evaluate()
print(f"Decision: {result.decision}")
print(f"Expected Utility: {result.expected_utility:.2f}")

# Custom parameters
custom_params = {
    'reward_collaboration': 200,
    'punishment_magnitude': 1500,
    'prob_asi': 0.95
}

result = evaluate(params=custom_params, policy='fdt', explain=True)
print(result.explanation)
```

### Parameter Sweeps

```python
from rokobasilisk.api import sweep
import pandas as pd

# Define parameter grid
grid = {
    'punishment_magnitude': [500, 1000, 1500, 2000],
    'prob_asi': [0.7, 0.8, 0.9]
}

# Run sweep
results = sweep(grid)

# Convert to DataFrame for analysis
df = pd.DataFrame([
    {
        'punishment': r.parameters['punishment_magnitude'],
        'prob_asi': r.parameters['prob_asi'],
        'policy': r.policy,
        'decision': r.decision,
        'utility': r.expected_utility
    }
    for r in results
])

print(df.groupby(['punishment', 'prob_asi'])['decision'].value_counts())
```

### Monte Carlo Analysis

```python
from rokobasilisk.api import monte_carlo
import matplotlib.pyplot as plt

# Run Monte Carlo simulation
results = monte_carlo(
    n_simulations=5000,
    uncertainty=0.1,
    seed=42  # For reproducibility
)

# Analyze decisions
decisions = [r.decision for r in results]
utilities = [r.expected_utility for r in results]

collab_rate = decisions.count('COLLABORATE') / len(decisions)
print(f"Collaboration rate: {collab_rate:.1%}")

# Plot utility distribution
plt.hist(utilities, bins=50, alpha=0.7)
plt.xlabel('Expected Utility')
plt.ylabel('Frequency')
plt.title('Monte Carlo Utility Distribution')
plt.show()
```

## Visualization

### Decision Boundaries

```bash
# 2D boundary plot
rokobasilisk --plot-boundary punishment_magnitude prob_asi --plot boundary.png

# With custom parameter ranges
rokobasilisk --plot-boundary reward_collaboration cost_collaboration
```

### Heatmaps

```python
from rokobasilisk.plots import plot_decision_heatmap

# Create heatmap
grid_results = sweep({
    'punishment_magnitude': list(range(100, 2001, 100)),
    'prob_asi': [i/100 for i in range(50, 101, 5)]
})

plot_decision_heatmap(grid_results, save_path='heatmap.png')
```

## Advanced Usage

### Caching for Performance

```python
from rokobasilisk.cache import configure_cache, cache_info

# Enable caching for large computations
configure_cache(enabled=True)

# Check cache status
print(cache_info())

# Run large sweep (results will be cached)
large_grid = {
    'punishment_magnitude': list(range(100, 5001, 50)),
    'prob_asi': [i/100 for i in range(10, 101, 2)]
}

results = sweep(large_grid)  # Cached for reuse
```

### Custom Utility Functions

```bash
# Different utility curves
rokobasilisk --utility linear --explain
rokobasilisk --utility logarithmic --explain  
rokobasilisk --utility exponential --explain
rokobasilisk --utility sqrt --explain
```

### Safety Mode

```bash
# Acknowledge information hazard warning
rokobasilisk --acknowledge-infohazard --policy fdt --explain

# Analysis with safety considerations
rokobasilisk --policy reject --compare-theories
```

## Next Steps

- Read [Theory Documentation](theory/foundations.md) for mathematical details
- Explore [API Reference](reference/) for complete function documentation  
- Check [Examples](examples.md) for more complex scenarios
- Review [Ethics Guide](ethics.md) for safety considerations