# Практическая работа. Модуль 4 (экзамен)

**Выполнил - Третьяков Александр Юрьевич**


Дисциплина ETL-процессы  
Тема реализация ETL-процесса  
Форма проверки Задание проверяется преподавателем  
Имя преподавателя Артём Озерков  
Время выполнения 10 часов  

## Цель задания

• Освоить работу с Yandex DataTransfer

• Научиться выполнять автоматизацию работы с Yandex Data Processing (Hadoop + Spark)

• Освоить работу с топиками Apache Kafka с помощью PySpark-заданий (Yandex Data Processing)

• Построить дашборды в DataLens для визуализации результатов

## Инструменты для выполнения ДЗ

Чтобы выполнить задания, вам понадобятся:

• Облачные сервисы: Yandex Cloud (Data Processing, DataLens, Managed Service for Apache Airflow, Managed Service for Apache Kafka)

• Базы данных: Hive/Spark SQL, YDB

• Язык запросов: SQL (HiveQL, Spark SQL, YQL)

• Инструменты разработки: GitHub (для хранения SQL-скриптов), Yandex Object Storage

## Правила приёма работы

Прикрепить в ЛМС ссылки на репозиторий GitHub. Репозиторий должен содержать подробный отчёт о проделанной работе. Настройки репозитория должны быть public.

## Важно:

• убедитесь, что по ссылке есть доступ, так как иногда доступ может быть закрыт для другого логина;

• название должно содержать фамилию и имя студента и название задания.

## Критерии оценивания

| Задание | Баллы |
|---------|-------|
| Задание 1. Работа с Yandex DataTransfer | 2 |
| Задание 2. Автоматизация работы с Yandex Data Processing при помощи Apache AirFlow | 2 |
| Задание 3. Работа с топиками Apache Kafka® с помощью PySpark-заданий в Yandex Data Processing | 3 |
| Задание 4. Визуализация в DataLens | 1 |
| **Итого** | **8** |

• Максимальное количество баллов, которое можно получить, отлично выполнив все требования, заявленные в критериях оценки, — 8.

• Преподаватель может добавить 1–2 балла к этой оценке за творческий подход к выполнению проекта, проработку решения, выходящую за рамки программы и расширяющую функционал проекта.

## Описание задания

В рамках развития корпоративной платформы данных необходимо интегрировать новые источники данных и реализовать дополнительные ETL/Streaming-процессы для расширения аналитических возможностей системы.

### Задание 1. Работа с Yandex DataTransfer


Требуется перенести данные из Managed Service for YDB в объектное хранилище Object Storage. Выполнить необходимо с использованием сервиса Data Transfer.

1. Создать БД Yandex DataBase.

2. Подготовить данные:

• transactions_v2

Данные можно взять здесь или подготовить их самостоятельно. Примерный объём не менее 30 Мб. Примерный формат:

call_id, call_time, client_id, region_code, campaign_type, call_status, client_response, duration_sec, follow_up_required

call_20260501_001, 2026-05-01 11:42:15, client_4412, DE - HE, credit_card_offer, answered, interested, 184, true

3. Создать трансфер в Object Storage.

4. Проверить работоспособность трансфера.

Все SQL-скрипты (YQL) необходимо сохранить в репозитории домашней работы (GitHub).

### Задание 2. Автоматизация работы с Yandex Data Processing при помощи Apache AirFlow.

Требуется обрабатывать файлы (parquet или CSV) из внешнего источника. Размер входящих файлов меняется в различные дни месяца.

Данные можно взять здесь или подготовить их самостоятельно.

1. Подготовить инфраструктуру.

2. Подготовить PySpark-задание.

• Создать кластер Yandex Data Processing

• Создать и запустить задание PySpark

• Удалить кластер Yandex Data Processing

3. Подготовить DAG-файл, запустить и проверить результат.

Требуемый объём файла не менее 50 Мб. Примерная структура плоской таблицы:

