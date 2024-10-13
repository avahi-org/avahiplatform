
from loguru import logger
import botocore.exceptions
import pymupdf
import docx


def get_user_friendly_error(self, error):
    # Customize user-friendly error messages here
    if isinstance(error, ValueError):
        return str(error)
    elif isinstance(error, botocore.exceptions.BotoCoreError):
        return "An error occurred with the AWS service. Please check your AWS resources and permissions."
    else:
        return f"An unexpected error occurred: {str(error)}."


def read_pdf(self, file_obj):
    logger.info(f"Reading PDF content from in-memory file object")
    doc = pymupdf.open(file_obj)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def read_pdf_from_stream(self, file_obj):
    logger.info(f"Reading PDF content from in-memory file object")
    doc = pymupdf.open(stream=file_obj, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def read_docx(self, file_obj):
    logger.info(f"Reading DOCX content from in-memory file object")
    doc = docx.Document(file_obj)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])
