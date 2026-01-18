"""
DynamoDB table definitions for the Retail Agentic AI platform.
"""

from typing import Any

from botocore.exceptions import ClientError

from config.aws import get_dynamodb_resource
from config.settings import settings


# ============================================================================
# Table Definitions
# ============================================================================

TABLE_DEFINITIONS: dict[str, dict[str, Any]] = {
    # ========================================================================
    # sk_stores - Store information
    # ========================================================================
    settings.stores_table: {
        "KeySchema": [
            {"AttributeName": "store_id", "KeyType": "HASH"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "store_id", "AttributeType": "S"},
            {"AttributeName": "city", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "city-index",
                "KeySchema": [
                    {"AttributeName": "city", "KeyType": "HASH"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
    # ========================================================================
    # sk_products - Product catalog
    # ========================================================================
    settings.products_table: {
        "KeySchema": [
            {"AttributeName": "product_id", "KeyType": "HASH"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "product_id", "AttributeType": "S"},
            {"AttributeName": "category", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "category-index",
                "KeySchema": [
                    {"AttributeName": "category", "KeyType": "HASH"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
    # ========================================================================
    # sk_inventory - Store inventory
    # PK: store_id, SK: sku (product_id#size#color)
    # ========================================================================
    settings.inventory_table: {
        "KeySchema": [
            {"AttributeName": "store_id", "KeyType": "HASH"},
            {"AttributeName": "sku", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "store_id", "AttributeType": "S"},
            {"AttributeName": "sku", "AttributeType": "S"},
            {"AttributeName": "product_id", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "product-index",
                "KeySchema": [
                    {"AttributeName": "product_id", "KeyType": "HASH"},
                    {"AttributeName": "store_id", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
    # ========================================================================
    # sk_sales - Daily sales records
    # PK: store_product_id (store_id#product_id), SK: sale_date
    # ========================================================================
    settings.sales_table: {
        "KeySchema": [
            {"AttributeName": "store_product_id", "KeyType": "HASH"},
            {"AttributeName": "sale_date", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "store_product_id", "AttributeType": "S"},
            {"AttributeName": "sale_date", "AttributeType": "S"},
            {"AttributeName": "store_id", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "store-date-index",
                "KeySchema": [
                    {"AttributeName": "store_id", "KeyType": "HASH"},
                    {"AttributeName": "sale_date", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
    # ========================================================================
    # sk_demand_forecast - ML demand forecasts (mocked)
    # PK: product_store_id (product_id#store_id), SK: forecast_period
    # ========================================================================
    settings.demand_forecast_table: {
        "KeySchema": [
            {"AttributeName": "product_store_id", "KeyType": "HASH"},
            {"AttributeName": "forecast_period", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "product_store_id", "AttributeType": "S"},
            {"AttributeName": "forecast_period", "AttributeType": "S"},
            {"AttributeName": "store_id", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "store-period-index",
                "KeySchema": [
                    {"AttributeName": "store_id", "KeyType": "HASH"},
                    {"AttributeName": "forecast_period", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
    # ========================================================================
    # sk_store_transfers - Inter-store transfer routes
    # PK: route_id (from_store_id#to_store_id)
    # ========================================================================
    settings.store_transfers_table: {
        "KeySchema": [
            {"AttributeName": "route_id", "KeyType": "HASH"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "route_id", "AttributeType": "S"},
            {"AttributeName": "from_store_id", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "from-store-index",
                "KeySchema": [
                    {"AttributeName": "from_store_id", "KeyType": "HASH"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
    # ========================================================================
    # sk_manufacturer_lead_times - Manufacturing lead times
    # PK: product_id, SK: manufacturer_id
    # ========================================================================
    settings.manufacturer_lead_times_table: {
        "KeySchema": [
            {"AttributeName": "product_id", "KeyType": "HASH"},
            {"AttributeName": "manufacturer_id", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "product_id", "AttributeType": "S"},
            {"AttributeName": "manufacturer_id", "AttributeType": "S"},
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
    # ========================================================================
    # sk_trend_analysis - Agent output: trend analysis results
    # PK: store_product_id, SK: analysis_date
    # ========================================================================
    settings.trend_analysis_table: {
        "KeySchema": [
            {"AttributeName": "store_product_id", "KeyType": "HASH"},
            {"AttributeName": "analysis_date", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "store_product_id", "AttributeType": "S"},
            {"AttributeName": "analysis_date", "AttributeType": "S"},
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
    # ========================================================================
    # sk_inventory_status - Agent output: inventory status analysis
    # PK: store_product_id, SK: analysis_timestamp
    # ========================================================================
    settings.inventory_status_table: {
        "KeySchema": [
            {"AttributeName": "store_product_id", "KeyType": "HASH"},
            {"AttributeName": "analysis_timestamp", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "store_product_id", "AttributeType": "S"},
            {"AttributeName": "analysis_timestamp", "AttributeType": "S"},
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
    # ========================================================================
    # sk_decisions - Decision audit trail and HITL queue
    # PK: decision_id
    # ========================================================================
    settings.decisions_table: {
        "KeySchema": [
            {"AttributeName": "decision_id", "KeyType": "HASH"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "decision_id", "AttributeType": "S"},
            {"AttributeName": "status", "AttributeType": "S"},
            {"AttributeName": "timestamp", "AttributeType": "S"},
            {"AttributeName": "decision_type", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "status-timestamp-index",
                "KeySchema": [
                    {"AttributeName": "status", "KeyType": "HASH"},
                    {"AttributeName": "timestamp", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
            {
                "IndexName": "type-timestamp-index",
                "KeySchema": [
                    {"AttributeName": "decision_type", "KeyType": "HASH"},
                    {"AttributeName": "timestamp", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
    # ========================================================================
    # sk_agent_runs - Structured agent run results
    # PK: run_id, SK: agent_id
    # Stores insights, recommendations, and metrics from each agent run
    # ========================================================================
    settings.agent_runs_table: {
        "KeySchema": [
            {"AttributeName": "run_id", "KeyType": "HASH"},
            {"AttributeName": "agent_id", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "run_id", "AttributeType": "S"},
            {"AttributeName": "agent_id", "AttributeType": "S"},
            {"AttributeName": "timestamp", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "agent-timestamp-index",
                "KeySchema": [
                    {"AttributeName": "agent_id", "KeyType": "HASH"},
                    {"AttributeName": "timestamp", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
    # ========================================================================
    # sk_agent_activity - Agent action activity logs
    # PK: activity_id
    # Logs individual agent actions (e.g., price changes, stock transfers)
    # ========================================================================
    settings.agent_activity_table: {
        "KeySchema": [
            {"AttributeName": "activity_id", "KeyType": "HASH"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "activity_id", "AttributeType": "S"},
            {"AttributeName": "agent_id", "AttributeType": "S"},
            {"AttributeName": "timestamp", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "agent-timestamp-index",
                "KeySchema": [
                    {"AttributeName": "agent_id", "KeyType": "HASH"},
                    {"AttributeName": "timestamp", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
}


# ============================================================================
# Table Management Functions
# ============================================================================


def create_table(table_name: str, table_config: dict[str, Any]) -> bool:
    """Create a single DynamoDB table."""
    dynamodb = get_dynamodb_resource()

    try:
        # Check if table already exists
        existing_tables = [t.name for t in dynamodb.tables.all()]
        if table_name in existing_tables:
            print(f"Table {table_name} already exists, skipping...")
            return True

        # Create the table
        kwargs = {
            "TableName": table_name,
            "KeySchema": table_config["KeySchema"],
            "AttributeDefinitions": table_config["AttributeDefinitions"],
            "BillingMode": table_config.get("BillingMode", "PAY_PER_REQUEST"),
        }

        if "GlobalSecondaryIndexes" in table_config:
            kwargs["GlobalSecondaryIndexes"] = table_config["GlobalSecondaryIndexes"]

        if "LocalSecondaryIndexes" in table_config:
            kwargs["LocalSecondaryIndexes"] = table_config["LocalSecondaryIndexes"]

        table = dynamodb.create_table(**kwargs)

        # Wait for table to be created
        print(f"Creating table {table_name}...")
        table.wait_until_exists()
        print(f"Table {table_name} created successfully!")
        return True

    except ClientError as e:
        print(f"Error creating table {table_name}: {e}")
        return False


def delete_table(table_name: str) -> bool:
    """Delete a single DynamoDB table."""
    dynamodb = get_dynamodb_resource()

    try:
        table = dynamodb.Table(table_name)
        table.delete()
        print(f"Deleting table {table_name}...")
        table.wait_until_not_exists()
        print(f"Table {table_name} deleted successfully!")
        return True

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            print(f"Table {table_name} does not exist, skipping...")
            return True
        print(f"Error deleting table {table_name}: {e}")
        return False


def create_all_tables() -> dict[str, bool]:
    """Create all DynamoDB tables."""
    results = {}
    for table_name, table_config in TABLE_DEFINITIONS.items():
        results[table_name] = create_table(table_name, table_config)
    return results


def delete_all_tables() -> dict[str, bool]:
    """Delete all DynamoDB tables."""
    results = {}
    for table_name in TABLE_DEFINITIONS.keys():
        results[table_name] = delete_table(table_name)
    return results


def list_tables() -> list[str]:
    """List all existing tables."""
    dynamodb = get_dynamodb_resource()
    return [t.name for t in dynamodb.tables.all()]


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "delete":
        print("Deleting all tables...")
        delete_all_tables()
    else:
        print("Creating all tables...")
        create_all_tables()
