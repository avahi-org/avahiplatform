import boto3
from .s3_helper import S3Helper
from .bedrock_helper import BedrockHelper
from loguru import logger
import botocore.exceptions


class BotoHelper:

    _bedrock_helper: BedrockHelper = None
    _s3_helper: S3Helper = None

    def __init__(self, aws_access_key_id=None,
                 aws_secret_access_key=None, region_name=None):
        self._session = boto3.Session(aws_access_key_id=aws_access_key_id,
                                      aws_secret_access_key=aws_secret_access_key, region_name=region_name)

    def _create_client(self, service_name):
        """ Create a Boto3 client for the specified service. """
        try:
            return self._session.client(service_name=service_name)
        except botocore.exceptions.NoCredentialsError:
            logger.error(f"No AWS credentials found for {
                         service_name}. Please provide credentials or configure your environment.")
            raise ValueError(f"AWS credentials are required for {
                             service_name}. Provide aws_access_key_id and aws_secret_access_key or configure your environment.")
        except Exception as e:
            logger.error(f"Error setting up {service_name} client: {str(e)}")
            raise

    def get_or_create_bedrock_helper(self) -> BedrockHelper:
        """ Get helper for the Bedrock service. """
        if self._bedrock_helper is None:
            bedrock_client = self._create_client(
                service_name="bedrock-runtime")
            self._bedrock_helper = BedrockHelper(bedrock_client=bedrock_client)
        return self._bedrock_helper

    def get_or_create_s3_helper(self) -> S3Helper:
        """ Get helper for the S3 service. """
        if self._s3_helper is None:
            s3_client = self._create_client(service_name="s3")
            self._s3_helper = S3Helper(s3_client=s3_client)
        return self._s3_helper
