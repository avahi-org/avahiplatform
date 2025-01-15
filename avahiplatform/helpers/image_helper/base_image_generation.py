from abc import ABC, abstractmethod
import base64

class BaseImageGeneration(ABC):
    """
    An abstract base class for image generation. Subclasses should implement
    the methods below to provide functionality for preparing and invoking the 
    generation request, as well as returning an image result.
    """

    @abstractmethod
    def _create_client(self):
        """
        Creates and returns the client for the underlying image generation service.

        Returns:
            A client object for invoking the generation service.
        """
        pass

    @abstractmethod
    def _get_model_details(self):
        """
        Retrieves and returns details about the selected model.

        Returns:
            dict: A dictionary containing model metadata.
        """
        pass

    @property
    @abstractmethod
    def get_model_details(self):
        """
        Returns important details about the model as a dictionary.

        Returns:
            dict: Dictionary containing model details (ARN, ID, provider, etc.).
        """
        pass

    @abstractmethod
    def _prepare_request(self, prompt, **kwargs):
        """
        Prepares the request body for the generation service based on 
        provided parameters (prompt, negative prompt, seed, etc.).

        Args:
            prompt (str or list): The main prompt(s).
            **kwargs: Additional parameters for the request.

        Returns:
            str: JSON-encoded request body.
        """
        pass

    @abstractmethod
    def _invoke(self, body):
        """
        Invokes the generation service with the given request body.

        Args:
            body (str): JSON-encoded request body.

        Returns:
            dict: Decoded JSON response from the service.
        """
        pass

    @abstractmethod
    def invoke(self, prompt, **kwargs):
        """
        High-level method that:
            1. Prepares the request body.
            2. Invokes the generation service.
            3. Decodes the response into an image and relevant metadata.

        Args:
            prompt (str or list): The prompt(s) for image generation.
            **kwargs: Additional parameters for the request.

        Returns:
            tuple: (PIL.Image.Image, dict)
                - The generated image.
                - A dictionary with additional details like model metadata and seed.

        Raises:
            Exception: If invocation fails or no valid image is found in the response.
        """
        pass

    def read_file_as_base64(self, file_path: str) -> str:
        """
        Reads a file from the given path and returns its contents 
        as a Base64-encoded string.

        Args:
            file_path (str): The path to the file to read.

        Returns:
            str: The Base64-encoded content of the file.
        """
        with open(file_path, "rb") as f:
            file_data = f.read()
        return base64.b64encode(file_data).decode("utf-8")

    def is_base64(self, input_str):
        """
        Read input_str to check if is a valid Base64 file

        Args:
            input_str (str): The path or an image as base64.

        Returns:
            bool: Flag to show if input_str is a valid image as base64.
        """
        try:
            # Attempt to decode and check if it's valid Base64
            base64.b64decode(input_str, validate=True)
            return True
        except (ValueError, TypeError):
            return False