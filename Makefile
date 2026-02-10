# ============================================================================
# FinOps SaaS - Makefile
# Local development automation
# ============================================================================

.PHONY: help dev-up dev-down dev-restart logs logs-follow clean clean-volumes \
        lint test fmt check status ps init-db seed-db validate-workflows \
        bootstrap dev-tools-up dev-tools-down tools-logs

.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# ============================================================================
# HELP
# ============================================================================

help: ## Show this help message
	@echo "$(BLUE)FinOps SaaS - Development Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Core Development:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' | \
		grep -E "dev-|logs|clean|ps|status"
	@echo ""
	@echo "$(GREEN)Code Quality:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' | \
		grep -E "lint|test|fmt|check|validate"
	@echo ""
	@echo "$(GREEN)Database:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' | \
		grep -E "init-db|seed-db"
	@echo ""
	@echo "$(GREEN)Bootstrap:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' | \
		grep -E "bootstrap"

# ============================================================================
# DEVELOPMENT ENVIRONMENT
# ============================================================================

dev-up: ## Start all development services (postgres, redis, kafka, minio, trino)
	@echo "$(GREEN)Starting development environment...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Creating .env from .env.example...$(NC)"; \
		cp .env.example .env; \
	fi
	@docker compose -f docker-compose.dev.yml up -d
	@echo "$(GREEN)✓ Development services started$(NC)"
	@echo ""
	@echo "$(BLUE)Services:$(NC)"
	@echo "  PostgreSQL:  localhost:5432"
	@echo "  Redis:       localhost:6379"
	@echo "  Kafka:       localhost:9092"
	@echo "  MinIO:       http://localhost:9000 (API)"
	@echo "  MinIO UI:    http://localhost:9001 (Console)"
	@echo "  Trino:       http://localhost:8080"
	@echo ""
	@echo "$(YELLOW)Run 'make dev-tools-up' to start observability tools$(NC)"

dev-down: ## Stop all development services
	@echo "$(YELLOW)Stopping development environment...$(NC)"
	@docker compose -f docker-compose.dev.yml down
	@echo "$(GREEN)✓ Development services stopped$(NC)"

dev-restart: dev-down dev-up ## Restart all development services

dev-tools-up: ## Start observability and development tools (keycloak, mailhog, otel, prometheus, grafana)
	@echo "$(GREEN)Starting development tools...$(NC)"
	@docker compose -f docker-compose.tools.yml up -d
	@echo "$(GREEN)✓ Development tools started$(NC)"
	@echo ""
	@echo "$(BLUE)Tools:$(NC)"
	@echo "  Keycloak:    http://localhost:8081 (admin/admin)"
	@echo "  MailHog:     http://localhost:8025"
	@echo "  Prometheus:  http://localhost:9090"
	@echo "  Grafana:     http://localhost:3000 (admin/admin)"
	@echo "  OTEL:        localhost:4317 (gRPC), localhost:4318 (HTTP)"

dev-tools-down: ## Stop development tools
	@echo "$(YELLOW)Stopping development tools...$(NC)"
	@docker compose -f docker-compose.tools.yml down
	@echo "$(GREEN)✓ Development tools stopped$(NC)"

# ============================================================================
# LOGS & MONITORING
# ============================================================================

logs: ## Show logs from all services (last 100 lines)
	@docker compose -f docker-compose.dev.yml logs --tail=100

logs-follow: ## Follow logs from all services
	@docker compose -f docker-compose.dev.yml logs -f

tools-logs: ## Show logs from development tools
	@docker compose -f docker-compose.tools.yml logs --tail=100

ps: ## Show running containers
	@echo "$(BLUE)Development Services:$(NC)"
	@docker compose -f docker-compose.dev.yml ps
	@echo ""
	@echo "$(BLUE)Development Tools:$(NC)"
	@docker compose -f docker-compose.tools.yml ps 2>/dev/null || echo "  (not running)"

status: ps ## Alias for ps

# ============================================================================
# CLEANUP
# ============================================================================

clean: dev-down dev-tools-down ## Stop all services and remove containers
	@echo "$(YELLOW)Cleaning up containers...$(NC)"
	@docker compose -f docker-compose.dev.yml down --remove-orphans
	@docker compose -f docker-compose.tools.yml down --remove-orphans
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

clean-volumes: ## Remove all Docker volumes (WARNING: deletes all data!)
	@echo "$(RED)WARNING: This will delete all data in Docker volumes!$(NC)"
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	@docker compose -f docker-compose.dev.yml down -v
	@docker compose -f docker-compose.tools.yml down -v
	@echo "$(GREEN)✓ Volumes removed$(NC)"

# ============================================================================
# CODE QUALITY
# ============================================================================

lint: ## Run linters across all packages and services
	@echo "$(GREEN)Running linters...$(NC)"
	@if [ -f scripts/lint_all.sh ]; then \
		bash scripts/lint_all.sh; \
	else \
		echo "$(YELLOW)No lint script found - create scripts/lint_all.sh$(NC)"; \
	fi

test: ## Run tests across all packages and services
	@echo "$(GREEN)Running tests...$(NC)"
	@echo "$(YELLOW)Test infrastructure not yet implemented$(NC)"
	@echo "Add test commands for your services here"

fmt: ## Format code across all packages and services
	@echo "$(GREEN)Formatting code...$(NC)"
	@echo "$(YELLOW)Add your formatter commands here (prettier, black, gofmt, etc)$(NC)"

check: lint test ## Run all checks (lint + test)

validate-workflows: ## Validate workflow YAML files
	@echo "$(GREEN)Validating workflows...$(NC)"
	@if [ -f scripts/validate_workflows.sh ]; then \
		bash scripts/validate_workflows.sh; \
	else \
		echo "$(YELLOW)No validation script found - create scripts/validate_workflows.sh$(NC)"; \
	fi

# ============================================================================
# DATABASE
# ============================================================================

init-db: ## Initialize database with schema migrations
	@echo "$(GREEN)Initializing database...$(NC)"
	@if [ -f scripts/run_migrations.sh ]; then \
		bash scripts/run_migrations.sh; \
	else \
		echo "$(YELLOW)No migration script found - create scripts/run_migrations.sh$(NC)"; \
	fi

seed-db: ## Seed database with demo data
	@echo "$(GREEN)Seeding database with demo data...$(NC)"
	@if [ -f scripts/seed_demo_data.sh ]; then \
		bash scripts/seed_demo_data.sh; \
	else \
		echo "$(YELLOW)No seed script found - create scripts/seed_demo_data.sh$(NC)"; \
	fi

# ============================================================================
# BOOTSTRAP
# ============================================================================

bootstrap: ## Bootstrap the entire development environment
	@echo "$(GREEN)Bootstrapping development environment...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Creating .env from .env.example...$(NC)"; \
		cp .env.example .env; \
	fi
	@echo "$(BLUE)Creating required configuration directories...$(NC)"
	@mkdir -p tools/trino tools/otel-collector tools/prometheus tools/grafana/provisioning/datasources
	@if [ -f scripts/bootstrap_dev.sh ]; then \
		bash scripts/bootstrap_dev.sh; \
	fi
	@$(MAKE) dev-up
	@sleep 5
	@$(MAKE) dev-tools-up
	@echo ""
	@echo "$(GREEN)✓ Bootstrap complete!$(NC)"
	@echo ""
	@echo "$(BLUE)Next steps:$(NC)"
	@echo "  1. Check service status: make ps"
	@echo "  2. View logs: make logs-follow"
	@echo "  3. Initialize database: make init-db"
	@echo "  4. Seed demo data: make seed-db"
