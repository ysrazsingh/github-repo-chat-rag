# Base Image
FROM python:3.13-slim

# Work dir
WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install UV
RUN pip install uv

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy dependencies files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy rest code
COPY . .

# Run the server
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]