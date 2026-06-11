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

```text
call_id, call_time, client_id, region_code, campaign_type, call_status, client_response, duration_sec, follow_up_required
```

```text
call_20260501_001, 2026-05-01 11:42:15, client_4412, DE - HE, credit_card_offer, answered, interested, 184, true
```

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

```text
application_id, event_time, customer_id, region_code, product_type, requested_amount, term_months, credit_score, risk_level, decision_status, approved_amount, channel, employee_review_flag, processing_time_sec
```

```text
app_20260501_001, 2026-05-01 09:14:22, cust_88421, DE-HE, cash_loan, 12000, 24, 734, low, approved, 12000, mobile, false, 12
```

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

### Задание 2

Задание выполняется по инструкции

https://yandex.cloud/ru/docs/managed-airflow/tutorials/data-processing-automation#%D1%83%D0%BF%D1%80%D0%BE%D1%89%D0%B5%D0%BD%D0%BD%D0%B0%D1%8F-%D0%BD%D0%B0%D1%81%D1%82%D1%80%D0%BE%D0%B9%D0%BA%D0%B0_2

Создадим кластер Apache Hive™ Metastore

<img src="assets/2026-06-10 203628.jpg" width="700">

Создадим кластер  Managed Service for Apache Airflow™.

<img src="assets/2026-06-10 204957.jpg" width="700">

Файлы `DAG` из `task_final_2\dags\kickstarter_dag.py`
и задания `Spark` из `task_final_2\spark_jobs\spark_agg.py`
поместим в бакет `kickstarter-data-bucket` в каталоги `dags` и `scripts` соответственно

<img src="assets/2026-06-10 205316.jpg" width="700">

Откроем `UI` airflow и запустим `DAG`

<img src="assets/2026-06-10 205347.jpg" width="700">

Дождемся успешного выполнения `DAG`

<img src="assets/2026-06-10 214531.jpg" width="700">

И проверим результат в бакете

<img src="assets/2026-06-10 214810.jpg" width="700">

<img src="assets/2026-06-10 214911.jpg" width="700">

Полученные файлы 
`task_final_2\results\_SUCCESS` и `task_final_2\results\part-00000-782f468c-3def-4fbb-bb3d-27d108aa4da5-c000.snappy.parquet`

Так же после выполнения в бакете появились логи

<img src="assets/2026-06-10 215408.jpg" width="700">

<img src="assets/2026-06-10 215432.jpg" width="700">

<img src="assets/2026-06-10 215502.jpg" width="700">

Файл `csv` из бакета обработан. Задание 2 выполено.

### Задание 3

Задание 3 выполняется по инструкции
https://yandex.cloud/ru/docs/managed-kafka/tutorials/data-processing

Создадим кластер `Yandex Data Processing`

<img src="assets/2026-06-11 175822.jpg" width="700">

и создадим кластер `Managed Service for Apache Kafka®`

<img src="assets/2026-06-11 181046.jpg" width="700">

Создадим бакет и положим в него исходный `csv` файл и скрипты для записи и чтения в `Kafka`

Датасет для задания использован тот же что и в первом задании
https://www.kaggle.com/datasets/kemical/kickstarter-projects?resource=download&select=ks-projects-201801.csv

<img src="assets/2026-06-11 195450.jpg" width="700">

В ходе чтения, плоский `csv` файл будет записан в топик `Kafka` в виде `json` файла, а затем `json` файл будет преобразован в плоский вид.

Запустим выполнения задания в `Yandex Data Processing`
Файл задания `task_final_2\data_proc_tasks\kafka-write.py`
Чтения задания из бакета 

<img src="assets/2026-06-11 204838.jpg" width="700">

После выполнения задания на чтения `csv` файла, преобразования его в `json` и записи в топики `kafka` проверия в UI `kafka` что в топиках есть данные.

<img src="assets/2026-06-11 210323.jpg" width="700">

<img src="assets/2026-06-11 204920.jpg" width="700">

<img src="assets/2026-06-11 204938.jpg" width="700">

Проверим что данные действительно представляют собой `json`

<img src="assets/2026-06-11 210041.jpg" width="700">

Теперь выполним чтение из `Kafka` `json` данных с преобразованием их в плоский вид.
Выполнять будем с помощью задания, файл задания `task_final_2\data_proc_tasks\kafka-read-stream.py` находится в бакете.

<img src="assets/2026-06-11 205723.jpg" width="700">

После успешного выполнения, проверим результат в бакете.

<img src="assets/2026-06-11 210425.jpg" width="700">

На этом задание 3 выполнено.

### Задание 4

Создадим подключение и привязку в `Yandex Query` к parquet файлу 
полученному в задании 2.
файл `task_final_2\results\part-00000-c481637e-b7b7-4855-b791-145755b085d1-c000.snappy.parquet` 

<img src="assets/2026-06-10 222736.jpg" width="700">

Проверим доступность данных

<img src="assets/2026-06-10 222928.jpg" width="700">

Затем создадим в `Yandex DataLens` 
- подключение
- датасет
- чарт


<img src="assets/2026-06-10 224405.jpg" width="700">

<img src="assets/2026-06-10 224843.jpg" width="700">

<img src="assets/2026-06-10 225127.jpg" width="700">

<img src="assets/2026-06-10 225232.jpg" width="700">

Данные визуализированны. Задание 4 выполнено.