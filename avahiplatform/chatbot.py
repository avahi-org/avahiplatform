import json
from typing import List, Tuple, Optional
import botocore.exceptions
import boto3
from loguru import logger
from .summarizer import BedrockSummarizer
from .pdfSummarizer import BedrockPdfSummarizer
from .grammarCorrection import BedrockGrammarCorrection




class BedrockChatbot:
    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, region_name=None,
                 max_conversation_turns=10, max_message_length=4000, default_model_name='claude-3-sonnet'):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.bedrock = self._get_bedrock_client()
        self.default_model_name = default_model_name
        self.summarizer = BedrockSummarizer(aws_access_key_id=aws_access_key_id,
                                            aws_secret_access_key=aws_secret_access_key,
                                            region_name=region_name)
        self.pdf_summarizer = BedrockPdfSummarizer(aws_access_key_id=aws_access_key_id,
                                                   aws_secret_access_key=aws_secret_access_key,
                                                   region_name=region_name)
        self.grammar_corrector = BedrockGrammarCorrection(aws_access_key_id=aws_access_key_id,
                                                          aws_secret_access_key=aws_secret_access_key,
                                                          region_name=region_name)
        self.conversation_history: List[dict] = []
        self.max_conversation_turns = max_conversation_turns
        self.max_message_length = max_message_length

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
                "AWS credentials are required. Please provide aws_access_key_id and aws_secret_access_key or configure your environment with AWS credentials.")
        except Exception as e:
            logger.error(f"Error setting up Bedrock client: {str(e)}")
            raise

    def chat(self, user_input: str) -> str:
        # Truncate user input if it exceeds max_message_length
        user_input = user_input[:self.max_message_length]

        # Process user input for special commands
        if user_input.startswith("/"):
            return self._handle_special_command(user_input)

        # Regular conversation
        self.conversation_history.append({"role": "human", "content": user_input})

        model_id, input_cost, output_cost = self._get_model_details(self.default_model_name)

        logger.info(f"Reached 2: {model_id}")

        body = json.dumps({
            "messages": self.conversation_history,
            "max_tokens": 1000,
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

            logger.info(f"Response: {response}")

            result = json.loads(response.get('body').read())
            ai_message = result['content'][0]['text']
            logger.info(f"Response 2: {response}")

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

    def _handle_special_command(self, command: str) -> str:
        if command.startswith("/summarize "):
            return self._handle_summarize(command[11:])
        elif command.startswith("/pdfsummarize "):
            return self._handle_pdfsummarize(command[14:])
        elif command.startswith("/grammar "):
            return self._handle_grammar_correction(command[9:])
        else:
            return "I'm sorry, I don't recognize that command. Can you please try again?"

    def _handle_summarize(self, text: str) -> str:
        summary, _, _, _ = self.summarizer.summarize_text(text)
        return f"Here's a summary of the text you provided: {summary}"

    def _handle_pdfsummarize(self, file_path: str) -> str:
        summary, _, _, _ = self.pdf_summarizer.summarize_pdf_file(file_path)
        return f"I've summarized the PDF for you: {summary}"

    def _handle_grammar_correction(self, text: str) -> str:
        corrected_text, _, _, _ = self.grammar_corrector.grammar_correction_text(text)
        return f"I've corrected the grammar in your text. Here's the result: {corrected_text}"

    def get_conversation_history(self) -> List[dict]:
        return self.conversation_history

    def clear_conversation_history(self) -> None:
        self.conversation_history.clear()

    def _get_user_friendly_error(error):
        # Customize user-friendly error messages here
        if isinstance(error, ValueError):
            return str(error)
        elif isinstance(error, botocore.exceptions.BotoCoreError):
            return "An error occurred with the AWS service. Please check your AWS resources and permissions."
        else:
            return f"An unexpected error occurred: {str(error)}."
