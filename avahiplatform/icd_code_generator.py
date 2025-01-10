from re import U
import os
import json
from loguru import logger
from avahiplatform.helpers.connectors.boto_helper import BotoHelper
from avahiplatform.helpers.connectors.s3_helper import S3Helper
from avahiplatform.helpers.connectors.utils import Utils

class ICDCodeGenerator:
    def __init__(self, boto_helper: BotoHelper, s3_helper: S3Helper):
        self.boto_helper = boto_helper
        self.s3_helper = s3_helper
        self.cm_client = self.boto_helper.create_client(service_name="comprehendmedical")

    def generate_icdcode(self, text):
        try:
            result = self.cm_client.infer_icd10_cm(Text=text)
            icd_entities = result['Entities']
            return json.dumps(icd_entities, indent=2)
        except Exception as ex:
            return None

    def generate_code_from_file(self, file_path):
        if not os.path.exists(file_path):
            raise ValueError(f"The file at {file_path} does not exist. Please check the file path.")

        _, file_extension = os.path.splitext(file_path)
        logger.info(f"Processing file: {file_path}")
        if file_extension.lower() == '.pdf':
            text = Utils.read_pdf(file_path)
        elif file_extension.lower() == '.docx':
            text = Utils.read_docx(file_path)
        else:
            with open(file_path, 'r', encoding="utf-8") as file:  # Explicitly setting encoding
                text = file.read()

        return self.generate_icdcode(text)

    def generate_code_from_s3_file(self, s3_file_path):
        text = self.s3_helper.read_s3_file(s3_file_path)

        return self.generate_icdcode(text)