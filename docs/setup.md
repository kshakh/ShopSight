# Setup Instructions

This guide provides detailed steps for setting up the ShopSight project environment.

## Prerequisites

Ensure you have the following installed before proceeding:

*   **Python:** Version 3.8 or higher.
*   **Java:** Version 8 or 11. This is required for running Apache Spark and Apache Kafka.
*   **Apache Spark:** Download and install Apache Spark. Make sure the `SPARK_HOME` environment variable is set correctly, or that the Spark binaries are included in your system's `PATH`.
*   **Apache Kafka:** A running Kafka instance is required. This can be a local installation or a remotely accessible cluster.

## Installation Steps

1.  **Clone the Repository:**
    Get a local copy of the project code:
    ```bash
    git clone <repository_url> # Replace <repository_url> with the actual URL
    cd ShopSight
    ```

2.  **Create and Activate Virtual Environment (Recommended):**
    It's best practice to use a virtual environment to manage project dependencies:
    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install Python Dependencies:**
    Install the required Python packages listed in `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

The application uses environment variables for key configurations. You can set these variables directly in your shell or create a `.env` file in the project's root directory (ensure this file is added to your `.gitignore` to avoid committing sensitive information).

**Required Environment Variables:**

*   `KAFKA_BROKER`: The address of your Kafka broker(s). 
    *   Default: `localhost:9092`
*   `KAFKA_TOPIC`: The Kafka topic to use for product events.
    *   Default: `product_events`
*   `DELTA_TABLE_PATH`: The file system path (local or distributed, e.g., S3) where the Delta Lake table will be stored.
    *   Default: `/tmp/delta/product_events`
    *   **Note:** For persistent storage, change this to a suitable location (e.g., `s3a://your-bucket/delta/product_events`).
*   `CHECKPOINT_LOCATION`: The directory Spark Streaming will use for checkpointing its progress. This is crucial for fault tolerance.
    *   Default: `/tmp/spark_checkpoints/product_events`
    *   **Note:** For production or persistent runs, change this to a reliable distributed filesystem location (e.g., HDFS or S3).

**Optional Environment Variables:**

*   `EVENTS_PER_SECOND`: Controls the rate at which the data simulator generates events (used by `src/data_simulation/simulate_data.py`).
    *   Default: `1.0`