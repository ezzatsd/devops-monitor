ifneq (,$(wildcard .env))
include .env
export
endif

APP_NAME ?= devops-monitor
IMAGE_NAME ?= devops-monitor
CONTAINER_NAME ?= devops-monitor-api
HOST ?= 127.0.0.1
PORT ?= 8000
CONTAINER_PORT ?= 8000
API_KEY ?= demo-key
PYTHON ?= python3
VENV ?= .venv
PIP := $(VENV)/bin/pip
PY := $(VENV)/bin/python

.PHONY: help init run build test test-api run-container stop clean

help:
	@echo "Available commands:"
	@echo "  make init          - Create a virtual environment and install dependencies"
	@echo "  make run           - Run the FastAPI app on the configured PORT"
	@echo "  make build         - Build the Docker image"
	@echo "  make test          - Run the unit tests"
	@echo "  make test-api      - Run HTTP checks against the running API"
	@echo "  make run-container - Run the app in a Docker container"
	@echo "  make stop          - Stop the running container"
	@echo "  make clean         - Remove stopped containers"

init:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run:
	$(PY) -m uvicorn api.main:app --host $(HOST) --port $(PORT)

build:
	docker build -t $(IMAGE_NAME) .

test:
	$(PY) -m pytest tests/ -v --cov=api --cov-report=term-missing

test-api:
	curl -f http://$(HOST):$(PORT)/health
	curl -f http://$(HOST):$(PORT)/metrics
	curl -f http://$(HOST):$(PORT)/servers
	curl -f -X POST http://$(HOST):$(PORT)/servers \
		-H "Content-Type: application/json" \
		-H "X-API-Key: $(API_KEY)" \
		-d '{"name":"make-test","host":"127.0.0.1","port":$(PORT)}'

run-container:
	docker run --rm -d \
		--name $(CONTAINER_NAME) \
		-p $(PORT):$(CONTAINER_PORT) \
		-e API_KEY=$(API_KEY) \
		$(IMAGE_NAME)

stop:
	docker stop $(CONTAINER_NAME)

clean:
	docker container prune -f
