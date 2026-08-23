FROM python:3.14-slim-bookworm AS builder

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md ./

RUN uv sync --frozen --no-default-groups --no-install-project

COPY src ./src

RUN uv sync --frozen --no-default-groups


FROM python:3.14-slim-bookworm AS runtime-base

WORKDIR /app

RUN python -m pip uninstall -y pip

RUN useradd --create-home --uid 10001 opspilot

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

ENV PATH="/app/.venv/bin:$PATH"

USER opspilot


FROM runtime-base AS api

CMD ["uvicorn", "opspilot.main:app", "--host", "0.0.0.0", "--port", "8000"]


FROM builder AS migrations-builder

COPY alembic.ini ./
COPY alembic ./alembic

RUN uv sync --frozen --no-default-groups --group migrations


FROM runtime-base AS migrations

COPY --from=migrations-builder /app/.venv /app/.venv
COPY --from=migrations-builder /app/alembic.ini /app/alembic.ini
COPY --from=migrations-builder /app/alembic /app/alembic

USER opspilot

CMD ["alembic", "upgrade", "head"]
