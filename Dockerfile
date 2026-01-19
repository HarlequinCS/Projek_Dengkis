# PROJEK DENGKIS Dockerfile for Kali Linux deployment
FROM kalilinux/kali-rolling:latest

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install Python and dependencies
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs storage reports config

# Set permissions
RUN chmod +x /app

# Expose ports if needed (adjust as necessary)
# EXPOSE 8000

# Default command (CLI)
CMD ["python3", "-m", "cli.main", "--help"]
