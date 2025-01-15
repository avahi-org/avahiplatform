"""
Bedrock Image Generation Module
-------------------------------

This module provides a convenient interface for using AWS Bedrock's foundation models 
for image generation. Currently, it supports the following model IDs and their 
respective parameters:

1. stability.stable-image-core-v1:0 
   - Parameters:
        - prompt (str): The main prompt text.
        - aspect_ratio (str): Aspect ratio in the form "width:height" (default "1:1").
        - mode (str): "text-to-image" or "image-to-image" (default "text-to-image").
        - output_format (str): The desired output format (default "png").
        - seed (int): Seed for reproducible generation (default 0).
        - negative_prompt (str): Negative prompt text (default "").

2. stability.stable-image-ultra-v1:0
   - Same parameters as `stability.stable-image-core-v1:0`.

3. stability.stable-diffusion-xl-v1
   - Parameters:
        - prompt (str or list): Primary prompt(s). If a list, `weight` should be a list.
        - weight (float or list): Weight(s) for the prompt(s).
        - cfg_scale (int): Classifier-free guidance scale (default 7).
        - clip_guidance_preset (str): Clip guidance preset, e.g., "FAST_BLUE" (default "FAST_BLUE").
        - sampler (str): Sampling method, e.g., "DDIM" (default "DDIM").
        - samples (int): Number of images to generate per request (default 1).
        - seed (int): Seed for reproducible generation (default 0).
        - steps (int): Number of steps for diffusion (default 30).
        - style_preset (str): Style preset, e.g., "photographic" (default "photographic").

      - Additional parameters for image-to-image (non-masking):
        - init_image (str, Base64 encoded): The initial image for conditioning.
        - init_image_mode (str): Mode for the init image, e.g., "IMAGE_STRENGTH" (default "IMAGE_STRENGTH").
        - image_strength (float): Strength of the init image (default 0.35).

      - Additional parameters for image-to-image with masking:
        - init_image (str, Base64 encoded): The initial image for conditioning (required).
        - mask_image (str, Base64 encoded): The mask image (required).
        - mask_source (str): The mask source, e.g., "ALPHA" (required).

4. stability.sd3-large-v1:0
   - Parameters:
        - prompt (str): The main prompt text.
        - aspect_ratio (str): Aspect ratio in the form "width:height" (default "1:1").
        - output_format (str): The desired output format (default "png").
        - seed (int): Seed for reproducible generation (default 0).
        - negative_prompt (str): Negative prompt text (default "").
        - mode (str): "text-to-image" or "image-to-image" (default "text-to-image").
          - If mode is "image-to-image":
             - image (str, Base64 encoded): The initial image for conditioning.
             - strength (float): Strength of the init image (default 0.75).
"""

import boto3
import json
import base64
import io
from PIL import Image
from .base_image_generation import BaseImageGeneration


