#!/usr/bin/env python3
from pyspark.sql import SparkSession
from pyspark.sql.functions import to_json, struct, col

spark = SparkSession.builder.appName("kafka-write").getOrCreate()

# Чтение CSV из  бакета
df = spark.read.option("header", True).csv("s3a://kickstarter-data-bucket/ks-projects-201801.csv")

# Преобразование строки во вложенный JSON
df_json = df.select(
    to_json(
        struct(
            col("ID").alias("id"),
            col("name").alias("name"),
            struct(
                col("category").alias("primary"),
                col("main_category").alias("main")
            ).alias("category"),
            struct(
                col("goal").cast("double").alias("goal"),
                col("pledged").cast("double").alias("pledged"),
                col("currency").alias("currency")
            ).alias("financial"),
            struct(
                col("launched").alias("launched"),
                col("deadline").alias("deadline")
            ).alias("dates"),
            col("backers").cast("int").alias("backers"),
            col("country").alias("country"),
            col("state").alias("state")
        )
    ).alias("value")
)

# Запись в Kafka
df_json.write \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "rc1b-4hggl9kfv1uqag9l.mdb.yandexcloud.net:9091") \
    .option("topic", "dataproc-kafka-topic") \
    .option("kafka.security.protocol", "SASL_SSL") \
    .option("kafka.sasl.mechanism", "SCRAM-SHA-512") \
    .option("kafka.sasl.jaas.config",
            'org.apache.kafka.common.security.scram.ScramLoginModule required '
            'username="user1" '
            'password="password1";') \
    .save()

spark.stop()