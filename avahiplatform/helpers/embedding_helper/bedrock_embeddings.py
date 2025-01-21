"""
Module: bedrock_embeddings
---------------------------
This module provides the 'BedrockEmbeddings' class which is a concrete implementation
of 'BaseEmbeddings' for interacting with an embeddings service such as AWS Bedrock.

Supported Models:
-----------------
1. amazon.titan-embed-text-v1
   - Required arguments: 
     - text (str): The input text to generate an embedding.
     
2. amazon.titan-embed-text-v2:0
   - Required arguments:
     - text (str): The input text to generate an embedding.
   - Optional arguments:**
     - dimensions (int, default=1024): The dimensionality of the embedding vector.
     - normalize (bool, default=True): Whether to normalize the output embedding.
     - embeddingTypes (list, default=["float"]): The desired types for the embedding values.
     
3. amazon.titan-embed-image-v1
   - Required arguments:
     - Either one or both of the following:
       - text (str): Optional input text to help guide the image embedding.
       - image (str or file path): The image input. If a file path is provided and it is not already Base64 encoded,
         it will be converted to a Base64 string.
   - Optional arguments:
     - dimensions (int, default=1024): The expected length of the output embedding vector.
     
4. cohere.embed-english-v3 and cohere.embed-multilingual-v3
   - Required arguments: 
     - text (str or list of str): The input text(s) to generate the embedding.
   - Optional arguments:**
     - embedding_types (list or str, default=["float"]): The desired types for the embedding values.
     - input_type (str, default="search_query"): Specifies the type of input.
     - truncate (str, default="NONE"): Indicates whether and how to truncate input text.

Usage Example:
--------------
# Initialize an embedding instance for a text model
embedder = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1", boto_helper=boto_helper)
result = embedder.generate_embeddings(text="Your input text goes here.")
print(result["embeddings"])
"""
from .base_embeddings import BaseEmbeddings
import json

