"""
AWS client configuration and utilities.
"""

import boto3
from botocore.config import Config
from functools import lru_cache
from typing import Any

from .settings import settings


class AWSConfig:
    """AWS configuration and client factory."""

    def __init__(self) -> None:
        self.region = settings.aws_region
        self.bedrock_region = settings.bedrock_region

        # Configure retry settings
        self.config = Config(
            region_name=self.region,
            retries={"max_attempts": 3, "mode": "adaptive"},
            connect_timeout=5,
            read_timeout=60,
        )

    def _get_credentials(self) -> dict[str, Any]:
        """Get AWS credentials if explicitly set."""
        creds: dict[str, Any] = {}
        if settings.aws_access_key_id:
            creds["aws_access_key_id"] = settings.aws_access_key_id
        if settings.aws_secret_access_key:
            creds["aws_secret_access_key"] = settings.aws_secret_access_key
        return creds

    def get_dynamodb_resource(self) -> Any:
        """Get DynamoDB resource."""
        kwargs: dict[str, Any] = {
            "region_name": self.region,
            **self._get_credentials(),
        }

        if settings.use_local_dynamodb and settings.dynamodb_endpoint_url:
            kwargs["endpoint_url"] = settings.dynamodb_endpoint_url

        return boto3.resource("dynamodb", **kwargs)

    def get_dynamodb_client(self) -> Any:
        """Get DynamoDB client."""
        kwargs: dict[str, Any] = {
            "region_name": self.region,
            "config": self.config,
            **self._get_credentials(),
        }

        if settings.use_local_dynamodb and settings.dynamodb_endpoint_url:
            kwargs["endpoint_url"] = settings.dynamodb_endpoint_url

        return boto3.client("dynamodb", **kwargs)

    def get_bedrock_client(self) -> Any:
        """Get Bedrock runtime client for model invocation."""
        return boto3.client(
            "bedrock-runtime",
            region_name=self.bedrock_region,
            config=Config(
                region_name=self.bedrock_region,
                retries={"max_attempts": 3, "mode": "adaptive"},
                read_timeout=120,
            ),
            **self._get_credentials(),
        )

    def get_bedrock_agent_client(self) -> Any:
        """Get Bedrock agent client."""
        return boto3.client(
            "bedrock-agent-runtime",
            region_name=self.bedrock_region,
            config=self.config,
            **self._get_credentials(),
        )


@lru_cache
def get_aws_config() -> AWSConfig:
    """Get cached AWS config instance."""
    return AWSConfig()


aws_config = get_aws_config()


def get_dynamodb_client() -> Any:
    """Get DynamoDB client."""
    return aws_config.get_dynamodb_client()


def get_dynamodb_resource() -> Any:
    """Get DynamoDB resource."""
    return aws_config.get_dynamodb_resource()


def get_bedrock_client() -> Any:
    """Get Bedrock runtime client."""
    return aws_config.get_bedrock_client()
