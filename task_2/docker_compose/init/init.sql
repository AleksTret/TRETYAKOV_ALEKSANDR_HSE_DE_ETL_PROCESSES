drop table if exists iot_temp_raw;
drop table if exists iot_temp_clean;
drop table if exists iot_temp_hot_cold_days;

-- Таблица для сырых данных из CSV
create table iot_temp_raw (
    id text,
    room_id text,
    noted_date text,
    temp float,
    out_in text
);

-- Загружаем данные из CSV
copy iot_temp_raw from '/docker-entrypoint-data/iot-temp.csv' 
delimiter ',' 
csv header;

-- Таблица для очищенных данных
create table iot_temp_clean (
    id text,
    room_id text,
    noted_date date,
    temp float,
    out_in text,
    year integer,
    month integer,
    day integer
);

-- Таблица для результатов: 5 самых жарких и холодных дней
create table iot_temp_hot_cold_days (
    ranking_type text,
    rank integer,
    noted_date date,
    max_temp float,
    year integer
);