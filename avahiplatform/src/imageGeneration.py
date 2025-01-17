from loguru import logger
from avahiplatform.helpers import BedrockImageGeneration

class ImageGeneration(BedrockImageGeneration):

    def __init__(self, boto_helper, default_model_id):
            """
            Initialize the ImageGeneration class
            
            Args:
                boto_helper: Helper object for AWS interactions
            """
            self.boto_helper = boto_helper
            self.model_id = default_model_id

    def generate_image(self, prompt):
        """
        Generate an image using AWS Bedrock
        
        Args:
            prompt (str): The prompt text for image generation
            
        Returns:
            tuple: (PIL.Image.Image, dict) - The generated image and its details
        """
        # Initialize the BedrockImageGeneration with the specific model
        bedrock_gen = BedrockImageGeneration(
            model_id=self.model_id,
            boto_helper=self.boto_helper
        )
        
        try:
            # Invoke the model to generate the image
            image, details = bedrock_gen.invoke(prompt=prompt)
            print(details)
            return image, details
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            raise