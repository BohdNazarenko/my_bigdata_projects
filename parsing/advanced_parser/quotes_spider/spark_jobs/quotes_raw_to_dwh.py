from pyspark.sql import SparkSession, functions as F, types as T

# Initialize Spark session
spark = (SparkSession.builder
    .appName("quotes_raw_to_dwh_flat")
    .config("spark.jars.packages", "org.postgresql:postgresql:42.7.4")  # include PostgreSQL JDBC driver
    .getOrCreate())

# PostgreSQL connection parameters
jdbc_url = "jdbc:postgresql://localhost:5432/quotes"
props = {"user": "postgres", "password": "postgres", "driver": "org.postgresql.Driver"}

# Read raw data from PostgreSQL
raw = spark.read.jdbc(jdbc_url, "public.quotes", properties=props)

# Define schema for JSON field "tags"
tags_schema = T.ArrayType(T.StringType())

# Clean and transform data
clean = (raw
    .withColumn("text", F.when(F.length("text") > 0, F.col("text")))  # remove empty text
    .withColumn("author", F.when(F.length("author") > 0, F.col("author")).otherwise(F.lit("Unknown")))  # fill empty authors
    .withColumn("tags", F.from_json(F.col("tags").cast("string"), tags_schema))  # parse JSON -> array
    .withColumn("created_at", F.col("parsed_at").cast("timestamp"))  # cast to timestamp
    .dropna(subset=["text", "author", "created_at"])  # drop rows with nulls
    .dropDuplicates(["text", "author"])  # remove duplicates
)

# Write cleaned data to DWH table
clean.select("text", "author", "tags", "created_at") \
    .write.jdbc(jdbc_url, "public.dwh_quotes_flat", mode="append", properties=props)

# Stop Spark session
spark.stop()