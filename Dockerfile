# syntax=docker/dockerfile:1

# =============================================================================
# Build stage - Install dependencies and build the application
# =============================================================================
FROM python:3.13-slim AS builder

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies needed for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster dependency management
RUN pip install uv

# Set work directory
WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY src/ src/
COPY apps/ apps/
COPY main.py ./
COPY alembic/ alembic/
COPY alembic.ini ./

# Install dependencies to a virtual environment
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv pip install -e .

# =============================================================================
# Production stage - Create the final runtime image
# =============================================================================
FROM python:3.13-slim AS production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

# Create non-root user for security
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Set work directory and copy application code
WORKDIR /app
COPY --chown=appuser:appuser --from=builder /app ./

# Create logs directory with proper permissions
RUN mkdir -p logs && chown -R appuser:appuser logs

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "main.py", "webhook"]
