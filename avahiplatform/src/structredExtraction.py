from loguru import logger
from typing import Optional, Union, Dict, Any
from avahiplatform.helpers.chats.bedrock_chat import BedrockChat


class BedrockStructuredExtraction:
    def __init__(self, 
                 bedrockchat: BedrockChat):
        """
        Initialize the BedrockStructuredExtraction with BedrockChat instance.
        
        Args:
            bedrockchat: BedrockChat instance for making API calls
        """
        self.bedrockchat = bedrockchat
        
        # Default system prompt for document entity extraction
        self.default_prompts = """Extract the following entities from the provided document in a structured JSON format:
                                1. Name:
                                2. Places:

                                Response should be JSON in the following format:

                                {
                                "Name": ["Name1", "Name2"],
                                "Places": ["Place1", "Place2"]
                                }

                                Ensure the output contains only the JSON structure without any additional text."""

    def _create_prompt_list(self, content_type: str, content: Union[str, bytes], system_prompt: Optional[str] = None) -> list:
        """
        Creates a list of prompts for the BedrockChat API.
        
        Args:
            content_type: Type of content ('document', 's3_document')
            content: The actual content or path to content
            system_prompt: Optional custom system prompt
            
        Returns:
            list: List of prompts formatted for BedrockChat
        """

        if not system_prompt:
            system_prompt = self.default_prompts

        if content_type == "text":
            prompts = [
                {"text": f"System prompt: {system_prompt} \n User: {content}"}
            ]
        else:
            prompts = [
                {"text": system_prompt},
                {content_type: content}
            ]
        return prompts

    def extract(self, 
               content_type: str,
               content: Union[str, bytes],
               system_prompt: Optional[str] = None,
               stream: bool = False) -> Dict[str, Any]:
        """
        Extract entities from content using the Bedrock model.
        
        Args:
            content_type: Type of content ('document', 's3_document')
            content: The content to extract entities from (can be text, file path, or S3 path)
            system_prompt: Optional custom system prompt
            stream: Whether to stream the response
            
        Returns:
            dict: Response containing extracted entities and metadata
        """
        try:
            prompts = self._create_prompt_list(content_type, content, system_prompt)
            
            if stream:
                return self.bedrockchat.invoke_stream_parsed(prompts)
            else:
                return self.bedrockchat.invoke(prompts)
                
        except Exception as e:
            logger.error(f"Error in entity extraction: {str(e)}")
            raise

    def extract_text(self, 
                      text: str, 
                      system_prompt: Optional[str] = None,
                      stream: bool = False) -> Dict[str, Any]:
        """
        Extract entities from text content.
        """
        return self.extract("text", text, system_prompt, stream)

    def extract_document(self, 
                         document_path: str,
                         system_prompt: Optional[str] = None,
                         stream: bool = False) -> Dict[str, Any]:
        """
        Extract entities from a local document file.
        
        Args:
            document_path: Path to the document file
            system_prompt: Optional custom system prompt
            stream: Whether to stream the response
            
        Returns:
            dict: Response containing extracted entities and metadata
        """
        return self.extract("document", document_path, system_prompt, stream)

    def extract_s3_document(self, 
                            s3_path: str,
                            system_prompt: Optional[str] = None,
                            stream: bool = False) -> Dict[str, Any]:
        """
        Extract entities from a document stored in S3.
        
        Args:
            s3_path: S3 path to the document file
            system_prompt: Optional custom system prompt
            stream: Whether to stream the response
            
        Returns:
            dict: Response containing extracted entities and metadata
        """
        return self.extract("s3_document", s3_path, system_prompt, stream)
