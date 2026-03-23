"""
DynamoDB client utilities for the Retail Agentic AI platform.
"""

import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any, TypeVar

from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

from config.aws import get_dynamodb_resource
from config.settings import settings

T = TypeVar("T")


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal types."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


def serialize_item(item: dict[str, Any]) -> dict[str, Any]:
    """Serialize a dictionary for DynamoDB storage."""
    serialized = {}
    for key, value in item.items():
        if value is None:
            continue
        if isinstance(value, float):
            serialized[key] = Decimal(str(value))
        elif isinstance(value, (datetime, date)):
            serialized[key] = value.isoformat()
        elif isinstance(value, dict):
            serialized[key] = serialize_item(value)
        elif isinstance(value, list):
            serialized[key] = [
                serialize_item(v) if isinstance(v, dict) else v for v in value
            ]
        else:
            serialized[key] = value
    return serialized


def deserialize_item(item: dict[str, Any]) -> dict[str, Any]:
    """Deserialize a DynamoDB item to Python types."""
    deserialized = {}
    for key, value in item.items():
        if isinstance(value, Decimal):
            # Convert to int if whole number, else float
            if value % 1 == 0:
                deserialized[key] = int(value)
            else:
                deserialized[key] = float(value)
        elif isinstance(value, dict):
            deserialized[key] = deserialize_item(value)
        elif isinstance(value, list):
            deserialized[key] = [
                deserialize_item(v) if isinstance(v, dict) else v for v in value
            ]
        else:
            deserialized[key] = value
    return deserialized


