# ShopSight - Real-Time Product Analytics Pipeline

This project implements a real-time product analytics pipeline using Apache Spark Streaming, Kafka, Delta Lake, and Python.

## Features

- Real-time ingestion of simulated product interaction data (e.g., clicks, views) via Kafka.
- Stream processing using Apache Spark Streaming to calculate metrics.
- Storing processed data efficiently in Delta Lake tables.
- Foundation for building dashboards (e.g., Tableau) for insights like conversion funnels, bounce rates.
- Basic anomaly detection capabilities.

## Project Structure

```
ShopSight/
├── config/                 # Configuration files (Kafka, Spark, Schemas)
├── data/                   # Data storage (e.g., Delta Lake tables location - often external like S3)
├── deployment/             # Deployment artifacts (Docker, requirements)
├── docs/                   # Project documentation
├── notebooks/              # Jupyter notebooks for exploration and analysis
├── src/                    # Source code
│   ├── data_simulation/    # Scripts to simulate data streams
│   ├── kafka_producer/     # Kafka producer logic
│   ├── spark_streaming/    # Spark Streaming job(s)
│   └── utils/              # Utility functions and modules
├── tests/                  # Unit and integration tests
├── .gitignore              # Git ignore file
└── README.md               # This file
└── requirements.txt        # Python dependencies
```

## Setup

1.  **Prerequisites:**
    *   Python 3.8+
    *   Java 8 or 11 (for Spark and Kafka)
    *   Apache Spark (ensure `SPARK_HOME` is set or Spark is in your `PATH`)
    *   Apache Kafka (running locally or accessible)

2.  **Clone the repository:**
    ```bash
    git clone https://github.com/kshakh/ShopSight.git
    cd ShopSight
    ```

3.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate # On Windows use `venv\Scripts\activate`
    ```

4.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure Environment Variables (Optional):**
    The scripts use environment variables for configuration (Kafka broker, topic, etc.). You can set these directly or create a `.env` file (ensure it's in `.gitignore`).
    *   `KAFKA_BROKER`: Default `localhost:9092`
    *   `KAFKA_TOPIC`: Default `product_events`
    *   `DELTA_TABLE_PATH`: Default `/tmp/delta/product_events` (Change for persistent storage, e.g., S3)
    *   `CHECKPOINT_LOCATION`: Default `/tmp/spark_checkpoints/product_events` (Change for persistent storage)
    *   `EVENTS_PER_SECOND`: Default `1.0` (for Kafka producer)

## Usage

1.  **Start Kafka:** Ensure your Kafka broker (and Zookeeper) is running.

2.  **Run the Kafka Producer:**
    Open a terminal, activate the virtual environment, and run:
    ```bash
    python src/kafka_producer/producer.py
    ```
    This will start generating simulated events and sending them to the configured Kafka topic.

3.  **Run the Spark Streaming Job:**
    Open another terminal, activate the virtual environment, and submit the Spark job. You might need to adjust memory settings (`--driver-memory`, `--executor-memory`) based on your system.
    ```bash
    spark-submit \
      --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,io.delta:delta-core_2.12:2.4.0 \
      src/spark_streaming/streaming_job.py
    ```
    *Note: Ensure the Spark version (e.g., 3.4.1) and Scala version (e.g., 2.12) in the `--packages` argument match your Spark installation.*

    This job will connect to Kafka, process the events, and write them to the Delta Lake table specified by `DELTA_TABLE_PATH`.

4.  **Querying Delta Lake Table (Example using Spark SQL):**
    You can use `spark-sql` or a separate Spark script/notebook to query the data written to the Delta table.
    ```python
    # Example in PySpark
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.appName("QueryDelta") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()

    delta_path = "/tmp/delta/product_events" # Or your configured path
    df = spark.read.format("delta").load(delta_path)

    df.show()
    df.printSchema()
    print(f"Total events processed: {df.count()}")
    ```

5.  **Stopping:**
    *   Press `Ctrl+C` in the Kafka producer terminal.
    *   Press `Ctrl+C` in the Spark Streaming job terminal (or kill the Spark application).

## Building Dashboards (Tableau Example)

Once the data is flowing into your Delta Lake table, you can connect visualization tools like Tableau to gain insights.

1.  **Data Source:** Connect Tableau directly to your Delta Lake table. Depending on where your Delta table resides (local filesystem, S3, etc.), the connection method will vary.
    *   **Databricks:** Use the Databricks connector.
    *   **S3/ADLS:** You might need a query engine like Spark SQL, Presto/Trino, or Athena that can read Delta tables and expose them via JDBC/ODBC for Tableau.
    *   **Local:** Less common for production, but you could potentially expose it via a local Spark SQL server.
2.  **Data Modeling:** You might want to create aggregated views or materialized tables on top of the raw `product_events` Delta table for better dashboard performance. For example, create daily/hourly summaries of key metrics.
3.  **Visualizations:**
    *   **Conversion Funnel:** Track users moving through `product_view` -> `add_to_cart` -> `checkout_start` -> `purchase`.
    *   **Bounce Rate:** Calculate the percentage of sessions with only one event (e.g., a `product_view` without further action).
    *   **Top Products:** Show products with the most views, adds-to-cart, or purchases.
    *   **User Activity:** Analyze events per user, session duration (requires sessionization logic), etc.

## Anomaly Detection

The pipeline provides a foundation for detecting anomalies in user behavior or system performance.

1.  **Metrics:** Identify key metrics to monitor (e.g., purchase volume per hour, add-to-cart rate, specific event counts).
2.  **Methods:**
    *   **Statistical Methods (Z-score, IQR):** Calculate rolling statistics (mean, standard deviation) for a metric within the Spark Streaming job or in a separate batch job querying the Delta table. Flag data points that fall outside a defined threshold (e.g., > 3 standard deviations from the mean).
    *   **Time Series Decomposition:** Use techniques like STL (Seasonal-Trend decomposition using Loess) to separate seasonality and trend, making anomalies in the residual component easier to spot.
    *   **Machine Learning:** Train models (e.g., Isolation Forest, One-Class SVM) on historical data to identify unusual patterns.
3.  **Implementation:**
    *   **Streaming:** Add anomaly detection logic directly into the `streaming_job.py` to flag anomalies in near real-time. This is suitable for simpler statistical methods.
    *   **Batch:** Run a separate Spark batch job periodically (e.g., hourly) on the Delta table to perform more complex anomaly detection analysis.
    *   **Alerting:** Integrate with alerting systems (e.g., PagerDuty, Slack) to notify teams when anomalies are detected.