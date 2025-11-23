.PHONY: help build up down restart logs logs-backend logs-users logs-gateway shell-backend shell-users db-shell-backend db-shell-users migrate-backend migrate-users migration-backend migration-users clean rebuild init

help: ## Показать эту справку
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Собрать Docker образы
	docker-compose build

up: ## Запустить все сервисы
	docker-compose up -d

down: ## Остановить все сервисы
	docker-compose down

restart: ## Перезапустить все сервисы
	docker-compose restart

logs: ## Показать логи всех сервисов
	docker-compose logs -f

logs-backend: ## Показать логи backend
	docker-compose logs -f backend

logs-users: ## Показать логи users-api
	docker-compose logs -f users-api

logs-gateway: ## Показать логи gateway
	docker-compose logs -f gateway

shell-backend: ## Bash в backend
	docker-compose exec backend bash

shell-users: ## Bash в users-api
	docker-compose exec users-api bash

db-shell-backend: ## PSQL в backend DB
	docker-compose exec backend-db psql -U bloguser -d blogdb

db-shell-users: ## PSQL в users DB
	docker-compose exec users-db psql -U bloguser -d usersdb

migrate-backend: ## Миграции backend
	docker-compose exec backend alembic upgrade head

migrate-users: ## Миграции users
	docker-compose exec users-api alembic upgrade head

migration-backend: ## Создать миграцию backend (MSG="...")
	docker-compose exec backend alembic revision --autogenerate -m "$(MSG)"

migration-users: ## Создать миграцию users (MSG="...")
	docker-compose exec users-api alembic revision --autogenerate -m "$(MSG)"

clean: ## Полная очистка
	docker-compose down -v

rebuild: ## Полная пересборка
	docker-compose down -v
	docker-compose build --no-cache
	docker-compose up -d
	@echo "Сервисы перезапущены!"
	@echo "Gateway: http://localhost:8000"
	@echo "Users Swagger: http://localhost:8001/docs"
	@echo "Backend Swagger: http://localhost:8002/docs"

init: ## Инициализация проекта (первый запуск)
	@echo "Запуск контейнеров..."
	docker-compose up -d
	@echo "Ожидание запуска баз данных (10 сек)..."
	@timeout /t 10 >nul 2>&1 || sleep 10
	@echo "Создание миграций для Users..."
	docker-compose exec users-api alembic revision --autogenerate -m "Initial users migration"
	@echo "Применение миграций для Users..."
	docker-compose exec users-api alembic upgrade head
	@echo "Создание миграций для Backend..."
	docker-compose exec backend alembic revision --autogenerate -m "Initial backend migration"
	@echo "Применение миграций для Backend..."
	docker-compose exec backend alembic upgrade head
	@echo "Готово! Проект инициализирован."
