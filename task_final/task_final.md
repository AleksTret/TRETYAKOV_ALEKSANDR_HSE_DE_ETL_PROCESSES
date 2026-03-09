# Итоговое задание по модулю 3

**Выполнил - Третьяков Александр Юрьевич**

### Решение

Используя `docker-compose.yml` файл выполним развертывание и выполним генерацию данных.

```powershell
# развертывание
docker-compose up -d
# генерация данных
docker-compose up data-generator
# проверка
docker-compose ps
```


<img src="./assets/2026-03-09 131046.jpg" width="700">

Проверим данные в MongoDB:
```powershell
docker exec -it de-mongodb mongosh

show dbs
use test

db.UserSessions.countDocuments()
db.EventLogs.countDocuments()
db.SupportTickets.countDocuments()
db.UserRecommendations.countDocuments()
db.ModerationQueue.countDocuments()

db.stats()

exit
```

<img src="./assets/2026-03-09 131603.jpg" width="700">

Проверим таблицы в `PostgreSQL` 

```powershell
docker exec -it de-postgres psql -U airflow -d etl_warehouse

\dt

# Подсчет в сырых таблицах
SELECT COUNT(*) FROM user_sessions;
SELECT COUNT(*) FROM event_logs;
SELECT COUNT(*) FROM support_tickets;
SELECT COUNT(*) FROM user_recommendations;
SELECT COUNT(*) FROM moderation_queue;

# Подсчет в витринах
SELECT COUNT(*) FROM user_activity_mart;
SELECT COUNT(*) FROM support_tickets_mart;
```

<img src="./assets/2026-03-09 132056.jpg" width="700">

Зайдем в Airflow UI http://localhost:8080 и убедимся в том что `DAG` созданы

<img src="./assets/2026-03-09 132202.jpg" width="900">

Схема перетекания данных: MongoDB → PostgreSQL
```text
MongoDB (коллекции)                    PostgreSQL (таблицы)
==================                    =====================

UserSessions
├── session_id                         user_sessions
├── user_id                     ─────> ├── session_id
├── start_time                         ├── user_id
├── end_time                           ├── start_time
├── pages_visited (array)              ├── end_time
├── device                              ├── pages_visited (TEXT[])
├── actions (array)                     ├── device
                                        └── actions (TEXT[])


EventLogs
├── event_id                            event_logs
├── timestamp                   ─────> ├── event_id
├── event_type                          ├── timestamp
└── details (object)                    ├── event_type
                                        └── details (JSONB)


SupportTickets
├── ticket_id                           support_tickets
├── user_id                     ─────> ├── ticket_id
├── status                               ├── user_id
├── issue_type                           ├── status
├── messages (array of objects)          ├── issue_type
├── created_at                           ├── messages (JSONB)
└── updated_at                           ├── created_at
                                         └── updated_at


UserRecommendations
├── user_id                              user_recommendations
├── recommended_products (array) ─────> ├── user_id
└── last_updated                         ├── recommended_products (TEXT[])
                                         └── last_updated


ModerationQueue
├── review_id                            moderation_queue
├── user_id                     ─────> ├── review_id
├── product_id                           ├── user_id
├── review_text                          ├── product_id
├── rating                               ├── review_text
├── moderation_status                    ├── rating
├── flags (array)                        ├── moderation_status
└── submitted_at                         ├── flags (TEXT[])
                                         └── submitted_at
```                                         
Каждая коллекция MongoDB → одна таблица PostgreSQL, с минимальными изменениями структуры.

Соответствие типов данных:
| MongoDB | PostgreSQL |
|---------|------------|
| string | VARCHAR или TEXT |
| number | INTEGER |
| ISO date string | TIMESTAMP |
| array of strings | TEXT[] |
| array of objects | JSONB |
| object | JSONB |

Схема `DAG`  `mongodb_to_postgres_replication`:
```text
mongodb_to_postgres_replication
├── start
├── process_user_sessions
│   ├── extract_user_sessions
│   ├── transform_user_sessions
│   └── load_user_sessions
├── process_event_logs
│   ├── extract_event_logs
│   ├── transform_event_logs
│   └── load_event_logs
├── process_support_tickets
│   ├── extract_support_tickets
│   ├── transform_support_tickets
│   └── load_support_tickets
├── process_user_recommendations
│   ├── extract_user_recommendations
│   ├── transform_user_recommendations
│   └── load_user_recommendations
├── process_moderation_queue
│   ├── extract_moderation_queue
│   ├── transform_moderation_queue
│   └── load_moderation_queue
└── end
```

```text
                    ┌→ process_user_sessions ─┐
                    ├→ process_event_logs ────┤
start ──────────────┼→ process_support_tickets ┼→ end
                    ├→ process_user_recommendations ─┤
                    └→ process_moderation_queue ─┘
```                    

Таблицы для витрин

Активность пользователей (на основе `user_sessions`)

- Количество сессий по дням/часам

- Среднее время на сайте

- Популярные страницы (из pages_visited)

- Популярные действия (из actions)

Таблица `user_activity_mart`:

- date (день)

- total_sessions

- avg_session_duration_minutes

- top_pages (JSON или массив)

- top_actions (JSON или массив)

Витрина 2: Эффективность поддержки (на основе `support_tickets`)

- Количество тикетов по статусам

- Количество тикетов по типам проблем

- Среднее время решения (updated_at - created_at)

- Открытые тикеты

`support_tickets_mart`:

- status

- ticket_count

- avg_resolution_hours

- issue_type_breakdown (JSON)

Структура `DAG` `analytics_marts`
```python
analytics_marts
├── start
├── create_user_activity_mart
│   ├── extract (из PostgreSQL)
│   ├── transform (агрегация)
│   └── load (в отдельную таблицу витрины)
├── create_support_tickets_mart
│   ├── extract
│   ├── transform
│   └── load
└── end
```

Выполним `DAG` репликации

<img src="./assets/2026-03-09 135449.jpg" width="900">

Проверим данные

```powershell
docker exec -it de-postgres psql -U airflow -d etl_warehouse

SELECT COUNT(*) FROM user_sessions;
SELECT COUNT(*) FROM event_logs;
SELECT COUNT(*) FROM support_tickets;
SELECT COUNT(*) FROM user_recommendations;
SELECT COUNT(*) FROM moderation_queue;

```
<img src="./assets/2026-03-09 144644.jpg" width="900">