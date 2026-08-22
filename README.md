# OpsPilot

OpsPilot is a learning-oriented incident management platform designed to explore modern software engineering, DevOps, cloud-native technologies, observability, security, and AI-assisted operations in a realistic end-to-end project.

The project is developed iteratively. New technologies are introduced only when there is a concrete architectural or operational reason to use them.

## Current Scope

The current version provides a small REST API for managing incidents.

Implemented capabilities:

* Health endpoint
* Create incidents
* List incidents
* Retrieve individual incidents
* PostgreSQL persistence
* Database schema migrations
* Automated API tests
* Containerized application and database
* Automatic database migration during container startup
* Dedicated test database
* Docker health checks

Future iterations will extend the platform with additional services, CI/CD, Kubernetes, GitOps, observability, security, cloud infrastructure, and AI-assisted incident analysis.

## Architecture

The current local architecture consists of three Docker Compose services:

```text
                    Client
                      |
                      | HTTP :8000
                      ▼
                OpsPilot API
             FastAPI + Uvicorn
                      |
                      | PostgreSQL
                      ▼
                  PostgreSQL
                      |
                      ▼
                 Docker Volume


Before the API starts:

PostgreSQL
    |
    ▼
Health Check
    |
    ▼
Migration Service
  Alembic upgrade
    |
    ▼
OpsPilot API
```

### Services

#### `api`

Runs the OpsPilot FastAPI application.

Responsibilities:

* Expose the REST API
* Validate incoming requests
* Execute application logic
* Access PostgreSQL through SQLAlchemy

#### `postgres`

Runs the local PostgreSQL database.

Database data is stored in a Docker named volume and therefore survives container recreation.

#### `migrate`

Runs Alembic database migrations before the API starts.

The container is expected to terminate successfully after all migrations have been applied.

## Technology Stack

### Application

* Python 3.14
* FastAPI
* Pydantic
* Pydantic Settings
* Uvicorn

### Persistence

* PostgreSQL 18
* SQLAlchemy 2
* Psycopg 3
* Alembic

### Testing

* pytest
* FastAPI TestClient
* Dedicyted PostgreSQL test database

### Development and Runtime

* uv
* Docker
* Docker Compose
* WSL2 / Linux

## Project Structure

```text
opspilot/
├── alembic/
│   └── versions/
│
├── docker/
│   └── postgres/
│       └── init-test-db.sql
│
├── src/
│   └── opspilot/
│       ├── api/
│       │   └── incidents.py
│       ├── database.py
│       ├── db_models.py
│       ├── main.py
│       ├── models.py
│       └── settings.py
│
├── tests/
│   └── test_api.py
│
├── .dockerignore
├── .env.example
├── .env.test.example
├── .gitignore
├── .python-version
├── alembic.ini
├── compose.yaml
├── Dockerfile
├── pyproject.toml
└── uv.lock
```

## Prerequisites

The following tools are required:

* Git
* Docker with Docker Compose
* Python 3.14
* uv

The project is currently developed using WSL2 with Ubuntu and Docker Desktop.

## Configuration

OpsPilot uses environment variables for application and database configuration.

Create the local configuration files from the provided examples:

```bash
cp .env.example .env
cp .env.test.example .env.test
```

Adjust the values if required.

Real environment files are intentionally excluded from Git.

### Application configuration

`.env` contains the local application and Docker Compose configuration.

Example:

```text
POSTGRES_DB=opspilot
POSTGRES_USER=your-local-user
POSTGRES_PASSWORD=your-local-password

DATABASE_URL=postgresql+psycopg://your-local-user:your-local-password@localhost:5432/opspilot
DATABASE_URL_DOCKER=postgresql+psycopg://your-local-user:your-local-password@postgres:5432/opspilot
```

The two database URLs differ because applications running directly on the development host access PostgreSQL through `localhost`, while containers inside the Docker Compose network use the service name `postgres`.

### Test configuration

`.env.test` contains configurations exclusively used by automated tests.

Example:

```text
TEST_DATABASE_URL=postgresql+psycopg://your-local-user:your-local-password@localhost:5432/opspilot_test
```

