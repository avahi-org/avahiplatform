import magic
import base64
from abc import ABC, abstractmethod

class BaseChat(ABC):
    """
    An abstract base class defining the interface for LLM-based chat classes.
    Subclasses must implement the following abstract methods:
    - _create_client(...)
    - _prepare_request(prompts)
    - _invoke_model(messages)
    - _invoke_model_streaming(messages)
    - invoke(prompts)
    - invoke_stream(prompts)
    - invoke_stream_parsed(prompts)
    - get_provider()

    This class also provides standard helper methods for reading image files.
    """

    ANTHROPIC_PROVIDER = "Anthropic"
    BEDROCK_PROVIDER = "Bedrock"

    @abstractmethod
    def _create_client(self, *args, **kwargs):
        """
        Abstract method to create a client (e.g., a model or service client).

        Subclasses must implement this to set up their specific LLM or API clients.
        """
        pass

    @abstractmethod
    def _prepare_request(self, prompts):
        """
        Prepares the request payload for model invocation based on the given prompts.

        Parameters:
            prompts (list): A list of prompt dictionaries.

        Returns:
            object: A prepared request structure suitable for the specific model API.
        """
        pass

    @abstractmethod
    def _invoke_model(self, messages):
        """
        Invokes the LLM model with the given request (non-streaming).

        Parameters:
            messages (object): The prepared request messages for the LLM.

        Returns:
            dict: The response from the LLM model.
        """
        pass

    @abstractmethod
    def _invoke_model_streaming(self, messages):
        """
        Invokes the LLM model with the given request in streaming mode.

        Parameters:
            messages (object): The prepared request messages for the LLM.

        Returns:
            generator or iterable: A streaming response that yields chunks of the model's output.
        """
        pass

    @abstractmethod
    def invoke(self, prompts):
        """
        Processes a list of prompts and returns a single LLM response in a non-streaming manner.

        Parameters:
            prompts (list): A list of prompt dictionaries.

        Returns:
            dict: A structured response containing the LLM's output and metrics.
        """
        pass

    @abstractmethod
    def invoke_stream(self, prompts):
        """
        Processes a list of prompts and returns a streaming response, yielding tokens or chunks as they arrive.

        Parameters:
            prompts (list): A list of prompt dictionaries.

        Yields:
            dict: Chunks of text or metadata as they become available.
        """
        pass

    @abstractmethod
    def invoke_stream_parsed(self, prompts):
        """
        Wraps the invoke_stream method to accumulate the full response and final metadata.

        Parameters:
            prompts (list): A list of prompt dictionaries.

        Returns:
            dict: A dictionary with the full response text and metadata.
        """
        pass

    @abstractmethod
    def get_provider(self):
        """
        Returns the provider type (e.g., 'Anthropic', 'Bedrock', etc.).

        Returns:
            str: The name of the provider.
        """
        pass

    def _read_image_base64(self, image_path):
        """
        Reads an image file and returns its base64-encoded string.

        Parameters:
            image_path (str): The path to the image file.

        Returns:
            str: Base64-encoded image data.
        """
        try:
            with open(image_path, 'rb') as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_image
        except Exception:
            raise

    def _read_file(self, file_path):
        """
        Reads file bytes given a file path.

        Parameters:
            file_path (str): The path to the file to read.

        Returns:
            bytes: The file content in bytes.
        """
        try:
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            return file_bytes
        except Exception:
            raise

    def _get_file_format(self, file):
        """
        Return format of file.

        Parameters:
            file (str or bytes): Path of a file or file as bytes.

        Returns:
            str: The file format.
        """
        try:
            if isinstance(file, str):
                file_format = magic.from_file(file, mime=True)
                file_format = file_format.split("/")[-1]
                file_format = "txt" if "plain" == file_format else file_format
                return file_format
            elif isinstance(file, bytes):
                file_format = magic.from_buffer(file, mime=True)
                file_format = file_format.split("/")[-1]
                file_format = "txt" if "plain" == file_format else file_format
                return file_format
            else:
                print("Invalid file format")
                raise
        except Exception:
            raise