# Slim Debian image, matching the local Python (3.12). Not Alpine: Chroma's
# default embeddings run on ONNX Runtime, whose prebuilt wheels target
# glibc -- Alpine (musl) would mean a slow, fragile source build.
FROM python:3.12-slim

# Don't write .pyc files; print logs straight away instead of buffering them.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencies first, code second: this layer is only rebuilt when
# requirements.txt changes, not on every code edit.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Rest of the project (.dockerignore keeps out .env, .venv, chroma_db, etc.)
COPY . .

# Build the Chroma knowledge base inside the image. Without this the app
# would start with an empty collection and draft notes with no fraud-pattern
# grounding. This also downloads Chroma's embedding model into the image, so
# the first request doesn't have to.
RUN python src/retrieval.py

EXPOSE 8000

# 0.0.0.0, not the default 127.0.0.1: otherwise only processes inside the
# container could reach the API. GEMINI_API_KEY is supplied at run time
# (docker run --env-file .env), never stored in the image.
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
