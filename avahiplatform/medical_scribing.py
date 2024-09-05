import boto3
import os
import json
from loguru import logger
from urllib.parse import urlparse
import botocore.exceptions
import uuid
import time


class MedicalScribe:
    def __init__(self, input_bucket_name, iam_arn,
                 aws_access_key_id=None,
                 aws_secret_access_key=None, region_name=None,
                 ):
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.iam_arn = iam_arn
        self.transcribe_client = self._get_medical_transcribe_client()
        self.s3_client = self._get_s3_client()
        self.input_bucket_name = input_bucket_name
        self.output_bucket_name = self.input_bucket_name.replace("input", "output")
        self.folder_name = str(uuid.uuid4())

    def _get_medical_transcribe_client(self):
        try:
            if self.aws_access_key_id and self.aws_secret_access_key:
                logger.info("Using provided AWS credentials for authentication.")
                session = boto3.Session(
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key,
                    region_name=self.region_name
                )
                return session.client(service_name="transcribe")
            else:
                logger.info("No explicit credentials provided. Attempting to use default credentials.")
                return boto3.client(service_name="transcribe", region_name=self.region_name)
        except botocore.exceptions.NoCredentialsError:
            logger.error("No AWS credentials found. Please provide credentials or configure your environment.")
            raise ValueError("AWS credentials are required. Please provide aws_access_key_id and aws_secret_access_key or configure your environment with AWS credentials.")
        except Exception as e:
            logger.error(f"Error setting up Bedrock client: {str(e)}")
            raise

    def _get_s3_client(self):
        try:
            if self.aws_access_key_id and self.aws_secret_access_key:
                logger.info("Using provided AWS credentials for authentication.")
                session = boto3.Session(
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key,
                    region_name=self.region_name
                )
                return session.client(service_name="s3")
            else:
                logger.info("No explicit credentials provided. Attempting to use default credentials.")
                return boto3.client(service_name="s3", region_name=self.region_name)
        except botocore.exceptions.NoCredentialsError:
            logger.error("No AWS credentials found. Please provide credentials or configure your environment.")
            raise ValueError("AWS credentials are required. Please provide aws_access_key_id and aws_secret_access_key or configure your environment with AWS credentials.")
        except Exception as e:
            logger.error(f"Error setting up Bedrock client: {str(e)}")
            raise

    def _bucket_exists(self, bucket_name):
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

    def _create_bucket(self, bucket_name):
        if self._bucket_exists(bucket_name):
            logger.info(f"Bucket already exists: {bucket_name}")
            return

        try:
            self.s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': self.region_name,
                }
            )
            logger.info(f"Bucket created: {bucket_name}")
        except self.s3_client.exceptions.BucketAlreadyOwnedByYou:
            logger.error(f"Bucket already exists and is owned by you: {bucket_name}")
        except self.s3_client.exceptions.BucketAlreadyExists:
            logger.error(f"Bucket already exists but is owned by someone else: {bucket_name}")
        except Exception as e:
            logger.error(f"Error creating bucket: {str(e)}")

    def _format_conversation(self, data):
        transcripts = data.get('Conversation', {}).get('TranscriptItems', [])
        dialogue = []
        current_speaker = "Speaker 1"
        last_speaker = "Speaker 1"
        speech_accumulator = ""
        for item in transcripts:
            content = " ".join(alt['Content'] for alt in item.get('Alternatives', []) if alt['Content'].strip())
            # Determine speaker change by questions and answers
            if content.endswith('?'):
                if last_speaker == "Speaker 1":
                    current_speaker = "Speaker 2"
                else:
                    current_speaker = "Speaker 1"
            if last_speaker != current_speaker:
                if speech_accumulator:
                    dialogue.append(f"{last_speaker}: {speech_accumulator.strip()}")
                    speech_accumulator = content + " "
                last_speaker = current_speaker
            else:
                speech_accumulator += content + " "
        # Add the last accumulated speech
        if speech_accumulator:
            dialogue.append(f"{current_speaker}: {speech_accumulator.strip()}")
        return "\n".join(dialogue)

    def _extract_clinical_report(self, data):
        output = []
        sections = data.get('ClinicalDocumentation', {}).get('Sections', [])
        for section in sections:
            output.append(f"Section: {section.get('SectionName')}")
            summaries = section.get('Summary', [])
            for summary in summaries:
                output.append(f"  {summary.get('SummarizedSegment')}")
            output.append("\n")
        return "\n".join(output)

    def _save_to_s3(self, filepath):
        # Extract filename from filepath
        filename = filepath.split('/')[-1]
        _, file_extension = os.path.splitext(filename)
        if file_extension not in [".mp3", ".wav"]:
            logger.error(f"{filepath} is not mp3 or wav")
            raise ValueError(f"{filepath} is not mp3 or wav")
        key = f"{self.folder_name}/{filename}"

        self._create_bucket(self.input_bucket_name)

        try:
            # Open the file in binary mode and read its content
            with open(filepath, 'rb') as file_content:
                self.s3_client.put_object(Bucket=self.input_bucket_name, Key=key, Body=file_content)
            logger.info(f"File saved to S3: {self.input_bucket_name}/{key}")
            return key
        except Exception as e:
            logger.error(f"Error saving file to S3: {str(e)}")
            return None

    def _fetch_and_save_to_s3(self, s3_uri):
        parsed_url = urlparse(s3_uri)
        source_bucket = parsed_url.netloc
        source_key = parsed_url.path.lstrip('/')

        try:
            response = self.s3_client.get_object(Bucket=source_bucket, Key=source_key)
            file_extension = os.path.splitext(source_key)[1]
            filename = source_key.split('/')[-1]

            if file_extension not in [".mp3", ".wav"]:
                logger.error(f"{s3_uri} is not mp3 or wav")
                raise ValueError(f"{s3_uri} is not mp3 or wav")

            # Save the file content to the desired S3 bucket
            key = f"{self.folder_name}/{filename}"
            self.s3_client.put_object(Bucket=self.input_bucket_name, Key=key, Body=response['Body'].read())
            logger.info(f"File fetched from {s3_uri} and saved to S3: {self.input_bucket_name}/{key}")
            return key, filename
        except Exception as e:
            logger.error(f"Error fetching file from S3 URI: {str(e)}")
            return None, None

    def _generate_medical_scribing(self, job_name, object_key):
        s3_input_uri = f"s3://{self.input_bucket_name}/{object_key}"

        self._create_bucket(self.output_bucket_name)

        response = self.transcribe_client.start_medical_scribe_job(
            MedicalScribeJobName=job_name,
            Media={
                'MediaFileUri': s3_input_uri
            },
            OutputBucketName=self.output_bucket_name,
            DataAccessRoleArn=self.iam_arn,
            Settings={
                'ShowSpeakerLabels': True,
                'MaxSpeakerLabels': 29,
                'ChannelIdentification': False
            }
        )
        while True:
            status = self.transcribe_client.get_medical_scribe_job(MedicalScribeJobName=job_name)
            if status['MedicalScribeJob']['MedicalScribeJobStatus'] in ['COMPLETED', 'FAILED']:
                break
            logger.info("Not ready yet...")
            time.sleep(5)

        logger.info("Job status: " + status.get('MedicalScribeJob').get('MedicalScribeJobStatus'))

        start_time = status.get('MedicalScribeJob').get('StartTime')
        completion_time = status.get('MedicalScribeJob').get('CompletionTime')
        diff = completion_time - start_time

        logger.info("Job duration: " + str(diff))
        transcript_file = status.get('MedicalScribeJob').get('MedicalScribeOutput').get('TranscriptFileUri')
        summary_file = status.get('MedicalScribeJob').get('MedicalScribeOutput').get('ClinicalDocumentUri')
        logger.info("Transcription file: " + transcript_file)
        logger.info("Summary file: " + summary_file)
        logger.info("Summary and transcript generated")

    def _start_medical_scribing(self, job_name, object_key):
        self._generate_medical_scribing(job_name, object_key)

        summary_file = job_name + "/summary.json"
        transcript_file = job_name + "/transcript.json"

        summary_obj = self.s3_client.get_object(Bucket=self.output_bucket_name, Key=summary_file)
        summary_json = json.loads(summary_obj['Body'].read())

        transcript_obj = self.s3_client.get_object(Bucket=self.output_bucket_name, Key=transcript_file)
        transcript_json = json.loads(transcript_obj['Body'].read())

        output_formated_transcript_json = self._format_conversation(transcript_json)
        report_data = self._extract_clinical_report(summary_json)

        return report_data, output_formated_transcript_json

    def fetch_medical_scribing_from_filepath(self, filepath):
        object_key = self._save_to_s3(filepath)
        filename = filepath.split('/')[-1]
        job_name = f"{self.folder_name}-{filename[:-4]}"
        logger.info("Medical-scribe job started")

        summary_report_data, output_formated_transcript_json = self._start_medical_scribing(job_name, object_key)

        return summary_report_data, output_formated_transcript_json

    def fetch_medical_scribing_from_s3_path(self, s3_path):
        object_key, filename = self._fetch_and_save_to_s3(s3_path)
        job_name = f"{self.folder_name}-{filename[:-4]}"
        logger.info("Medical-scribe job started")

        summary_report_data, output_formated_transcript_json = self._start_medical_scribing(job_name, object_key)

        return summary_report_data, output_formated_transcript_json

    def _get_user_friendly_error(self, error):
        # Customize user-friendly error messages here
        if isinstance(error, ValueError):
            return str(error)
        elif isinstance(error, botocore.exceptions.BotoCoreError):
            return "An error occurred with the AWS service. Please check your AWS resources and permissions."
        else:
            return f"An unexpected error occurred: {str(error)}."
