.PHONY: help build up down restart logs dev

help:
	@printf "\033[33mUsage:\033[0m\n  make [target] [arg=\"val\"...]\n\n\033[33mTargets:\033[0m\n"
	@grep -E '^[-a-zA-Z0-9_\.\/]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[32m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build env (first command after project pulling)
	docker-compose build

up: ## Run containers
	docker-compose up -d
	@echo "🚀 Container is successfully spun up! Go http://localhost:8000"

down: ## Stop containers (take a break, last command after deal)
	docker-compose down

restart: ## Restart
	docker-compose down && docker-compose up -d

logs: ## Check last logs
	docker-compose logs -f

dev: ## Dev only
	pip install -r requirements.txt
	uvicorn main:app --reload --port 8000
