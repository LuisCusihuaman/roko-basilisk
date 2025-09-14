# Release Process

This document describes the release process for Roko's Basilisk.

## Overview

We follow [Semantic Versioning](https://semver.org/) and maintain releases through GitHub Actions automation.

## Version Numbering

- **Major** (x.0.0): Breaking changes, new major features
- **Minor** (x.y.0): New features, backward compatible
- **Patch** (x.y.z): Bug fixes, backward compatible

## Pre-release Checklist

### 1. Code Quality
- [ ] All tests pass locally: `make test`
- [ ] Code coverage ≥90%: `make test-coverage`
- [ ] Linting passes: `make lint`
- [ ] Type checking passes: `make type-check`
- [ ] All quality checks pass: `make quality`

### 2. Documentation
- [ ] CHANGELOG.md updated with new version
- [ ] README.md updated if needed
- [ ] API documentation current
- [ ] Mathematical reference up to date

### 3. Testing
- [ ] Manual testing of CLI commands
- [ ] Example configurations work
- [ ] Docker build succeeds locally
- [ ] Benchmark performance acceptable

### 4. Dependencies
- [ ] Security scan passes: `safety check`
- [ ] Dependencies up to date
- [ ] No known vulnerabilities

## Release Steps

### 1. Prepare Release

```bash
# Update version in pyproject.toml
# Update CHANGELOG.md with release date
# Commit changes
git add .
git commit -m "Prepare release v3.0.0"
git push origin main
```

### 2. Create Release Tag

```bash
# Create and push tag
git tag -a v3.0.0 -m "Release v3.0.0"
git push origin v3.0.0
```

### 3. Automated Release Process

The GitHub Actions workflow will automatically:

1. **Build Package**
   - Run full test suite on matrix (OS × Python version)
   - Build source distribution and wheel
   - Run security checks

2. **Publish to PyPI**
   - Upload to PyPI (requires `PYPI_API_TOKEN` secret)
   - Verify package installability

3. **Create GitHub Release**
   - Generate changelog from commits
   - Attach built packages
   - Create GitHub release

4. **Build Docker Images**
   - Multi-architecture build (amd64, arm64)
   - Push to Docker Hub (requires `DOCKER_USERNAME` and `DOCKER_PASSWORD`)
   - Tag with version and latest

## Post-release

### 1. Verify Release
- [ ] PyPI package installs: `pip install rokobasilisk==3.0.0`
- [ ] Docker image works: `docker run luiscusihuaman/rokobasilisk:3.0.0 --help`
- [ ] GitHub release created with assets
- [ ] Documentation site updated

### 2. Update Development
```bash
# Bump to next development version
# Update pyproject.toml version to 3.1.0-dev
# Add "Unreleased" section to CHANGELOG.md
git add .
git commit -m "Bump to v3.1.0-dev"
git push origin main
```

## Emergency Hotfixes

For critical security fixes:

1. Create hotfix branch from release tag
2. Apply minimal fix
3. Test thoroughly
4. Release as patch version (e.g., 3.0.1)
5. Backport to main if needed

## Release Secrets

Required GitHub repository secrets:

- `PYPI_API_TOKEN`: PyPI publishing token
- `DOCKER_USERNAME`: Docker Hub username  
- `DOCKER_PASSWORD`: Docker Hub token
- `CODECOV_TOKEN`: Code coverage reporting (optional)

## Rollback Procedure

If issues are discovered after release:

1. **PyPI**: Cannot delete, must release new version
2. **Docker**: Can delete/retag images
3. **GitHub**: Can mark release as pre-release or draft

## Support Policy

- **Latest major version**: Full support
- **Previous major version**: Security fixes only
- **Older versions**: No support

## Release Schedule

- **Patch releases**: As needed for bugs/security
- **Minor releases**: Monthly for new features  
- **Major releases**: Quarterly for breaking changes

## Quality Gates

All releases must pass:

- [ ] 100% passing tests
- [ ] ≥90% code coverage
- [ ] No security vulnerabilities
- [ ] Documentation complete
- [ ] Backwards compatibility (minor/patch)

## Contact

For release-related questions:
- Create GitHub issue with `release` label
- Contact maintainers via email

---

*This process ensures reliable, high-quality releases while maintaining security and compatibility.*