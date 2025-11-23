# Blog API (Microservices)

Микросервисная архитектура для блога на FastAPI с PostgreSQL, разделенная на сервисы пользователей и статей.

## Архитектура

Проект разделен на независимые микросервисы:
- **Users API** (Port 8001): Управление пользователями, аутентификация (JWT). Своя БД (`users-db`).
- **Backend API** (Port 8002): Управление статьями и комментариями. Своя БД (`backend-db`).
- **API Gateway** (Port 8000): Nginx, маршрутизирующий запросы к нужным сервисам.

## Возможности

- 🔐 **Users API**: Регистрация, вход, профиль пользователя.
- 📝 **Backend API**: Статьи, комментарии, теги (без прямой связи с таблицей пользователей).
- 🚀 **Gateway**: Единая точка входа http://localhost:8000.
- 🐳 **Docker**: Полная контейнеризация всех компонентов.
- 📜 **Scripts**: Удобные скрипты управления (`manage.ps1` для Windows, `Makefile` для Linux/Mac).

## Технологический стек

- **Services**: FastAPI, Python 3.11
- **Database**: PostgreSQL 16 (две независимые базы)
- **ORM**: SQLAlchemy 2.0 (Async)
- **Gateway**: Nginx
- **Migrations**: Alembic
- **DevOps**: Docker Compose

## 🚀 Быстрый старт

### Windows (PowerShell)

1. **Инициализация проекта** (первый запуск):
   ```powershell
   .\manage.ps1 init
   ```
   *Команда запустит контейнеры, дождется БД и применит миграции.*

2. **Запуск**:
   ```powershell
   .\manage.ps1 up
   ```

3. **Остановка**:
   ```powershell
   .\manage.ps1 down
   ```

### Linux / macOS (Make)

1. **Инициализация**:
   ```bash
   make init
   ```

2. **Запуск / Остановка**:
   ```bash
   make up
   make down
   ```

## 📚 Документация API

После запуска сервисы доступны по адресам:

| Сервис | URL | Swagger UI | Описание |
|--------|-----|------------|----------|
| **Gateway** | `http://localhost:8000` | - | Основной API для клиентов |
| **Users** | `http://localhost:8000/api/users` | [http://localhost:8001/docs](http://localhost:8001/docs) | Пользователи и Auth |
| **Backend** | `http://localhost:8000/api/articles` | [http://localhost:8002/docs](http://localhost:8002/docs) | Статьи и Комментарии |

## Структура проекта

```
.
├── gateway/                 # Nginx конфигурация
│   └── nginx.conf
├── services/
│   ├── users/              # Микросервис пользователей
│   │   ├── src/
│   │   ├── alembic/        # Миграции пользователей
│   │   └── Dockerfile
│   └── backend/            # Микросервис статей (Backend)
│       ├── src/
│       ├── alembic/        # Миграции статей
│       └── Dockerfile
├── manage.ps1              # Скрипт управления для Windows
├── Makefile                # Скрипт управления для Linux/Mac
├── docker-compose.yml      # Оркестрация сервисов
└── README.md               # Этот файл
```

## Разработка и Миграции

Так как базы данных разделены, миграции управляются отдельно для каждого сервиса.

### Управление миграциями (Windows)

```powershell
# Создать миграцию (после изменения моделей)
.\manage.ps1 migration-users -Msg "Add avatar field"
.\manage.ps1 migration-backend -Msg "Add tags"

# Применить миграции
.\manage.ps1 migrate-users
.\manage.ps1 migrate-backend
```

### Управление миграциями (Linux/Mac)

```bash
make migration-users MSG="Add avatar"
make migration-backend MSG="Add tags"
make migrate-users
make migrate-backend
```

## Переменные окружения

Настройки находятся в `docker-compose.yml` (environment section) или могут быть вынесены в `.env`.

- `POSTGRES_USER`, `POSTGRES_PASSWORD` - учетные данные БД.
- `JWT_SECRET` - секретный ключ для подписи токенов (должен совпадать в обоих сервисах!).

## Полезные команды

- **Просмотр логов**:
  ```powershell
  .\manage.ps1 logs           # Все логи
  .\manage.ps1 logs-backend   # Только backend
  .\manage.ps1 logs-users     # Только users
  .\manage.ps1 logs-gateway   # Только gateway
  ```

- **Полная очистка** (удаление баз данных):
  ```powershell
  .\manage.ps1 clean
  ```
