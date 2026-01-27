Проверить установку
```bash
docker --version
docker-compose --version
```

Подготовить структуру
```text
корневая папка/
├── docker-compose.yml
├── init/
│   └── init.sql
├── airflow/
│   ├── dags
│   └── logs/
└── jupyter/
    └── notebooks/
```
```bash
mkdir -p init airflow/{dags/logs} jupyter/notebooks
```
Создать init.sql
```sql
-- Таблицу с сырыми данными json
CREATE TABLE IF NOT EXISTS pets
-- Заполнить ее 
INSERT INTO raw_pets_json (json_data)
-- Сделать таблицу для плоских данных
CREATE TABLE IF NOT EXISTS pets_flat

-- Сделать таблицу с сырыми данными xml
CREATE TABLE IF NOT EXISTS raw_nutrition_xml
-- Заполнить ее
INSERT INTO raw_nutrition_xml (xml_data) 
-- Сделать таблицу для плоских данных
CREATE TABLE IF NOT EXISTS nutrition_flat 
-- И вторую
CREATE TABLE IF NOT EXISTS daily_values

```
Обычный запуск (все сервисы)
```bash
docker-compose up -d
```
Запуск с пересборкой (Пересоберет образы если изменился Dockerfile )
```bash
docker-compose up -d --build
```
Иначе достаточно 
```bash
docker-compose down -v
docker-compose up -d --build
```
Пошаговый запуск (для отладки)
```bash
# Сначала только PostgreSQL
docker-compose up -d postgres

# После готовности БД (лог или healthcheck)
docker-compose logs postgres

# Инициализация Airflow
docker-compose up airflow-init

# Остальные сервисы
docker-compose up -d airflow-webserver airflow-scheduler nifi jupyter
```
Проверка работы сервисов
```bash
docker-compose ps
```
Доступ к сервисам
Airflow UI: http://localhost:8080

Логин: admin

Пароль: admin

NiFi: http://localhost:8081

Jupyter Lab: http://localhost:8888

PostgreSQL: localhost:5432

База: airflow

Пользователь: airflow

Пароль: airflow

Остановка сервисов:
```bash
docker-compose stop
```
Остановка с удалением контейнеров:
```bash
docker-compose down
```
Перезапуск:
```bash
docker-compose restart
# или для конкретного сервиса
docker-compose restart airflow-webserver
```
Удаление всех данных (очистка)
```bash
# Удаляет контейнеры, сети и тома
docker-compose down -v
```
Проверка healthcheck
```bash
docker inspect de-postgres --format='{{.State.Health.Status}}'
```
Проверить существующие connections:
```bash
docker exec de-airflow-web airflow connections get postgres_default
```
Удалить неправильный connection:
```bash
docker exec de-airflow-web airflow connections delete postgres_default
```
Создать правильный connection:
```bash
docker exec de-airflow-web airflow connections add "postgres_default" --conn-type "postgres" --conn-host "postgres" --conn-schema "airflow" --conn-login "airflow" --conn-password "airflow" --conn-port "5432"
```

Обновление DAGs (если добавил новые файлы):
```bash
docker exec de-airflow-webserver airflow db upgrade
```
Просмотр логов:
```bash
# Все логи
docker-compose logs

# Конкретного сервиса
docker-compose logs airflow-webserver
docker-compose logs postgres

# Логи в реальном времени
docker-compose logs -f
```
Важные примечания
- Первоначальная инициализация может занять несколько минут

- Airflow-init выполняется только один раз при первом запуске

- Тома данных сохраняются между перезапусками

- При изменении docker-compose.yml может потребоваться docker-compose up -d --build

Если возникнут проблемы при запуске, смотри логи:

```bash
docker-compose logs --tail=50
```

Проверить вручную таблицы
```bash
# Подключиться к PostgreSQL
docker exec -it de-postgres psql -U airflow -d airflow

# Проверить сырые данные
SELECT * FROM raw_pets_json;
SELECT * FROM raw_nutrition_xml;

# Проверить целивые таблицы
SELECT jsonb_pretty(json_data) as pretty
FROM raw_pets_json;

SELECT * FROM nutrition_flat;
SELECT * FROM daily_values;

# Проверить результат после запуска DAG
SELECT * FROM pets_flat;
```

Просмотр логов airflow 
```bash
docker logs de-airflow-scheduler --tail=100 2>&1 | findstr /i "simple_json_parser ERROR FAILED"
```