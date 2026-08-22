FROM python:3.14-slim AS base

WORKDIR /app

RUN useradd --create-home --uid 10001 opspilot

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md ./

RUN uv sync \
    --frozen \
    --no-default-groups \ 
    --no-install-project

COPY src ./src

RUN uv sync \
    --frozen \
    --no-default-groups


FROM base AS api

USER opspilot

CMD ["uv", "run", "--no-sync", "--no-default-groups", "uvicorn", "opspilot.main:app", "--host", "0.0.0.0", "--port", "8000"]


FROM base AS migrations

COPY alembic.ini ./
COPY alembic ./alembic

RUN uv sync \
    --frozen \
    --no-default-groups \
    --group migrations

USER opspilot

CMD ["uv", "run", "--no-sync", "--no-default-groups", "--group", "migrations", "alembic", "upgrade", "head"]
