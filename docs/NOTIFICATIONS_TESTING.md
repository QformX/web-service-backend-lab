# Тестирование системы уведомлений

## Обзор
Система уведомлений позволяет пользователям подписываться на авторов и получать push-уведомления при публикации новых статей.

## Архитектура
- **Backend API** ставит задачи в Redis очередь при создании статей
- **Notifications Worker** обрабатывает очередь и отправляет уведомления подписчикам
- **Push Notificator** - тестовый сервис для приёма push-уведомлений
- **Alembic ORM** - автоматическая генерация миграций на основе моделей SQLAlchemy

## Шаг 1: Регистрация пользователей

### Регистрация автора (User 1)
```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "author@example.com",
    "username": "author",
    "password": "password123"
  }'
```

Сохраните `id` из ответа (например, `1`).

### Регистрация подписчика (User 2)
```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "subscriber@example.com",
    "username": "subscriber",
    "password": "password123"
  }'
```

Сохраните `id` из ответа (например, `2`).

## Шаг 2: Получение токенов

### Логин автора
```bash
AUTHOR_TOKEN=$(curl -s -X POST http://localhost:8000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "author@example.com",
    "password": "password123"
  }' | jq -r '.access_token')

echo "Author token: $AUTHOR_TOKEN"
```

### Логин подписчика
```bash
SUBSCRIBER_TOKEN=$(curl -s -X POST http://localhost:8000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "subscriber@example.com",
    "password": "password123"
  }' | jq -r '.access_token')

echo "Subscriber token: $SUBSCRIBER_TOKEN"
```

## Шаг 3: Получение subscription_key

1. Откройте в браузере: **http://localhost:8005**
2. Нажмите кнопку **"Subscribe"** или **"Enable Push Notifications"**
3. Разрешите уведомления в браузере
4. Скопируйте ключ подписки из интерфейса (обычно отображается как `subscription_key` или `token`)

Пример ключа: `eyJlbmRwb2ludCI6Imh0dHBzOi8vZmNtLmdvb2dsZWFwaXMuY29tL2ZjbS9zZW5kLy4uLiJ9`

## Шаг 4: Сохранение subscription_key для подписчика

```bash
SUBSCRIPTION_KEY="YOUR_KEY_FROM_PUSH_SERVICE"

curl -X PUT http://localhost:8000/api/users/me/subscription-key \
  -H "Authorization: Bearer $SUBSCRIBER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"subscription_key\": \"$SUBSCRIPTION_KEY\"}"
```

Ожидаемый ответ: данные пользователя с заполненным `subscription_key`.

## Шаг 5: Подписка на автора

```bash
curl -X POST http://localhost:8000/api/users/subscribe \
  -H "Authorization: Bearer $SUBSCRIBER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target_user_id": 1
  }'
```

Ожидаемый ответ: HTTP 204 No Content.

## Шаг 6: Публикация статьи автором

```bash
curl -X POST http://localhost:8000/api/articles \
  -H "Authorization: Bearer $AUTHOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Тестовая статья",
    "description": "Описание статьи",
    "body": "Содержимое статьи...",
    "tagList": ["test", "notifications"]
  }'
```

## Шаг 7: Проверка уведомлений

### Проверка в браузере
- Откройте вкладку с http://localhost:8005
- Вы должны увидеть push-уведомление: "Пользователь 1 выпустил новую статью: Тестовая с..."

### Проверка логов worker
```bash
docker compose logs --tail=20 notifications-worker
```

Ожидаемые логи:
```
INFO:__main__:Push delivered
INFO:__main__:Job completed
```

### Проверка очереди Redis
```bash
docker compose exec redis redis-cli LLEN post_notifications
```

Должно вернуть `0` (очередь пустая, так как задачи обработаны).

## Шаг 8: Проверка идемпотентности

Попробуйте создать ещё одну статью от автора - подписчик получит новое уведомление.

Если вы попытаетесь вручную поставить ту же задачу в очередь (с тем же `article_id`), уведомление **не** будет отправлено повторно благодаря таблице `notificationdelivery`.

## Проверка базы данных

### Таблица subscriptions
```bash
docker compose exec users-db psql -U bloguser -d usersdb -c "SELECT * FROM subscription;"
```

### Таблица notification deliveries
```bash
docker compose exec users-db psql -U bloguser -d usersdb -c "SELECT * FROM notificationdelivery;"
```

## Troubleshooting

### Worker не обрабатывает задачи
```bash
# Перезапустите worker
docker compose restart notifications-worker

# Проверьте логи
docker compose logs notifications-worker
```

### Нет subscription_key
- Убедитесь, что браузер поддерживает push-уведомления
- Проверьте, что вы разрешили уведомления для localhost:8005
- Скопируйте ключ из интерфейса push-сервиса

### Уведомления не приходят
1. Проверьте, что subscription_key сохранён: `GET /api/users/me`
2. Проверьте подписку в БД: `SELECT * FROM subscription WHERE subscriber_id=2`
3. Проверьте логи worker: `docker compose logs notifications-worker`
4. Проверьте очередь Redis: `docker compose exec redis redis-cli LLEN post_notifications`

## Переменные окружения

Настройка в `.env`:
```env
REDIS_URL=redis://redis:6379/0
NOTIFICATIONS_QUEUE=post_notifications
PUSH_SERVICE_URL=http://push-notificator:8000/api/v1/notify
NOTIFICATION_MAX_ATTEMPTS=5
NOTIFICATION_BACKOFF_BASE=2
NOTIFICATION_BACKOFF_MAX=30
```

- `NOTIFICATION_MAX_ATTEMPTS` - максимальное количество попыток доставки
- `NOTIFICATION_BACKOFF_BASE` - база для экспоненциальной задержки (секунды)
- `NOTIFICATION_BACKOFF_MAX` - максимальная задержка между попытками (секунды)

## API Endpoints

### Users API
- `PUT /api/users/me/subscription-key` - сохранить ключ подписки
- `POST /api/users/subscribe` - подписаться на автора
- `GET /api/users/me` - получить данные текущего пользователя

### Backend API
- `POST /api/articles` - создать статью (триггер уведомлений)

### Push Notificator
- `http://localhost:8005` - веб-интерфейс для получения subscription_key
- `POST http://push-notificator:8000/api/v1/notify` - эндпоинт для отправки push (используется worker)
