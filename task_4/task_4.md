# Домашнее задание Практическая работа Дисциплина «ETL- процессы»

## Тема Тема 9. Работа с big data и Тема 10. NoSQL в ETL-процессах.

**Выполнил - Третьяков Александр Юрьевич**

### Задание
Форма проверки
Самостоятельное задание с разбором на вебинаре.

Совет: выполняйте его сразу, как только изучите тему.

Имя преподавателя
Артём Озерков.

Время выполнения
2 часа.

Цель задания
Практика работы с big data и NoSQL в облаке

Инструменты для выполнения ДЗ
Yandex Data Processing, Apache Hadoop, Apache Spark, Managed Service for
Kafka, Yandex StoreDoc, Yandex Data Transfer

Правила приёма работы
Сделайте скриншот изначальных и изменённых данных. Прикрепите в LMS
файл или ссылку на GitHub со скриншотами.

Важно:
- убедитесь, что по ссылке есть доступ;
- название должно содержать фамилию и имя студента, номер и название ДЗ.

Чек-лист самопроверки
Задание считается выполненным, если:
- прикреплена ссылка с выполненным заданием;
- по ссылке содержится выполненное задание;
- доступ к материалам открыт.

Дедлайн
6 дней после открытия задания на платформе.

Описание задания
Повторите работу из демонстрации вебинаров.
- Вебинар «Работа с big data»
    1. Разверните кластер Hadoop и Spark с помощью Yandex Data Processing.
    2. Загрузите данные для обработки.
    3. Проведите трансформацию и запись в Yandex Data Processing.
- Вебинр «NoSQL в ETL-процессах» (материалы демонстрации)
В кластер Yandex StoreDoc можно в реальном времени поставлять данные из
топиков Apache Kafka®.
Чтобы запустить поставку данных:
    1. Подготовьте тестовые данные.
    2. Подготовьте и активируйте трансфер.
    3. Проверьте работоспособность трансфера.
Удалите созданные ресурсы.


<div style="page-break-after: always;"></div>

### Решение

Создадим и настроим кластер

<img src="./assets/2026-04-30 141844.png" width="700">

<img src="./assets/2026-04-30 141907.png" width="700">

<img src="./assets/2026-04-30 141925.png" width="700">

<img src="./assets/2026-04-30 141953.png" width="700">

Загрузим json файл в бакет

<img src="./assets/2026-04-30 143255.png" width="700">

Подключимся по SSH и запустим spark

Выполнил код в spark

```python
import pyspark.sql.functions as F

df = spark.read.option("multiline", "true").json("s3a://mars17bucket/clients.json", multiLine=True)

# Выделяем passport
passport = df.select(
    F.col("passport.type"),
    F.col("passport.dcm_serial_no"),
    F.col("passport.dcm_no"),
    F.col("passport.dcm_date"),
    F.col("passport.issued_by"),
    F.col("tax_number").alias("client_tax_number")
)

passport.show()
passport.write.parquet("s3a://mars17bucket/passport.parquet")

# Основная таблица клиентов
clients = df.select(
    "name_cyr",
    "is_resident",
    "tax_number",
    "last_name",
    "first_name",
    "middle_name",
    "birth_date",
    "death_date",
    "registry_date",
    "risk_status",
    "risk_group",
    "sex",
    "country",
    "birth_place"
)

clients.show()
clients.write.parquet("s3a://mars17bucket/clients.parquet")

# ПРОВЕРКА
passport_check.show(5, truncate=False)
clients_check.show(5, truncate=False)
```

<img src="./assets/2026-04-30 141737.png" width="700">

<img src="./assets/2026-04-30 142344.png" width="700">

<img src="./assets/2026-04-30 150936.png" width="700">

<img src="./assets/2026-04-30 152936.png" width="700">

<img src="./assets/2026-04-30 153043.png" width="700">

После выполнения, parqet файлы находятся в бакете

<img src="./assets/2026-04-30 153620.png" width="700">