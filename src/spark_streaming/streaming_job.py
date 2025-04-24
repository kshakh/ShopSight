import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, current_timestamp, window, count # Added window, count
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType

from config import settings # Import the settings

# --- Configuration (Consider moving to a config file or env vars later) ---
# KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'localhost:9092') # Removed
# KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC', 'product_events') # Removed
# DELTA_TABLE_PATH = os.environ.get('DELTA_TABLE_PATH', '/tmp/delta/product_events') # Removed
# CHECKPOINT_LOCATION = os.environ.get('CHECKPOINT_LOCATION', '/tmp/spark_checkpoints/product_events') # Removed
APP_NAME = "ShopSightStreaming"
# ------------------------------------------------------------------------

def main():
    """Main function to run the Spark Streaming job."""

    print("Initializing Spark Session...")
    spark = (
        SparkSession.builder.appName(APP_NAME)
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        # Add Kafka package - ensure this matches your Spark/Kafka setup
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,io.delta:delta-core_2.12:2.4.0")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN") # Reduce verbosity
    print("Spark Session Initialized.")

    # Define the schema for the incoming Kafka messages (JSON)
    schema = StructType([
        StructField("event_id", StringType(), True),
        StructField("user_id", StringType(), True),
        StructField("session_id", StringType(), True),
        StructField("product_id", StringType(), True),
        StructField("event_type", StringType(), True),
        StructField("timestamp", StringType(), True), # Keep as string initially for parsing flexibility
        StructField("user_agent", StringType(), True),
        StructField("ip_address", StringType(), True),
        StructField("platform", StringType(), True),
        StructField("country", StringType(), True),
        StructField("view_duration_seconds", IntegerType(), True),
        StructField("quantity", IntegerType(), True),
        StructField("price", DoubleType(), True),
        StructField("total_amount", DoubleType(), True),
        StructField("currency", StringType(), True),
    ])

    print(f"Reading from Kafka topic: {settings.KAFKA_TOPIC} at {settings.KAFKA_BROKER}") # Use settings
    # Read from Kafka
    kafka_df = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", settings.KAFKA_BROKER) # Use settings
        .option("subscribe", settings.KAFKA_TOPIC) # Use settings
        .option("startingOffsets", "latest") # Process only new messages
        .load()
    )

    # Process the data
    processed_df = (
        kafka_df.selectExpr("CAST(value AS STRING)") # Select the 'value' column (message content)
        .select(from_json(col("value"), schema).alias("data")) # Parse JSON string using the defined schema
        .select("data.*") # Flatten the struct
        .withColumn("event_timestamp", col("timestamp").cast(TimestampType())) # Convert string timestamp to Timestamp type
        .withColumn("processing_timestamp", current_timestamp()) # Add processing time
    )

    # --- Real-time Aggregation (Example: Count events by type per minute) ---
    print("Setting up real-time aggregation...")
    aggregation_df = (
        processed_df
        .withWatermark("event_timestamp", "2 minutes") # Handle late data
        .groupBy(
            window(col("event_timestamp"), "1 minute"), # 1-minute tumbling window
            col("event_type")
        )
        .agg(count("*").alias("event_count"))
    )

    # --- Write Aggregated Stream to Console (for monitoring) ---
    aggregation_query = (
        aggregation_df.writeStream
        .outputMode("update") # Use update mode for aggregations
        .format("console")
        .option("truncate", "false") # Show full column content
        .trigger(processingTime='1 minute') # Process data every minute
        .start()
    )
    print("Aggregation query started (writing to console).")

    print(f"Writing raw event stream to Delta table: {settings.DELTA_TABLE_PATH}") # Use settings
    # Write the raw event stream to Delta Lake
    raw_event_query = (
        processed_df.writeStream.format("delta")
        .outputMode("append") # Append new data
        .option("checkpointLocation", settings.CHECKPOINT_LOCATION) # Use settings
        .option("path", settings.DELTA_TABLE_PATH) # Use settings
        .start()
    )

    print(f"Raw event streaming query started. Checkpoint location: {settings.CHECKPOINT_LOCATION}") # Use settings

    # Await termination for both queries (or manage them appropriately)
    # For simplicity here, we just await the raw event query.
    # In a real application, you might want more robust handling.
    raw_event_query.awaitTermination()
    # aggregation_query.awaitTermination() # Usually you await one, or manage termination externally

if __name__ == "__main__":
    main()