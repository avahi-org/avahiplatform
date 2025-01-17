from typing import Optional, Any
import boto3
from boto3.session import Session
from boto3.resources.base import ServiceResource
from botocore.client import BaseClient
from loguru import logger
import botocore.exceptions


class BotoHelper:
    """A helper class to manage AWS SDK (boto3) interactions.

    This class provides a wrapper around boto3 Session to create clients and resources
    with proper error handling and logging.
    """

    def __init__(
        self,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: Optional[str] = None,
        aws_session_token: Optional[str] = None,
    ) -> None:
        """Initialize a new BotoHelper instance.

        Args:
            aws_access_key_id: AWS access key ID. If not provided, will use environment variables.
            aws_secret_access_key: AWS secret access key. If not provided, will use environment variables.
            region_name: AWS region name. If not provided, will use environment variables.
        """
        self._session: Session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            region_name=region_name
        )

    def create_client(self, service_name: str) -> BaseClient:
        """Create a Boto3 client for the specified service.

        Args:
            service_name: The name of the AWS service (e.g., 's3', 'ec2', etc.)

        Returns:
            A boto3 client instance for the specified service.

        Raises:
            ValueError: If AWS credentials are not properly configured.
            Exception: For other boto3-related errors.
        """
        try:
            return self._session.client(service_name=service_name)
        except botocore.exceptions.NoCredentialsError as e:
            logger.error(f"No AWS credentials found for {service_name}. Please provide credentials or configure your environment.")
            raise ValueError(
                f"AWS credentials are required for {service_name}. "
                "Provide aws_access_key_id and aws_secret_access_key or configure your environment."
            ) from e
        except botocore.exceptions.PartialCredentialsError as e:
            logger.error(f"Incomplete AWS credentials for {service_name}. Both access key and secret key are required.")
            raise ValueError(
                f"Incomplete AWS credentials for {service_name}. "
                "Both aws_access_key_id and aws_secret_access_key are required."
            ) from e
        except Exception as e:
            logger.error(f"Error setting up {service_name} client: {str(e)}")
            raise

    def create_resource(self, service_name: str) -> ServiceResource:
        """Create a Boto3 resource for the specified service.

        Args:
            service_name: The name of the AWS service (e.g., 's3', 'ec2', etc.)

        Returns:
            A boto3 resource instance for the specified service.

        Raises:
            ValueError: If AWS credentials are not properly configured.
            Exception: For other boto3-related errors.
        """
        try:
            return self._session.resource(service_name=service_name)
        except botocore.exceptions.NoCredentialsError as e:
            logger.error(f"No AWS credentials found for {service_name}. Please provide credentials or configure your environment.")
            raise ValueError(
                f"AWS credentials are required for {service_name}. "
                "Provide aws_access_key_id and aws_secret_access_key or configure your environment."
            ) from e
        except botocore.exceptions.PartialCredentialsError as e:
            logger.error(f"Incomplete AWS credentials for {service_name}. Both access key and secret key are required.")
            raise ValueError(
                f"Incomplete AWS credentials for {service_name}. "
                "Both aws_access_key_id and aws_secret_access_key are required."
            ) from e
        except Exception as e:
            logger.error(f"Error setting up {service_name} resource: {str(e)}")
            raise
