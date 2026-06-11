#!/usr/bin/env python3
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, IntegerType, DoubleType

spark = SparkSession.builder.appName("kafka-read-stream").getOrCreate()

# Схема вложенного JSON 
category_schema = StructType().add("primary", StringType()).add("main", StringType())
financial_schema = StructType().add("goal", DoubleType()).add("pledged", DoubleType()).add("currency", StringType())
dates_schema = StructType().add("launched", StringType()).add("deadline", StringType())

json_schema = StructType() \
    .add("id", StringType()) \
    .add("name", StringType()) \
    .add("category", category_schema) \
    .add("financial", financial_schema) \
    .add("dates", dates_schema) \
    .add("backers", IntegerType()) \
    .add("country", StringType()) \
    .add("state", StringType())

# Чтение из Kafka
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "rc1b-4hggl9kfv1uqag9l.mdb.yandexcloud.net:9091") \
    .option("subscribe", "dataproc-kafka-topic") \
    .option("kafka.security.protocol", "SASL_SSL") \
    .option("kafka.sasl.mechanism", "SCRAM-SHA-512") \
    .option("kafka.sasl.jaas.config",
            'org.apache.kafka.common.security.scram.ScramLoginModule required '
            'username="user1" '
            'password="password1";') \
    .option("startingOffsets", "earliest") \
    .load() \
    .selectExpr("CAST(value AS STRING) as json")

# Разворачиваем JSON
df_parsed = df_raw.select(from_json(col("json"), json_schema).alias("data")).select("data.*")

# Вывод в консоль и сохранение в бакет
query = df_parsed.writeStream \
    .outputMode("append") \
    .format("parquet") \
    .option("path", "s3a://kickstarter-data-bucket/kafka_results/") \
    .option("checkpointLocation", "s3a://kickstarter-data-bucket/checkpoints/") \
    .trigger(once=True) \
    .start()

query.awaitTermination()

spark.stop()