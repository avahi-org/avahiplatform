import time
import json
import os
from .base_chat import BaseChat
from avahiplatform.helpers.connectors.s3_helper import S3Helper


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
        input_tokens_price (float): Price per 1,000 input tokens
        output_tokens_price (float): Price per 1,000 output tokens
    """
    def __init__(self, 
                 model_id,
                 boto_helper,
                 max_tokens=512, 
                 temperature=0.6, 
                 p=0.5,
                 input_tokens_price=None,
                 output_tokens_price=None):
        """
        Initializes the BedrockChat with the specified model ID, parameters, and optional custom prices.
        """
        self.model_id = model_id
        self.boto_helper = boto_helper

        self.max_tokens = max_tokens
        self.temperature = temperature
        self.p = p

        # Get model name
        self.model_details = self._get_model_details()
        self.model_name = self.model_details["modelName"]

        # Load default pricing from external JSON file
        self.default_pricing = self._load_default_pricing()

        # Check if user provided custom prices. If not, fall back to default pricing.
        model_pricing = self.default_pricing.get(self.model_name, {})
        self.input_tokens_price = (
            input_tokens_price if input_tokens_price is not None
            else model_pricing.get("input_tokens_price", 0.0)
        )
        self.output_tokens_price = (
            output_tokens_price if output_tokens_price is not None
            else model_pricing.get("output_tokens_price", 0.0)
        )

        # Create Bedrock client
        self.bedrock = self._create_client()
        self.s3_client = self.boto_helper.create_client(service_name="s3")
        self.s3_helper = S3Helper(s3_client=self.s3_client)

    def _create_client(self, *args, **kwargs):
        """
        Creates a Bedrock client using the boto_helper.

        Returns:
            object: A Bedrock client instance.
        """
        return self.boto_helper.create_client(service_name="bedrock-runtime")

    def _load_default_pricing(self):
        """
        Loads the default pricing dictionary from a JSON file.

        Returns:
            dict: Dictionary where keys are model names and values are their default pricing configuration.
        """
        # Adjust the file path as needed
        current_dir = os.path.dirname(__file__)
        pricing_file = os.path.join(current_dir, "models_pricing/default_bedrock_models_pricing.json")

        try:
            with open(pricing_file, "r") as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            # Fallback: return empty dict if file doesn't exist
            return {}
        except json.JSONDecodeError:
            # Fallback: return empty dict if JSON is malformed
            return {}

    def _get_model_details(self):
        """
        Retrieves detailed information about the foundation model using the Bedrock (non-runtime) service.

        Returns:
            dict: The model details retrieved from the Bedrock service.
        """
        # Create a separate client for the Bedrock control plane (non-runtime) API
        bedrock_control_client = self.boto_helper.create_client(service_name="bedrock")
        try:
            if self.model_id.startswith("us."):
                model_id = self.model_id.split("us.")[1]
            else:
                model_id = self.model_id
            response = bedrock_control_client.get_foundation_model(
                modelIdentifier=model_id
            )
            return response["modelDetails"]
        except Exception as e:
            raise

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
            elif "s3_document" in prompt:
                # Document prompt
                doc_name = "document"
                if isinstance(prompt["s3_document"], str):
                    doc_bytes = self.s3_helper.read_s3_file(prompt["s3_document"])
                message = {
                    "document": {
                        "format": "txt",
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
                    "Invalid prompt. Each prompt must include one of: 'text', 'image', 's3_document', 'document', or 'video'."
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
        
        # Extract the text from the response
        response_text = response["output"]["message"]["content"][0]["text"]
        
        # Extract token usage
        model_usage = response.get("usage", {})
        inputTokens = model_usage.get("inputTokens")
        outputTokens = model_usage.get("outputTokens")
        
        # Compute costs
        # Note: Because prices are per 1,000 tokens, we divide by 1,000
        input_token_cost = (self.input_tokens_price * inputTokens) / 1000 if inputTokens else 0
        output_token_cost = (self.output_tokens_price * outputTokens) / 1000 if outputTokens else 0
        total_cost = input_token_cost + output_token_cost

        # Determine which model was actually used
        if "trace" in response:
            model_id = response["trace"]["promptRouter"]["invokedModelId"]
        else:
            model_id = self.model_id

        return {
            "response_text": response_text, 
            "inputTokens": inputTokens,
            "outputTokens": outputTokens, 
            "time_to_first_token": None,  # Not measured here
            "time_to_last_token": time_to_last_token,
            "time_per_output_token": None,
            "input_token_cost": input_token_cost,
            "output_token_cost": output_token_cost,
            "total_cost": total_cost,
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
            # Content blocks contain the actual text
            if "contentBlockDelta" in chunk:
                if flag_ttft:
                    # On receiving the first content, record the time to first token
                    time_to_first_token = time.perf_counter() - start_t
                    flag_ttft = False
                delta_text = chunk["contentBlockDelta"]["delta"].get("text", "")
                yield {"text": delta_text}

            # contentBlockStop indicates the LLM finished sending tokens
            if "contentBlockStop" in chunk:
                time_to_last_token = time.perf_counter() - start_t
            
             # The metadata block arrives at the end of the conversation
            if "metadata" in chunk:
                metadata = chunk["metadata"]

                # After streaming ends, extract token usage
                usage = metadata.get("usage", {})
                input_tokens = usage.get("inputTokens")
                output_tokens = usage.get("outputTokens")
                
                # Compute time per output token
                if output_tokens and time_to_last_token and time_to_first_token:
                    generation_time = time_to_last_token - time_to_first_token
                    time_per_output_token = generation_time / max(output_tokens - 1, 1)

                # Compute costs
                input_token_cost = (self.input_tokens_price * input_tokens) / 1000 if input_tokens else 0
                output_token_cost = (self.output_tokens_price * output_tokens) / 1000 if output_tokens else 0
                total_cost = input_token_cost + output_token_cost
                
                # Determine model ID
                if "trace" in metadata:
                    model_id = metadata["trace"]["promptRouter"]["invokedModelId"]
                    model_id = f"prompt-router:{model_id.split('/')[-1]}"
                else:
                    model_id = self.model_id

                # Return the metadata chunk (including cost info)
                yield {
                    "metadata": {
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "time_to_first_token": time_to_first_token,
                        "time_to_last_token": time_to_last_token,
                        "time_per_output_token": time_per_output_token,
                        "input_token_cost": input_token_cost,
                        "output_token_cost": output_token_cost,
                        "total_cost": total_cost,
                        "model_id": model_id,
                        "provider": self.get_provider(),
                    }
                }

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
        return f"{self.BEDROCK_PROVIDER}:{self.bedrock.meta.region_name}:{self.model_details['providerName']}"

    def get_model_pricing(self):
        """
        Retrieve the pricing details of the model once an instance is created.

        Returns:
            dict: A dictionary containing pricing information for the model.
        """
        return {
            "model_id": self.model_id,
            "model_name": self.model_name,
            "provider": self.get_provider(),
            "input_tokens_price": self.input_tokens_price,
            "output_tokens_price": self.output_tokens_price
        }