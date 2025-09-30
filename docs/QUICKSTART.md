# 🚀 Быстрый старт

## Запуск с Docker (рекомендуется)

### 1. Убедитесь, что Docker запущен

```bash
docker ps
```

Если команда не работает, запустите Docker Desktop.

### 2. Запустите проект

```bash
# Первоначальная настройка (создаст .env и запустит всё)
make setup

# ИЛИ вручную:
cp env.example .env
docker-compose up -d
```

### 3. Откройте в браузере

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **ReDoc**: http://localhost:8000/redoc

## Полезные команды

```bash
# Просмотр логов
make logs

# Просмотр статуса
make status

# Остановка
make down

# Перезапуск
make restart

# Подключение к базе данных
make db-shell
```

## Первое API тестирование

1. Откройте http://localhost:8000/docs
2. Попробуйте endpoint `/health` - нажмите "Try it out" → "Execute"
3. Зарегистрируйте пользователя через `POST /api/users`
4. Войдите через `POST /api/users/login` и получите JWT токен
5. Используйте токен для авторизованных запросов (кнопка "Authorize" в Swagger UI)

### Пример через curl:

```bash
# Регистрация
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@example.com","password":"SecurePass123!"}'

# Вход (получение токена)
curl -X POST http://localhost:8000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"SecurePass123!"}'
```

## Миграции базы данных

```bash
# Создать миграцию после изменения моделей
make migration MSG="Add new field"

# Применить миграции
make migrate

# Показать историю миграций
docker-compose exec app alembic history
```

## Разработка

```bash
# Запуск с логами (интерактивный режим)
make dev

# Пересборка после изменения dependencies
docker-compose build

# Подключение к контейнеру приложения
make shell
```

## Troubleshooting

### Порт 8000 занят

Измените в `.env`:
```bash
APP_PORT=8001
```

### Порт PostgreSQL 5432 занят

Измените в `.env`:
```bash
POSTGRES_PORT=5433
DATABASE_URL=postgresql+psycopg://bloguser:blogpassword@localhost:5433/blogdb
```

### Контейнеры не запускаются

```bash
# Проверьте логи
make logs

# Полная перезагрузка
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### База данных не подключается

```bash
# Проверьте healthcheck
docker-compose ps

# Проверьте логи базы данных
make logs-db

# Попробуйте подключиться вручную
make db-shell
```

## Структура проекта

```
.
├── src/
│   ├── api/v1/        # API endpoints
│   ├── common/        # Общие утилиты
│   └── infrastructure/# База данных
├── alembic/           # Миграции
├── docker-compose.yml # Docker конфигурация
├── Dockerfile         # Docker образ
└── Makefile          # Команды управления
```

## Дальнейшие шаги

1. Прочитайте [README.md](README.md) для полной документации
2. Изучите [DOCKER.md](DOCKER.md) для деталей Docker setup
3. Посмотрите [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) для понимания архитектуры

## Важные замечания

⚠️ **PostgreSQL драйвер**: Используется `psycopg` версии 3 (не psycopg2!)
- URL формат: `postgresql+psycopg://user:pass@host:port/db`
- Совместим с Python 3.13

🔐 **Безопасность**: Для production обязательно:
- Сгенерируйте `JWT_SECRET`: `openssl rand -hex 32`
- Измените пароли базы данных
- Не коммитьте `.env` файл

📝 **Hot-reload**: В development режиме код автоматически перезагружается при изменениях
