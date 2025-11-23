.PHONY: help build up down restart logs shell db-shell migrate migration clean

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

logs-app: ## Показать логи приложения
	docker-compose logs -f app

logs-db: ## Показать логи базы данных
	docker-compose logs -f db

shell: ## Открыть bash в контейнере приложения
	docker-compose exec app bash

db-shell: ## Открыть psql в контейнере базы данных
	docker-compose exec db psql -U bloguser -d blogdb

migrate: ## Применить миграции
	docker-compose exec app alembic upgrade head

migration: ## Создать новую миграцию (использование: make migration MSG="описание")
	docker-compose exec app alembic revision --autogenerate -m "$(MSG)"

migration-history: ## Показать историю миграций
	docker-compose exec app alembic history

migration-current: ## Показать текущую версию миграции
	docker-compose exec app alembic current

clean: ## Остановить и удалить все контейнеры и volumes
	docker-compose down -v

rebuild: ## Полная пересборка (полезно при смене ОС)
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d
	@echo "Проект пересобран! API доступен на http://localhost:8000"

setup: ## Первоначальная настройка проекта
	@echo "Настройка проекта..."
	@if [ ! -f .env ]; then \
		echo "Создание .env файла..."; \
		cp env.example .env; \
		echo "Отредактируйте .env файл перед продолжением!"; \
	fi
	@echo "Запуск Docker контейнеров..."
	docker-compose up -d
	@echo "Ожидание запуска базы данных..."
	sleep 5
	@echo "Применение миграций..."
	docker-compose exec app alembic upgrade head || true
	@echo "Готово! API доступен на http://localhost:8000"
	@echo "Документация API: http://localhost:8000/docs"

dev: ## Запустить в режиме разработки
	docker-compose up

test: ## Запустить тесты (когда будут добавлены)
	docker-compose exec app pytest

status: ## Показать статус контейнеров
	docker-compose ps

prod-up: ## Запустить в production режиме
	docker-compose -f docker-compose.prod.yml up -d

prod-down: ## Остановить production
	docker-compose -f docker-compose.prod.yml down

prod-logs: ## Показать логи production
	docker-compose -f docker-compose.prod.yml logs -f

prod-build: ## Собрать production образ
	docker-compose -f docker-compose.prod.yml build