class BedrockEmbeddings(BaseEmbeddings):
    """
    An implementation of BaseEmbeddings that leverages AWS Bedrock to generate embeddings.
    This class provides functionalities to:
        - Initialize a Bedrock client using a provided boto_helper.
        - Fetch model metadata from the Bedrock control plane API.
        - Prepare JSON requests for different embedding models.
        - Execute the model invocation to generate embeddings.
        - Return embeddings along with metadata such as token count and latency.
    """

    def __init__(self, model_id, boto_helper):
        """
        Initializes the BedrockEmbeddings client with a specific model and AWS helper.

        Args:
            model_id (str): The identifier of the model to be invoked, e.g.,
                            'amazon.titan-embed-text-v1' or 'cohere.embed-english-v3'.
            boto_helper (object): Helper object for AWS service interactions.
        """
        self.model_id = model_id
        self.boto_helper = boto_helper

        # Create a Bedrock runtime client for invoking the model
        self.bedrock = self._create_client()

        # Retrieve and store model metadata from the Bedrock control plane
        self.model_details = self._get_model_details()

    def _create_client(self, *args, **kwargs):
        """
        Creates an AWS Bedrock runtime client using boto_helper.

        Returns:
            object: A Bedrock runtime client instance used for model invocation.
        """
        return self.boto_helper.create_client(service_name="bedrock-runtime")

    def _get_model_details(self):
        """
        Retrieves metadata about the requested foundation model from AWS Bedrock.

        Uses the control plane API (non-runtime) client to get details such as the model ARN,
        model name, provider, input/output modalities, and region.

        Returns:
            dict: A dictionary containing model metadata including:
                  - modelArn
                  - modelId
                  - modelName
                  - providerName
                  - inputModalities
                  - outputModalities
                  - region_name (added from client metadata)
        
        Raises:
            Exception: Propagates any exceptions that occur during the API call.
        """
        # Create a client for the Bedrock control plane (non-runtime API)
        bedrock_control_client = self.boto_helper.create_client(service_name="bedrock")
        try:
            response = bedrock_control_client.get_foundation_model(
                modelIdentifier=self.model_id
            )
            # Include the region in the model details for additional context
            response["modelDetails"].update({
                "region_name": bedrock_control_client.meta.region_name
            })
            return response["modelDetails"]
        except Exception as e:
            raise e

    @property
    def get_model_details(self):
        """
        Retrieves important details about the model in a simplified dictionary format.

        Returns:
            dict: A dictionary containing:
                  - model_arn: The ARN of the model.
                  - model_id: The model identifier.
                  - model_name: The human-readable name of the model.
                  - privider: A composite string indicating the provider, region, and provider name.
                  - input_modalities: The supported input modalities.
                  - output_modalities: The supported output modalities.
        """
        return {
            "model_arn": self.model_details["modelArn"],
            "model_id": self.model_details["modelId"],
            "model_name": self.model_details["modelName"],
            "privider": f"Bedrock:{self.model_details['region_name']}:{self.model_details['providerName']}",
            "input_modalities": self.model_details["inputModalities"],
            "output_modalities": self.model_details["outputModalities"]
        }

    def _prepare_request(self, **kwargs):
        """
        Prepares and returns a JSON-encoded request body for generating embeddings based on the model.

        Supported models and their expected parameters:
            - amazon.titan-embed-text-v1:
                  Expects a parameter "text" for generating text embeddings.
            - amazon.titan-embed-text-v2:0:
                  Supports "text", "dimensions", "normalize", and "embeddingTypes".
            - amazon.titan-embed-image-v1:
                  Expects an "embeddingConfig" with "dimensions", and optionally "inputText" and/or "inputImage".
                  If an image is provided, it is converted to base64 if not already.
            - cohere.embed-english-v3, cohere.embed-multilingual-v3:
                  Expects "text" (or a list of texts), "input_type", "truncate", and "embedding_types".

        Args:
            **kwargs: Keyword arguments containing input data and configuration parameters.

        Returns:
            str: A JSON string representing the request body to be sent to the model.

        Raises:
            ValueError: If the model_id is unsupported.
        """
        if self.model_id == "amazon.titan-embed-text-v1":
            request_body = {
                "inputText": kwargs.get("text"),
            }
        elif self.model_id == "amazon.titan-embed-text-v2:0":
            request_body = {
                "inputText": kwargs.get("text"),
                "dimensions": kwargs.get("dimensions", 1024),
                "normalize": kwargs.get("normalize", True),
                "embeddingTypes": kwargs.get("embeddingTypes", ["float"]),
            }
        elif self.model_id == "amazon.titan-embed-image-v1":
            request_body = {
                "embeddingConfig": {
                    "outputEmbeddingLength": kwargs.get("dimensions", 1024)
                }
            }
            if "text" in kwargs:
                request_body["inputText"] = kwargs.get("text")
            if "image" in kwargs:
                image = kwargs.get("image")
                if not self.is_base64(image):
                    image = self.read_file_as_base64(image)
                request_body["inputImage"] = image
        elif self.model_id in ["cohere.embed-english-v3", "cohere.embed-multilingual-v3"]:
            texts = kwargs.get("text")
            if not isinstance(texts, list):
                texts = [texts]
            embedding_types = kwargs.get("embedding_types", ["float"])
            if not isinstance(embedding_types, list):
                embedding_types = [embedding_types]
            request_body = {
                "texts": texts,
                "input_type": kwargs.get("input_type", "search_query"),
                "truncate": kwargs.get("truncate", "NONE"),
                "embedding_types": embedding_types
            }
        else:
            raise ValueError(f"Unsupported model ID: {self.model_id}")

        return json.dumps(request_body)

    def _execute_request(self, body):
        """
        Invokes the Bedrock model using the provided request body.

        Args:
            body (str): A JSON string representing the prepared request body.

        Returns:
            object: The response from the Bedrock service which includes metadata and the response body.

        Raises:
            Exception: Propagates any exceptions encountered during model invocation.
        """
        try:
            response = self.bedrock.invoke_model(
                body=body,
                modelId=self.model_id,
                accept="application/json",
                contentType="application/json"
            )
            return response
        except Exception as e:
            raise e

    def generate_embeddings(self, **kwargs):
        """
        Generates embeddings for the given input(s) using the specified model.

        Prepares the request, invokes the model, and then parses the response to extract embeddings
        along with metadata such as the number of input tokens and invocation latency.

        Args:
            **kwargs: Keyword arguments expected by the underlying model. For example, a "text" key
                      for text-based models or "image" for image-based embeddings.

        Returns:
            dict: A dictionary containing:
                  - embeddings: The generated embeddings.
                  - inputTokens: The number of input tokens counted by Bedrock.
                  - latency: The model invocation latency as reported by Bedrock.
                  - model_id: The identifier of the model used.
                  - provider: A string that identifies the provider and region.
        """
        # Prepare the request body as a JSON string
        request_body = self._prepare_request(**kwargs)

        # Execute the request using the Bedrock runtime client
        response = self._execute_request(request_body)

        # Extract header metadata such as token count and latency
        inputTokens = response.get("ResponseMetadata").get("HTTPHeaders").get("x-amzn-bedrock-input-token-count", 0)
        latency = response.get("ResponseMetadata").get("HTTPHeaders").get("x-amzn-bedrock-invocation-latency", 0)

        # Parse the response body containing the embeddings
        results = json.loads(response.get('body').read())
        if self.model_id in ["amazon.titan-embed-text-v1", "amazon.titan-embed-text-v2:0", "amazon.titan-embed-image-v1"]:
            embeddings = results.get("embedding")
        elif self.model_id in ["cohere.embed-english-v3", "cohere.embed-multilingual-v3"]:
            embeddings = results.get("embeddings")
        else:
            embeddings = None

        # Return the embeddings along with metadata information
        return {
            "embeddings": embeddings,
            "inputTokens": inputTokens,
            "latency": latency,
            "model_id": self.model_id,
            "provider": f"Bedrock:{self.model_details['region_name']}:{self.model_details['providerName']}"
        }