```text
task_final/
├── docker_compose/           # все файлы внутри этой папки
│   ├── docker-compose.yml
│   ├── airflow/
│   ├── postgres/
│   ├── mongo/
│   ├── scripts/
│   └── data/
└── readme.md
```

Краткий план запуска:
1. Очистить и поднять инфраструктуру:
```powershell
docker-compose down -v
docker-compose up -d
```
2. Сгенерировать данные:
```powershell
docker-compose up data-generator
```
3. Проверить данные в MongoDB:
```powershell
docker exec -it de-mongodb mongosh
test> show dbs
test> use test
test> db.UserSessions.countDocuments()
test> exit
```

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

Схема DAG:
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