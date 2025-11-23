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

## Технологический стек

- **Services**: FastAPI, Python 3.11
- **Database**: PostgreSQL 16 (две независимые базы)
- **ORM**: SQLAlchemy 2.0 (Async)
- **Gateway**: Nginx
- **Migrations**: Alembic
- **DevOps**: Docker Compose

## 🚀 Быстрый старт

Для запуска вам понадобятся **Docker** и **Docker Compose**.

1. **Настройка переменных окружения**:
   Создайте файл `.env` на основе примера:
   ```bash
   # Windows
   copy env.example .env
   
   # Linux/Mac
   cp env.example .env
   ```

2. **Запуск приложения**:
   ```bash
   docker-compose up -d
   ```

3. **Применение миграций** (только при первом запуске):
   ```bash
   # Создание миграций (если база пустая)
   docker-compose exec users-api alembic revision --autogenerate -m "Init users"
   docker-compose exec backend alembic revision --autogenerate -m "Init backend"
   
   # Применение миграций
   docker-compose exec users-api alembic upgrade head
   docker-compose exec backend alembic upgrade head
   ```

4. **Остановка**:
   ```bash
   docker-compose down
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
├── docker-compose.yml      # Оркестрация сервисов
├── env.example             # Пример переменных окружения
└── README.md               # Этот файл
```

## Разработка и Миграции

Так как базы данных разделены, миграции управляются отдельно для каждого сервиса.

### Управление миграциями

Вместо `alembic` используйте команды через `docker-compose exec`:

```bash
# Создать миграцию (после изменения моделей)
# Для Users:
docker-compose exec users-api alembic revision --autogenerate -m "Add avatar field"
# Для Backend:
docker-compose exec backend alembic revision --autogenerate -m "Add tags"

# Применить миграции
docker-compose exec users-api alembic upgrade head
docker-compose exec backend alembic upgrade head
```

## Переменные окружения

Настройки находятся в файле `.env` (см. `env.example`).

- `POSTGRES_USER`, `POSTGRES_PASSWORD` - учетные данные БД.
- `JWT_SECRET` - секретный ключ для подписи токенов (должен совпадать в обоих сервисах!).
- `GATEWAY_PORT`, `USERS_PORT`, `BACKEND_PORT` - порты для доступа к сервисам.

## Полезные команды

- **Просмотр логов**:
  ```bash
  docker-compose logs -f            # Все логи
  docker-compose logs -f backend    # Только backend
  docker-compose logs -f users-api  # Только users
  docker-compose logs -f gateway    # Только gateway
  ```

- **Полная очистка** (удаление контейнеров и данных баз данных):
  ```bash
  docker-compose down -v
  ```
