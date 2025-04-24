# System Architecture

This document outlines the architecture of the ShopSight real-time product analytics pipeline.

## Components

The system consists of the following core components:

1.  **Data Simulation (`src/data_simulation`)**: A Python script that generates realistic mock product interaction events (e.g., page views, add-to-cart, purchases).
2.  **Kafka Producer (`src/kafka_producer`)**: A Python application that takes the simulated data and publishes it as messages to an Apache Kafka topic.
3.  **Apache Kafka**: Acts as the central message broker, decoupling the data producers from the stream processor. It provides a durable and scalable buffer for incoming events.
4.  **Spark Streaming Job (`src/spark_streaming`)**: An Apache Spark application that consumes events from the Kafka topic in near real-time. It performs transformations, aggregations, and potentially anomaly detection on the data stream.
5.  **Delta Lake (`data/` or configured path like S3)**: A storage layer built on top of data lakes (like HDFS or S3) that brings ACID transactions, schema enforcement, and time travel capabilities to the processed data. The Spark Streaming job writes its output to a Delta table.
6.  **Query Engine (e.g., Spark SQL, Presto, Trino)**: Tools used to query the processed data stored in the Delta Lake table for analysis, reporting, and dashboarding.

## Data Flow

1.  The **Data Simulation** script generates events.
2.  The **Kafka Producer** sends these events to the designated **Kafka** topic (`product_events` by default).
3.  The **Spark Streaming Job** subscribes to the Kafka topic, reads the incoming event stream.
4.  Inside Spark, the job parses the event data (e.g., JSON), potentially enriches it, performs necessary aggregations or calculations (e.g., counting events per product, calculating session durations).
5.  The processed data is written micro-batches to the **Delta Lake** table.
6.  Downstream systems or analysts use a **Query Engine** to read data from the Delta Lake table for insights and visualization.