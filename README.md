# Blog API

RESTful API для блога на FastAPI с PostgreSQL.

## Возможности

- 🔐 Аутентификация и авторизация с JWT
- 📝 Управление статьями (создание, чтение, обновление, удаление)
- 💬 Система комментариев
- 👤 Управление пользователями
- 🐳 Docker-ready с PostgreSQL
- 📊 SQLAlchemy ORM
- 🔄 Миграции базы данных с Alembic

## Технологический стек

- **Framework**: FastAPI 0.115.0
- **Database**: PostgreSQL 16 (через SQLAlchemy 2.0.35 + psycopg 3.2.3)
- **Authentication**: JWT (PyJWT 2.9.0)
- **Password Hashing**: Passlib с bcrypt
- **Migrations**: Alembic 1.13.2
- **Validation**: Pydantic 2.9.2 (с email-validator)
- **Server**: Uvicorn с uvloop
- **Runtime**: Python 3.13

## 📚 Документация

- **[QUICKSTART.md](docs/QUICKSTART.md)** - 🚀 Быстрый старт для начинающих
- **[DOCKER.md](docs/DOCKER.md)** - 🐳 Подробное руководство по Docker
- **[MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md)** - 📖 Руководство по миграции на PostgreSQL
- **[COMPLETED.md](docs/COMPLETED.md)** - ✅ Что было сделано и текущий статус

## Быстрый старт

> 💡 **Для подробных инструкций см. [QUICKSTART.md](docs/QUICKSTART.md)**

### С Docker (рекомендуется)

1. **Клонируйте репозиторий**:
   ```bash
   git clone <repository-url>
   cd web-service-backend-lab
   ```

2. **Настройте окружение**:
   ```bash
   cp env.example .env
   # Отредактируйте .env при необходимости
   ```

3. **Запустите приложение**:
   ```bash
   docker-compose up -d
   ```

4. **Примените миграции**:
   ```bash
   docker-compose exec app alembic upgrade head
   ```

5. **Откройте документацию API**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

Подробнее о работе с Docker см. [DOCKER.md](docs/DOCKER.md)

### Локальная разработка

1. **Создайте виртуальное окружение**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # или
   venv\Scripts\activate  # Windows
   ```

2. **Установите зависимости**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Настройте переменные окружения**:
   ```bash
   cp env.example .env
   # Отредактируйте .env с вашими настройками
   ```

4. **Запустите PostgreSQL** (или используйте Docker):
   ```bash
   docker-compose up -d db
   ```

5. **Примените миграции**:
   ```bash
   alembic upgrade head
   ```

6. **Запустите приложение**:
   ```bash
   uvicorn src.main:app --reload
   ```

## API Endpoints

### Пользователи
- `POST /api/users` - Регистрация нового пользователя
- `POST /api/users/login` - Вход пользователя (получение JWT токена)
- `GET /api/users/me` - Получить текущего пользователя
- `PUT /api/users/me` - Обновить профиль

### Статьи
- `GET /api/articles` - Список статей
- `GET /api/articles/{id}` - Получить статью
- `POST /api/articles` - Создать статью (требуется авторизация)
- `PUT /api/articles/{id}` - Обновить статью (требуется авторизация)
- `DELETE /api/articles/{id}` - Удалить статью (требуется авторизация)

### Комментарии
- `GET /api/articles/{article_id}/comments` - Список комментариев к статье
- `POST /api/articles/{article_id}/comments` - Добавить комментарий (требуется авторизация)
- `DELETE /api/comments/{id}` - Удалить комментарий (требуется авторизация)

## Структура проекта

```
.
├── alembic/                  # Миграции базы данных
│   ├── versions/            # Файлы миграций
│   └── env.py               # Конфигурация Alembic
├── src/
│   ├── api/                 # API endpoints
│   │   └── v1/             # API версия 1
│   │       ├── users/      # Пользователи
│   │       ├── articles/   # Статьи
│   │       └── comments/   # Комментарии
│   ├── common/             # Общие утилиты
│   │   ├── security/       # Безопасность (JWT, пароли)
│   │   └── utils/          # Вспомогательные функции
│   ├── infrastructure/     # Инфраструктура
│   │   └── db/            # База данных
│   │       ├── models/    # SQLAlchemy модели
│   │       ├── config.py  # Конфигурация БД
│   │       ├── session.py # Сессии БД
│   │       └── deps.py    # Зависимости FastAPI
│   └── main.py            # Точка входа приложения
├── docker-compose.yml      # Docker Compose конфигурация
├── Dockerfile             # Docker образ приложения
├── alembic.ini           # Конфигурация Alembic
├── requirements.txt      # Python зависимости
└── README.md            # Этот файл
```

## Разработка

### Создание миграций

После изменения моделей:

```bash
# С Docker
docker-compose exec app alembic revision --autogenerate -m "Description"
docker-compose exec app alembic upgrade head

# Локально
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### Просмотр логов

```bash
docker-compose logs -f app
```

### Тестирование API

Используйте встроенную документацию Swagger UI по адресу http://localhost:8000/docs

## Переменные окружения

Основные переменные (см. `env.example`):

- `DATABASE_URL` - URL подключения к PostgreSQL
- `SECRET_KEY` - Секретный ключ для JWT
- `ALGORITHM` - Алгоритм шифрования JWT (по умолчанию HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Время жизни токена в минутах

## Безопасность

- Пароли хешируются с помощью bcrypt
- JWT токены для аутентификации
- Защита от SQL injection через SQLAlchemy ORM
- Валидация данных с Pydantic

## Лицензия

MIT

## TODO

- [ ] Добавить тесты (pytest)
- [ ] Настроить CI/CD
- [ ] Добавить rate limiting
- [ ] Добавить кеширование (Redis)
- [ ] Добавить полнотекстовый поиск
- [ ] Добавить пагинацию для всех списков
- [ ] Добавить загрузку изображений
- [ ] Добавить email уведомления