application_id, event_time, customer_id, region_code, product_type, requested_amount, term_months, credit_score, risk_level, decision_status, approved_amount, channel, employee_review_flag, processing_time_sec

app_20260501_001, 2026-05-01 09:14:22, cust_88421, DE-HE, cash_loan, 12000, 24, 734, low, approved, 12000, mobile, false, 12

### Задание 3. Работа с топиками Apache Kafka® с помощью PySpark-заданий в Yandex Data Processing.

Требуется настроить чтение топиков kafka для реализации потоковой аналитики.

1. Подготовить архитектуру

2. Создать задания PySpark

3. Разложить JSON в плоский вид

Требуемый объём для передачи не менее 20 Мб. Пример JSON для отправки в топик:

```json
{
  "application_id": "loan_784512",
  "customer": {
    "customer_id": "cust_441",
    "region": "DE-HE"
  },
  "loan": {
    "amount": 15000,
    "term_months": 36
  },
  "scoring": {
    "score": 712,
    "risk_level": "medium"
  },
  "documents": [
    {
      "type": "passport",
      "status": "verified"
    }
  ],
  "decision_status": "manual_review",
  "submitted_at": "2026-05-01T10:15:11Z"
}
```

### Задание 4. Визуализация в DataLens.

С помощью Yandex DataLens построить дашборды для визуализации загруженных данных.

По завершении выполнения заданий подготовьте подробный отчёт в свободной форме с описанием проделанных действий.


<div style="page-break-after: always;"></div>

## Решение

### Задание 1

Задание выполняется по инструкции 

https://yandex.cloud/ru/docs/data-transfer/tutorials/ydb-to-object-storage


Создадим бакет Object Storage `kickstarter-data-bucket` для результатов `data transfer` из YBD.

И создадим бакет для исходных данных `kickstarter-raw-bucket`.

Датасет для задания
https://www.kaggle.com/datasets/kemical/kickstarter-projects?resource=download&select=ks-projects-201801.csv


<img src="assets/2026-06-10 111751.jpg" width="700">

Бакет для исходных данных необходим по причине того, что Yandex Cloud с 1 июня 2026 года запретил использовать новые OAuth-токены (которые можно было получить через браузер) для доступа к API и  `YBD CLI`, поэтому команды yc и ydb выдают ошибку аутентификации.


```powershell
ERROR: Unable to list clouds: rpc error: code = Unauthenticated desc = iam token create failed: rpc error: code = InvalidArgument desc = OAuth token for user 'ajetu6pbc3hnt1oaphr4', issued after '2026-06-01', is not supported for IAM token exchange
```

Загрузим датасет в бакет `kickstarter-raw-bucket`.

<img src="assets/2026-06-10 134940.jpg" width="700">

Создадим эндпоинты

<img src="assets/2026-06-10 140311.jpg" width="700">

В эндпоинте для чтения из `csv` файла укажем как создавать таблицу

<img src="assets/2026-06-10 165156.jpg" width="700">

<img src="assets/2026-06-10 165216.jpg" width="700">

Создадим трансфер типа Копирование, используя созданные эндпоинты.

<img src="assets/2026-06-10 140406.jpg" width="700">

Выполним трансфер из `csv` файла из бакета  `kickstarter-raw-bucket` в `YBD`

<img src="assets/2026-06-10 160330.jpg" width="700">

Проверим наличие данных в таблице

<img src="assets/2026-06-10 160948.jpg" width="700">

Создадим эндпоинты для трансфера из `YBD` в бакет

<img src="assets/2026-06-10 165524.jpg" width="700">

<img src="assets/2026-06-10 165653.jpg" width="700">

И создадим трансфер с этими эндпоинтами

<img src="assets/2026-06-10 165808.jpg" width="700">

<img src="assets/2026-06-10 170815.jpg" width="700">

Проверим наличие `csv` файла в бакете

<img src="assets/2026-06-10 170937.jpg" width="700">

На этом задание 1 выполнено. 