FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --only main
COPY ../../../src/ ./src/

EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "ekaine.app.main:app", "--host", "0.0.0.0", "--port", "8000"]