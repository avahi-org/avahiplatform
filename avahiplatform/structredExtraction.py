import os
from loguru import logger
from .helpers import Helpers

class BedrockstructredExtraction:
    def __init__(self, default_model_name='sonnet-3', aws_access_key_id=None,
                 aws_secret_access_key=None, region_name=None):
        self.helpers = Helpers(default_model_name=default_model_name,
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              region_name=region_name)

    def extract_text(self, text, user_prompt=None, model_name=None):
        if not text:
            logger.error("Input text cannot be empty.")
            raise ValueError("Input text cannot be empty.")

        prompt = user_prompt if user_prompt else f"""extract the below entities from this model in structured format:
1. Name:
2. Places:


Text: {text}

response should be json in below format

""" + """response should be json in below format

{
  "Name": ["Name1", "Name2"]
  "Places": [
    "Place1",
    "Place2"
  ] 
}

Make sure output has only json output. No other extra words"""
        return self.helpers.model_invoke(prompt, model_name)

    def extract_file(self, file_path, user_prompt=None, model_name=None):
        if not os.path.exists(file_path):
            logger.error(f"The file at {file_path} does not exist. Please check the file path.")
            raise ValueError(f"The file at {file_path} does not exist. Please check the file path.")

        _, file_extension = os.path.splitext(file_path)
        logger.info(f"Processing file: {file_path}")
        if file_extension.lower() == '.pdf':
            text = self.helpers.read_pdf(file_path)
        elif file_extension.lower() == '.docx':
            text = self.helpers.read_docx(file_path)
        else:
            with open(file_path, 'r', encoding="utf-8") as file:  # Explicitly setting encoding
                text = file.read()

        return self.extract_text(text, user_prompt, model_name)

    def extract_s3_file(self, s3_file_path, user_prompt=None, model_name=None):
        text = self.helpers.read_s3_file(s3_file_path=s3_file_path)
        return self.extract_text(text, user_prompt, model_name)
