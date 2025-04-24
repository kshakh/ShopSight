# Usage Guide

This guide explains how to run the different components of the ShopSight pipeline.

## Running the Pipeline

1.  **Start Kafka:**
    Ensure your Apache Kafka broker (and Zookeeper, if applicable) is running and accessible using the configured `KAFKA_BROKER` address (default: `localhost:9092`).

2.  **Run the Kafka Producer:**
    This script simulates user interaction events and sends them to the Kafka topic.
    *   Open a terminal.
    *   Navigate to the project root directory (`ShopSight`).
    *   Activate your virtual environment (`source venv/bin/activate` or `.\venv\Scripts\activate`).
    *   Run the producer script:
        ```bash
        python src/kafka_producer/producer.py
        ```
    *   You can adjust the event rate using the `EVENTS_PER_SECOND` environment variable.
    *   Leave this terminal running.

3.  **Run the Spark Streaming Job:**
    This job reads from Kafka, processes the data, and writes it to Delta Lake.
    *   Open a *new* terminal.
    *   Navigate to the project root directory (`ShopSight`).
    *   Activate your virtual environment.
    *   Submit the Spark job using `spark-submit`. You may need to adjust memory settings (`--driver-memory`, `--executor-memory`) for your environment.
        ```bash
        spark-submit \
          --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,io.delta:delta-core_2.12:2.4.0 \
          src/spark_streaming/streaming_job.py
        ```
    *   **Important:** Ensure the Spark version (e.g., `3.4.1`) and Scala version (`2.12`) in the `--packages` argument match your Spark installation. Update these if necessary.
    *   The job will start processing events from Kafka and writing to the location specified by `DELTA_TABLE_PATH` (default: `/tmp/delta/product_events`) using the checkpoint location `CHECKPOINT_LOCATION` (default: `/tmp/spark_checkpoints/product_events`).
    *   Leave this terminal running.

4.  **Querying the Delta Lake Table:**
    Once the streaming job has run for a while and processed some data, you can query the results stored in the Delta table.
    *   **Using PySpark (Example):**
        You can use a separate Python script or a Spark shell/notebook.
        ```python
        from pyspark.sql import SparkSession

        spark = SparkSession.builder.appName("QueryDelta") \
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
            .getOrCreate()

        # Use the same path configured via DELTA_TABLE_PATH
        delta_path = "/tmp/delta/product_events" # Or your configured path (e.g., S3)

        df = spark.read.format("delta").load(delta_path)

        print("Sample data:")
        df.show()

        print("Schema:")
        df.printSchema()

        print(f"Total events processed so far: {df.count()}")

        # Example query: Count events by type
        df.groupBy("event_type").count().show()

        spark.stop()
        ```
    *   **Using `spark-sql`:**
        If you have `spark-sql` configured, you can launch it and query the Delta table directly.

## Stopping the Pipeline

1.  Press `Ctrl+C` in the terminal running the Kafka producer (`producer.py`).
2.  Press `Ctrl+C` in the terminal running the Spark Streaming job (`spark-submit`). Alternatively, you can kill the Spark application through the Spark UI or command-line tools if it's running on a cluster.