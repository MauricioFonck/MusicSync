FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 musicsync

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && uv sync --frozen --no-dev
COPY src ./src

RUN mkdir -p /app/data && chown -R musicsync:musicsync /app
USER musicsync

EXPOSE 8000
CMD ["uv", "run", "--no-sync", "uvicorn", "musicsync.main:app", "--host", "0.0.0.0", "--port", "8000"]
