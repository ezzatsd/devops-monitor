# DevOps Monitoring Dashboard

Final project for the SupDeVinci Python DevOps course.

This project provides a DevOps monitoring dashboard built with **FastAPI**, **Streamlit**, **Docker**, **GitHub Actions**, and **Azure**. It exposes live system metrics, server registration, health checks, and a dashboard for monitoring infrastructure status.

## Live Project

| Resource | URL |
|---|---|
| GitHub repository | https://github.com/ezzatsd/devops-monitor |
| Azure dashboard | https://dashbord-bfeng7bmc9gxb4de.francecentral-01.azurewebsites.net |
| Local Swagger UI | http://127.0.0.1:8000/docs |
| Local Streamlit dashboard | http://127.0.0.1:8501 |

The Azure deployment serves the Streamlit dashboard. The FastAPI backend is started internally when the dashboard runs on Azure App Service, so the public entry point for the deployed project is the dashboard URL.

## Features

- FastAPI backend with typed routes
- Streamlit dashboard with live metrics and charts
- CPU, memory, and disk monitoring with `psutil`
- API key protection for server registration and delete operations
- Server registry with status filtering
- Immediate server health checks
- WebSocket endpoint for real-time metrics
- Dockerfiles for API and dashboard
- Docker Compose stack for local containerized execution
- Makefile automation for setup, tests, Docker, and API checks
- Pytest test suite with coverage gate above 75%
- GitHub Actions workflow for CI/CD
- Azure App Service deployment

## Architecture

```text
GitHub Repository
  -> GitHub Actions
      -> lint
      -> unit tests with coverage
      -> deployment to Azure

Local Docker runtime:
  api        FastAPI    http://127.0.0.1:8000
  dashboard  Streamlit  http://127.0.0.1:8501

Azure runtime:
  dashboard  Streamlit public web app
  api        FastAPI embedded internally for the dashboard
```

## Project Structure

```text
devops-monitor/
├── api/
│   ├── __init__.py
│   ├── auth.py
│   ├── main.py
│   ├── metrics.py
│   ├── models.py
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
├── .gitignore
├── Makefile
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.11+
- Docker Desktop
- Docker Compose
- Make
- Git

## Environment Variables

Create a local `.env` file from the example:

```bash
cp .env.example .env
```

| Variable | Description | Example |
|---|---|---|
| `API_KEY` | API key used by protected endpoints | `demo-key` |
| `API_BASE_URL` | API URL used by the dashboard | `http://api:8000` for Docker |
| `API_PORT` | Local API port | `8000` |
| `DASHBOARD_PORT` | Local dashboard port | `8501` |

The `.env` file is ignored by Git and must not be committed.

## Run Locally With Docker

From the repository root:

```bash
cp .env.example .env
make up
```

Open:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8501
```

Stop the stack:

```bash
make down
```

View logs:

```bash
make logs
```

## Run Locally Without Docker

Install dependencies:

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

Open:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8501
```

## API Examples

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Metrics:

```bash
curl http://127.0.0.1:8000/metrics
```

List servers:

```bash
curl http://127.0.0.1:8000/servers
```

Register a server:

```bash
curl -X POST http://127.0.0.1:8000/servers \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-key" \
  -d '{"name":"api-prod","host":"127.0.0.1","port":8000}'
```

Run a manual health check:

```bash
curl -X POST http://127.0.0.1:8000/servers/1/check
```

## Makefile Commands

| Command | Description |
|---|---|
| `make help` | Show available commands |
| `make init` | Create virtual environment and install dependencies |
| `make run-api` | Run the FastAPI backend locally |
| `make run-dashboard` | Run the Streamlit dashboard locally |
| `make up` | Start the Docker Compose stack |
| `make down` | Stop the Docker Compose stack |
| `make logs` | Follow Docker Compose logs |
| `make build` | Build Docker images |
| `make test` | Run unit tests with coverage |
| `make lint` | Run flake8 |
| `make test-api` | Test the running API with curl |
| `make clean` | Clean temporary Python test artifacts |

## Tests

Run the full test suite:

```bash
make test
```

Current validated result:

```text
10 passed
Coverage: 93.50%
Required coverage: 75%
```

Run lint:

```bash
make lint
```

## Docker Validation

```bash
docker compose config
make build
make up
make test-api
docker compose ps
```

Expected services:

```text
devops-monitor-api        healthy  0.0.0.0:8000->8000/tcp
devops-monitor-dashboard  running  0.0.0.0:8501->8501/tcp
```

## Azure Deployment

The deployed dashboard is available here:

```text
https://dashbord-bfeng7bmc9gxb4de.francecentral-01.azurewebsites.net
```

GitHub Actions runs on every push to `main`:

```text
test -> build/deploy
```

Required GitHub secrets are configured in:

```text
Repository Settings > Secrets and variables > Actions
```

No secrets are stored in the repository.

## Security Notes

- `.env` is ignored by Git.
- API keys and Azure credentials must stay in GitHub Secrets or Azure settings.
- Do not commit local secrets, tokens, or Azure credentials.

## Screenshots

### Servers Dashboard

<img src="./assets/servers-dashboard.png" alt="Servers dashboard" width="900">

### Immediate Health Check

<img src="./assets/health-check.png" alt="Immediate health check" width="900">

### Tests and Coverage

<img src="./assets/tests-coverage.png" alt="Tests and coverage" width="900">
