import json
from typing import List, Optional
import botocore.exceptions
import boto3
from loguru import logger


class BedrockChatbot:
    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, region_name=None, max_conversation_turns=10,
                 max_message_length=4000, default_model_name='sonnet-3'):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.bedrock = self._get_bedrock_client()
        self.default_model_name = default_model_name
        self.conversation_history: List[dict] = []
        self.max_conversation_turns = max_conversation_turns
        self.max_message_length = max_message_length
        self.system_prompt: Optional[str] = None

    def _get_bedrock_client(self):
        try:
            if self.aws_access_key_id and self.aws_secret_access_key:
                logger.info("Using provided AWS credentials for authentication.")
                session = boto3.Session(
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key,
                    region_name=self.region_name
                )
                return session.client(service_name="bedrock-runtime")
            else:
                logger.info("No explicit credentials provided. Attempting to use default credentials.")
                return boto3.client(service_name="bedrock-runtime", region_name=self.region_name)
        except botocore.exceptions.NoCredentialsError:
            logger.error("No AWS credentials found. Please provide credentials or configure your environment.")
            raise ValueError(
                "AWS credentials are required. Please provide aws_access_key_id and aws_secret_access_key or configure your environment with AWS credentials."
            )
        except Exception as e:
            logger.error(f"Error setting up Bedrock client: {str(e)}")
            raise

    def chat(self, user_input: str, system_prompt: str, model_name: Optional[str] = None) -> str:
        # Truncate user input if it exceeds max_message_length
        user_input = user_input[:self.max_message_length]

        # Set system prompt if it has not been set yet
        if self.system_prompt is None:
            self.system_prompt = system_prompt[:self.max_message_length]
            self.conversation_history.append({"role": "system", "content": self.system_prompt})

        # Prepare the prompt for model invocation
        main_prompt = f"System: {self.system_prompt}\nUser: {user_input}"

        self.conversation_history.append({"role": "user", "content": user_input})

        if model_name is None:
            model_name = self.default_model_name

        model_id, input_cost, output_cost = self._get_model_details(model_name)
        logger.info(f"model_id: {model_id}")

        body = json.dumps({
            "messages": [{"role": "user", "content": main_prompt}],  # Model input should have only the combined prompt
            "max_tokens": 4000,
            "temperature": 0.7,
            "anthropic_version": "bedrock-2023-05-31"
        })
        logger.info(f"Body: {body}")

        try:
            logger.info(f"INVOKING MODEL")
            response = self.bedrock.invoke_model(
                body=body,
                modelId=model_id,
                accept="application/json",
                contentType="application/json"
            )

            result = json.loads(response.get('body').read())
            ai_message = result['content'][0]['text']
            self.conversation_history.append({"role": "assistant", "content": ai_message})

            # Trim conversation history if it exceeds max_conversation_turns
            if len(self.conversation_history) > self.max_conversation_turns * 2:
                self.conversation_history = self.conversation_history[-self.max_conversation_turns * 2:]

            return ai_message
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return "I'm sorry, but I encountered an error while processing your request. Could you please try again?"

    def _get_model_details(self, model_name):
        if model_name.lower() == "sonnet-3.5":
            model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
            input_cost = 0.003
            output_cost = 0.015
        elif model_name.lower() == "sonnet-3":
            model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
            input_cost = 0.003
            output_cost = 0.015
        elif model_name.lower() == "haiku-3.0":
            model_id = "anthropic.claude-3-haiku-20240307-v1:0"
            input_cost = 0.00025
            output_cost = 0.00125
        else:
            logger.error(f"Unrecognized model name: {model_name}")
            raise ValueError(f"Unrecognized model name: {model_name}")

        logger.info(f"Using model: {model_id}")
        return model_id, input_cost, output_cost

    def get_conversation_history(self) -> str:
        beautified_history = "\n".join(f"{turn['role'].upper()}: {turn['content']}" for turn in self.conversation_history)
        return beautified_history

    def clear_conversation_history(self) -> None:
        self.conversation_history.clear()
        self.system_prompt = None

    def _get_user_friendly_error(self, error):
        # Customize user-friendly error messages here
        if isinstance(error, ValueError):
            return str(error)
        elif isinstance(error, botocore.exceptions.BotoCoreError):
            return "An error occurred with the AWS service. Please check your AWS resources and permissions."
        else:
            return f"An unexpected error occurred: {str(error)}."