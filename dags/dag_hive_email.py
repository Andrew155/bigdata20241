from airflow import DAG
from airflow.providers.apache.hive.operators.hive import HiveOperator
from airflow.operators.email_operator import EmailOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from airflow.hooks.hive_hooks import HiveServer2Hook

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
    'email': ['nguyenlongnhatt155@gmail.com'],
    'email_on_failure': False  
}

def generate_covid_report(**context):
    hive_hook = HiveServer2Hook(hiveserver2_conn_id='hive_nam')
    
    # Query lay 1 vai thong tin report
    latest_data_query = """
    SELECT 
        global_new_confirmed,
        global_new_deaths,
        global_new_recovered,
        extracted_timestamp
    FROM covid_global 
    ORDER BY extracted_timestamp DESC
    LIMIT 1
    """
    latest_result = hive_hook.get_first(latest_data_query)

    # Query cho top 3 quốc gia
    top_countries_query = """
    SELECT 
        country_name,
        country_new_confirmed
    FROM covid_country
    WHERE country_new_confirmed > 0
    ORDER BY country_new_confirmed DESC
    LIMIT 3
    """
    top_countries = hive_hook.get_records(top_countries_query)
    # Format email
    email_content = f"""
    <h2>COVID-19 Daily Update Report</h2>
    <p><strong>Report Date:</strong> {latest_result[3]}</p>
    
    <h3>Global Daily Numbers:</h3>
    <ul>
        <li>New Cases: {latest_result[0]:,}</li>
        <li>New Deaths: {latest_result[1]:,}</li>
        <li>New Recoveries: {latest_result[2]:,}</li>
    </ul>
    
    <h3>Top 3 Countries (New Cases):</h3>
    <ul>
    """
    
    for country in top_countries:
        email_content += f"<li>{country[0]}: +{country[1]:,} new cases</li>"
    
    email_content += "</ul>"
    
    return email_content
with DAG('covid_data_pipeline',
         default_args=default_args,
         schedule_interval='@daily',
         catchup=False) as dag:

    # Task 1: Create External Tables
    create_external_tables = HiveOperator(
        task_id='create_external_tables',
        hql="""
        -- Global metrics table
        CREATE EXTERNAL TABLE IF NOT EXISTS covid_global (
            global_new_confirmed INT,
            global_new_deaths INT,
            global_new_recovered INT,
            global_total_confirmed INT,
            global_total_deaths INT,
            global_total_recovered INT,
            extracted_timestamp TIMESTAMP
        )
        ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
        STORED AS TEXTFILE
        LOCATION '/covid19_data1/global_kafka_out';

        -- Country metrics table
        CREATE EXTERNAL TABLE IF NOT EXISTS covid_country (
            country_code STRING,
            country_name STRING,
            country_new_deaths INT,
            country_new_confirmed INT,
            country_new_recovered INT,
            death_rate DECIMAL(10,6),
            recovery_rate DECIMAL(10,6),
            extracted_timestamp TIMESTAMP
        )
        ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
        STORED AS TEXTFILE
        LOCATION '/covid19_data1/country_kafka_out';

        -- Top countries metrics table
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
        ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
        STORED AS TEXTFILE
        LOCATION '/covid19_data1/top_countries_kafka_out';

        -- Weekly metrics table
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
        ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
        STORED AS TEXTFILE
        LOCATION '/covid19_data1/weekly_kafka_out';

        -- Continent metrics table
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
        ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
        STORED AS TEXTFILE
        LOCATION '/covid19_data1/continent_kafka_out';
        """,
        hive_cli_conn_id='hive_nam'
    )

    # Task 2: Validate Data
    validate_data = HiveOperator(
        task_id='validate_data',
        hql="""
        SELECT 'Global Metrics' as table_name, COUNT(*) as record_count FROM covid_global
        UNION ALL
        SELECT 'Country Metrics', COUNT(*) FROM covid_country
        UNION ALL
        SELECT 'Top Countries Metrics', COUNT(*) FROM top_countries_metrics
        UNION ALL
        SELECT 'Weekly Metrics', COUNT(*) FROM weekly_metrics
        UNION ALL
        SELECT 'Continent Metrics', COUNT(*) FROM continent_metrics;
        """,
        hive_cli_conn_id='hive_nam'
    )

    # Task 3: Generate Report
    generate_report = PythonOperator(
        task_id='generate_covid_report',
        python_callable=generate_covid_report,
        provide_context=True
    )

    # Task 4: Send Email
    send_report = EmailOperator(
        task_id='send_covid_report',
        to=['nguyenlongnhatt155@gmail.com'],
        subject='COVID-19 Report',
        html_content="{{ task_instance.xcom_pull(task_ids='generate_covid_report') }}"
    )

    # Define task dependencies
    create_external_tables >> validate_data >> generate_report >> send_report
