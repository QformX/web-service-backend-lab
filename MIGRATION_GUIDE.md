# Руководство по миграции на PostgreSQL + Docker

Этот документ описывает все изменения, внесенные для миграции с SQLite на PostgreSQL и Docker.

## 🎯 Что было сделано

### 1. Docker Конфигурация

#### Создано:
- **Dockerfile** - образ приложения Python 3.13
- **docker-compose.yml** - конфигурация для разработки с hot-reload
- **docker-compose.prod.yml** - конфигурация для production без hot-reload
- **.dockerignore** - исключение ненужных файлов из образа

#### Особенности:
- Использование PostgreSQL 16 Alpine (легковесный образ)
- Автоматическое ожидание готовности БД (healthcheck)
- Hot-reload для разработки
- Restart policy для production
- Volume для данных PostgreSQL

### 2. База данных

#### Обновлено:
- **src/infrastructure/db/session.py** - добавлена поддержка PostgreSQL
  - Условная конфигурация для SQLite/PostgreSQL
  - Правильные `connect_args` для каждой БД

#### Конфигурация БД:
- Поддержка переменной окружения `DATABASE_URL`
- По умолчанию SQLite (для быстрого тестирования)
- В Docker - PostgreSQL

### 3. Миграции (Alembic)

#### Создано:
- **alembic.ini** - конфигурация Alembic
- **alembic/env.py** - скрипт окружения миграций
- **alembic/script.py.mako** - шаблон для миграций

#### Использование:
```bash
# Создать миграцию
alembic revision --autogenerate -m "Описание"

# Применить миграции
alembic upgrade head

# Откатить миграцию
alembic downgrade -1
```

### 4. Автоматизация

#### Создано:
- **docker-entrypoint.sh** - скрипт запуска контейнера
  - Ожидание готовности БД
  - Автоматическое применение миграций
  - Запуск приложения

- **wait-for-db.py** - Python скрипт ожидания БД
  - Проверка подключения к БД
  - Retry логика (30 попыток с задержкой 2 сек)

- **Makefile** - удобные команды для управления
  - `make setup` - первоначальная настройка
  - `make up/down` - запуск/остановка
  - `make migrate` - применение миграций
  - `make logs` - просмотр логов
  - И многое другое (см. `make help`)

### 5. Переменные окружения

#### Создано:
- **env.example** - пример конфигурации

#### Переменные:
```bash
# PostgreSQL
POSTGRES_USER=bloguser
POSTGRES_PASSWORD=blogpassword
POSTGRES_DB=blogdb
POSTGRES_PORT=5432

# Application
APP_PORT=8000
DATABASE_URL=postgresql://...

# JWT (обновлено для соответствия коду)
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRES_MIN=30
```

**Важно**: Переменные обновлены для соответствия используемым в коде (`JWT_SECRET` вместо `SECRET_KEY`)

### 6. Зависимости

#### Обновлено:
- **requirements.txt** - добавлено:
  - `alembic==1.13.2` - миграции БД
  - `python-dotenv==1.1.1` - загрузка переменных окружения
  - `pydantic[email]==2.9.2` - валидация с поддержкой email

**Важно**: Используется `psycopg[binary]==3.2.3` (версия 3) вместо `psycopg2-binary`, так как:
- `psycopg2-binary 2.9.9` не совместим с Python 3.13
- `psycopg` версия 3 - современный драйвер с полной поддержкой Python 3.13
- Требует использования URL формата `postgresql+psycopg://` вместо `postgresql://`

### 7. Документация

#### Создано:
- **README.md** - обновлено полное описание проекта
- **DOCKER.md** - детальное руководство по Docker
- **MIGRATION_GUIDE.md** - этот документ

### 8. Улучшения приложения

#### Обновлено:
- **src/main.py** - добавлено:
  - Health check endpoint (`/health`)
  - Расширенное описание API
  - Комментарии о миграциях

#### **.gitignore** - обновлено:
  - Исключение файлов БД (*.db, *.sqlite)
  - Разрешен env.example
  - Разрешен alembic.ini

## 🚀 Как использовать

### Первый запуск (Разработка)

```bash
# 1. Скопируйте конфигурацию
cp env.example .env

# 2. Отредактируйте .env при необходимости
nano .env

# 3. Запустите всё одной командой
make setup

# ИЛИ вручную:
docker-compose up -d
docker-compose exec app alembic upgrade head
```

### Доступ к приложению

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

### Разработка

```bash
# Запустить с логами (интерактивно)
make dev

# Просмотр логов
make logs

# Создание миграций
make migration MSG="Add user avatar"

# Применение миграций
make migrate

# Подключение к БД
make db-shell
```

### Production