class BedrockImageGeneration(BaseImageGeneration):
    """
    Provides a high-level interface to invoke image generation using AWS Bedrock 
    diffusion models.

    Attributes:
        model_id (str): Identifier of the model to use for generation.
        boto_helper (object): Helper object for AWS interactions.
    """

    def __init__(
        self,
        model_id,
        boto_helper
    ):
        """
        Initializes the BedrockImageGeneration with the specified model ID and parameters.

        Args:
            model_id (str): Identifier of the model to be invoked, e.g., 
                            'stability.stable-diffusion-xl-v1'.
            boto_helper (object): Helper object for AWS interactions.
        """
        self.model_id = model_id
        self.boto_helper = boto_helper

        # Create the Bedrock client
        self.bedrock = self._create_client()

        # Retrieve and store model details
        self.model_details = self._get_model_details()

    def _create_client(self, *args, **kwargs):
        """
        Creates a Bedrock client using the boto_helper.

        Returns:
            object: A Bedrock client instance.
        """
        return self.boto_helper.create_client(service_name="bedrock-runtime")

    def _get_model_details(self):
        """
        Retrieves details about the foundation model from the Bedrock service.

        Returns:
            dict: A dictionary containing model metadata (ARN, ID, name, provider, etc.).

        Raises:
            Exception: If the retrieval of model details fails.
        """
        # Create a separate client for the Bedrock control plane (non-runtime) API
        bedrock_control_client = self.boto_helper.create_client(service_name="bedrock")
        try:
            response = bedrock_control_client.get_foundation_model(
                modelIdentifier=self.model_id
            )
            response["modelDetails"].update({
                "region_name": bedrock_control_client.meta.region_name
            })
            return response["modelDetails"]
        except Exception as e:
            raise

    @property
    def get_model_details(self):
        """
        Returns important details about the model as a dictionary.

        Returns:
            dict: Dictionary containing:
                  - model_arn
                  - model_id
                  - model_name
                  - privider
                  - input_modalities
                  - output_modalities
        """
        return {
            "model_arn": self.model_details["modelArn"],
            "model_id": self.model_details["modelId"],
            "model_name": self.model_details["modelName"],
            "privider": f"Bedrock:{self.model_details['region_name']}:{self.model_details['providerName']}",
            "input_modalities": self.model_details['inputModalities'],
            "output_modalities": self.model_details['outputModalities']
        }

    def _prepare_request(self, prompt, **kwargs):
        """
        Prepares the request body for different model types based on the provided parameters.

        Args:
            prompt (str or list): The main prompt text(s).
            **kwargs: Additional parameters specific to the model type.

        Returns:
            str: JSON-encoded request body.

        Raises:
            ValueError: If unsupported model ID is provided or if required parameters 
                        for masking are not supplied.
            Exception: For invalid argument combinations in stable-diffusion-xl prompt or weights.
        """
        # Stable Image Core and Stable Image Ultra (same parameter structure)
        if self.model_id in ['stability.stable-image-core-v1:0', 
                             'stability.stable-image-ultra-v1:0']:
            request_body = {
                "prompt": prompt,
                "aspect_ratio": kwargs.get("aspect_ratio", "1:1"),
                "mode": kwargs.get("mode", "text-to-image"),
                "output_format": kwargs.get("output_format", "png"),
                "seed": kwargs.get("seed", 0),
                "negative_prompt": kwargs.get("negative_prompt", "")
            }

        # Stable Diffusion XL
        elif self.model_id == 'stability.stable-diffusion-xl-v1':
            weight = kwargs.get("weight", 1.0)

            # Handle text prompts (single prompt vs multiple prompts)
            if isinstance(prompt, str) and isinstance(weight, float):
                text_prompts = [{"text": prompt, "weight": weight}]
            elif isinstance(prompt, list) and isinstance(weight, list):
                text_prompts = []
                for p, w in zip(prompt, weight):
                    text_prompts.append({"text": p, "weight": w})
            else:
                raise Exception(
                    "Invalid argument combination: 'prompt' must be a string or a list of "
                    "strings, and 'weight' must match that type (float or list of floats)."
                )

            # Common parameters for SDXL
            cfg_scale = kwargs.get("cfg_scale", 7)
            clip_guidance_preset = kwargs.get("clip_guidance_preset", "FAST_BLUE")
            sampler = kwargs.get("sampler", "DDIM")
            samples = kwargs.get("samples", 1)
            seed = kwargs.get("seed", 0)
            steps = kwargs.get("steps", 30)
            style_preset = kwargs.get("style_preset", "photographic")

            request_body = {
                "text_prompts": text_prompts,
                "cfg_scale": cfg_scale,
                "clip_guidance_preset": clip_guidance_preset,
                "sampler": sampler,
                "samples": samples,
                "seed": seed,
                "steps": steps,
                "style_preset": style_preset,
            }

            # Image-to-image with masking
            if "mask_source" in kwargs and "mask_image" in kwargs:
                if "init_image" not in kwargs:
                    raise ValueError(
                        "For image-to-image masking, 'init_image' is required."
                    )
                init_image = kwargs.get("init_image")
                if not self.is_base64(init_image):
                    init_image = self.read_file_as_base64(init_image)
                request_body["init_image"] = init_image
                request_body["mask_source"] = kwargs.get("mask_source"),
                request_body["mask_image"] = kwargs.get("mask_image")

            # Image-to-image without masking
            elif "init_image" in kwargs:
                init_image = kwargs.get("init_image")
                if not self.is_base64(init_image):
                    init_image = self.read_file_as_base64(init_image)
                request_body.update({
                    "init_image": init_image,
                    # Optional parameters for standard image-to-image
                    "init_image_mode": kwargs.get("init_image_mode", "IMAGE_STRENGTH"),
                    "image_strength": kwargs.get("image_strength", 0.35),
                })

            # Text-to-image
            else:
                request_body.update({
                    "height": kwargs.get("height", 512),
                    "width": kwargs.get("width", 512),
                })

        # Stable Diffusion 3 Large
        elif self.model_id == 'stability.sd3-large-v1:0':
            mode = kwargs.get("mode", "text-to-image")
            request_body = {
                "prompt": prompt,
                "output_format": kwargs.get("output_format", "png"),
                "seed": kwargs.get("seed", 0),
                "negative_prompt": kwargs.get("negative_prompt", "")
            }

            # If image-to-image
            if mode == "image-to-image":
                image = kwargs.get("image")
                if not self.is_base64(image):
                    image = self.read_file_as_base64(image)
                request_body.update({
                    "image": image,
                    "strength": kwargs.get("strength", 0.75),
                    "mode": mode
                })
            else:
                request_body.update({
                    "aspect_ratio": kwargs.get("aspect_ratio", "1:1"),
                    "mode": mode
                })

        else:
            raise ValueError(f"Unsupported model ID: {self.model_id}")

        return json.dumps(request_body)

    def _invoke(self, body):
        """
        Invokes the Bedrock model with the given request body.

        Args:
            body (str): JSON-encoded request body.

        Returns:
            dict: Decoded JSON response from the model invocation.

        Raises:
            Exception: If any error occurs while reading the response.
        """
        response = self.bedrock.invoke_model(
            modelId=self.model_id,
            body=body,
            accept="application/json",
            contentType="application/json"
        )

        return response

    def invoke(self, prompt, **kwargs):
        """
        Invokes the model using the provided prompt and additional parameters, 
        and returns both the generated image and a details dictionary.

        The details dictionary includes the model metadata (ARN, ID, name, provider, 
        input/output modalities), the seed used for generation, and, if available, 
        the invocation latency from the Bedrock service.

        Args:
            prompt (str or list): The primary prompt(s) for image generation. 
                Refer to the module-level docstring for details on supported models 
                and parameter structures.
            **kwargs: Additional parameters specific to the selected model, such as 
                'aspect_ratio', 'negative_prompt', 'init_image', etc.

        Returns:
            tuple:
                - PIL.Image.Image: The generated image object.
                - dict: A dictionary containing additional details, including:
                    - Model metadata (ARN, ID, name, provider)
                    - Seed used for generation
                    - Invocation latency (if available)

        Raises:
            Exception: If the invocation fails or no valid image is found in the response.

        Example:
            >>> bedrock_gen = BedrockImageGeneration("stability.stable-image-core-v1:0")
            >>> image, details = bedrock_gen.invoke(prompt="A surreal landscape with floating islands")
            >>> image.show()  # Display the generated image
            >>> print(details) # Print metadata and seed
        """
        # Step 1: Prepare the request body based on the model and given parameters.
        body = self._prepare_request(prompt, **kwargs)

        # Step 2: Invoke the model using the prepared request body.
        response = self._invoke(body)

        # Step 3: Decode the response from JSON format.
        body_response = json.loads(response["body"].read().decode("utf-8"))

        # Step 4: Check for the presence of base64-encoded images under known keys.
        if "images" in body_response:
            # Some models return a list of images and seeds
            base64_image = body_response["images"][0]
            seed = body_response["seeds"][0]
        elif "artifacts" in body_response and len(body_response["artifacts"]) > 0:
            # Other models may return artifacts with 'base64' and 'seed'
            base64_image = body_response["artifacts"][0].get("base64")
            seed = body_response["artifacts"][0].get("seed")
        else:
            # If no recognized image data is present, raise an exception
            raise Exception(
                f"Model invocation failed: {body_response.get('finish_reasons', 'Unknown error')}"
            )

        # Step 5: Ensure the base64 image data is valid.
        if not base64_image:
            raise Exception("No base64-encoded image found in the response.")

        # Step 6: Convert the base64 string into an image object.
        image_data = base64.b64decode(base64_image)
        image = Image.open(io.BytesIO(image_data))

        # Step 7: Collect additional details, including model metadata and seed.
        details = self.get_model_details
        details["seed"] = seed

        # Attempt to retrieve invocation latency from the response metadata.
        metadata = response["ResponseMetadata"]["HTTPHeaders"]
        if 'x-amzn-bedrock-invocation-latency' in metadata:
            details["Latency"] = metadata["x-amzn-bedrock-invocation-latency"]

        # Step 8: Return both the generated image and the details dictionary.
        return image, details