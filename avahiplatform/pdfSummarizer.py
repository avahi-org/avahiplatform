import boto3
import time
import json
import os
import pymupdf
from loguru import logger
import botocore.exceptions





class BedrockPdfSummarizer:
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
            raise ValueError("AWS credentials are required. Please provide aws_access_key_id and aws_secret_access_key or configure your environment with AWS credentials.")
        except Exception as e:
            logger.error(f"Error setting up Bedrock client: {str(e)}")
            raise

    def model_invoke(self, prompt, model_name=None, max_retries=15, initial_delay=2):
        if model_name is None:
            model_name = self.default_model_name

        model_id, input_cost, output_cost = self._get_model_details(model_name)

        body = json.dumps({
            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
            "max_tokens": 1000,
            "temperature": 0,
            "anthropic_version": "bedrock-2023-05-31"
        })

        accept = "application/json"
        content_type = "application/json"
        retries = 0

        total_input_tokens = 0.0
        total_output_tokens = 0.0

        while retries < max_retries:
            try:
                logger.info("Invoking model to extracting content.")
                response = self.bedrock.invoke_model(
                    body=body,
                    modelId=model_id,
                    accept=accept,
                    contentType=content_type
                )
                input_token_count = float(
                    response["ResponseMetadata"]["HTTPHeaders"]["x-amzn-bedrock-input-token-count"])
                output_token_count = float(
                    response["ResponseMetadata"]["HTTPHeaders"]["x-amzn-bedrock-output-token-count"])
                total_input_tokens += input_token_count
                total_output_tokens += output_token_count
                input_token_cost = (total_input_tokens / 1000) * input_cost
                output_token_cost = (total_output_tokens / 1000) * output_cost
                total_cost = input_token_cost + output_token_cost

                result = json.loads(response.get('body').read())['content'][0]['text']
                logger.info(f"Model invocation successful. Total cost: ${total_cost:.6f}")
                return result, input_token_cost, output_token_cost, total_cost

            except self.bedrock.exceptions.ThrottlingException as e:
                retries += 1
                wait_time = initial_delay * (2 ** (retries - 1))  # Exponential backoff
                logger.warning(f"Service is being throttled. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            except Exception as e:
                user_friendly_error = self._get_user_friendly_error(e)
                logger.error(user_friendly_error)
                break

        return None, 0, 0, 0.0

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

    def summarize_pdf_file(self, file_path, user_prompt=None, model_name=None):
        if not os.path.exists(file_path):
            logger.error(f"The file at {file_path} does not exist. Please check the file path.")
            raise ValueError(f"The file at {file_path} does not exist. Please check the file path.")

        _, file_extension = os.path.splitext(file_path)
        logger.info(f"Processing file: {file_path}")
        if file_extension.lower() == '.pdf':
            text = self._read_pdf(file_path)
        else:
            raise ValueError("Input file should be PDF.")

        return self.summarize_pdf_text(text, user_prompt, model_name)

    def _read_pdf(self, file_obj):
        logger.info(f"Reading PDF content from in-memory file object")
        doc = pymupdf.open(file_obj)
        text = ""
        for page in doc:
            text += page.get_text()
        return text

    def summarize_pdf_text(self, text, user_prompt=None, model_name=None):
        if not text:
            logger.error("Issue with the PDF file, please validate.")
            raise ValueError("Issue with the PDF file, please validate.")

        prompt = user_prompt if user_prompt else f"Please summarize the following text: {text}"
        return self.model_invoke(prompt, model_name)

    def _get_user_friendly_error(error):
        # Customize user-friendly error messages here
        if isinstance(error, ValueError):
            return str(error)
        elif isinstance(error, botocore.exceptions.BotoCoreError):
            return "An error occurred with the AWS service. Please check your AWS resources and permissions."
        else:
            return f"An unexpected error occurred: {str(error)}."
