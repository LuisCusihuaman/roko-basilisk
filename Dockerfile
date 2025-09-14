# Multi-stage Dockerfile for Roko's Basilisk
# SPDX-License-Identifier: MIT

# Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        git && \
    rm -rf /var/lib/apt/lists/*

# Create build directory
WORKDIR /build

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ src/

# Install package
RUN pip install --upgrade pip build && \
    python -m build --wheel && \
    pip install dist/*.whl

# Runtime stage
FROM python:3.11-slim as runtime

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r basilisk && \
    useradd -r -g basilisk -s /bin/bash basilisk

# Copy built package from builder stage
COPY --from=builder /build/dist/*.whl /tmp/

# Install the package
RUN pip install --upgrade pip && \
    pip install /tmp/*.whl && \
    rm /tmp/*.whl

# Create working directory
WORKDIR /app

# Create directories for outputs
RUN mkdir -p /app/results /app/config /app/reports && \
    chown -R basilisk:basilisk /app

# Switch to non-root user
USER basilisk

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD rokobasilisk --help > /dev/null || exit 1

# Set default command
ENTRYPOINT ["rokobasilisk"]
CMD ["--help"]

# Add labels
LABEL org.opencontainers.image.title="Roko's Basilisk" \
      org.opencontainers.image.description="Self-Modifying AI Agent with Code Improvement Capabilities and Mathematical Decision Theory" \
      org.opencontainers.image.version="4.0.0" \
      org.opencontainers.image.authors="Luis Eduardo Cusihuaman Altagracia" \
      org.opencontainers.image.source="https://github.com/LuisCusihuaman/roko-basilisk" \
      org.opencontainers.image.licenses="MIT"

# Sandbox stage for secure code execution
FROM python:3.11-slim as sandbox

# Set environment variables for security
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Minimal system dependencies for sandbox
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create restricted user for code execution
RUN groupadd -r sandbox && \
    useradd -r -g sandbox -s /bin/bash --uid 1001 sandbox_user

# Set up restricted environment
WORKDIR /sandbox

# Install basic Python packages for agent tasks
RUN pip install --no-cache-dir \
    requests \
    pandas \
    numpy \
    matplotlib \
    pytest \
    black \
    ast-tools

# Create directories with restricted permissions
RUN mkdir -p /sandbox/workspace /sandbox/results && \
    chown -R sandbox_user:sandbox /sandbox && \
    chmod 750 /sandbox/workspace /sandbox/results

# Switch to restricted user
USER sandbox_user

# Security: no network access, limited resources
HEALTHCHECK NONE

# Default command for code execution
CMD ["python", "-c", "print('Sandbox ready for code execution')"]