class DynamoDBClient:
    """DynamoDB client wrapper with utility methods."""

    def __init__(self) -> None:
        self.resource = get_dynamodb_resource()
        self._tables: dict[str, Any] = {}

    def _get_table(self, table_name: str) -> Any:
        """Get or create table reference."""
        if table_name not in self._tables:
            self._tables[table_name] = self.resource.Table(table_name)
        return self._tables[table_name]

    # ========================================================================
    # Generic Operations
    # ========================================================================

    def put_item(self, table_name: str, item: dict[str, Any]) -> bool:
        """Put an item into a table."""
        try:
            table = self._get_table(table_name)
            serialized = serialize_item(item)
            table.put_item(Item=serialized)
            return True
        except ClientError as e:
            print(f"Error putting item to {table_name}: {e}")
            return False

    def get_item(
        self, table_name: str, key: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Get a single item by key."""
        try:
            table = self._get_table(table_name)
            response = table.get_item(Key=key)
            item = response.get("Item")
            return deserialize_item(item) if item else None
        except ClientError as e:
            print(f"Error getting item from {table_name}: {e}")
            return None

    def query(
        self,
        table_name: str,
        key_condition: Any,
        filter_expression: Any | None = None,
        index_name: str | None = None,
        limit: int | None = None,
        **kwargs,
    ) -> list[dict[str, Any]]:
        """Query items from a table."""
        try:
            table = self._get_table(table_name)
            query_kwargs: dict[str, Any] = {"KeyConditionExpression": key_condition}

            if filter_expression:
                query_kwargs["FilterExpression"] = filter_expression
            if index_name:
                query_kwargs["IndexName"] = index_name
            if limit:
                query_kwargs["Limit"] = limit
            
            # Add any additional kwargs (e.g. ScanIndexForward)
            query_kwargs.update(kwargs)

            response = table.query(**query_kwargs)
            items = response.get("Items", [])
            return [deserialize_item(item) for item in items]
        except ClientError as e:
            print(f"Error querying {table_name}: {e}")
            return []

    def scan(
        self,
        table_name: str,
        filter_expression: Any | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Scan all items from a table (handles pagination)."""
        try:
            table = self._get_table(table_name)
            kwargs: dict[str, Any] = {}

            if filter_expression:
                kwargs["FilterExpression"] = filter_expression

            all_items = []
            while True:
                response = table.scan(**kwargs)
                items = response.get("Items", [])
                all_items.extend([deserialize_item(item) for item in items])

                # Check if we have enough items (if limit specified)
                if limit and len(all_items) >= limit:
                    return all_items[:limit]

                # Check for more pages
                if "LastEvaluatedKey" not in response:
                    break
                kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]

            return all_items
        except ClientError as e:
            print(f"Error scanning {table_name}: {e}")
            return []

    def update_item(
        self,
        table_name: str,
        key: dict[str, Any],
        update_expression: str,
        expression_values: dict[str, Any],
        expression_names: dict[str, str] | None = None,
    ) -> bool:
        """Update an item in a table."""
        try:
            table = self._get_table(table_name)
            kwargs: dict[str, Any] = {
                "Key": key,
                "UpdateExpression": update_expression,
                "ExpressionAttributeValues": serialize_item(expression_values),
            }
            if expression_names:
                kwargs["ExpressionAttributeNames"] = expression_names

            table.update_item(**kwargs)
            return True
        except ClientError as e:
            print(f"Error updating item in {table_name}: {e}")
            return False

    def delete_item(self, table_name: str, key: dict[str, Any]) -> bool:
        """Delete an item from a table."""
        try:
            table = self._get_table(table_name)
            table.delete_item(Key=key)
            return True
        except ClientError as e:
            print(f"Error deleting item from {table_name}: {e}")
            return False

    def batch_write(
        self, table_name: str, items: list[dict[str, Any]]
    ) -> bool:
        """Batch write items to a table."""
        try:
            table = self._get_table(table_name)
            with table.batch_writer() as batch:
                for item in items:
                    serialized = serialize_item(item)
                    batch.put_item(Item=serialized)
            return True
        except ClientError as e:
            print(f"Error batch writing to {table_name}: {e}")
            return False

    # ========================================================================
    # Store Operations
    # ========================================================================

    def get_all_stores(self) -> list[dict[str, Any]]:
        """Get all stores."""
        return self.scan(settings.stores_table)

    def get_store(self, store_id: str) -> dict[str, Any] | None:
        """Get a single store by ID."""
        return self.get_item(settings.stores_table, {"store_id": store_id})

    # ========================================================================
    # Product Operations
    # ========================================================================

    def get_all_products(self) -> list[dict[str, Any]]:
        """Get all products."""
        return self.scan(settings.products_table)

    def get_product(self, product_id: str) -> dict[str, Any] | None:
        """Get a single product by ID."""
        return self.get_item(settings.products_table, {"product_id": product_id})

    def get_products_by_category(self, category: str) -> list[dict[str, Any]]:
        """Get products by category."""
        return self.scan(
            settings.products_table,
            filter_expression=Attr("category").eq(category),
        )

    # ========================================================================
    # Inventory Operations
    # ========================================================================

    def get_inventory_by_store(self, store_id: str) -> list[dict[str, Any]]:
        """Get all inventory for a store."""
        return self.query(
            settings.inventory_table,
            key_condition=Key("store_id").eq(store_id),
        )

    def get_store_inventory(self, store_id: str) -> list[dict[str, Any]]:
        """Get all inventory for a store (Alias for consistency)."""
        return self.get_inventory_by_store(store_id)

    def get_product_inventory(self, product_id: str) -> list[dict[str, Any]]:
        """Get inventory for a product across all stores."""
        # This requires a Scan if no GSI exists on product_id. Assuming explicit scan for now or use GSI if available.
        # For small scale, scan is acceptable.
        return self.scan(
            settings.inventory_table,
            filter_expression=Attr("product_id").eq(product_id),
        )

    def get_inventory_by_store_product(
        self, store_id: str, product_id: str
    ) -> list[dict[str, Any]]:
        """Get inventory for a specific product at a store."""
        return self.query(
            settings.inventory_table,
            key_condition=Key("store_id").eq(store_id),
            filter_expression=Attr("product_id").eq(product_id),
        )

    def get_total_stock_by_store_product(
        self, store_id: str, product_id: str
    ) -> int:
        """Get total stock quantity for a product at a store."""
        items = self.get_inventory_by_store_product(store_id, product_id)
        return sum(item.get("quantity", 0) for item in items)

    # ========================================================================
    # Sales Operations
    # ========================================================================

    def get_sales_by_store_product(
        self,
        store_id: str,
        product_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """Get sales for a product at a store within a date range."""
        pk = f"{store_id}#{product_id}"
        key_condition = Key("store_product_id").eq(pk)

        if start_date and end_date:
            key_condition = key_condition & Key("sale_date").between(
                start_date.isoformat(), end_date.isoformat()
            )
        elif start_date:
            key_condition = key_condition & Key("sale_date").gte(
                start_date.isoformat()
            )
        elif end_date:
            key_condition = key_condition & Key("sale_date").lte(
                end_date.isoformat()
            )

        return self.query(settings.sales_table, key_condition=key_condition)

    def get_total_sales_quantity(
        self,
        store_id: str,
        product_id: str,
        start_date: date,
        end_date: date,
    ) -> int:
        """Get total units sold for a product at a store in a date range."""
        sales = self.get_sales_by_store_product(
            store_id, product_id, start_date, end_date
        )
        return sum(s.get("quantity_sold", 0) for s in sales)

    # ========================================================================
    # Demand Forecast Operations
    # ========================================================================

    def get_demand_forecast(
        self, product_id: str, store_id: str, forecast_period: str
    ) -> dict[str, Any] | None:
        """Get demand forecast for a product at a store."""
        pk = f"{product_id}#{store_id}"
        return self.get_item(
            settings.demand_forecast_table,
            {"product_store_id": pk, "forecast_period": forecast_period},
        )

    def get_all_forecasts_for_period(
        self, forecast_period: str
    ) -> list[dict[str, Any]]:
        """Get all forecasts for a specific period."""
        return self.scan(
            settings.demand_forecast_table,
            filter_expression=Attr("forecast_period").eq(forecast_period),
        )

    def get_store_forecasts(
        self, store_id: str, period: str | None = None
    ) -> list[dict[str, Any]]:
        """Get all forecasts for a specific store."""
        # Note: Ideally this should use a GSI on store_id. Using Scan for prototype.
        filter_expr = Attr("store_id").eq(store_id)
        if period:
            filter_expr = filter_expr & Attr("forecast_period").eq(period)
            
        return self.scan(
            settings.demand_forecast_table,
            filter_expression=filter_expr
        )
        
    def get_store_sales(
        self, store_id: str, days: int = 30
    ) -> list[dict[str, Any]]:
        """Get recent sales for a specific store."""
        # Note: Using Scan for prototype. Add GSI on store_id for prod.
        # Simple implementation: get all sales for store.
        # Date filtering would be added here in a real implementation.
        return self.scan(
            settings.sales_table,
            filter_expression=Attr("store_id").eq(store_id)
        )

    # ========================================================================
    # Store Transfer Operations
    # ========================================================================

    def get_transfer_route(
        self, from_store_id: str, to_store_id: str
    ) -> dict[str, Any] | None:
        """Get transfer route between two stores."""
        pk = f"{from_store_id}#{to_store_id}"
        return self.get_item(settings.store_transfers_table, {"route_id": pk})

    def get_all_routes_from_store(
        self, from_store_id: str
    ) -> list[dict[str, Any]]:
        """Get all transfer routes from a store."""
        return self.scan(
            settings.store_transfers_table,
            filter_expression=Attr("from_store_id").eq(from_store_id),
        )

    # ========================================================================
    # Manufacturer Lead Time Operations
    # ========================================================================

    def get_manufacturer_lead_time(
        self, product_id: str
    ) -> dict[str, Any] | None:
        """Get manufacturer lead time for a product."""
        items = self.scan(
            settings.manufacturer_lead_times_table,
            filter_expression=Attr("product_id").eq(product_id),
            limit=1,
        )
        return items[0] if items else None

    # ========================================================================
    # Decision Operations
    # ========================================================================

    def save_decision(self, decision: dict[str, Any]) -> bool:
        """Save a decision to the decisions table."""
        return self.put_item(settings.decisions_table, decision)

    def get_pending_decisions(self) -> list[dict[str, Any]]:
        """Get all pending decisions awaiting approval."""
        return self.scan(
            settings.decisions_table,
            filter_expression=Attr("status").eq("pending_approval"),
        )

        return self.update_item(
            settings.decisions_table,
            {"decision_id": decision_id},
            update_expr,
            expr_values,
            expr_names,
        )

    def get_all_decisions(self) -> list[dict[str, Any]]:
        """Get all decisions."""
        return self.scan(settings.decisions_table)

    def get_decision(self, decision_id: str) -> dict[str, Any] | None:
        """Get a single decision by ID."""
        return self.get_item(settings.decisions_table, {"decision_id": decision_id})

    def update_decision(self, decision_id: str, updates: dict[str, Any]) -> bool:
        """
        Update a decision with arbitrary fields.
        Automatically handles UpdateExpression generation.
        """
        if not updates:
            return True
            
        update_parts = []
        expr_values = {}
        expr_names = {}
        
        for key, value in updates.items():
            # Handle reserved words if necessary, simplified here
            attr_name = f"#{key}"
            val_name = f":{key}"
            
            update_parts.append(f"{attr_name} = {val_name}")
            expr_names[attr_name] = key
            expr_values[val_name] = value
            
        update_expr = "SET " + ", ".join(update_parts)
        
        # Add updated_at if not present
        if "updated_at" not in updates:
            update_expr += ", #updated_at_auto = :updated_at_auto"
            expr_names["#updated_at_auto"] = "updated_at"
            expr_values[":updated_at_auto"] = datetime.utcnow().isoformat()
            
        return self.update_item(
            settings.decisions_table,
            {"decision_id": decision_id},
            update_expr,
            expr_values,
            expr_names
        )

    def get_active_decisions(self, decision_type: str = None, days: int = 30) -> list[dict[str, Any]]:
        """
        Get active (approved/executed) decisions for context awareness.
        
        Args:
            decision_type: Optional filter for decision type (e.g., 'pricing', 'replenishment')
            days: Number of days to look back (default 30)
            
        Returns:
            List of active decisions that agents should be aware of
        """
        from datetime import datetime, timedelta
        
        # Get all non-pending decisions
        filter_expr = Attr("status").is_in(["approved", "executed"])
        
        # Calculate cutoff date
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        filter_expr = filter_expr & Attr("timestamp").gte(cutoff_date)
        
        try:
            decisions = self.scan(settings.decisions_table, filter_expression=filter_expr)
            
            # Filter by type if specified
            if decision_type:
                decisions = [d for d in decisions if decision_type in d.get("decision_type", "")]
            
            return decisions
        except Exception as e:
            print(f"Error getting active decisions: {e}")
            return []

    def get_decisions_for_product(self, product_id: str, days: int = 30) -> list[dict[str, Any]]:
        """
        Get all recent decisions for a specific product.
        
        Args:
            product_id: The product ID to check
            days: Number of days to look back
            
        Returns:
            List of decisions affecting this product
        """
        from datetime import datetime, timedelta
        
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        filter_expr = Attr("timestamp").gte(cutoff_date)
        
        try:
            decisions = self.scan(settings.decisions_table, filter_expression=filter_expr)
            
            # Filter for decisions involving this product
            product_decisions = []
            for d in decisions:
                data = d.get("data", {})
                if data.get("product_id") == product_id:
                    product_decisions.append(d)
            
            return product_decisions
        except Exception as e:
            print(f"Error getting product decisions: {e}")
            return []


# Global client instance
db_client = DynamoDBClient()
