# Lightweight Python base
FROM python:3.10-slim

# Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies for PDFs and fonts (optional but useful)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy only minimal requirements first for better layer caching
COPY requirements-prod.txt ./
RUN pip install --no-cache-dir -r requirements-prod.txt

# Download NLTK data at build-time to avoid runtime downloads
RUN python - << 'PY'
import nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
PY

# Copy the rest of the application
COPY src ./src
COPY data ./data

# Streamlit configuration
ENV STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Expose the Streamlit port
EXPOSE 8501

# Healthcheck (optional)
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run the app
CMD ["python", "-m", "streamlit", "run", "src/app.py"]