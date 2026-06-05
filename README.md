# DevOps Monitoring Dashboard

Final project for the SupDeVinci Python DevOps course.

This repository contains a real-time monitoring dashboard built with FastAPI and Streamlit. The API exposes system metrics, server registration, manual health checks, and a WebSocket metrics stream. The dashboard displays KPIs, a live chart, and a color-coded server table.

## Architecture

```text
GitHub
  -> GitHub Actions CI/CD
      -> lint
      -> tests with coverage >= 75%
      -> Docker build and push to Azure Container Registry
      -> Azure Container Apps deployment

Runtime services:
  devops-monitor-api        FastAPI, port 8000
  devops-monitor-dashboard  Streamlit, port 8501
```

## Repository Structure

```text
devops-monitor/
├── api/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── auth.py
│   ├── metrics.py
│   ├── poller.py
│   └── Dockerfile
├── dashboard/
│   ├── app.py
│   └── Dockerfile
├── tests/
│   ├── test_metrics.py
│   └── test_routes.py
├── .github/workflows/ci-cd.yml
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── Makefile
├── requirements.txt
├── README.md
└── SUBMISSION.txt
```

## Features

- FastAPI backend with typed routes and lifespan background polling
- API key authentication for write operations
- CPU, memory, and disk metrics via `psutil`
- WebSocket endpoint streaming metrics every second
- Streamlit dashboard with metrics, chart, server table, and forms
- Docker Compose local stack
- Makefile automation
- Pytest coverage gate above 75%
- GitHub Actions CI/CD for Azure Container Apps

## Prerequisites

- Python 3.11
- Docker and Docker Compose
- Make
- Azure CLI for manual Azure setup
- GitHub repository secrets for CI/CD deployment

## Environment Variables

Copy the template and edit values:

```bash
cp .env.example .env
```

| Variable | Description | Local example |
|---|---|---|
| `API_KEY` | API key required for protected routes | `demo-key` |
| `API_BASE_URL` | API URL used by Streamlit | `http://api:8000` in Docker |
| `API_PORT` | Local API port | `8000` |
| `DASHBOARD_PORT` | Local dashboard port | `8501` |

`.env` is intentionally ignored by Git.

## Local Run With Docker

```bash
cp .env.example .env
make up
```

Open:

```text
API:       http://127.0.0.1:8000/docs
Dashboard: http://127.0.0.1:8501
```

Stop the stack:

```bash
make down
```

Follow logs:

```bash
make logs
```

## Local Run Without Docker

```bash
make init
```

Terminal 1:

```bash
make run-api
```

Terminal 2:

```bash
make run-dashboard
```

## API Commands

Health:

```bash
curl http://127.0.0.1:8000/health
```

Metrics:

```bash
curl http://127.0.0.1:8000/metrics
```

Create a server:

```bash
curl -X POST http://127.0.0.1:8000/servers \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-key" \
  -d '{"name":"api-prod","host":"127.0.0.1","port":8000}'
```

List servers:

```bash
curl http://127.0.0.1:8000/servers
```

Manual health check:

```bash
curl -X POST http://127.0.0.1:8000/servers/1/check
```

## Makefile Commands

```bash
make help
make init
make up
make down
make logs
make dev
make run-api
make run-dashboard
make test
make lint
make build
make test-api
make clean
```

## Tests

```bash
make test
```

The test target enforces:

```text
pytest tests/ -v --cov=api --cov-fail-under=75
```

## Lint

```bash
make lint
```

## Azure Deployment

The GitHub Actions workflow builds two images and deploys them to Azure Container Apps:

- `devops-monitor-api`
- `devops-monitor-dashboard`

Required GitHub secrets:

| Secret | Description |
|---|---|
| `AZURE_CREDENTIALS` | JSON credentials for `azure/login` |
| `ACR_NAME` | Azure Container Registry name |
| `AZURE_RESOURCE_GROUP` | Resource group containing Container Apps |
| `API_KEY` | Runtime API key |
| `API_BASE_URL` | Public API URL used by dashboard |

The workflow runs:

```text
test -> build -> deploy
```

Build and deploy are restricted to pushes on `main`.

## Live URLs

Fill after Azure deployment:

```text
API:       TODO
Dashboard: TODO
```

## Screenshots

### Servers Dashboard

<img src="./assets/servers-dashboard.png" alt="Servers dashboard" width="900">

### Immediate Health Check

<img src="./assets/health-check.png" alt="Immediate health check" width="900">

### Tests and Coverage

<img src="./assets/tests-coverage.png" alt="Tests and coverage" width="900">
