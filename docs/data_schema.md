# Data Schema

This document describes the structure of the JSON events produced by the Kafka producer and processed by the Spark Streaming job. This schema is also reflected in the Delta Lake table where the processed data is stored.

## Event Fields

Each event is a JSON object with the following fields:

| Field Name              | Data Type | Description                                                                 | Example                               |
| ----------------------- | --------- | --------------------------------------------------------------------------- | ------------------------------------- |
| `event_id`              | String    | Unique identifier for the event.                                            | `"a1b2c3d4-e5f6-7890-1234-567890abcdef"` |
| `user_id`               | String    | Unique identifier for the user associated with the event.                   | `"b2c3d4e5-f6a7-8901-2345-67890abcdef0"` |
| `session_id`            | String    | Identifier for the user's session.                                          | `"abcdef1234567890"`                  |
| `product_id`            | String    | Identifier of the product involved in the event.                            | `"prod_456"`                          |
| `event_type`            | String    | The type of interaction recorded.                                           | `"product_view"`, `"add_to_cart"`      |
| `timestamp`             | String    | ISO 8601 formatted timestamp (UTC) indicating when the event occurred.      | `"2023-10-27T10:30:00.123Z"`         |
| `user_agent`            | String    | The user agent string of the client browser or application.                 | `"Mozilla/5.0 (...)"`                 |
| `ip_address`            | String    | The IP address of the client.                                               | `"192.168.1.100"`                     |
| `platform`              | String    | The platform from which the event originated.                               | `"web"`, `"mobile_app"`, `"tablet"`     |
| `country`               | String    | Two-letter country code (ISO 3166-1 alpha-2) derived from the IP address. | `"US"`, `"GB"`, `"CA"`                |

## Event-Specific Fields

Some fields are only present for specific `event_type` values:

*   **For `event_type: 'product_view'`:**
    | Field Name              | Data Type | Description                             |
    | ----------------------- | --------- | --------------------------------------- |
    | `view_duration_seconds` | Integer   | Duration the product was viewed (sec).  |

*   **For `event_type: 'add_to_cart'`:**
    | Field Name              | Data Type | Description                             |
    | ----------------------- | --------- | --------------------------------------- |
    | `quantity`              | Integer   | Number of units added to the cart.      |
    | `price`                 | Float     | Price per unit of the item added.       |

*   **For `event_type: 'purchase'`:**
    | Field Name              | Data Type | Description                             |
    | ----------------------- | --------- | --------------------------------------- |
    | `quantity`              | Integer   | Number of units purchased.              |
    | `total_amount`          | Float     | Total monetary value of the purchase.   |
    | `currency`              | String    | Currency code for the `total_amount`.   | `"USD"`                               |

## Notes

*   The Spark Streaming job reads these JSON events, parses them, and writes them into a Delta Lake table. The Delta table schema generally mirrors this structure.
*   Timestamps are crucial for time-based analysis and aggregations.