# COVID-19 Data Pipeline Project
<img src="https://scontent.fhan2-3.fna.fbcdn.net/v/t1.15752-9/462571607_979947827484140_4826484144837939755_n.png?_nc_cat=111&ccb=1-7&_nc_sid=9f807c&_nc_ohc=V0OrYMqnRvcQ7kNvgEFlCav&_nc_oc=AdhaMiS-XNnKDdXKtN86_KFQYUa-Hicr_EFc3SE1jBtw0cr7-CVkq-EDZmF1u--G_rq0bghYqczGCYFGR-AljzR3&_nc_zt=23&_nc_ht=scontent.fhan2-3.fna&oh=03_Q7cD1QEaVUB_MHYlQpNl3Ze9TE_Bd912DzpScKb8U1BZfkQF9A&oe=67892D33" width="800" alt="Project Architecture"/>

## Overview
This project is designed to store and process COVID-19 data using various big data technologies like Kafka, Spark, Hive, and Superset, with the goal of creating a scalable data pipeline for COVID-19-related information. The pipeline includes several stages: data ingestion via Kafka, data transformation with Spark, storage in HDFS, and visualization using Superset.

## System Requirements
- RAM: Minimum 16 GB
- Storage: Minimum 30 GB
- Operating System: Linux-based system (Ubuntu or similar)
- Docker: To run the services using Docker Compose
- EC2 (Optional): If using AWS EC2, ensure an instance with at least the minimum specs

## Setup Instructions

### 1. Set up an EC2 instance (Optional)
1. Create an EC2 account on AWS
2. Launch an EC2 instance with at least 16 GB RAM and 30 GB storage
3. Configure SSH access to the instance by generating an SSH key pair and downloading the .pem file
4. SSH into the instance:
   ```bash
   chmod 400 /path/to/your-key.pem
   ssh -i /path/to/your-key.pem ec2-user@your-instance-public-ip
   ```

### 2. Clone the Project Repository
```bash
git clone https://github.com/Andrew155/bigdata20241/tree/main
```

### 3. Install Docker and Docker Compose
Install Docker:
```bash
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl enable docker
sudo systemctl start docker
```

Install Docker Compose:
```bash
sudo apt-get install -y docker-compose
```

### 4. Start the Services with Docker Compose
Navigate to the project directory and run:
```bash
docker-compose up -d
```

## Data Pipeline Flow
The pipeline consists of the following steps:
1. NiFi Flow: Ingests COVID-19 data from an API into Kafka
2. Spark Streaming: Processes data from Kafka and stores it in HDFS
3. Airflow DAG: Manages and schedules tasks like creating an external table in Hive and sending email reports
4. Hive: Stores processed data in tables for querying
5. Superset: Visualizes the processed data for reporting

## Component Setup and Usage

### Kafka Topics
To check the Kafka topic:
```bash
docker exec -i -t hdp_kafka bash
bin/kafka-console-consumer.sh --bootstrap-server kafka:9092 --from-beginning --topic your-topic
```

### Running Spark Streaming
Copy the spark_streaming.py file to the Docker container:
```bash
docker cp /path/to/your-local-file/spark_streaming.py hdp_spark-master:/spark_streaming.py
```

Run the Spark job:
```bash
docker exec -it hdp_spark-master bash
chmod 755 /spark_streaming.py
./spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.0 --master local[2] /spark_streaming.py
```

### Hive Queries
To interact with Hive:
```bash
docker exec -i -t hdp_hive-server bash
hive
```

### Superset Setup
Create an admin account for Superset:
```bash
docker exec -i -t superset bash
superset fab create-admin --username admin --password admin --firstname Admin --lastname User --email admin@superset.com
superset db upgrade
superset init
```

Restart Superset:
```bash
docker-compose restart superset
```

## File Path Modifications
Make sure to adjust the file paths according to your environment:
- Kafka Topics: `/your-kafka-topic`
- HDFS Locations: `/path/to/your/hdfs/directory`
- Spark Job File: `/path/to/your-local-file/spark_streaming.py`
- Airflow DAG Script: `/path/to/your-airflow-dags/dag_hive_script.py`

## Useful Commands

### Checking HDFS Files
```bash
docker exec -i -t hdp_namenode bash
hadoop fs -ls /path/to/hdfs/directory
hadoop fs -cat /path/to/file/on/hdfs
```

### Safe Mode Check in HDFS
```bash
hadoop dfsadmin -safemode get
hadoop dfsadmin -safemode leave
```
You can also check the UI webserver at http://localhost:9870.

### Kafka Consumer
To consume Kafka messages:
```bash
bin/kafka-console-consumer.sh --bootstrap-server kafka:9092 --from-beginning --topic your-topic
```