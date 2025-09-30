# Docker Setup Guide

Это руководство поможет вам запустить приложение с использованием Docker и PostgreSQL.

## Требования

- Docker
- Docker Compose

## Быстрый старт

### 1. Настройка окружения

Создайте файл `.env` на основе `env.example`:

```bash
cp env.example .env
```

Отредактируйте `.env` файл и измените значения по необходимости (особенно `SECRET_KEY` для production).

### 2. Запуск приложения

Запустите все сервисы (PostgreSQL + API):

```bash
docker-compose up -d
```

Эта команда:
- Скачает образ PostgreSQL
- Соберет Docker образ для вашего приложения
- Запустит базу данных PostgreSQL
- Запустит FastAPI приложение на порту 8000

### 3. Применение миграций базы данных

После первого запуска примените миграции:

```bash
# Создайте первую миграцию (если еще не создана)
docker-compose exec app alembic revision --autogenerate -m "Initial migration"

# Примените миграции
docker-compose exec app alembic upgrade head
```

### 4. Проверка работы

Откройте в браузере:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Полезные команды

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Только приложение
docker-compose logs -f app

# Только база данных
docker-compose logs -f db
```

### Остановка сервисов

```bash
# Остановить все сервисы
docker-compose down

# Остановить и удалить volumes (удалит данные БД!)
docker-compose down -v
```

### Перезапуск после изменений

```bash
# Пересобрать образ приложения
docker-compose build app

# Перезапустить приложение
docker-compose restart app
```

### Подключение к базе данных

```bash
# Через Docker
docker-compose exec db psql -U bloguser -d blogdb

# Локально (если PostgreSQL установлен)
psql -h localhost -U bloguser -d blogdb
```

### Выполнение команд внутри контейнера

```bash
# Запустить bash в контейнере приложения
docker-compose exec app bash

# Создать миграцию
docker-compose exec app alembic revision --autogenerate -m "Migration message"

# Применить миграции
docker-compose exec app alembic upgrade head

# Откатить последнюю миграцию
docker-compose exec app alembic downgrade -1
```

## Разработка

### Режим разработки с hot-reload

По умолчанию в `docker-compose.yml` включен режим `--reload` для uvicorn, который автоматически перезагружает приложение при изменении кода.

Код примонтирован как volume:
```yaml
volumes:
  - ./src:/app/src
```

Это означает, что изменения в директории `src` будут сразу видны в контейнере.

### Локальная разработка без Docker

Если вы хотите разрабатывать локально без Docker:

```bash
# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установите зависимости
pip install -r requirements.txt

# Настройте .env файл с DATABASE_URL
export DATABASE_URL="postgresql://bloguser:blogpassword@localhost:5432/blogdb"

# Запустите только PostgreSQL через Docker
docker-compose up -d db

# Примените миграции
alembic upgrade head

# Запустите приложение
uvicorn src.main:app --reload
```

## Production

Для production окружения используйте отдельный docker-compose файл:

1. Создайте `.env` файл с безопасными значениями:
   ```bash
   # Генерация безопасного SECRET_KEY
   openssl rand -hex 32
   ```

2. Запустите с production конфигурацией:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. Убедитесь, что установлены все необходимые переменные:
   - `JWT_SECRET` - криптографически стойкий ключ
   - `POSTGRES_PASSWORD` - сложный пароль
   - `DATABASE_URL` - правильный URL подключения

4. Рассмотрите дополнительные меры безопасности:
   - Используйте nginx в качестве reverse proxy
   - Настройте HTTPS с Let's Encrypt
   - Используйте Docker secrets для чувствительных данных
   - Настройте backup базы данных
   - Включите мониторинг и логирование

### Production конфигурация

В production режиме (`docker-compose.prod.yml`):
- ✅ Автоматический запуск миграций при старте
- ✅ Ожидание готовности базы данных
- ✅ Restart policy (unless-stopped)
- ❌ Без hot-reload
- ❌ Без volume монтирования исходного кода

## Troubleshooting

### База данных не запускается

Проверьте логи:
```bash
docker-compose logs db
```

Убедитесь, что порт 5432 не занят другим процессом.

### Приложение не может подключиться к базе данных

1. Проверьте, что база данных запущена:
   ```bash
   docker-compose ps
   ```

2. Проверьте переменные окружения в `.env`

3. Проверьте healthcheck базы данных:
   ```bash
   docker-compose exec db pg_isready -U bloguser
   ```

### Ошибки миграций

Если миграции не применяются:

```bash
# Проверьте текущую версию
docker-compose exec app alembic current

# Проверьте историю миграций
docker-compose exec app alembic history

# Попробуйте применить заново
docker-compose exec app alembic upgrade head
```

## Структура

- `Dockerfile` - образ приложения
- `docker-compose.yml` - конфигурация сервисов
- `.dockerignore` - файлы, игнорируемые при сборке образа
- `env.example` - пример переменных окружения
- `alembic.ini` - конфигурация миграций
- `alembic/` - директория с миграциями
