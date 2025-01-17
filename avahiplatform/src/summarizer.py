from loguru import logger
from typing import Optional, Union, Dict, Any
from avahiplatform.helpers.chats.bedrock_chat import BedrockChat


class BedrockSummarizer:
    def __init__(self, 
                 bedrockchat: BedrockChat):
        """
        Initialize the BedrockSummarizer with BedrockChat instance.
        
        Args:
            bedrockchat: BedrockChat instance for making API calls
        """
        self.bedrockchat = bedrockchat
        
        # Default system prompts for different types of content
        self.default_prompts = {
            "text": "Please provide a comprehensive summary of the following text, highlighting the key points and main ideas:",
            "document": "Please analyze this document and provide a detailed summary, including key points, main arguments, and important conclusions:",
            "s3_document": "Please analyze this document and provide a detailed summary, including key points, main arguments, and important conclusions:",
            "image": "Please describe this image in detail and provide a comprehensive analysis of its content, including any notable elements, themes, or patterns:",
            "video": "Please analyze this video content and provide a detailed summary of its key scenes, main message, and notable elements:"
        }

    def _create_prompt_list(self, content_type: str, content: Union[str, bytes], system_prompt: Optional[str] = None) -> list:
        """
        Creates a list of prompts for the BedrockChat API.
        
        Args:
            content_type: Type of content ('text', 'document', 'image', 'video', 's3_document')
            content: The actual content or path to content
            system_prompt: Optional custom system prompt
            
        Returns:
            list: List of prompts formatted for BedrockChat
        """
        if not system_prompt:
            system_prompt = self.default_prompts.get(content_type, self.default_prompts["text"])
        
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

    def summarize(self, 
                 content_type: str,
                 content: Union[str, bytes],
                 system_prompt: Optional[str] = None,
                 stream: bool = False) -> Dict[str, Any]:
        """
        Summarize content using the Bedrock model.
        
        Args:
            content_type: Type of content ('text', 'document', 'image', 'video', 's3_document')
            content: The content to summarize (can be text, file path, or S3 path)
            system_prompt: Optional custom system prompt
            stream: Whether to stream the response
            
        Returns:
            dict: Response containing summary and metadata
        """
        try:
            prompts = self._create_prompt_list(content_type, content, system_prompt)
            
            if stream:
                return self.bedrockchat.invoke_stream_parsed(prompts)
            else:
                return self.bedrockchat.invoke(prompts)
                
        except Exception as e:
            logger.error(f"Error in summarization: {str(e)}")
            raise

    def summarize_text(self, 
                      text: str, 
                      system_prompt: Optional[str] = None,
                      stream: bool = False) -> Dict[str, Any]:
        """
        Summarize text content.
        """
        return self.summarize("text", text, system_prompt, stream)

    def summarize_document(self, 
                         document_path: str,
                         system_prompt: Optional[str] = None,
                         stream: bool = False) -> Dict[str, Any]:
        """
        Summarize a document file.
        """
        return self.summarize("document", document_path, system_prompt, stream)

    def summarize_image(self, 
                       image_path: str,
                       system_prompt: Optional[str] = None,
                       stream: bool = False) -> Dict[str, Any]:
        """
        Analyze and summarize an image.
        """
        return self.summarize("image", image_path, system_prompt, stream)

    def summarize_video(self, 
                       video_path: str,
                       system_prompt: Optional[str] = None,
                       stream: bool = False) -> Dict[str, Any]:
        """
        Analyze and summarize a video.
        """
        return self.summarize("video", video_path, system_prompt, stream)

    def summarize_s3_document(self, 
                            s3_path: str,
                            system_prompt: Optional[str] = None,
                            stream: bool = False) -> Dict[str, Any]:
        """
        Summarize a document stored in S3.
        """
        return self.summarize("s3_document", s3_path, system_prompt, stream)