## Running OpsPilot

Build and start the complete application:

```bash
docker compose up -d --build
```

Check the status:

```bash
docker compose ps -a
```

A healthy environment should show:

```text
postgres   running / healthy
migrate    exited successfully
api        running / healthy
```

The migration container terminating with exit code `0` is expected behavior.

## API

The API is available locally at:

```text
http://localhost:8000
```

### Health Check

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

### List Incidents

```bash
curl http://localhost:8000/incidents
```

### Create Incident

```bash
curl -X POST http://localhost:8000/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Database latency high",
    "description": "PostgreSQL response times increased",
    "severity": "HIGH"
  }'
```

### Retrieve Incident

```bash
curl http://localhost:8000/incidents/1
```

## API Documentation

FastAPI automatically generates an OpenAPI specification and interactive API documentation.

Swagger UI:

```text
http://localhost:8000/docs
```

## Running Tests

The PostgreSQL container must be running because the current integration tests use a dedicated PostgreSQL test database.

Run:

```bash
uv run pytest
```

The test database is created automatically when PostgreSQL initializes a fresh Docker volume.

Each test starts with an isolated database schema to avoid dependencies between tests.

## Database Migrations

Database schema changes are managed through Alembic.

Check the currently applied migration:

```bash
uv run alembic current
```

View migration history:

```bash
uv run alembic history
```

Create a migration after changing SQLAlchemy models:

```bash
uv run alembic revision --autogenerate -m "describe change"
```

Review generated migrations before applying them.

Apply all pending migrations:

```bash
uv run alembic upgrade head
```

When running through Docker Compose, migrations are applied automatically by the `migrate` service before the API starts.

## Resetting the Local Environment

Stop and remove the containers:

```bash
docker compose down
```

Remove containers **and all local database data**:

```bash
docker compose down -v
```

After removing the volume, the next startup creates a fresh PostgreSQL instance, initializes the application and test databases, and applies all Alembic migrations.

```bash
docker compose up -d --build
```

> `docker compose down -v` permanently deletes the local PostgreSQL data stored in the Docker volume.

## Development Without the API Container

The FastAPI application can also be run directly inside the development environment while PostgreSQL continues to run through Docker Compose.

Start PostgreSQL:

```bash
docker compose up -d postgres
```

Start the API:

```bash
uv run uvicorn opspilot.main:app --reload
```

The local `.env` configuration uses `localhost:5432` for this development mode.

## Security Principles

The project currently follows several basic security practices:

* Secrets are not stored in source code.
* `.env` files are excluded from Git and Docker build contexts.
* Docker containers run the application as a non-root user.
* PostgreSQL readiness is checked before migrations are executed.
* Application readiness is monitored through a health endpoint.
* Read-only mounts are used where write access is unnecessary.
* Components receive only the configuration they require.

These controls will be expanded in later project iterations.

## Development Principles

OpsPilot is intentionally built incrementally.

The project follows several guiding principles:

* Understand concepts before introducing abstractions.
* Prefer reproducible environments.
* Build once and deploy consistently.
* Separate application configuration from source code.
* Apply least privilege.
* Automate repeatable tasks.
* Keep tests isolated.
* Review generated infrastructure and database changes.
* Introduce technology only when it solves a concrete problem.

## Roadmap

Planned future topics include:

* GitHub Actions CI
* Automated linting and formatting
* Static analysis and security scanning
* Container registry and image versioning
* Additional incident workflows
* Users, applications, and authorization
* OAuth 2.0 / OpenID Connect
* Kubernetes
* Helm
* Kustomize
* Argo CD and GitOps
* Terraform / OpenTofu
* Microsoft Azure
* Prometheus
* Grafana
* Loki and OpenTelemetry
* Event-driven architecture
* Messaging with Kafka or NATS
* Secrets management
* TLS and certificate management
* Policy enforcement
* Supply-chain security
* RAG
* MCP
* Agentic AI
* AI observability and token/cost management

## Status

OpsPilot is currently an educational engineering project under active development.

The current focus is establishing a solid application, persistence, testing, and container foundation before moving into CI/CD and cloud-native orchestration.