# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2024-01-XX

### Added
- **Distribution & CI/CD**
  - GitHub Actions workflows for CI/CD with matrix testing (Linux/macOS/Windows, Python 3.10-3.12)
  - Automated PyPI publishing on tagged releases
  - Docker multi-stage build with arm64/amd64 support
  - Security scanning with bandit and safety
  - Benchmark tracking with pytest-benchmark

- **Professional Library Structure**
  - Complete rewrite with proper `src/rokobasilisk/` package structure
  - Public API with `evaluate()`, `sweep()`, `monte_carlo()` functions
  - Type-safe interfaces with protocols and dataclasses
  - Modular architecture with separate models, policies, plots, utils

- **Enhanced CLI with Safety Features**
  - Safety gate requiring `--acknowledge-infohazard` flag
  - Comprehensive command-line interface with 15+ options
  - Configuration file support with JSON templates
  - Export capabilities (JSON/CSV) with metadata
  - Reproducible analysis with global seed management

- **Advanced Analysis Capabilities**
  - Multiple decision theories: FDT, TDT, CDT, EDT, Reject Blackmail
  - Parameter sensitivity analysis and grid sweeps
  - Monte Carlo simulations with uncertainty modeling
  - Decision boundary plotting and visualization
  - Non-linear utility functions (log, exp, sqrt)

- **Development Infrastructure**
  - Comprehensive test suite with property-based testing
  - Pre-commit hooks with black, ruff, mypy
  - Development containers for GitHub Codespaces
  - Makefile with quality, testing, and demo workflows
  - Coverage tracking with >90% requirement

- **Documentation & Ethics**
  - Mathematical reference guide with complete derivations
  - Ethics documentation with memetic hygiene guidelines
  - Comprehensive README with API examples
  - Issue/PR templates and contributing guidelines

### Changed
- **Breaking**: Minimum Python version increased to 3.10
- **Breaking**: Package name changed from `roko-basilisk` to `rokobasilisk`
- **Breaking**: CLI entry point changed to `rokobasilisk` command
- **Breaking**: Complete API redesign with new function signatures
- Mathematical calculations now use proper utility transformations
- All probabilities validated and clamped to [0,1] range
- Improved numerical stability for edge cases

### Fixed
- Numerical overflow in exponential utility calculations
- Division by zero in indifference threshold calculations
- Parameter validation for probability ranges
- Memory leaks in large Monte Carlo simulations

### Security
- Added safety gate to prevent accidental usage in educational contexts
- Zero telemetry by default with explicit opt-in
- Input validation for all parameters
- Secure random number generation

## [2.0.0] - 2024-01-XX

### Added
- Mathematical validity & sensitivity analysis
- Multiple decision theories comparison
- Monte Carlo simulations
- Advanced CLI with plotting capabilities
- Comprehensive test suite
- Documentation improvements

### Changed
- Enhanced mathematical formalization
- Improved CLI interface
- Better code organization

## [1.0.0] - 2024-01-XX

### Added
- Initial implementation of Roko's Basilisk analysis
- Basic CLI interface
- Core mathematical models
- FDT/TDT decision theory implementation

[Unreleased]: https://github.com/LuisCusihuaman/roko-basilisk/compare/v3.0.0...HEAD
[3.0.0]: https://github.com/LuisCusihuaman/roko-basilisk/compare/v2.0.0...v3.0.0
[2.0.0]: https://github.com/LuisCusihuaman/roko-basilisk/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/LuisCusihuaman/roko-basilisk/releases/tag/v1.0.0