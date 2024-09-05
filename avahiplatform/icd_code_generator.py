import boto3
import os
import json
from loguru import logger
import pymupdf
import docx
from io import BytesIO
import botocore.exceptions


class ICDCodeGenerator:
    def __init__(self, aws_access_key_id=None,
                 aws_secret_access_key=None, region_name=None):
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.cm_client = self._get_comprehend_client()

    def _get_comprehend_client(self):
        try:
            if self.aws_access_key_id and self.aws_secret_access_key:
                logger.info("Using provided AWS credentials for authentication.")
                session = boto3.Session(
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key,
                    region_name=self.region_name
                )
                return session.client(service_name="comprehendmedical")
            else:
                logger.info("No explicit credentials provided. Attempting to use default credentials.")
                return boto3.client(service_name="comprehendmedical", region_name=self.region_name)
        except botocore.exceptions.NoCredentialsError:
            logger.error("No AWS credentials found. Please provide credentials or configure your environment.")
            raise ValueError("AWS credentials are required. Please provide aws_access_key_id and aws_secret_access_key or configure your environment with AWS credentials.")
        except Exception as e:
            logger.error(f"Error setting up Bedrock client: {str(e)}")
            raise

    def generate_icdcode(self, text):
        try:
            result = self.cm_client.infer_icd10_cm(Text=text)
            icd_entities = result['Entities']
            return json.dumps(icd_entities, indent=2)
        except Exception as ex:
            logger.error(f"Error generating the icd code: {str(ex)}")
            return None

    def _read_pdf(self, file_obj):
        logger.info(f"Reading PDF content from in-memory file object")
        doc = pymupdf.open(file_obj)
        text = ""
        for page in doc:
            text += page.get_text()
        return text

    def _read_pdf_from_stream(self, file_obj):
        logger.info(f"Reading PDF content from in-memory file object")
        doc = pymupdf.open(stream=file_obj, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text

    def _read_docx(self, file_obj):
        logger.info(f"Reading DOCX content from in-memory file object")
        doc = docx.Document(file_obj)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])

    def generate_code_from_file(self, file_path):
        if not os.path.exists(file_path):
            logger.error(f"The file at {file_path} does not exist. Please check the file path.")
            raise ValueError(f"The file at {file_path} does not exist. Please check the file path.")

        _, file_extension = os.path.splitext(file_path)
        logger.info(f"Processing file: {file_path}")
        if file_extension.lower() == '.pdf':
            text = self._read_pdf(file_path)
        elif file_extension.lower() == '.docx':
            text = self._read_docx(file_path)
        else:
            with open(file_path, 'r', encoding="utf-8") as file:  # Explicitly setting encoding
                text = file.read()

        return self.generate_icdcode(text)

    def generate_code_from_s3_file(self, s3_file_path):
        s3 = boto3.client('s3')
        bucket_name, key_name = self._parse_s3_path(s3_file_path)
        try:
            logger.info(f"Fetching file from S3: {s3_file_path}")
            response = s3.get_object(Bucket=bucket_name, Key=key_name)
            content_type = response['ContentType']
            body = response['Body'].read()
            _, file_extension = os.path.splitext(key_name)
            logger.info(f"file_extension: {file_extension}")

            if 'application/pdf' in content_type or file_extension.lower() == '.pdf':
                text = self._read_pdf_from_stream(BytesIO(body))
            elif 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type or file_extension.lower() == '.docx':
                text = self._read_docx(BytesIO(body))
            else:
                text = body.decode('utf-8')

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

        return self.generate_icdcode(text)

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
