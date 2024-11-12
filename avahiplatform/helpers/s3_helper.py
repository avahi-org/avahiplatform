from loguru import logger
from io import BytesIO
from .utils import Utils


class S3Helper:
    def __init__(self, s3_client):
        self.s3_client = s3_client

    def read_s3_file(self, s3_file_path):
        bucket_name, key_name = self._parse_s3_path(s3_file_path)
        try:
            logger.info(f"Fetching file from S3: {s3_file_path}")
            response = self.s3_client.get_object(
                Bucket=bucket_name, Key=key_name)
            content_type = response['ContentType']
            body = response['Body'].read()

            if 'application/pdf' in content_type:
                text = self.read_pdf_from_stream(BytesIO(body))
            elif 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type:
                text = self.read_docx(BytesIO(body))
            else:
                text = body.decode('utf-8')

        except self.s3_client.exceptions.NoSuchKey:
            logger.error(f"The file {
                         s3_file_path} does not exist in the S3 bucket. Please check the S3 file path.")
            raise ValueError(f"The file {
                             s3_file_path} does not exist in the S3 bucket. Please check the S3 file path.")
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
