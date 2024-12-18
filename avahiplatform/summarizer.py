import os
from loguru import logger
from helpers.utils import Utils
from helpers.bedrock_helper import BedrockHelper


class BedrockSummarizer:
    def __init__(self, bedrock_helper: BedrockHelper):
        self.bedrock_helper = bedrock_helper

    def summarize_text(self, text, user_prompt=None, model_name=None):
        if not text:
            logger.error("Input text cannot be empty.")
            raise ValueError("Input text cannot be empty.")

        prompt = user_prompt if user_prompt else f"Please summarize the following text: {
            text}"
        return self.bedrock_helper.model_invoke(prompt, model_name)

    def summarize_file(self, file_path, user_prompt=None, model_name=None):
        if not os.path.exists(file_path):
            logger.error(f"The file at {
                         file_path} does not exist. Please check the file path.")
            raise ValueError(
                f"The file at {file_path} does not exist. Please check the file path.")

        _, file_extension = os.path.splitext(file_path)
        logger.info(f"Processing file: {file_path}")
        if file_extension.lower() == '.pdf':
            text = Utils.read_pdf(file_path)
        elif file_extension.lower() == '.docx':
            text = Utils.read_docx(file_path)
        else:
            with open(file_path, 'r', encoding="utf-8") as file:  # Explicitly setting encoding
                text = file.read()

        return self.summarize_text(text, user_prompt, model_name)

    def summarize_s3_file(self, s3_file_path, user_prompt=None, model_name=None):
        text = Utils.read_s3_file(s3_file_path=s3_file_path)

        return self.summarize_text(text, user_prompt, model_name)
