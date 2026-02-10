.PHONY: help install dev build test lint clean docker-up docker-down migrate seed

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	@echo "Installing dependencies..."
	npm install
	cd packages/common && npm install
	cd packages/config && npm install
	cd services/gateway-api && npm install
	cd apps/web && npm install

dev: ## Start development environment
	docker-compose -f docker-compose.dev.yml up -d
	@echo "Development environment started"

tools: ## Start development tools
	docker-compose -f docker-compose.tools.yml up -d
	@echo "Development tools started"

build: ## Build all services and apps
	@echo "Building all services..."
	npm run build

test: ## Run all tests
	@echo "Running tests..."
	npm test

test-unit: ## Run unit tests
	npm run test:unit

test-integration: ## Run integration tests
	npm run test:integration

test-e2e: ## Run end-to-end tests
	npm run test:e2e

lint: ## Run linters
	@echo "Running linters..."
	npm run lint

lint-fix: ## Fix linting issues
	npm run lint:fix

clean: ## Clean build artifacts
	@echo "Cleaning..."
	rm -rf node_modules
	rm -rf */node_modules
	rm -rf dist build out .next
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

docker-up: ## Start all Docker services
	docker-compose -f docker-compose.dev.yml -f docker-compose.tools.yml up -d

docker-down: ## Stop all Docker services
	docker-compose -f docker-compose.dev.yml -f docker-compose.tools.yml down

docker-logs: ## View Docker logs
	docker-compose -f docker-compose.dev.yml -f docker-compose.tools.yml logs -f

migrate: ## Run database migrations
	./scripts/run_migrations.sh

seed: ## Seed database with demo data
	./scripts/seed_demo_data.sh

bootstrap: install tools migrate seed ## Bootstrap development environment
	@echo "Development environment bootstrapped successfully"

validate-workflows: ## Validate workflow definitions
	./scripts/validate_workflows.sh

smoke-test: ## Run smoke tests
	./scripts/smoke_test.sh

generate-api: ## Generate OpenAPI documentation
	./scripts/generate_openapi.sh

security-check: ## Run security checks
	npm audit
	@echo "Consider running: trivy fs ."
