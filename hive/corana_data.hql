CREATE EXTERNAL TABLE IF NOT EXISTS covid_global (
    global_new_confirmed INT,
    global_new_deaths INT, 
    global_new_recovered INT,
    global_total_confirmed INT,
    global_total_deaths INT,
    global_total_recovered INT,
    extracted_timestamp TIMESTAMP
)
ROW FORMAT DELIMITED 
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/covid19_data1/global_kafka_out';

CREATE EXTERNAL TABLE IF NOT EXISTS covid_country (
    country_code STRING,
    country_name STRING,
    country_total_deaths INT,
    country_new_confirmed INT,
    country_total_recovered INT,
    death_rate DECIMAL(10,6),
    recovery_rate DECIMAL(10,6),
    extracted_timestamp TIMESTAMP
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/covid19_data1/country_kafka_out';


-- Bảng cho top countries data
CREATE EXTERNAL TABLE IF NOT EXISTS top_countries_metrics (
    country_name STRING,
    country_code STRING,
    average_death_rate DOUBLE,
    monthly_avg_cases DOUBLE,
    monthly_avg_deaths DOUBLE,
    total_cases BIGINT,
    total_deaths BIGINT,
    window_start TIMESTAMP,
    window_end TIMESTAMP
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/covid19_data1/top_countries_kafka_out';

-- Bảng cho weekly analysis data
CREATE EXTERNAL TABLE IF NOT EXISTS weekly_metrics (
    country_code STRING,
    country_name STRING,
    weekly_death_rate DOUBLE,
    weekly_new_cases BIGINT,
    weekly_new_deaths BIGINT,
    window_start TIMESTAMP,
    window_end TIMESTAMP,
    weekly_growth_rate DOUBLE
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/covid19_data1/weekly_kafka_out';

-- Bảng cho continent analysis data
CREATE EXTERNAL TABLE IF NOT EXISTS continent_metrics (
    continent STRING,
    continent_new_cases BIGINT,
    continent_new_deaths BIGINT,
    continent_new_recovered BIGINT,
    avg_death_rate DOUBLE,
    avg_recovery_rate DOUBLE,
    window_start TIMESTAMP,
    window_end TIMESTAMP
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/covid19_data1/continent_kafka_out';