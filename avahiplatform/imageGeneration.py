import boto3
import time
import json
import random
import base64
from loguru import logger
from io import BytesIO
from PIL import Image
import botocore.exceptions

class BedrockImageGeneration:
    
    def __init__(self, default_model_name='amazon.titan.v1', aws_access_key_id=None,
                 aws_secret_access_key=None, region_name=None):
        self.region_name = region_name
        self.default_model_name = default_model_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.bedrock = self._get_bedrock_client()
        
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
            raise ValueError("AWS credentials are required. Please provide aws_access_key_id and aws_secret_access_key or configure your environment with AWS credentials.")
        except Exception as e:
            logger.error(f"Error setting up Bedrock client: {str(e)}")
            raise
            
    def model_invoke(self, prompt, seed=None, model_name=None, max_retries=15, initial_delay=2):
        
        if model_name is None:
            model_name = self.default_model_name
        
        if seed is None:
            seed = random.randint(0, 2**31 - 1)

        model_id, output_cost = self._get_model_details(model_name)
        
        if model_name == 'amazon.titan.v1' or model_name == 'amazon.titan.v2':
            native_request = {
                "taskType": "TEXT_IMAGE",  # Task type indicating text-to-image generation
                "textToImageParams": {
                    "text": prompt,  # Text prompt for image generation
                },
                "imageGenerationConfig": {
                    "quality": "premium",  # Image quality setting
                    "height": 1024,  # Image height in pixels
                    "width": 1024,  # Image width in pixels
                    "seed": seed,  # Seed for reproducibility
                },
            }
        elif model_name == 'sdxl':
            # Create a request payload for Stability AI's SDXL model
            native_request = {
                "text_prompts": [{"text": prompt, "weight": 1.0}],  # Text prompt with weight
                "seed": seed,  # Seed for reproducibility
                "height": 1024,  # Image height in pixels
                "width": 1024,  # Image width in pixels
            }
            
        body = json.dumps(native_request)
        
        accept = "application/json"
        content_type = "application/json"
        retries = 0
        
        while retries < max_retries:
            try:
                logger.info("Invoking model to generate images.")
                response = self.bedrock.invoke_model(
                    body=body,
                    modelId=model_id,
                    accept=accept,
                    contentType=content_type
                )
                
                total_cost = output_cost
                
                result = self._transform_response_to_pillow(response, model_name)
                logger.info(f"Model invocation successful. Total cost: ${total_cost:.6f}")
                return result, seed, total_cost

            except self.bedrock.exceptions.ThrottlingException as e:
                retries += 1
                wait_time = initial_delay * (2 ** (retries - 1))  # Exponential backoff
                logger.warning(f"Service is being throttled. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            except Exception as e:
                user_friendly_error = self._get_user_friendly_error(e)
                logger.error(user_friendly_error)
                break

        return None, None, 0.0
        
    def _get_model_details(self, model_name):
        if model_name.lower() == "amazon.titan.v1":
            model_id = "amazon.titan-image-generator-v1"
            output_cost = 0.012
        elif model_name.lower() == "amazon.titan.v2":
            model_id = "amazon.titan-image-generator-v2:0"
            output_cost = 0.012
        elif model_name.lower() == "sdxl":
            model_id = "stability.stable-diffusion-xl-v1"
            output_cost = 0.04
        else:
            logger.error(f"Unrecognized model name: {model_name}")
            raise ValueError(f"Unrecognized model name: {model_name}")

        logger.info(f"Using model: {model_id}")
        return model_id, output_cost
    
    def generate_image(self, prompt, seed=None, model_name=None):
        
        if not prompt:
            logger.error("Input prompt cannot be empty.")
            raise ValueError("Input prompt cannot be empty.") 
        
        return self.model_invoke(prompt=prompt, seed=seed, model_name=model_name)
    
    def _transform_response_to_pillow(self, response, model_name):
        
        model_response = json.loads(response.get('body').read())
        
        if model_name == 'amazon.titan.v1' or model_name == 'amazon.titan.v2':
            base64_image = model_response["images"][0]
        elif model_name == 'sdxl':
            base64_image = model_response["artifacts"][0]["base64"]
            
        image_decoded = base64.b64decode(base64_image)
        image_decoded = BytesIO(image_decoded)
        image = Image.open(image_decoded).convert("RGB")
        
        return image   
    
    def _get_user_friendly_error(self, error):
        # Customize user-friendly error messages here
        if isinstance(error, ValueError):
            return str(error)
        elif isinstance(error, botocore.exceptions.BotoCoreError):
            return "An error occurred with the AWS service. Please check your AWS resources and permissions."
        else:
            return f"An unexpected error occurred: {str(error)}."