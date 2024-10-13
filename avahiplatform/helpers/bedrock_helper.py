import time
import json
from .utils import Utils
from loguru import logger


class BedrockHelper:
    def __init__(self, bedrock_client):
        self._bedrock_client = bedrock_client

    def model_invoke(self, prompt, model_name=None, max_retries=15, initial_delay=2):
        if model_name is None:
            model_name = "sonnet-3"

        model_id, input_cost, output_cost = self._get_model_details(model_name)

        body = json.dumps({
            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
            "max_tokens": 1000,
            "temperature": 0,
            "anthropic_version": "bedrock-2023-05-31"
        })

        accept = "application/json"
        content_type = "application/json"
        retries = 0

        total_input_tokens = 0.0
        total_output_tokens = 0.0

        while retries < max_retries:
            try:
                logger.info("Invoking model to summarize content.")
                response = self.bedrock.invoke_model(
                    body=body,
                    modelId=model_id,
                    accept=accept,
                    contentType=content_type
                )
                input_token_count = float(
                    response["ResponseMetadata"]["HTTPHeaders"]["x-amzn-bedrock-input-token-count"])
                output_token_count = float(
                    response["ResponseMetadata"]["HTTPHeaders"]["x-amzn-bedrock-output-token-count"])
                total_input_tokens += input_token_count
                total_output_tokens += output_token_count
                input_token_cost = (total_input_tokens / 1000) * input_cost
                output_token_cost = (total_output_tokens / 1000) * output_cost
                total_cost = input_token_cost + output_token_cost

                result = json.loads(response.get('body').read())[
                    'content'][0]['text']
                logger.info(f"Model invocation successful. Total cost: ${
                            total_cost:.6f}")
                return result, input_token_cost, output_token_cost, total_cost

            except self.bedrock.exceptions.ThrottlingException as e:
                retries += 1
                wait_time = initial_delay * \
                    (2 ** (retries - 1))  # Exponential backoff
                logger.warning(f"Service is being throttled. Retrying in {
                               wait_time} seconds...")
                time.sleep(wait_time)
            except Exception as e:
                user_friendly_error = Utils.get_user_friendly_error(e)
                logger.error(user_friendly_error)
                break

        return None, 0, 0, 0.0

    def _get_model_details(self, model_name):
        if model_name.lower() == "sonnet-3.5":
            model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
            input_cost = 0.003
            output_cost = 0.015
        elif model_name.lower() == "sonnet-3":
            model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
            input_cost = 0.003
            output_cost = 0.015
        elif model_name.lower() == "haiku-3.0":
            model_id = "anthropic.claude-3-haiku-20240307-v1:0"
            input_cost = 0.00025
            output_cost = 0.00125
        else:
            logger.error(f"Unrecognized model name: {model_name}")
            raise ValueError(f"Unrecognized model name: {model_name}")

        logger.info(f"Using model: {model_id}")
        return model_id, input_cost, output_cost
