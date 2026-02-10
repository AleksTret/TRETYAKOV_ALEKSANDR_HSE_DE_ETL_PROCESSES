-- Создаём базу данных 
CREATE DATABASE data_warehouse;

\c data_warehouse;

-- Создаём таблицу для сырых данных (точные имена как в CSV)
CREATE TABLE iot_temp_raw (
    id TEXT,
    "room_id/id" TEXT,
    noted_date TEXT,
    temp FLOAT,
    "out/in" TEXT
);

-- Создаём таблицу для очищенных данных
CREATE TABLE iot_temp_clean (
    id TEXT,
    "room_id/id" TEXT,
    noted_date DATE,
    event_time TIMESTAMP,
    temp FLOAT,
    "out/in" TEXT
);

-- Таблица для топ-5 жарких и холодных дней
CREATE TABLE iot_temp_hot_cold_days (
    noted_date DATE,
    temp FLOAT,
    type TEXT
);

-- права пользователю airflow 
GRANT ALL PRIVILEGES ON DATABASE data_warehouse TO airflow;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO airflow;