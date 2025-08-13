.PHONY: help build up down logs clean test

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build all Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## Show logs for all services
	docker-compose logs -f

logs-api: ## Show API logs
	docker-compose logs -f api

logs-worker: ## Show Celery worker logs
	docker-compose logs -f celery-worker

logs-beat: ## Show Celery beat logs
	docker-compose logs -f celery-beat

clean: ## Remove all containers, networks, and volumes
	docker-compose down -v --remove-orphans
	docker system prune -f

test: ## Run tests
	docker-compose exec api python -m pytest

shell: ## Open shell in API container
	docker-compose exec api bash

worker-shell: ## Open shell in Celery worker container
	docker-compose exec celery-worker bash

restart: ## Restart all services
	docker-compose restart

status: ## Show status of all services
	docker-compose ps