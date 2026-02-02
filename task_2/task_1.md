# Домашнее задание Практическая работа Дисциплина «ETL- процессы»
Тема «Основы трансформации данных».

**Выполнил - Третьяков Александр Юрьевич**

### Задание
Форма проверки - 
Самостоятельное задание с разбором на вебинаре.

Совет: выполняйте домашнее задание сразу, как только изучите тему.

Имя преподавателя
Артём Озерков

Время выполнения
120 минут

Цель задания
- Отработать навыки преобразования данных.
- Инструменты для выполнения ДЗ
- Apache Airflow и датасет.

Правила приёма работы

Прикрепите в LMS ссылку на GitHub с выполненным заданием и скриншот из
Аirflow, чтобы был виден успешно завершившийся процесс.

Важно:
- убедитесь, что по ссылке есть доступ;
- название должно содержать фамилию и имя студента, номер и название
ДЗ.

Чек-лист самопроверки

Задание считается выполненным, если:
- прикреплена ссылка с выполненным заданием;
- по ссылке содержится выполненное задание;
- доступ к материалам открыт.

Дедлайн
6 дней после открытия задания на платформе
Описание задания

Описание задания:

Выполните преобразование данных. Для этого используйте датасет.
Что необходимо сделать:
- вычислите 5 самых жарких и самых холодных дней за год;
- отфильтруйте out/in = in;
- поле noted_date переведите в формат ‘yyyy-MM-dd’ с типом данных date;
- очистите температуру по 5-му и 95-му процентилю.

<div style="page-break-after: always;"></div>

### Решение

Используя `docker-compose.yml` файл выполним развертывание

<img src="./assets/2026-02-02 171449.jpg" width="700">

Убедимся что "сырые" данные есть в таблицы, а таблицы для обработанных данных пустые.

```bash
docker exec de-postgres psql -U airflow -d airflow -c "SELECT COUNT(*) FROM iot_temp_raw;"

docker exec de-postgres psql -U airflow -d airflow -c "SELECT COUNT(*) FROM iot_temp_clean;"
docker exec de-postgres psql -U airflow -d airflow -c "SELECT COUNT(*) FROM iot_temp_hot_cold_days;"
```
<img src="./assets/2026-02-02 171906.jpg" width="900">

Зайдем в `Airflow UI` http://localhost:8080 и запустим выполнения `DAG`

<img src="./assets/2026-02-02 172047.jpg" width="700">

<img src="./assets/2026-02-02 172112.jpg" width="700">

<img src="./assets/2026-02-02 172221.jpg" width="700">

Проверим содержимое таблиц после выполнения `DAG`

```bash
docker exec -it de-postgres psql -U airflow -d airflow
```

```sql
SELECT COUNT(*) FROM iot_temp_clean;
SELECT noted_date, temp FROM iot_temp_clean LIMIT 5;
SELECT * FROM iot_temp_hot_cold_days ORDER BY ranking_type, rank;
```

<img src="./assets/2026-02-02 172711.jpg" width="900">

Проверим отчистку по процентилям

```sql
SELECT 
  percentile_cont(0.05) WITHIN GROUP (ORDER BY temp) as p5,
  percentile_cont(0.95) WITHIN GROUP (ORDER BY temp) as p95,
  MIN(temp) as min_temp,
  MAX(temp) as max_temp
FROM iot_temp_clean;
```

<img src="./assets/2026-02-02 173406.jpg" width="900">

На этом заданиен выполнено.