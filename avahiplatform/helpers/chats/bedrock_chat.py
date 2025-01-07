import time
import boto3
from .base_chat import BaseChat 

class BedrockChat(BaseChat):
    """
    A class to handle text and image queries using an LLM with support for streaming responses.

    Attributes:
        model_id (str): The ID of the LLM model to be used for responses.
        max_tokens (int): The maximum number of tokens to generate.
        temperature (float): The temperature parameter for controlling randomness in generation.
        p (float): The p parameter for nucleus (top-p) sampling.
        aws_access_key_id (str): AWS access key ID.
        aws_secret_access_key (str): AWS secret access key.
        aws_session_token (str): AWS session token.
        region_name (str): AWS region name.
    """

    def __init__(self, 
                 model_id, 
                 max_tokens=512, 
                 temperature=0.6, 
                 p=0.5,
                 region_name=None,
                 aws_access_key_id=None,
                 aws_secret_access_key=None,
                 aws_session_token=None):
        """
        Initializes the BedrockChat with the specified model ID and parameters.
        """
        self.model_id = model_id
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.p = p
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_session_token = aws_session_token
        self.bedrock = self._create_client()

    def _create_client(self):
        """
        Creates the Bedrock client for invoking the language model.

        Returns:
            boto3.client: A boto3 client for Bedrock runtime service.
        """
        bedrock_client = boto3.client(
            service_name="bedrock-runtime",
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_session_token=self.aws_session_token
        )
        return bedrock_client

    def _prepare_request(self, prompts):
        """
        Prepares the request payload for the model invocation based on the given prompts.
        
        Supports keys: "text", "image", "document", "video"

        Parameters:
            prompts (list): A list of prompt dictionaries. Each prompt should be a dict with either:
                            - "text": str
                            - "image": str (path to the image file)
                            - "documet": str (path to the document file)
                            - "video": str (path to the video file)

        Returns:
            list: A list representing the conversation for the LLM, formatted as required by the Bedrock API.

        Raises:
            ValueError: If a prompt does not contain a "text", "image", "document" or "video" key.
        """
        messages = []
        for prompt in prompts:
            if "text" in prompt:
                # Text prompt
                message = {
                    "text": prompt["text"]
                }
            elif "image" in prompt:
                # Image prompt
                image_format = self._get_file_format(prompt["image"])
                if isinstance(prompt["image"], str):   
                    encoded_image = self._read_file(prompt["image"])
                elif isinstance(prompt["image"], bytes):
                    encoded_image = prompt["image"]
                message = {
                    "image": {
                        "format": image_format,
                        "source": {
                            "bytes": encoded_image
                        }
                    }
                }
            elif "document" in prompt:
                # Document prompt
                doc_name = "document"
                doc_format = self._get_file_format(prompt["document"])
                if isinstance(prompt["document"], str):
                    doc_bytes = self._read_file(prompt["document"])
                elif isinstance(prompt["document"], bytes):
                    doc_bytes = prompt["document"]
                message = {
                    "document": {
                        "format": doc_format,
                        "name": doc_name,
                        "source": {
                            "bytes": doc_bytes
                        }
                    }
                }
            elif "video" in prompt:
                # Video prompt
                video_format = self._get_file_format(prompt["video"])
                if isinstance(prompt["video"], str):
                    video_bytes = self._read_file(prompt["video"])
                elif isinstance(prompt["video"], bytes):
                    video_bytes = prompt["video"]
                message = {
                    "video": {
                        "format": video_format,
                        "source": {
                            "bytes": video_bytes
                        }
                    }
                }
            else:
                raise ValueError(
                    "Invalid prompt. Each prompt must include one of: 'text', 'image', 'document', or 'video'."
                )
            messages.append(message)
        # The Bedrock API expects the conversation in a list with role/content
        conversation = [
            {
                "role": "user", 
                "content": messages
            }
        ]
        return conversation

    def _invoke_model(self, messages):
        """
        Invokes the LLM model with the given request and returns the response.

        Parameters:
            messages (List): A List representing the conversation for the LLM.

        Returns:
            dict: The response from the LLM model.
        """
        try:
            response = self.bedrock.converse(
                modelId=self.model_id,
                messages=messages,
                inferenceConfig={
                    "maxTokens": self.max_tokens,
                    "temperature": self.temperature,
                    "topP": self.p
                },
            )
            return response
        except Exception as e:
            raise

    def _invoke_model_streaming(self, messages):
        """
        Invokes the LLM model with the given request and returns a streaming_response generator.

        Parameters:
            messages (List): A List representing the conversation for the LLM.

        Returns:
            dict: A dictionary containing a "stream" key that yields streaming chunks.
        """
        try:
            streaming_response = self.bedrock.converse_stream(
                modelId=self.model_id,
                messages=messages,
                inferenceConfig={
                    "maxTokens": self.max_tokens,
                    "temperature": self.temperature,
                    "topP": self.p
                },
            )
            return streaming_response
        except Exception as e:
            raise

    def invoke(self, prompts):
        """
        Processes a list of prompts and returns the LLM response.

        Parameters:
            prompts (list): A list of prompt dictionaries. Each prompt should be a dict with either:
                            - "text": str
                            - "image": str (path to the image file)
                            - "documet": str (path to the document file)
                            - "video": str (path to the video file)

        Returns:
            dict: A structured response containing the LLM's output and metrics.
        """
        if not isinstance(prompts, list):
            raise ValueError('prompts must be a list')

        # Prepare the request
        messages = self._prepare_request(prompts)

        # Invoke the model and get the response
        start_t = time.perf_counter()
        response = self._invoke_model(messages)
        time_to_last_token = time.perf_counter() - start_t

        response_text = response["output"]["message"]["content"][0]["text"]
        model_usage = response.get("usage", {})
        inputTokens = model_usage.get("inputTokens")
        outputTokens = model_usage.get("outputTokens")

        if "trace" in response:
            model_id = response["trace"]["promptRouter"]["invokedModelId"]
        else:
            model_id = self.model_id

        return {
            "response_text": response_text, 
            "inputTokens": inputTokens,
            "outputTokens": outputTokens, 
            "time_to_first_token": None,
            "time_to_last_token": time_to_last_token,
            "time_per_output_token": None,
            "model_id": model_id,
            "provider": self.get_provider()
        }

    def invoke_stream(self, prompts):
        """
        Processes a list of prompts and returns a streaming LLM response.

        Parameters:
            prompts (list): A list of prompt dictionaries.

        Returns:
            generator: Yields chunks of the response text or metadata as received from the LLM.
        """
        if not isinstance(prompts, list):
            raise ValueError('prompts must be a list')

        # Prepare the request
        messages = self._prepare_request(prompts)
        # Record the start time for measuring streaming performance
        start_t = time.perf_counter()
        # Invoke the model and get the response
        streaming_response = self._invoke_model_streaming(messages)
        # Initialize a flag to capture the time to first token (TTFT)
        flag_ttft = True
        time_to_first_token = None
        time_to_last_token = None
        time_per_output_token = None

        for chunk in streaming_response["stream"]:
            if "contentBlockDelta" in chunk:
                if flag_ttft:
                    # On receiving the first content, record the time to first token
                    time_to_first_token = time.perf_counter() - start_t
                    flag_ttft = False
                delta_text = chunk["contentBlockDelta"]["delta"].get("text", "")
                yield {"text": delta_text}

            if "contentBlockStop" in chunk:
                time_to_last_token = time.perf_counter() - start_t

            if "metadata" in chunk:
                metadata = chunk["metadata"]

                # After streaming ends, extract token usage
                usage = metadata.get("usage", {})
                input_tokens = usage.get("inputTokens")
                output_tokens = usage.get("outputTokens")
                if output_tokens and time_to_last_token and time_to_first_token:
                    generation_time = time_to_last_token - time_to_first_token
                    time_per_output_token = generation_time / max(output_tokens - 1, 1)

                if "trace" in metadata:
                    model_id = metadata["trace"]["promptRouter"]["invokedModelId"]
                    model_id = f"prompt-router:{model_id.split('/')[-1]}"
                else:
                    model_id = self.model_id

                yield {"metadata": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "time_to_first_token": time_to_first_token,
                    "time_to_last_token": time_to_last_token,
                    "time_per_output_token": time_per_output_token,
                    "model_id": model_id,
                    "provider": self.get_provider()
                }}

    def invoke_stream_parsed(self, prompts):
        """
        Wraps the invoke_stream method to measure timing and token usage.

        Parameters:
            prompts (list): A list of prompt dictionaries.

        Returns:
            dict: A dictionary with response text, timing, and token usage.
        """
        if not isinstance(prompts, list):
            raise ValueError('prompts must be a list')
            
        response_stream = self.invoke_stream(prompts)
        
        response_text = ""
        metadata = {}
        for chunk in response_stream:
            if "text" in chunk:
                response_text += chunk.get("text", "")
            elif "metadata" in chunk:
                metadata = chunk["metadata"]

        return {"response_text": response_text, **metadata}

    def get_provider(self):
        """
        Returns the provider type.

        Returns:
            str: The name of the provider, e.g., "Bedrock".
        """
        return f"{self.BEDROCK_PROVIDER}:{self.bedrock.meta.region_name}"