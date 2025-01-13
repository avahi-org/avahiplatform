import time
import base64
import anthropic
import os
from .base_chat import BaseChat

class AnthropicChat(BaseChat):
    """
    A class to handle text and image queries using an Anthropic model with support for both
    non-streaming and streaming responses.

    Attributes:
        model_id (str): The ID of the Anthropic model to be used.
        max_tokens (int): The maximum number of tokens to generate.
        temperature (float): The temperature parameter for controlling randomness in generation.
        p (float): The p parameter for nucleus (top-p) sampling.
        anthropic_client (anthropic.Anthropic): The Anthropic client object used for model invocation.
    """

    def __init__(self, 
                 model_id, 
                 max_tokens=512, 
                 temperature=0.6, 
                 p=0.5,
                 api_key=None):
        """
        Initializes the AnthropicChat with the specified model ID and parameters.
        """
        if api_key is None:
            api_key = os.environ.get("ANTHROPIC_API_KEY")

        self.model_id = model_id
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.p = p
        self.api_key = api_key
        self.anthropic_client = self._create_client()

    def _create_client(self):
        """
        Creates the Anthropic client for invoking the language model.

        Returns:
            anthropic.Anthropic: The Anthropic client object.
        """
        return anthropic.Anthropic(api_key=self.api_key)

    def _prepare_request(self, prompts):
        """
        Prepares the request payload for the Anthropic model invocation based on the given prompts.

        Parameters:
            prompts (list): A list of prompt dictionaries.

        Returns:
            list: A list representing the conversation for the Anthropic API.
        """
        messages = []
        for prompt in prompts:
            if "text" in prompt:
                # Text prompt
                message = {
                    "type": "text",
                    "text": prompt["text"]
                }
            elif "image" in prompt:
                image_format = self._get_file_format(prompt["image"])
                if isinstance(prompt["image"], str):
                    encoded_image = self._read_image_base64(prompt["image"])
                elif isinstance(prompt["image"], bytes):
                    encoded_image = base64.b64encode(prompt["image"]).decode('utf-8')
                message = {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": f"image/{image_format}",
                        "data": encoded_image,
                    }
                }
            else:
                raise ValueError(
                    "Invalid prompt. Each prompt must include one of: 'text', 'image', 'document', or 'video'."
                )
            messages.append(message)
        # The Anthropic API expects the conversation in a list with role/content
        conversation = [
            {
                "role": "user", 
                "content": messages
            }
        ]
        return conversation

    def _invoke_model(self, messages):
        """
        Invokes the Anthropic model with the given request in non-streaming mode.
        """
        response = self.anthropic_client.messages.create(
            model=self.model_id,
            max_tokens=self.max_tokens,
            messages=messages,
            temperature=self.temperature,
            top_p=self.p
        )
        return response

    def _invoke_model_streaming(self, messages):
        """
        Invokes the Anthropic model with the given request and returns a streaming response object.
        """
        streaming_response = self.anthropic_client.messages.stream(
            model=self.model_id,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.p,
            messages=messages
        )
        return streaming_response

    def invoke(self, prompts):
        """
        Processes a list of prompts and interacts with the LLM in a non-streaming manner.
        """
        if not isinstance(prompts, list):
            raise ValueError('prompts must be a list')

        # Prepare the request
        messages = self._prepare_request(prompts)

        # Invoke the model and get the response
        start_t = time.perf_counter()
        response = self._invoke_model(messages)
        time_to_last_token = time.perf_counter() - start_t

        # Extracting content and usage according to Anthropic response format
        response_text = response.content[0].text
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens

        return {
            "response_text": response_text,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "time_to_first_token": None,
            "time_to_last_token": time_to_last_token,
            "time_per_output_token": None,
            "model_id": self.model_id,
            "provider": self.get_provider()
        }

    def invoke_stream(self, prompts):
        """
        Processes a list of prompts and returns a generator that yields text tokens as they arrive.
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

        with streaming_response as stream:
            for text in stream.text_stream:
                if flag_ttft:
                    # On receiving the first content, record the time to first token
                    time_to_first_token = time.perf_counter() - start_t
                    flag_ttft = False
                yield {"text": text}
            
            time_to_last_token = time.perf_counter() - start_t
            # After streaming ends, extract token usage
            input_tokens = stream._MessageStream__final_message_snapshot.usage.input_tokens
            output_tokens = stream._MessageStream__final_message_snapshot.usage.output_tokens
            if output_tokens and time_to_last_token and time_to_first_token:
                generation_time = time_to_last_token - time_to_first_token
                time_per_output_token = generation_time / max(output_tokens - 1, 1)

            yield {"metadata": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "time_to_first_token": time_to_first_token,
                "time_to_last_token": time_to_last_token,
                "time_per_output_token": time_per_output_token,
                "model_id": self.model_id,
                "provider": self.get_provider()
            }}

    def invoke_stream_parsed(self, prompts):
        """
        Wraps the invoke_stream method to measure timing and token usage.
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
            str: The name of the provider, e.g., "Anthropic".
        """
        return self.ANTHROPIC_PROVIDER