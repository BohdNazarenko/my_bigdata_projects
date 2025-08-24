from itertools import groupby

from pyspark.sql import SparkSession
from pyspark.sql import types as T, functions as F

spark = SparkSession.builder.master("local[*]").appName("RetailStoreSales").getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

#csv path
retail_part = "retail_store_sales.csv"

#Entry df
df = (spark.read
      .option("header", "True")
      .option("sep", ",")
      .option("inferSchema", "True")
      .csv(retail_part)
      )

# 1.1 First 5 rows and schema print
df.show(5)
df.printSchema()

#clean column names method
def snake_case(col_names: list[str]):
    clean_name = []

    for col_name in col_names:
        result = col_name.strip().replace(" ", "_").lower()
        clean_name.append(result)

    return clean_name


# 1.2 Cleaned column names -> ['transaction_id', 'customer_id', 'category', 'item', 'price_per_unit',
# 'quantity', 'total_spent', 'payment_method', 'location', 'transaction_date', 'discount_applied']
cleaned_names = snake_case(df.columns)
df = df.toDF(*cleaned_names)

# 1.3 Data Type Conversion
schema = T.StructType([
    T.StructField("transaction_id", T.StringType(), False),
    T.StructField("customer_id", T.StringType(), False),
    T.StructField("category", T.StringType(), False),
    T.StructField("item", T.StringType(), True),
    T.StructField("price_per_unit", T.DoubleType(), True),
    T.StructField("quantity", T.DoubleType(), True),
    T.StructField("total_spent", T.DoubleType(), True),
    T.StructField("payment_method", T.StringType(), True),
    T.StructField("location", T.StringType(), True),
    T.StructField("transaction_date", T.DateType(), False),
    T.StructField("discount_applied", T.BooleanType(), True)
])

df = spark.createDataFrame(df.rdd, schema=schema)

df.printSchema()
df.show()

# 2.1.1 Products unique
uniq_products = (df
                 .select(F.col("category").alias("cat_ref"), F.col("item").alias("item_ref"),
                         F.col("price_per_unit").alias("price_ref"))
                 .dropna(subset=["item_ref", "price_ref"])
                 .dropDuplicates(["cat_ref", "item_ref"])
                 )

uniq_products.show(30)

# 2.1.2 restored product names
name_restored_df = (df
                    .join(
    uniq_products,
    on=(df.category == uniq_products.cat_ref) & (df.price_per_unit == uniq_products.price_ref),
    how="left"
)
                    .withColumn("item",
                                F.when(F.col("item").isNull(), F.col("item_ref")).otherwise(F.col("item")))
                    .drop("item_ref", "cat_ref", "price_ref"))
name_restored_df.show(20)

# 2.2 total spend restore

df = df.withColumn("total_spent",
                   F.when(
                       F.col("total_spent").isNull() & F.col("price_per_unit").isNotNull() & F.col(
                           "quantity").isNotNull(),
                       F.col("price_per_unit") * F.col("quantity")
                   ).otherwise(F.col("total_spent"))
                   )

df.show()

# 2.3 Fill quantity и price_per_unit

df = df.withColumn("quantity",
                   F.when(
                       F.col("quantity").isNull() & F.col("total_spent").isNotNull() & F.col(
                           "price_per_unit").isNotNull() & (F.col("price_per_unit") != 0),
                       F.round((F.col("total_spent") / F.col("price_per_unit")))
                   ).otherwise(F.col("quantity"))
                   )

df = df.withColumn("price_per_unit",
                   F.when(
                       F.col("price_per_unit").isNull() & F.col("total_spent").isNotNull() & F.col(
                           "quantity").isNotNull() & (F.col("quantity") != 0),
                       F.round(F.col("total_spent") / F.col("quantity"), 2)
                   ).otherwise(F.col("price_per_unit"))
                   )

df.show()

# 2.4 Delete Category, Quantity ,Total Spent и Rrice Rer Unit if NULL

df = df.filter(
        F.col("category").isNotNull() &
        F.col("quantity").isNotNull() &
        F.col("total_spent").isNotNull() &
        F.col("price_per_unit").isNotNull()
)

df.show()

#3.1 Top 5 product popular

products_popular = (df
                    .groupBy("category")
                    .agg(F.sum("quantity").alias("sum_quantity"))
                    .orderBy(F.desc("sum_quantity"))
                    .limit(5)
)

products_popular.show()

#3.2.1 total_spent for payment_method avg

avg_payment_total_spend = (df
                     .groupby("payment_method")
                     .agg(F.round(F.avg("total_spent"), 2).alias("avg_total_spend"))
                     )
avg_payment_total_spend.show()

#3.2.2 total_spent for location avg

avg_location_total_spent = (df
                            .groupby("location")
                            .agg(F.round(F.avg("total_spent"), 2).alias("avg_total_spent"))
                            )
avg_location_total_spent.show()

#4.1 create two new columns: day_of_week and transaction_month

df = df.withColumns({"day_of_week": F.dayofweek("transaction_date"), "transaction_month" : F.dayofmonth("transaction_date")})
df.show()
#4.2 calkulate avg total_spent for day_of_week

avg_spend_per_day = (df
                           .groupby("day_of_week")
                           .agg(F.round(F.avg("total_spent"), 2).alias("avg_total_spent"))
                           .sort("day_of_week")
                           )

avg_spend_per_day.show()

#4.3 calculate avg total_spent for day_of_week

avg_total_per_month = (df
                       .groupby("transaction_month")
                       .agg(F.round(F.avg("total_spent"), 2).alias("avg_total_spent"))
                       .sort("transaction_month")
                       )

avg_total_per_month.show()


#4.4 customer_lifetime_value - sum of all transactions for all time

customer_lifetime_value = (df
                           .groupby("customer_id")
                           .agg(F.round(F.sum("total_spent"), 2).alias("customer_lifetime_value"))
                           .sort(F.desc("customer_lifetime_value"))
                           .limit(10)
                           )

customer_lifetime_value.show()


spark.stop()