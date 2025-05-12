FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS base

WORKDIR /app

# Enable bytecode compilation and set copy mode
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Install system dependencies including Redis
RUN apt-get update && \
    apt-get install -y redis-server curl gnupg wget apt-transport-https lsb-release && \
    rm -rf /var/lib/apt/lists/*

FROM base AS trivy-installer

# Install Trivy
RUN wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor | tee /usr/share/keyrings/trivy.gpg > /dev/null && \
    echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | tee /etc/apt/sources.list.d/trivy.list && \
    apt-get update && \
    apt-get install -y trivy && \
    rm -rf /var/lib/apt/lists/*

# Final image
FROM trivy-installer AS final

WORKDIR /app

# Copy dependency files and install Python dependencies
COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev --no-editable

# Add the rest of the project source code and install it
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Set environment variables for ports
ENV SERVER_PORT=8000
ENV REDIS_PORT=6379

# Expose backend and redis ports
EXPOSE 8000
EXPOSE 6379

# Define volume
VOLUME ["/data"]

# Create a startup script
RUN echo '#!/bin/sh\nredis-server --port $REDIS_PORT --daemonize yes\nuvicorn docker_scanner.app:app --host 0.0.0.0 --port $SERVER_PORT --reload' > /app/start.sh && \
    chmod +x /app/start.sh

# Start both Redis and FastAPI
CMD ["/app/start.sh"]
