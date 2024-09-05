import boto3
import time
from loguru import logger
import botocore.exceptions
import pandas as pd
import io
import os
import langchain
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_aws import ChatBedrock


class QueryCSV:
    def __init__(self, default_model_name='sonnet-3', aws_access_key_id=None,
                 aws_secret_access_key=None, region_name=None):
        self.region_name = region_name
        self.default_model_name = default_model_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.bedrock = self._get_bedrock_client()

    def _get_bedrock_client(self):
        try:
            if self.aws_access_key_id and self.aws_secret_access_key:
                logger.info("Using provided AWS credentials for authentication.")
                session = boto3.Session(
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key,
                    region_name=self.region_name
                )
                return session.client(service_name="bedrock-runtime")
            else:
                logger.info("No explicit credentials provided. Attempting to use default credentials.")
                return boto3.client(service_name="bedrock-runtime", region_name=self.region_name)
        except botocore.exceptions.NoCredentialsError:
            logger.error("No AWS credentials found. Please provide credentials or configure your environment.")
            raise ValueError(
                "AWS credentials are required. Please provide aws_access_key_id and aws_secret_access_key or configure your environment with AWS credentials.")
        except Exception as e:
            logger.error(f"Error setting up Bedrock client: {str(e)}")
            raise

    def model_invoke(self, query, df, model_name=None, max_retries=15, initial_delay=2):
        if model_name is None:
            model_name = self.default_model_name

        model_id, _, _ = self._get_model_details(model_name)
        llm = ChatBedrock(model_id=model_id, client=self.bedrock, model_kwargs={"temperature": 0})

        agent_executor = create_pandas_dataframe_agent(
            llm,
            df,
            verbose=False,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            allow_dangerous_code=True,
        )
        langchain.debug = False

        retries = 0
        while retries < max_retries:
            try:
                result = agent_executor.invoke(query)["output"]
                return result

            except self.bedrock.exceptions.ThrottlingException as e:
                retries += 1
                wait_time = initial_delay * (2 ** (retries - 1))  # Exponential backoff
                logger.warning(f"Service is being throttled. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            except Exception as e:
                user_friendly_error = self._get_user_friendly_error(e)
                logger.error(user_friendly_error)
                break

        return None

    def _get_model_details(self, model_name):
        if model_name.lower() == "sonnet-3.5":
            model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
            input_cost = 0.003
            output_cost = 0.015
        elif model_name.lower() == "sonnet-3":
            model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
            input_cost = 0.003
            output_cost = 0.015
        elif model_name.lower() == "haiku-3.0":
            model_id = "anthropic.claude-3-haiku-20240307-v1:0"
            input_cost = 0.00025
            output_cost = 0.00125
        else:
            logger.error(f"Unrecognized model name: {model_name}")
            raise ValueError(f"Unrecognized model name: {model_name}")

        logger.info(f"Using model: {model_id}")
        return model_id, input_cost, output_cost

    def query_from_local_path(self, user_query, csv_file_path, model_name=None):
        try:
            df = pd.read_csv(str(csv_file_path))

        except Exception as e:
            user_friendly_error = self._get_user_friendly_error(e)
            logger.error(user_friendly_error)
            raise ValueError(user_friendly_error)

        return self.model_invoke(user_query, df, model_name)

    def query_from_s3(self, user_query, s3_file_path, model_name=None):
        s3 = boto3.client('s3')
        bucket_name, key_name = self._parse_s3_path(s3_file_path)
        try:
            logger.info(f"Fetching file from S3: {s3_file_path}")
            response = s3.get_object(Bucket=bucket_name, Key=key_name)
            content_type = response['ContentType']
            body = response['Body'].read()
            _, file_extension = os.path.splitext(key_name)

            if content_type == 'text/csv' or file_extension.lower() == '.csv':
                # Read the CSV file content into a DataFrame
                df = pd.read_csv(io.StringIO(body.decode('utf-8')))
            else:
                logger.error(f"Unsupported content type: {content_type}. Expected 'text/csv'.")
                raise ValueError(f"Unsupported content type: {content_type}. Expected 'text/csv'.")

        except s3.exceptions.NoSuchKey:
            logger.error(f"The file {s3_file_path} does not exist in the S3 bucket. Please check the S3 file path.")
            raise ValueError(f"The file {s3_file_path} does not exist in the S3 bucket. Please check the S3 file path.")
        except s3.exceptions.NoSuchBucket:
            logger.error(f"The S3 bucket does not exist. Please check the bucket name in the S3 file path.")
            raise ValueError(f"The S3 bucket does not exist. Please check the bucket name in the S3 file path.")
        except Exception as e:
            user_friendly_error = self._get_user_friendly_error(e)
            logger.error(user_friendly_error)
            raise ValueError(user_friendly_error)

        return self.model_invoke(user_query, df, model_name)

    def _parse_s3_path(self, s3_file_path):
        if not s3_file_path.startswith('s3://'):
            logger.error("S3 path should start with 's3://'. Please check the S3 file path.")
            raise ValueError("S3 path should start with 's3://'. Please check the S3 file path.")
        parts = s3_file_path[5:].split('/', 1)
        if len(parts) != 2:
            logger.error("Invalid S3 path format. It should be 's3://bucket_name/key_name'.")
            raise ValueError("Invalid S3 path format. It should be 's3://bucket_name/key_name'.")
        return parts[0], parts[1]

    def _get_user_friendly_error(self, error):
        # Customize user-friendly error messages here
        if isinstance(error, ValueError):
            return str(error)
        elif isinstance(error, botocore.exceptions.BotoCoreError):
            return "An error occurred with the AWS service. Please check your AWS resources and permissions."
        else:
            return f"An unexpected error occurred: {str(error)}."
