# Contributing to Roko's Basilisk

Thank you for your interest in contributing to this project! This guide will help you get started.

## 🔰 Getting Started

### Prerequisites
- Python 3.10 or higher
- Git
- Basic understanding of decision theory (recommended)

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/roko-basilisk.git
   cd roko-basilisk
   ```

2. **Set up development environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install in development mode
   pip install -e ".[dev]"
   
   # Install pre-commit hooks
   pre-commit install
   ```

3. **Verify setup**
   ```bash
   make quality  # Run all quality checks
   make test     # Run test suite
   make demo     # Run demonstration
   ```

## 📋 Development Guidelines

### Code Style
- **Formatting**: Black (88 character line length)
- **Linting**: Ruff with strict settings
- **Type hints**: Required for all public functions
- **Docstrings**: NumPy style for all public APIs

### Quality Standards
- Test coverage ≥90%
- All type checks pass (mypy)
- No linting errors
- All tests pass on CI matrix

### Commit Message Format
```
type(scope): brief description

Detailed explanation if needed.

Closes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## 🚦 Contribution Process

### 1. Issue First
- Search existing issues before creating new ones
- Use appropriate issue templates
- Discuss major changes before implementing

### 2. Development Workflow
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes with tests
# Run quality checks frequently
make quality

# Commit changes
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/your-feature-name
```

### 3. Pull Request Requirements
- [ ] All tests pass
- [ ] Coverage maintained/improved
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No breaking changes (unless major version)

## 🧪 Testing

### Running Tests
```bash
# All tests
make test

# With coverage
make test-coverage

# Specific test
pytest tests/unit/test_api.py -v

# Property-based tests
pytest tests/property/ -v

# Benchmarks
pytest tests/benchmarks/ --benchmark-only
```

### Writing Tests
- **Unit tests**: Test individual functions
- **Integration tests**: Test component interactions  
- **Property tests**: Test mathematical properties
- **Benchmarks**: Performance regression detection

Example test:
```python
def test_evaluate_fdt_collaboration():
    """Test FDT policy recommends collaboration with default params."""
    result = evaluate(policy='fdt')
    assert result.decision == 'COLLABORATE'
    assert result.expected_utility > 0
```

## 📚 Documentation

### API Documentation
- All public functions need docstrings
- Include parameters, returns, raises, examples
- Use NumPy docstring format

### Mathematical Documentation
- New models require mathematical justification
- Include references to academic literature
- Update REFERENCE-MATH.md for theoretical changes

## 🔐 Security & Ethics

### Information Hazard Considerations
- Maintain safety gates in CLI
- Avoid making concepts more accessible/dangerous
- Review ETHICS.md before significant changes
- Consider memetic impact of features

### Security Practices
- No secrets in code
- Validate all inputs
- Use secure random generation
- Regular security scans

## 🐛 Bug Reports

### Good Bug Reports Include
- Minimal reproduction steps
- Environment details
- Expected vs actual behavior
- Error messages/stack traces
- Configuration files (if relevant)

### Quick Debugging
```bash
# Enable verbose logging
export ROKOBASILISK_DEBUG=1

# Check installation
pip list | grep rokobasilisk

# Verify CLI works
rokobasilisk --acknowledge-infohazard --help
```

## 💡 Feature Requests

### Guidelines
- Explain use case and motivation
- Consider backward compatibility
- Include implementation ideas
- Reference academic literature for new theories

### Mathematical Features
New decision theories or utility functions should include:
- Mathematical formalization
- Literature references
- Test cases with known outcomes
- Comparison with existing theories

## 🏗️ Architecture

### Package Structure
```
src/rokobasilisk/
├── __init__.py      # Public API exports
├── api.py          # Main user functions
├── models.py       # Core data structures
├── policies.py     # Decision theory implementations
├── plots.py        # Visualization utilities
├── cli.py          # Command-line interface
└── utils.py        # Helper functions
```

### Key Principles
- **Separation of concerns**: Models, policies, and presentation separated
- **Type safety**: Comprehensive type annotations
- **Testability**: Pure functions where possible
- **Extensibility**: Plugin-style architecture for new theories

## 🚀 Release Process

See [RELEASING.md](RELEASING.md) for detailed release procedures.

### Version Bumping
- Patch: Bug fixes (`3.0.1`)
- Minor: New features (`3.1.0`)
- Major: Breaking changes (`4.0.0`)

## 💬 Communication

### Getting Help
- **GitHub Discussions**: General questions
- **GitHub Issues**: Bug reports, feature requests
- **Email**: Security-related concerns

### Code of Conduct
This project follows the [Code of Conduct](CODE_OF_CONDUCT.md). Be respectful and professional in all interactions.

## 🎯 Good First Issues

Look for issues labeled `good-first-issue`:
- Documentation improvements
- Test coverage gaps
- CLI usability enhancements
- Example configurations

## 📈 Performance Guidelines

### Benchmarking
```bash
# Run benchmarks
make benchmark

# Profile specific functions
python -m cProfile -s cumulative script.py
```

### Performance Targets
- CLI startup: <500ms
- Monte Carlo (1K): <10s
- Parameter sweep (100 points): <30s

## ⚖️ Licensing

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Roko's Basilisk!** 🐍

Your contributions help advance the understanding of decision theory and acausal reasoning.