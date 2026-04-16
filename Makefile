.PHONY: dev test build clean install setup help

# Default target
help:
	@echo "EHS Monorepo - Available Commands"
	@echo "=================================="
	@echo ""
	@echo "Development:"
	@echo "  make dev          - Start frontend development server"
	@echo "  make dev:backend  - Start Python AI service in development mode"
	@echo "  make dev:java     - Start Java business service in development mode"
	@echo "  make dev:all      - Start all services concurrently"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run all tests"
	@echo "  make test:frontend - Run frontend tests"
	@echo "  make test:python  - Run Python AI service tests"
	@echo "  make test:java    - Run Java business service tests"
	@echo "  make test:coverage - Run tests with coverage report"
	@echo ""
	@echo "Build:"
	@echo "  make build        - Build all services"
	@echo "  make build:frontend - Build frontend only"
	@echo "  make build:python - Build Python AI service"
	@echo "  make build:java   - Build Java business service"
	@echo ""
	@echo "Setup:"
	@echo "  make install      - Install all dependencies"
	@echo "  make setup        - Run setup script"
	@echo "  make clean        - Clean build artifacts"
	@echo ""

# Development
dev:
	@echo "Starting frontend development server..."
	cd apps/admin-console && pnpm run dev

dev-backend:
	@echo "Starting Python AI service..."
	cd apps/ehs-ai && poetry run uvicorn src.api.rest:app --reload --host 0.0.0.0 --port 8000

dev-java:
	@echo "Starting Java business service..."
	cd apps/ehs-business && mvn spring-boot:run

dev-all:
	@echo "Starting all services..."
	npx concurrently \
		"pnpm run dev" \
		"cd apps/ehs-ai && poetry run uvicorn src.api.rest:app --reload --host 0.0.0.0 --port 8000" \
		"cd apps/ehs-business && mvn spring-boot:run" \
		--names "frontend,python,java" \
		--prefix-colors "blue,green,yellow"

# Testing
test: test-frontend test-python
	@echo "All tests completed"

test-frontend:
	@echo "Running frontend tests..."
	cd apps/admin-console && pnpm test

test-python:
	@echo "Running Python AI service tests..."
	cd apps/ehs-ai && poetry run pytest

test-java:
	@echo "Running Java business service tests..."
	cd apps/ehs-business && mvn test

test-coverage:
	@echo "Running tests with coverage..."
	cd apps/admin-console && pnpm run test:coverage
	cd apps/ehs-ai && poetry run pytest --cov=src --cov-report=html

# Building
build: build-frontend build-python
	@echo "All builds completed"

build-frontend:
	@echo "Building frontend..."
	cd apps/admin-console && pnpm run build

build-python:
	@echo "Building Python AI service..."
	cd apps/ehs-ai && poetry build

build-java:
	@echo "Building Java business service..."
	cd apps/ehs-business && mvn package -DskipTests

# Setup and Installation
install: install-frontend install-python
	@echo "All dependencies installed"

install-frontend:
	@echo "Installing frontend dependencies..."
	cd apps/admin-console && pnpm install

install-python:
	@echo "Installing Python dependencies..."
	cd apps/ehs-ai && poetry install

setup:
	@echo "Running setup script..."
	./scripts/setup.sh

# Cleaning
clean:
	@echo "Cleaning build artifacts..."
	rm -rf apps/admin-console/.next
	rm -rf apps/admin-console/node_modules
	rm -rf apps/ehs-ai/dist
	rm -rf apps/ehs-ai/__pycache__
	rm -rf apps/ehs-ai/.pytest_cache
	rm -rf apps/ehs-ai/coverage
	rm -rf apps/ehs-business/target
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Clean completed"

# Docker
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-build:
	docker-compose build

# Linting
lint:
	@echo "Running linters..."
	cd apps/admin-console && npm run lint
	cd apps/ehs-ai && poetry run black --check src tests
	cd apps/ehs-ai && poetry run ruff check src tests

format:
	@echo "Formatting code..."
	cd apps/admin-console && npm run lint -- --fix
	cd apps/ehs-ai && poetry run black src tests
	cd apps/ehs-ai && poetry run ruff check --fix src tests

# Type checking
typecheck:
	@echo "Running type checks..."
	cd apps/admin-console && npm run typecheck
	cd apps/ehs-ai && poetry run mypy src
