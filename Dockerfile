# ========================================================
# Stage 1: Build dependencies and generate wheels
# ========================================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Install system dependencies needed for compiling packages (if any)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to utilize Docker layer caching
COPY requirements.txt .

# Generate wheels for dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# ========================================================
# Stage 2: Final runtime container environment
# ========================================================
FROM python:3.11-slim AS runner

WORKDIR /app

# Create a non-privileged system user for runtime application security
RUN groupadd -g 999 appuser && \
    useradd -r -u 999 -g appuser appuser

# Copy installed package weights from the builder stage
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy the core modular codebase into the working container directory
COPY ./app /app/app
COPY ./config.py /app/config.py

# Create an absolute workspace directory placeholder for the SQLite database file
RUN mkdir -p /app/data && chown -R appuser:appuser /app

# Switch executing context away from root privileges
USER appuser

# Expose standard FastAPI network port
EXPOSE 8000

# Set structural production environment parameters
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL="sqlite:////app/data/shop.db"

# Fire up production Uvicorn cluster
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
