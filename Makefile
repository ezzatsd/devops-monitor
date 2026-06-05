ifneq (,$(wildcard .env))
include .env
export
endif

PYTHON ?= python3
VENV ?= .venv
COURSE_VENV ?= ../../../.venv
PY := $(shell if [ -x "$(VENV)/bin/python" ]; then echo "$(VENV)/bin/python"; elif [ -x "$(COURSE_VENV)/bin/python" ]; then echo "$(COURSE_VENV)/bin/python"; else echo "$(PYTHON)"; fi)
PIP := $(PY) -m pip

API_HOST ?= 127.0.0.1
API_PORT ?= 8000
DASHBOARD_PORT ?= 8501
API_KEY ?= demo-key
API_BASE_URL ?= http://localhost:8000

.PHONY: help init up down logs dev run-api run-dashboard test lint build test-api clean

help:
	@echo "Available commands:"
	@echo "  make init          - Create a virtual environment and install dependencies"
	@echo "  make up            - Start the full Docker Compose stack"
	@echo "  make down          - Stop the Docker Compose stack and volumes"
	@echo "  make logs          - Follow Docker Compose logs"
	@echo "  make dev           - Run API and dashboard locally without Docker"
	@echo "  make run-api       - Run the FastAPI API locally"
	@echo "  make run-dashboard - Run the Streamlit dashboard locally"
	@echo "  make test          - Run tests with coverage >= 75%"
	@echo "  make lint          - Run flake8"
	@echo "  make build         - Build Docker images"
	@echo "  make test-api      - Run HTTP checks against a running API"
	@echo "  make clean         - Remove local Python and test cache files"

init:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install -r requirements.txt

up:
	docker compose up --build -d

down:
	docker compose down -v

logs:
	docker compose logs -f

dev:
	@echo "Starting API on http://$(API_HOST):$(API_PORT)"
	@echo "Starting dashboard on http://localhost:$(DASHBOARD_PORT)"
	@API_KEY=$(API_KEY) $(PY) -m uvicorn api.main:app --host $(API_HOST) --port $(API_PORT) & \
	API_BASE_URL=$(API_BASE_URL) API_KEY=$(API_KEY) $(PY) -m streamlit run dashboard/app.py --server.port $(DASHBOARD_PORT)

run-api:
	API_KEY=$(API_KEY) $(PY) -m uvicorn api.main:app --host $(API_HOST) --port $(API_PORT)

run-dashboard:
	API_BASE_URL=$(API_BASE_URL) API_KEY=$(API_KEY) $(PY) -m streamlit run dashboard/app.py --server.port $(DASHBOARD_PORT)

test:
	$(PY) -m pytest tests/ -v --cov=api --cov-fail-under=75

lint:
	$(PY) -m flake8 api/ dashboard/ tests/

build:
	docker compose build

test-api:
	curl -f http://$(API_HOST):$(API_PORT)/health
	curl -f http://$(API_HOST):$(API_PORT)/metrics
	curl -f http://$(API_HOST):$(API_PORT)/servers
	curl -f -X POST http://$(API_HOST):$(API_PORT)/servers \
		-H "Content-Type: application/json" \
		-H "X-API-Key: $(API_KEY)" \
		-d '{"name":"make-test","host":"127.0.0.1","port":$(API_PORT)}'

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	rm -rf .pytest_cache .coverage htmlcov
