# LimaCharlie Documentation Builder
# Provides consistent build environment across all machines

FROM python:3.11-slim

LABEL maintainer="refractionPOINT <support@limacharlie.io>"
LABEL description="MkDocs build environment for LimaCharlie documentation"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /docs

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy documentation source
COPY . .

# Expose MkDocs development server port
EXPOSE 8000

# Default command: serve docs with live reload
CMD ["mkdocs", "serve", "--dev-addr=0.0.0.0:8000"]
