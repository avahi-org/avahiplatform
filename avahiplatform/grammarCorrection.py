from typing import Optional, Union, Dict, Any
from avahiplatform.helpers.chats.bedrock_chat import BedrockChat


class GrammarCorrection:
    def __init__(self, bedrockchat: BedrockChat):
        """
        Initialize the GrammarCorrection with BedrockChat instance.

        Args:
            bedrockchat (BedrockChat): BedrockChat instance for making API calls.
        """
        self.bedrockchat = bedrockchat

        # Default system prompts for different types of content
        self.default_prompts = {
            "text": "Please correct the grammar and spelling of the following text:",
            "document": "Please correct the grammar and spelling of the following document content:",
            "s3_document": "Please correct the grammar and spelling of the following document content:"
        }

    def _create_prompt_list(self, content_type: str, content: Union[str, bytes], system_prompt: Optional[str] = None) -> list:
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

    def grammar_correction(
        self,
        content_type: str,
        content: Union[str, bytes],
        system_prompt: Optional[str] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Correct grammar and spelling in the provided content using the Bedrock model.

        Args:
            content_type (str): Type of content ('text', 'document').
            content (Union[str, bytes]): The content to correct (can be text or file path).
            system_prompt (Optional[str]): Optional custom system prompt.
            stream (bool): Whether to stream the response.

        Returns:
            Dict[str, Any]: Response containing corrected text and metadata.
        """
        try:
            prompts = self._create_prompt_list(content_type, content, system_prompt)

            if stream:
                response = self.bedrockchat.invoke_stream_parsed(prompts)
            else:
                response = self.bedrockchat.invoke(prompts)

            return response

        except Exception as e:
            raise

    def correct_text(
        self,
        text: str,
        system_prompt: Optional[str] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Correct grammar and spelling in text content.

        Args:
            text (str): The input text to be corrected.
            system_prompt (Optional[str]): Optional custom system prompt.
            stream (bool): Whether to stream the response.

        Returns:
            Dict[str, Any]: Response containing corrected text and metadata.
        """
        return self.grammar_correction("text", text, system_prompt, stream)

    def correct_document(
        self,
        document_path: str,
        system_prompt: Optional[str] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Correct grammar and spelling in a local document file.

        Args:
            document_path (str): Path to the document file.
            system_prompt (Optional[str]): Optional custom system prompt.
            stream (bool): Whether to stream the response.

        Returns:
            Dict[str, Any]: Response containing corrected text and metadata.
        """

        return self.grammar_correction("document", document_path, system_prompt, stream)

    def correct_s3_document(
        self,
        s3_path: str,
        system_prompt: Optional[str] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Correct grammar and spelling in a local document file.

        Args:
            s3_path (str): Path to the document file.
            system_prompt (Optional[str]): Optional custom system prompt.
            stream (bool): Whether to stream the response.

        Returns:
            Dict[str, Any]: Response containing corrected text and metadata.
        """

        return self.grammar_correction("s3_document", s3_path, system_prompt, stream)

    
