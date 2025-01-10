import json
from typing import List, Optional, Dict, Any, Union
from loguru import logger
from .helpers.chats.bedrock_chat import BedrockChat
from .helpers.connectors.boto_helper import BotoHelper
import sqlalchemy
from sqlalchemy import create_engine, text


class BedrockServices:
    """
    A unified class that provides various Bedrock-based services including:
    - Chatbot
    - Data Masking
    - Grammar Correction
    - Natural Language to SQL
    - Product Description Generation
    - CSV Query
    - Structured Data Extraction
    """

    def __init__(self, 
                 bedrockchat: BedrockChat):
        """
        Initialize BedrockServices with BedrockChat instance.
        
        Args:
            bedrockchat: BedrockChat instance for making API calls
        """
        self.bedrockchat = bedrockchat
        
        # Default system prompts for different services
        self.default_prompts = {
            "chat": "You are a helpful AI assistant. Please provide informative, accurate, and engaging responses.",
            "data_masking": "You are a data masking specialist. Your task is to identify and mask sensitive information while preserving the data's utility.",
            "grammar": "You are a grammar correction specialist. Your task is to correct grammar, spelling, and improve text clarity while maintaining the original meaning.",
            "nl2sql": "You are a SQL expert. Your task is to convert natural language queries into accurate SQL statements and explain the results.",
            "product_description": "You are a product description specialist. Your task is to create compelling and accurate product descriptions.",
            "csv_query": "You are a data analysis expert. Your task is to analyze CSV data and provide insights based on user queries.",
            "structured_extraction": "You are a data extraction specialist. Your task is to extract structured information from unstructured text."
        }

    def _create_prompt_list(self, service_type: str, content: Union[str, Dict], 
                          system_prompt: Optional[str] = None, 
                          additional_context: Optional[Dict] = None) -> list:
        """
        Creates a list of prompts for the BedrockChat API.
        """
        if not system_prompt:
            system_prompt = self.default_prompts.get(service_type)
        
        prompts = [{"text": system_prompt}]
        
        if additional_context:
            prompts.append({"text": json.dumps(additional_context)})
            
        if isinstance(content, str):
            prompts.append({"text": content})
        elif isinstance(content, dict):
            prompts.append(content)
            
        return prompts

    def chat(self, 
             user_input: str,
             conversation_history: Optional[List[Dict]] = None,
             system_prompt: Optional[str] = None,
             stream: bool = False) -> Dict[str, Any]:
        """
        Chat with the AI model.
        """
        context = {"conversation_history": conversation_history} if conversation_history else None
        prompts = self._create_prompt_list("chat", user_input, system_prompt, context)
        
        if stream:
            return self.bedrockchat.invoke_stream_parsed(prompts)
        return self.bedrockchat.invoke(prompts)

    def mask_data(self,
                 content: str,
                 sensitive_fields: Optional[List[str]] = None,
                 system_prompt: Optional[str] = None,
                 stream: bool = False) -> Dict[str, Any]:
        """
        Mask sensitive data in the content.
        """
        context = {"sensitive_fields": sensitive_fields} if sensitive_fields else None
        prompts = self._create_prompt_list("data_masking", content, system_prompt, context)
        
        if stream:
            return self.bedrockchat.invoke_stream_parsed(prompts)
        return self.bedrockchat.invoke(prompts)

    def correct_grammar(self,
                       text: str,
                       style_guide: Optional[str] = None,
                       system_prompt: Optional[str] = None,
                       stream: bool = False) -> Dict[str, Any]:
        """
        Correct grammar and improve text.
        """
        context = {"style_guide": style_guide} if style_guide else None
        prompts = self._create_prompt_list("grammar", text, system_prompt, context)
        
        if stream:
            return self.bedrockchat.invoke_stream_parsed(prompts)
        return self.bedrockchat.invoke(prompts)

    def natural_to_sql(self,
                      nl_query: str,
                      db_schema: str,
                      db_type: str = "SQL",
                      system_prompt: Optional[str] = None,
                      stream: bool = False) -> Dict[str, Any]:
        """
        Convert natural language to SQL query.
        """
        context = {
            "db_schema": db_schema,
            "db_type": db_type
        }
        prompts = self._create_prompt_list("nl2sql", nl_query, system_prompt, context)
        
        if stream:
            return self.bedrockchat.invoke_stream_parsed(prompts)
        return self.bedrockchat.invoke(prompts)

    def generate_product_description(self,
                                   product_info: Dict[str, Any],
                                   target_audience: Optional[str] = None,
                                   system_prompt: Optional[str] = None,
                                   stream: bool = False) -> Dict[str, Any]:
        """
        Generate product description.
        """
        context = {"target_audience": target_audience} if target_audience else None
        prompts = self._create_prompt_list("product_description", product_info, system_prompt, context)
        
        if stream:
            return self.bedrockchat.invoke_stream_parsed(prompts)
        return self.bedrockchat.invoke(prompts)

    def query_csv(self,
                 query: str,
                 csv_content: str,
                 system_prompt: Optional[str] = None,
                 stream: bool = False) -> Dict[str, Any]:
        """
        Query CSV data.
        """
        context = {"csv_content": csv_content}
        prompts = self._create_prompt_list("csv_query", query, system_prompt, context)
        
        if stream:
            return self.bedrockchat.invoke_stream_parsed(prompts)
        return self.bedrockchat.invoke(prompts)

    def extract_structured_data(self,
                              content: str,
                              extraction_schema: Optional[Dict] = None,
                              system_prompt: Optional[str] = None,
                              stream: bool = False) -> Dict[str, Any]:
        """
        Extract structured data from unstructured text.
        """
        context = {"extraction_schema": extraction_schema} if extraction_schema else None
        prompts = self._create_prompt_list("structured_extraction", content, system_prompt, context)
        
        if stream:
            return self.bedrockchat.invoke_stream_parsed(prompts)
        return self.bedrockchat.invoke(prompts)
