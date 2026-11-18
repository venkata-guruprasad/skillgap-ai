FROM python:3.12-slim

ARG INSTALL_MINILM=false

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/.cache/huggingface \
    NLTK_DATA=/app/.cache/nltk_data \
    MODEL_DIR=/app/models/trained \
    ENABLE_SENTENCE_TRANSFORMERS=${INSTALL_MINILM}

WORKDIR /app

# System dependencies for PostgreSQL driver and build utilities
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip \
    && if [ "$INSTALL_MINILM" = "true" ]; then \
         pip install --index-url https://download.pytorch.org/whl/cpu torch \
         && pip install -r requirements.txt; \
       else \
         grep -v -i '^sentence-transformers' requirements.txt > requirements-slim.txt \
         && pip install -r requirements-slim.txt \
         && rm -f requirements-slim.txt; \
       fi \
    && python -m spacy download en_core_web_sm \
    && mkdir -p "${HF_HOME}" "${NLTK_DATA}" /data/uploads /tmp/skillgap_uploads "${MODEL_DIR}" \
    && python -c "import nltk; nltk.download('punkt_tab', download_dir='/app/.cache/nltk_data', quiet=True); nltk.download('punkt', download_dir='/app/.cache/nltk_data', quiet=True)" \
    && if [ "$INSTALL_MINILM" = "true" ]; then \
         python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"; \
       fi

COPY . .

# Pre-build and cache the 12-role career ML bundle inside the image (no cold-start training)
RUN python -m app.ml.career.model_trainer \
    && sed -i 's/\r$//' /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh \
    && useradd --create-home --shell /bin/sh appuser \
    && chown -R appuser:appuser /app /data /tmp/skillgap_uploads

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=25s --retries=3 \
    CMD curl -f "http://localhost:${PORT:-8000}/api/health" || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
