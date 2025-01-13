from typing import Optional, Tuple
from avahiplatform.helpers.chats.bedrock_chat import BedrockChat


class ProductDescriptionGeneration:
    def __init__(self, bedrockchat: BedrockChat):
        """
        Initializes the ProductDescriptionGeneration with a BedrockChat instance.

        Args:
            bedrock_chat (BedrockChat): An instance of BedrockChat for model interactions.
        """
        self.bedrock_chat = bedrockchat

    def generate_product_description(
        self, 
        product_sku: str, 
        event_name: str, 
        customer_segmentation: str, 
        user_prompt: Optional[str] = None,
        stream: bool = False
    ) -> Tuple[str, float, float, float]:
        """
        Generates a product description based on provided parameters.

        Args:
            product_sku (str): The SKU of the product.
            event_name (str): The name of the event.
            customer_segmentation (str): The customer segmentation.
            user_prompt (Optional[str]): Additional prompt provided by the user.
            stream (bool): Whether to use streaming for the response.

        Returns:
            Tuple[str, float, float, float]: A tuple containing the product description, input token cost,
            output token cost, and total cost.
        """
        if not product_sku or not event_name or not customer_segmentation:
            raise ValueError(
                "Incomplete input provided. Please ensure you provide the product SKU, event name, "
                "and customer segmentation to generate the product description."
            )

        prompt = self._construct_prompt(product_sku, event_name, customer_segmentation, user_prompt)

        try:
            if stream:
                response = self.bedrock_chat.invoke_stream_parsed(
                    prompts=[{"text": prompt}]
                )
            else:
                response = self.bedrock_chat.invoke(
                    prompts=[{"text": prompt}],
                )

            return response

        except Exception as e:
            raise

    def _construct_prompt(
        self, 
        product_sku: str, 
        event_name: str, 
        customer_segmentation: str, 
        user_prompt: Optional[str]
    ) -> str:
        """
        Constructs the prompt for product description generation.

        Args:
            product_sku (str): The SKU of the product.
            event_name (str): The name of the event.
            customer_segmentation (str): The customer segmentation.
            user_prompt (Optional[str]): Additional prompt provided by the user.

        Returns:
            str: The constructed prompt.
        """
        base_prompt = (
            f"Generate a product description for the following parameters:\n"
            f"- Product SKU: {product_sku}\n"
            f"- Event: {event_name}\n"
            f"- Customer Segment: {customer_segmentation}\n"
            "The description should be tailored to the specific event and customer segment."
        )

        if user_prompt:
            prompt = f"{base_prompt}\n{user_prompt}"
        else:
            prompt = base_prompt

        return prompt
