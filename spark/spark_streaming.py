from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import json
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import split, to_json, struct, col, udf, date_format, window, sum, avg, count, desc, lag, abs, year, month, weekofyear, expr, when, lit, concat
from pyspark.sql import Window
from pyspark.sql.functions import max as spark_max, min as spark_min 

# Initialize Spark session
spark = SparkSession.builder \
    .appName("pyspark-notebook") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.0") \
    .getOrCreate()

# Read streaming data from Kafka  
kafka_stream = spark.readStream \
    .format('kafka') \
    .option('kafka.bootstrap.servers', 'kafka:9092') \
    .option('subscribe', 'project_data1_csv') \
    .option("failOnDataLoss", "false") \
    .option('startingOffsets', 'earliest') \
    .load() \
    .selectExpr("CAST(value AS STRING)")

# Updated schema with IntegerType for numeric fields
userSchema = StructType([
    StructField('Global_new_confirmed', IntegerType()),
    StructField('Global_new_deaths', IntegerType()),
    StructField('Global_new_recovered', IntegerType()),
    StructField('Global_total_confirmed', IntegerType()),
    StructField('Global_total_deaths', IntegerType()),
    StructField('Global_total_recovered', IntegerType()),
    StructField('Country_code', StringType()),
    StructField('Country_name', StringType()),
    StructField('Country_new_deaths', IntegerType()),
    StructField('Country_new_recovered', IntegerType()),
    StructField('Country_new_confirmed', IntegerType()),
    StructField('Country_total_deaths', IntegerType()),
    StructField('Country_total_confirmed', IntegerType()),
    StructField('Country_total_recovered', IntegerType()),
    StructField('Country_slug', StringType()),
    StructField('Extracted_timestamp', TimestampType())
])

def parse_data_from_kafka_message(sdf, schema):
    assert sdf.isStreaming == True, "DataFrame doesn't receive streaming data"
    col = split(sdf['value'], ',')
    for idx, field in enumerate(schema):
        sdf = sdf.withColumn(field.name, col.getItem(idx).cast(field.dataType))
    return sdf.select([field.name for field in schema])

df = parse_data_from_kafka_message(kafka_stream, userSchema)

# Define UDFs for additional computations - Updated to handle integer inputs
def compute_recovery_rate(total_recovered, total_confirmed):
    try:
        return float(total_recovered) / float(total_confirmed) * 100 if total_confirmed > 0 else 0.0
    except:
        return None

def compute_death_rate(total_deaths, total_confirmed):
    try:
        return float(total_deaths) / float(total_confirmed) * 100 if total_confirmed > 0 else 0.0
    except:
        return None

recovery_rate_udf = udf(compute_recovery_rate, DoubleType())  # Changed to DoubleType for decimal results
death_rate_udf = udf(compute_death_rate, DoubleType())

# Process country data
country_df = df.withColumn("Recovery_Rate", 
    recovery_rate_udf(col("Country_total_recovered"), col("Country_total_confirmed"))) \
    .withColumn("Death_Rate", 
    death_rate_udf(col("Country_total_deaths"), col("Country_total_confirmed")))

country_grouped = country_df.groupBy(
    "Country_code", "Country_name", "Country_new_deaths", "Country_new_recovered",  
    "Country_new_confirmed", "Extracted_timestamp", "Recovery_Rate", "Death_Rate"
).count()


# Process global data
global_grouped = df.groupBy(
    "Global_new_confirmed", "Global_new_deaths", "Global_new_recovered",
    "Global_total_confirmed", "Global_total_deaths", "Global_total_recovered",
    "Extracted_timestamp"
).count()
# Prepare outputs for Kafka
country_output = country_grouped.select(to_json(struct(
    'Country_code', 'Country_name', 'Country_new_deaths',
    'Country_new_recovered', 'Country_new_confirmed',
    date_format('Extracted_timestamp', 'yyyy-MM-dd HH:mm:ss').alias('Extracted_timestamp'), 'Recovery_Rate', 'Death_Rate'
)).alias('value'))


