import os
from loguru import logger
from typing import Optional, Union, Dict, Any
from avahiplatform.helpers.chats.bedrock_chat import BedrockChat
import pymupdf
import docx
from io import BytesIO
import boto3
import botocore.exceptions


class DataMasking:
    def __init__(self, bedrockchat: BedrockChat):
        """
        Initialize the DataMasking with BedrockChat instance.

        Args:
            bedrockchat (BedrockChat): BedrockChat instance for making API calls.
        """
        self.bedrockchat = bedrockchat

        # Default system prompts for different types of content
        self.default_prompts = {
            "text": "Please selectively mask specific types of sensitive data in the following text by replacing only the characters of the sensitive information with '*'. Leave all other text unchanged:\n\n",
            "document": "Please selectively mask specific types of sensitive data in the following document content by replacing only the characters of the sensitive information with '*'. Leave all other text unchanged:\n\n",
            "s3_document": "Please selectively mask specific types of sensitive data in the following document content by replacing only the characters of the sensitive information with '*'. Leave all other text unchanged:\n\n"
        }

    def _create_prompt_list(
        self,
        content_type: str,
        content: Union[str, bytes],
        system_prompt: Optional[str] = None
    ) -> list:
        """
        Creates a list of prompts for the BedrockChat API.

        Args:
            content_type (str): Type of content ('text', 'document').
            content (Union[str, bytes]): The actual content or path to content.
            system_prompt (Optional[str]): Optional custom system prompt.

        Returns:
            list: List of prompts formatted for BedrockChat.
        """
        if not system_prompt:
            system_prompt = self.default_prompts.get(content_type, self.default_prompts["text"])

        if content_type == "text":
            prompts = [
                {"text": f"system_prompt: {system_prompt}\n user_prompt: {content}"}
            ]
        else:
            prompts = [
                {"text": system_prompt},
                {content_type: content}
            ]

        return prompts

    def mask(
        self,
        content_type: str,
        content: Union[str, bytes],
        system_prompt: Optional[str] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Mask sensitive data in the provided content using the Bedrock model.

        Args:
            content_type (str): Type of content ('text', 'document').
            content (Union[str, bytes]): The content to mask (can be text or file path).
            system_prompt (Optional[str]): Optional custom system prompt.
            stream (bool): Whether to stream the response.

        Returns:
            Dict[str, Any]: Response containing masked text and metadata.
        """
        try:
            prompts = self._create_prompt_list(content_type, content, system_prompt)

            if stream:
                logger.info("Invoking BedrockChat in streaming mode for Data Masking.")
                response = self.bedrockchat.invoke_stream_parsed(prompts)
            else:
                logger.info("Invoking BedrockChat in standard mode for Data Masking.")
                response = self.bedrockchat.invoke(prompts)

            return response

        except Exception as e:
            logger.error(f"Error in data masking: {str(e)}")
            raise

    def mask_text(
        self,
        text: str,
        system_prompt: Optional[str] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Mask sensitive data in text content.

        Args:
            text (str): The input text to be masked.
            system_prompt (Optional[str]): Optional custom system prompt.
            stream (bool): Whether to stream the response.

        Returns:
            Dict[str, Any]: Response containing masked text and metadata.
        """
        return self.mask("text", text, system_prompt, stream)

    def mask_document(
        self,
        file_path: str,
        system_prompt: Optional[str] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Mask sensitive data in a local document file.

        Args:
            file_path (str): Path to the document file.
            system_prompt (Optional[str]): Optional custom system prompt.
            stream (bool): Whether to stream the response.

        Returns:
            Dict[str, Any]: Response containing masked text and metadata.
        """
        return self.mask("document", file_path, system_prompt, stream)

    def mask_s3_file(
        self,
        s3_file_path: str,
        system_prompt: Optional[str] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Mask sensitive data in a file stored in S3.

        Args:
            s3_file_path (str): S3 path to the input file.
            system_prompt (Optional[str]): Optional custom system prompt.
            stream (bool): Whether to stream the response.

        Returns:
            Dict[str, Any]: Response containing masked text and metadata.
        """
        return self.mask("s3_document", s3_file_path, system_prompt, stream)

