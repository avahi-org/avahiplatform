from loguru import logger
from io import BytesIO
from .utils import Utils
import os
import pandas as pd
import io


class S3Helper:
    def __init__(self, s3_client):
        self.s3_client = s3_client

    def read_s3_file(self, s3_file_path):
        bucket_name, key_name = self.parse_s3_path(s3_file_path)
        try:
            logger.info(f"Fetching file from S3: {s3_file_path}")
            response = self.s3_client.get_object(
                Bucket=bucket_name, Key=key_name)
            content_type = response['ContentType']
            body = response['Body'].read()

            if 'application/pdf' in content_type:
                text = Utils.read_pdf_from_stream(BytesIO(body))
            elif 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type:
                text = Utils.read_docx(BytesIO(body))
            else:
                text = body.decode('utf-8')

        except self.s3_client.exceptions.NoSuchKey:
            logger.error(f"The file {s3_file_path} does not exist in the S3 bucket. Please check the S3 file path.")
            raise ValueError(f"The file {s3_file_path} does not exist in the S3 bucket. Please check the S3 file path.")
        except self.s3_client.exceptions.NoSuchBucket:
            logger.error(
                f"The S3 bucket does not exist. Please check the bucket name in the S3 file path.")
            raise ValueError(
                f"The S3 bucket does not exist. Please check the bucket name in the S3 file path.")
        except Exception as e:
            user_friendly_error = Utils.get_user_friendly_error(e)
            logger.error(user_friendly_error)
            raise ValueError(user_friendly_error)

        return text

    def parse_s3_path(self, s3_file_path):
        if not s3_file_path.startswith('s3://'):
            logger.error(
                "S3 path should start with 's3://'. Please check the S3 file path.")
            raise ValueError(
                "S3 path should start with 's3://'. Please check the S3 file path.")
        parts = s3_file_path[5:].split('/', 1)
        if len(parts) != 2:
            logger.error(
                "Invalid S3 path format. It should be 's3://bucket_name/key_name'.")
            raise ValueError(
                "Invalid S3 path format. It should be 's3://bucket_name/key_name'.")
        return parts[0], parts[1]

    def get_s3_object(self, bucket_name, key_name):
        try:
            response = self.s3_client.get_object(Bucket=bucket_name, Key=key_name)
            content_type = response['ContentType']
            image_data = response['Body'].read()

            if "image" not in content_type:
                logger.error("Invalid S3 object. The ContentType of the object should be an image.")
                raise ValueError("Invalid S3 object. The ContentType of the object should be an image.")

        except self.s3_client.exceptions.NoSuchKey:
            logger.error(f"The file {key_name} does not exist in the S3 bucket. Please check the S3 file path.")
            raise ValueError(f"The file {key_name} does not exist in the S3 bucket. Please check the S3 file path.")
        except self.s3_client.exceptions.NoSuchBucket:
            logger.error(f"The S3 bucket does not exist. Please check the bucket name in the S3 file path.")
            raise ValueError(f"The S3 bucket does not exist. Please check the bucket name in the S3 file path.")
        except Exception as e:
            user_friendly_error = Utils.get_user_friendly_error(e)
            logger.error(user_friendly_error)
            raise ValueError(user_friendly_error)

        return image_data

    def get_s3_folder_objects(self, bucket_name, folder_name):
        try:
            # List all objects in the bucket
            all_objects = self.s3_client.list_objects(Bucket=bucket_name)['Contents']
        except self.s3_client.exceptions.NoSuchBucket:
            raise ValueError(f"The S3 bucket does not exist. Please check the bucket name in the S3 file path.")
        except Exception as e:
            user_friendly_error = Utils.get_user_friendly_error(e)
            logger.error(user_friendly_error)
            raise ValueError(user_friendly_error)

        folder_objects = {}
        # Filter and fetch objects in the folder
        for _object in all_objects:
            key_name = _object['Key']
            if (folder_name + "/") in key_name:
                response = self.s3_client.get_object(Bucket=bucket_name, Key=key_name)
                content_type = response['ContentType']
                if "image" in content_type:
                    folder_objects[key_name] = response['Body'].read()

        # Check if the folder is empty
        if not folder_objects:
            raise ValueError(f"The folder '{folder_name}' is empty or does not exist in the bucket '{bucket_name}'.")

        return folder_objects

    def bucket_exists(self, bucket_name):
        try:
            # Check if the bucket exists
            self.s3_client.head_bucket(Bucket=bucket_name)
            return True
        except self.s3_client.exceptions.NoSuchBucket:
            return False
        except self.s3_client.exceptions.ClientError as e:
            # If a client error is thrown, check that it was a 404 error.
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                return False
            raise

    def create_bucket(self, bucket_name, region_name):
        if self.bucket_exists(bucket_name):
            logger.info(f"Bucket already exists: {bucket_name}")
            return

        try:
            self.s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': region_name,
                }
            )
            logger.info(f"Bucket created: {bucket_name}")
        except self.s3_client.exceptions.BucketAlreadyOwnedByYou:
            logger.error(f"Bucket already exists and is owned by you: {bucket_name}")
        except self.s3_client.exceptions.BucketAlreadyExists:
            logger.error(f"Bucket already exists but is owned by someone else: {bucket_name}")
        except Exception as e:
            logger.error(f"Error creating bucket: {str(e)}")

    def save_to_s3(self, filepath, bucket_name, folder_name, allowed_extensions=None):
        # Extract filename from filepath
        filename = filepath.split('/')[-1]
        _, file_extension = os.path.splitext(filename)
        
        if allowed_extensions and file_extension not in allowed_extensions:
            logger.error(f"{filepath} has invalid extension. Allowed extensions: {allowed_extensions}")
            raise ValueError(f"{filepath} has invalid extension. Allowed extensions: {allowed_extensions}")
        
        key = f"{folder_name}/{filename}" if folder_name else filename

        try:
            # Open the file in binary mode and read its content
            with open(filepath, 'rb') as file_content:
                self.s3_client.put_object(Bucket=bucket_name, Key=key, Body=file_content)
            logger.info(f"File saved to S3: {bucket_name}/{key}")
            return key
        except Exception as e:
            logger.error(f"Error saving file to S3: {str(e)}")
            return None

    def fetch_and_save_to_s3(self, s3_uri, target_bucket, folder_name, allowed_extensions=None):
        from urllib.parse import urlparse
        
        parsed_url = urlparse(s3_uri)
        source_bucket = parsed_url.netloc
        source_key = parsed_url.path.lstrip('/')

        try:
            response = self.s3_client.get_object(Bucket=source_bucket, Key=source_key)
            file_extension = os.path.splitext(source_key)[1]
            filename = source_key.split('/')[-1]

            if allowed_extensions and file_extension not in allowed_extensions:
                logger.error(f"{s3_uri} has invalid extension. Allowed extensions: {allowed_extensions}")
                raise ValueError(f"{s3_uri} has invalid extension. Allowed extensions: {allowed_extensions}")

            # Save the file content to the target S3 bucket
            key = f"{folder_name}/{filename}" if folder_name else filename
            self.s3_client.put_object(Bucket=target_bucket, Key=key, Body=response['Body'].read())
            logger.info(f"File fetched from {s3_uri} and saved to S3: {target_bucket}/{key}")
            return key, filename
        except Exception as e:
            logger.error(f"Error fetching file from S3 URI: {str(e)}")
            return None, None

    def fetch_csv_files(self, s3_file_paths: dict) -> dict:
        dataframes = {}
        for name, s3_file_path in s3_file_paths.items():
            bucket_name, key_name = self.parse_s3_path(s3_file_path)
            try:
                logger.info(f"Fetching file from S3: {s3_file_path}")
                response = self.s3_client.get_object(Bucket=bucket_name, Key=key_name)
                content_type = response['ContentType']
                body = response['Body'].read()
                _, file_extension = os.path.splitext(key_name)
                
                if content_type == 'text/csv' or file_extension.lower() == '.csv':
                    dataframes[name] = pd.read_csv(io.StringIO(body.decode('utf-8')))
                else:
                    logger.error(f"Unsupported content type: {content_type}. Expected 'text/csv'.")
                    raise ValueError(f"Unsupported content type: {content_type}. Expected 'text/csv'.")
                    
            except self.s3_client.exceptions.NoSuchKey:
                logger.error(f"The file {s3_file_path} does not exist in the S3 bucket.")
                raise ValueError(f"The file {s3_file_path} does not exist in the S3 bucket.")
            except self.s3_client.exceptions.NoSuchBucket:
                logger.error(f"The S3 bucket {bucket_name} does not exist.")
                raise ValueError(f"The S3 bucket {bucket_name} does not exist.")
            except Exception as e:
                logger.error(f"Error fetching CSV from S3: {str(e)}")
                raise ValueError(f"Error fetching CSV from S3: {str(e)}")
                
        return dataframes