global_output = global_grouped.select(to_json(struct(
    'Global_new_confirmed', 'Global_new_deaths', 'Global_new_recovered',
    'Global_total_confirmed', 'Global_total_deaths', 'Global_total_recovered',
    date_format('Extracted_timestamp', 'yyyy-MM-dd HH:mm:ss').alias('Extracted_timestamp'),
)).alias('value'))

# Define continent mapping
continent_mapping = {
    'Asia': ['AF', 'BH', 'BD', 'BN', 'KH', 'CN', 'IN', 'ID', 'IR', 'IQ', 'IL', 'JP', 'JO', 'KZ', 'KR', 'KW', 'KG', 'LA', 'LB', 'MY', 'MV', 'MM', 'NP', 'OM', 'PK', 'PH', 'QA', 'SA', 'SG', 'LK', 'SY', 'TW', 'TJ', 'TH', 'TR', 'TM', 'AE', 'UZ', 'VN', 'YE'],
    'Europe': ['AL', 'AD', 'AT', 'BY', 'BE', 'BA', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 'HU', 'IS', 'IE', 'IT', 'LV', 'LI', 'LT', 'LU', 'MT', 'MD', 'MC', 'ME', 'NL', 'NO', 'PL', 'PT', 'RO', 'RU', 'SM', 'RS', 'SK', 'SI', 'ES', 'SE', 'CH', 'UA', 'GB', 'VA'],
    'Africa': ['DZ', 'AO', 'BJ', 'BW', 'BF', 'BI', 'CM', 'CV', 'CF', 'TD', 'KM', 'CD', 'DJ', 'EG', 'GQ', 'ER', 'ET', 'GA', 'GM', 'GH', 'GN', 'GW', 'CI', 'KE', 'LS', 'LR', 'LY', 'MG', 'MW', 'ML', 'MR', 'MU', 'MA', 'MZ', 'NA', 'NE', 'NG', 'RW', 'ST', 'SN', 'SC', 'SL', 'SO', 'ZA', 'SS', 'SD', 'TZ', 'TG', 'TN', 'UG', 'EH', 'ZM', 'ZW'],
    'North America': ['AG', 'BS', 'BB', 'BZ', 'CA', 'CR', 'CU', 'DM', 'DO', 'SV', 'GD', 'GT', 'HT', 'HN', 'JM', 'MX', 'NI', 'PA', 'KN', 'LC', 'VC', 'TT', 'US'],
    'South America': ['AR', 'BO', 'BR', 'CL', 'CO', 'EC', 'GY', 'PY', 'PE', 'SR', 'UY', 'VE'],
    'Oceania': ['AU', 'FJ', 'NZ', 'PG']
}

get_continent = udf(lambda code: next((k for k, v in continent_mapping.items() if code in v), "Other"), StringType())

# Analysis sections
# 1. Continent-based Analysis 
continent_analysis = country_df \
    .withColumn("Continent", get_continent(col("Country_code"))) \
    .withWatermark("Extracted_timestamp", "7 days") \
    .groupBy(
        "Continent",
        window("Extracted_timestamp", "7 days", "7 days")  
    ) \
    .agg(
        sum("Country_new_confirmed").alias("Continent_New_Cases"),
        sum("Country_new_deaths").alias("Continent_New_Deaths"),
        sum("Country_new_recovered").alias("Continent_New_Recovered"),
        avg("Death_Rate").alias("Avg_Death_Rate"),
        avg("Recovery_Rate").alias("Avg_Recovery_Rate")
    )

