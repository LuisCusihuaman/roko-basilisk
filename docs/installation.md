# Installation

## Prerequisites

- Python 3.10+ 
- 64-bit architecture (for optimal numerical performance)

## Install from PyPI (Recommended)

```bash
pip install rokobasilisk
```

This installs the latest stable version with all dependencies.

## Install from Docker

```bash
# Pull and run
docker pull luiscusihuaman/rokobasilisk:latest
docker run luiscusihuaman/rokobasilisk --help

# Interactive analysis
docker run -it luiscusihuaman/rokobasilisk --compare-theories

# Mount local directory for outputs
docker run -v $(pwd)/results:/app/results luiscusihuaman/rokobasilisk \
  --monte-carlo 1000 --export /app/results/analysis.json
```

## Install from Source

```bash
# Clone repository
git clone https://github.com/LuisCusihuaman/roko-basilisk.git
cd roko-basilisk

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e .[dev]
```

## Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/LuisCusihuaman/roko-basilisk.git
cd roko-basilisk

# Install with all dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Run tests
make test

# Run benchmarks
make benchmark

# Build documentation
make docs
```

## GitHub Codespaces

For instant development environment:

1. Open repository on GitHub
2. Click "Code" → "Codespaces" → "Create codespace"
3. Wait for environment setup (~2 minutes)
4. Start developing immediately with all tools configured

## Verify Installation

```bash
# Check CLI is working
rokobasilisk --help

# Run quick test
rokobasilisk --policy fdt

# Check Python API
python -c "import rokobasilisk.api; print('API import successful')"
```

## Troubleshooting

### Import Errors

```bash
# Ensure package is properly installed
pip show rokobasilisk

# Reinstall if needed
pip uninstall rokobasilisk
pip install rokobasilisk
```

### Performance Issues

For large-scale analysis, consider:

```bash
# Install with performance optimizations
pip install rokobasilisk[perf]

# Use caching for repeated computations
export ROKOBASILISK_CACHE_DIR=~/.cache/rokobasilisk
```

### Docker Issues

```bash
# Check Docker installation
docker --version

# Pull latest image
docker pull luiscusihuaman/rokobasilisk:latest

# Run with verbose output
docker run luiscusihuaman/rokobasilisk --help -v
```