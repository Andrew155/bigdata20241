FROM apache/superset:lastest
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    g++ \
    build-essential \
    libpq-dev \
    && apy-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pyhive[hive] thrift sasl thrift-sasl pandas sqlalchemy