# 2. Weekly Trends Analysis 
weekly_analysis = country_df \
    .withWatermark("Extracted_timestamp", "7 days") \
    .groupBy(
        "Country_code", 
        "Country_name",
        window("Extracted_timestamp", "7 days", "7 days")
    ) \
    .agg(
        sum("Country_new_confirmed").alias("Weekly_New_Cases"),
        sum("Country_new_deaths").alias("Weekly_New_Deaths"),
        avg("Death_Rate").alias("Weekly_Death_Rate"),
        ((spark_max("Country_new_confirmed") - spark_min("Country_new_confirmed")) / spark_min("Country_new_confirmed") * 100)
        .alias("Weekly_Growth_Rate")
    )

# 3. Top 10 Most Affected Countries - Monthly Analysis
top_countries = country_df \
    .withWatermark("Extracted_timestamp", "30 days") \
    .groupBy(
        "Country_code", 
        "Country_name",
        window("Extracted_timestamp", "30 days", "30 days")  
    ) \
    .agg(
        sum("Country_new_confirmed").alias("Total_Cases"),
        sum("Country_new_deaths").alias("Total_Deaths"),
        avg("Death_Rate").alias("Average_Death_Rate"),
        avg("Country_new_confirmed").alias("Monthly_Avg_Cases"),
        avg("Country_new_deaths").alias("Monthly_Avg_Deaths")
    ) \
    .orderBy(desc("Total_Cases")) \
    .limit(10)


# output
continent_output = continent_analysis.select(to_json(struct(
    "Continent",
    date_format(col("window.start"), "yyyy-MM-dd HH:mm:ss").alias("window_start"),
    date_format(col("window.end"), "yyyy-MM-dd HH:mm:ss").alias("window_end"),
    "Continent_New_Cases",
    "Continent_New_Deaths",
    "Continent_New_Recovered",
    "Avg_Death_Rate",
    "Avg_Recovery_Rate"
)).alias("value"))

weekly_output = weekly_analysis.select(to_json(struct(
    "Country_code",
    "Country_name",
    date_format(col("window.start"), "yyyy-MM-dd HH:mm:ss").alias("window_start"),
    date_format(col("window.end"), "yyyy-MM-dd HH:mm:ss").alias("window_end"),
    "Weekly_New_Cases",
    "Weekly_New_Deaths",
    "Weekly_Death_Rate",
    "Weekly_Growth_Rate"
)).alias("value"))

top_countries_output = top_countries.select(to_json(struct(
    "Country_code",
    "Country_name",
    date_format(col("window.start"), "yyyy-MM-dd HH:mm:ss").alias("window_start"),
    date_format(col("window.end"), "yyyy-MM-dd HH:mm:ss").alias("window_end"),
    "Total_Cases",
    "Total_Deaths",
    "Average_Death_Rate",
    "Monthly_Avg_Cases",
    "Monthly_Avg_Deaths"
)).alias("value"))

query1 = country_output.writeStream \
    .format("kafka") \
    .outputMode("complete") \
    .option("failOnDataLoss", "false") \
    .option('checkpointLocation', '/checkpoint/country') \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("topic", "covid_country_metrics") \
    .start()

query2 = global_output.writeStream \
    .format("kafka") \
    .outputMode("complete") \
    .option("failOnDataLoss", "false") \
    .option('checkpointLocation', '/checkpoint/global') \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("topic", "covid_global_metrics") \
    .start()

query3 = continent_output.writeStream \
    .format("kafka") \
    .outputMode("complete") \
    .option("failOnDataLoss", "false") \
    .option("checkpointLocation", "/checkpoint/continent") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("topic", "covid_analysis_continent") \
    .start()


query4 = weekly_output.writeStream \
    .format("kafka") \
    .outputMode("complete") \
    .option("failOnDataLoss", "false") \
    .option("checkpointLocation", "/checkpoint/weekly") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("topic", "covid_analysis_weekly") \
    .start()

query5 = top_countries_output.writeStream \
    .format("kafka") \
    .outputMode("complete") \
    .option("failOnDataLoss", "false") \
    .option("checkpointLocation", "/checkpoint/top_countries") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("topic", "covid_analysis_top_countries") \
    .start()

# Wait for all queries to terminate
spark.streams.awaitAnyTermination()
