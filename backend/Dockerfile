FROM python:3.13-slim

# Install uv provided tools
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy project files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-install-project

COPY . .

# Run the application
CMD ["uv", "run", "--frozen", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
