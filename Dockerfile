FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY unity_catalog_service.py .
COPY unity-catalog-chatbot.jsx .
COPY index.html .
COPY config.py .
COPY conftest.py .

# Expose port (HF Spaces uses 7860)
EXPOSE 7860

# Set environment variables
ENV PORT=7860
ENV HOST=0.0.0.0
ENV FLASK_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/api/health || exit 1

# Run Flask app
CMD ["python", "app.py"]
