from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count

spark = SparkSession.builder.appName("KickstarterAgg").enableHiveSupport().getOrCreate()

df = spark.read \
    .option("header", True) \
    .option("quote", "\"") \
    .option("escape", "\"") \
    .option("multiLine", False) \
    .csv("s3a://kickstarter-raw-bucket/ks-projects-201801.csv")

result = df.groupBy("main_category", "state").agg(count("*").alias("cnt"))

result.write.mode("overwrite") \
    .option("path", "s3a://kickstarter-data-bucket/kickstarter_stats") \
    .saveAsTable("kickstarter_stats")