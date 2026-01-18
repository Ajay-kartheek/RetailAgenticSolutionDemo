"""
Application settings and configuration.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # AWS Configuration
    aws_region: str = "us-east-1"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None

    # DynamoDB Configuration
    dynamodb_endpoint_url: str | None = None
    use_local_dynamodb: bool = True

    # Bedrock Configuration
    bedrock_region: str = "us-east-1"
    bedrock_model_id: str = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    bedrock_image_model_id: str = "amazon.nova-canvas-v1:0"

    # Application Configuration
    app_env: Literal["development", "staging", "production"] = "development"
    app_debug: bool = True
    log_level: str = "INFO"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True

    # Agent Configuration
    agent_max_iterations: int = 10
    agent_timeout_seconds: int = 120
    hitl_enabled: bool = True

    # Table Names
    table_prefix: str = "sk_"

    @property
    def stores_table(self) -> str:
        return f"{self.table_prefix}stores"

    @property
    def products_table(self) -> str:
        return f"{self.table_prefix}products"

    @property
    def inventory_table(self) -> str:
        return f"{self.table_prefix}inventory"

    @property
    def sales_table(self) -> str:
        return f"{self.table_prefix}sales"

    @property
    def demand_forecast_table(self) -> str:
        return f"{self.table_prefix}demand_forecast"

    @property
    def store_transfers_table(self) -> str:
        return f"{self.table_prefix}store_transfers"

    @property
    def manufacturer_lead_times_table(self) -> str:
        return f"{self.table_prefix}manufacturer_lead_times"

    @property
    def trend_analysis_table(self) -> str:
        return f"{self.table_prefix}trend_analysis"

    @property
    def inventory_status_table(self) -> str:
        return f"{self.table_prefix}inventory_status"

    @property
    def decisions_table(self) -> str:
        return f"{self.table_prefix}decisions"

    @property
    def agent_runs_table(self) -> str:
        return f"{self.table_prefix}agent_runs"

    @property
    def agent_activity_table(self) -> str:
        return f"{self.table_prefix}agent_activity"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