```bash
# 1. Создайте безопасный .env
cp env.example .env
openssl rand -hex 32  # Используйте для JWT_SECRET

# 2. Запустите production
make prod-up

# 3. Проверьте статус
docker-compose -f docker-compose.prod.yml ps

# 4. Просмотр логов
make prod-logs
```

## 📊 Сравнение SQLite vs PostgreSQL

| Аспект | SQLite (до) | PostgreSQL (после) |
|--------|-------------|-------------------|
| Одновременные подключения | Ограничено | Неограниченно |
| Транзакции | Файловый уровень | Row-level locking |
| Производительность | Ок для разработки | Отлично для production |
| Масштабируемость | Не масштабируется | Горизонтальное масштабирование |
| Backup | Копирование файла | pg_dump, WAL архивы |
| Полнотекстовый поиск | Ограниченно | Отличная поддержка |

## 🔐 Безопасность

### Обязательно для production:

1. **Сгенерируйте безопасный JWT_SECRET**:
   ```bash
   openssl rand -hex 32
   ```

2. **Используйте сложные пароли БД**

3. **Не коммитьте .env файл** (уже в .gitignore)

4. **Настройте HTTPS** (nginx + Let's Encrypt)

5. **Ограничьте доступ к БД**:
   - Не открывайте порт 5432 наружу
   - Используйте приватные сети

6. **Регулярный backup**:
   ```bash
   docker-compose exec db pg_dump -U bloguser blogdb > backup.sql
   ```

## 🧪 Тестирование миграции

### Проверка работы:

1. **Health check**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **API документация**:
   Откройте http://localhost:8000/docs

3. **Подключение к БД**:
   ```bash
   make db-shell
   \dt  # Список таблиц
   \d users  # Структура таблицы users
   ```

4. **Проверка миграций**:
   ```bash
   docker-compose exec app alembic current
   docker-compose exec app alembic history
   ```

## 📝 Структура миграций

После первого создания миграций:

```bash
alembic/
├── env.py
├── script.py.mako
└── versions/
    ├── 001_initial_migration.py
    ├── 002_add_avatar_to_users.py
    └── ...
```

Каждая миграция содержит:
- `upgrade()` - применение изменений
- `downgrade()` - откат изменений
- Автоматически сгенерированный код (при `--autogenerate`)

## 🛠️ Troubleshooting

### Проблема: "Cannot connect to database"

**Решение**:
```bash
# Проверьте запущена ли БД
docker-compose ps

# Проверьте логи
docker-compose logs db

# Перезапустите
docker-compose restart db
```

### Проблема: "Port 5432 already in use"

**Решение**:
```bash
# Измените порт в .env
POSTGRES_PORT=5433

# Или остановите локальный PostgreSQL
brew services stop postgresql  # macOS
sudo systemctl stop postgresql  # Linux
```

### Проблема: Миграции не применяются

**Решение**:
```bash
# Проверьте текущую версию
docker-compose exec app alembic current

# Примените принудительно
docker-compose exec app alembic upgrade head

# Если не помогает - пересоздайте БД
docker-compose down -v
docker-compose up -d
```

## 📚 Полезные команды

### Docker

```bash
# Полная пересборка
docker-compose build --no-cache

# Удалить всё (включая данные!)
docker-compose down -v

# Посмотреть использование ресурсов
docker stats
```

### PostgreSQL

```bash
# Backup
docker-compose exec db pg_dump -U bloguser blogdb > backup.sql

# Restore
cat backup.sql | docker-compose exec -T db psql -U bloguser -d blogdb

# Размер БД
docker-compose exec db psql -U bloguser -d blogdb -c "\l+"
```

### Alembic

```bash
# Создать пустую миграцию
alembic revision -m "Description"

# Создать миграцию с автогенерацией
alembic revision --autogenerate -m "Description"

# Применить конкретную миграцию
alembic upgrade +1  # следующая
alembic upgrade <revision>  # конкретная

# Откат
alembic downgrade -1  # предыдущая
alembic downgrade base  # к началу
```

## ✅ Checklist перед деплоем

- [ ] Обновлен .env с безопасными значениями
- [ ] JWT_SECRET сгенерирован через openssl
- [ ] Пароль PostgreSQL изменен
- [ ] Применены все миграции
- [ ] Протестированы все API endpoints
- [ ] Настроен backup базы данных
- [ ] Настроен мониторинг (опционально)
- [ ] Настроен nginx + HTTPS (рекомендуется)

## 🎉 Результат

Теперь ваше приложение:
- ✅ Использует PostgreSQL вместо SQLite
- ✅ Запускается в Docker контейнере
- ✅ Имеет автоматические миграции БД
- ✅ Готово к production деплою
- ✅ Имеет удобные команды управления (Makefile)
- ✅ Документировано

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи: `make logs`
2. Проверьте статус: `make status`
3. Прочитайте [DOCKER.md](DOCKER.md)
4. Изучите README.md

Удачного использования! 🚀
