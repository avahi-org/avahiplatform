from abc import ABC, abstractmethod
import base64

class BaseEmbeddings(ABC):
    """
    An abstract base class for embeddings-related functionalities. 
    This class provides not only the generation of embeddings from prompts
    but also additional methods such as computing similarities between embeddings.
    
    Subclasses should implement:
        - Methods to prepare and execute the embeddings generation request.
        - Retrieval of model details.
        - The computation of similarity metrics between embeddings.
    """

    @abstractmethod
    def _create_client(self):
        """
        Creates and returns the client for the underlying embeddings service.

        Returns:
            An initialized client object for invoking the embeddings service.
        """
        pass

    @abstractmethod
    def _get_model_details(self):
        """
        Retrieves and returns details about the selected embeddings model.

        Returns:
            dict: A dictionary containing metadata about the model.
        """
        pass

    @property
    @abstractmethod
    def get_model_details(self):
        """
        Returns important details about the embeddings model as a dictionary.

        Returns:
            dict: Dictionary containing model details (e.g., ARN, ID, provider, etc.).
        """
        pass

    @abstractmethod
    def _prepare_request(self, prompt, **kwargs):
        """
        Prepares the request body for the embeddings generation service based on
        provided parameters (e.g., prompt, configuration options, etc.).

        Args:
            prompt (str or list): The main prompt(s) for generating embeddings.
            **kwargs: Additional parameters for the request.

        Returns:
            str: JSON-encoded request body.
        """
        pass

    @abstractmethod
    def _execute_request(self, body):
        """
        Executes the embeddings generation request with the given request body.

        Args:
            body (str): JSON-encoded request body.

        Returns:
            dict: Decoded JSON response containing the generated embeddings and any metadata.
        """
        pass

    @abstractmethod
    def generate_embeddings(self, prompt, **kwargs):
        """
        High-level method that:
            1. Prepares the request body.
            2. Executes the embeddings generation request.
            3. Decodes the response into generated embeddings along with relevant metadata.

        Args:
            prompt (str or list): The prompt(s) for generating embeddings.
            **kwargs: Additional parameters for the request.

        Returns:
            tuple: (embedding, dict)
                - embedding: The generated embeddings (e.g., a list or array of floats).
                - A dictionary with additional details like model metadata and configuration.

        Raises:
            Exception: If the request execution fails or the response does not contain valid embeddings.
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