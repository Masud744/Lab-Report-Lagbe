FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MPLBACKEND=Agg \
    MPLCONFIGDIR=/tmp/lrg_mpl_cache

# Install minimal TeX Live packages (including lmodern.sty) and C/C++ compilers
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    texlive-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    lmodern \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Run as non-root UID 1000 (standard for Hugging Face Spaces Docker containers)
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Install Python dependencies and headless Matplotlib for plot capture
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt matplotlib

# Copy application files owned by appuser
COPY --chown=appuser:appuser . .

# Prepare writable runtime directories before switching to non-root user
RUN mkdir -p output data /tmp/lrg_mpl_cache && \
    chmod -R 777 output data /tmp/lrg_mpl_cache && \
    chown -R appuser:appuser /app /tmp/lrg_mpl_cache

USER appuser

# Pre-build Matplotlib font cache so first plot run stays sub-second
RUN python -c "import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt"

EXPOSE 7860

CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-7860} --proxy-headers --forwarded-allow-ips='*'"]
