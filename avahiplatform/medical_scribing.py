import json
from loguru import logger
import uuid
import time
from avahiplatform.helpers.connectors.boto_helper import BotoHelper
from avahiplatform.helpers.connectors.s3_helper import S3Helper
from avahiplatform.helpers.connectors.utils import Utils

class MedicalScribe:
    def __init__(self, input_bucket_name, iam_arn,
                 boto_helper: BotoHelper,
                 s3_helper: S3Helper,
                 ):
        self.iam_arn = iam_arn
        self.boto_helper = boto_helper
        self.s3_helper = s3_helper
        self.s3_client = self.boto_helper.create_client(service_name="s3")
        self.transcribe_client = self.boto_helper.create_client(service_name="transcribe")
        self.input_bucket_name = input_bucket_name
        self.output_bucket_name = self.input_bucket_name.replace("input", "output")
        self.folder_name = str(uuid.uuid4())

    def _generate_medical_scribing(self, job_name, object_key):
        s3_input_uri = f"s3://{self.input_bucket_name}/{object_key}"

        self.s3_helper.create_bucket(self.output_bucket_name)

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

        output_formated_transcript_json = Utils.format_conversation(transcript_json)
        report_data = Utils.extract_clinical_report(summary_json)

        return report_data, output_formated_transcript_json

    def fetch_medical_scribing_from_filepath(self, filepath):
        object_key = self.s3_helper.save_to_s3(filepath)
        filename = filepath.split('/')[-1]
        job_name = f"{self.folder_name}-{filename[:-4]}"
        logger.info("Medical-scribe job started")

        summary_report_data, output_formated_transcript_json = self._start_medical_scribing(job_name, object_key)

        return summary_report_data, output_formated_transcript_json

    def fetch_medical_scribing_from_s3_path(self, s3_path):
        object_key, filename = self.s3_helper.fetch_and_save_to_s3(s3_path)
        job_name = f"{self.folder_name}-{filename[:-4]}"
        logger.info("Medical-scribe job started")

        summary_report_data, output_formated_transcript_json = self._start_medical_scribing(job_name, object_key)

        return summary_report_data, output_formated_transcript_json