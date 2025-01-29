import json
from loguru import logger
from avahiplatform.helpers.connectors.boto_helper import BotoHelper


class TokenValidation:
    """
    Provides a high-level interface to validate user tokens by invoking the 
    token validation Lambda function.

    Attributes:
        lambda_name (str): Name of the Lambda function to invoke for token validation.
        boto_helper (BotoHelper): Helper object for AWS interactions.
    """

    def __init__(self, lambda_name: str, boto_helper: BotoHelper):
        """
        Initializes the TokenValidation with the specified Lambda function name.

        Args:
            lambda_name (str): Name of the Lambda function for token validation.
            boto_helper (BotoHelper): Helper object for AWS interactions.
        """
        self.lambda_name = "AvahiSDK_TokenValidation"
        self.boto_helper = boto_helper

        # Create the Lambda client
        self.lambda_client = self._create_client()

    def _create_client(self):
        """
        Creates a Lambda client using the boto_helper.

        Returns:
            BaseClient: A Lambda client instance.

        Raises:
            Exception: If the client creation fails.
        """
        try:
            logger.info(f"Creating Lambda client for function: {self.lambda_name}")
            return self.boto_helper.create_client(service_name="lambda")
        except Exception as e:
            logger.error(f"Failed to create Lambda client: {str(e)}")
            raise

    def validate_token(self, token: str) -> dict:
        """
        Validates the given token by invoking the token validation Lambda function.

        Args:
            token (str): The token to be validated.

        Returns:
            dict: A dictionary containing the validation status and any additional information.

        Raises:
            Exception: If the Lambda invocation or validation fails.
        """
        try:
            # Prepare the payload for Lambda invocation
            payload = json.dumps({"token": token})
            logger.info(f"Invoking Lambda function '{self.lambda_name}' with payload: {payload}")

            # Invoke the Lambda function
            response = self.lambda_client.invoke(
                FunctionName=self.lambda_name,
                InvocationType="RequestResponse",
                Payload=payload
            )

            # Parse the response
            response_payload = json.loads(response['Payload'].read().decode('utf-8'))
            logger.debug(f"Lambda response: {response_payload}")

            # Check for validation status
            if response_payload.get('statusCode') == 200:
                body = json.loads(response_payload['body'])
                logger.info("Token validation successful.")
                return {
                    "status": "valid",
                    "message": body.get("message", "Token is valid."),
                    "credentials": body.get("aws_credentials", {}),
                    "details": body.get("details", {})
                }
            else:
                logger.warning("Token validation failed.")
                return {
                    "status": "invalid",
                    "message": response_payload.get("body", "Token validation failed.")
                }
        except Exception as e:
            logger.error(f"Error validating token: {str(e)}")
            raise Exception(f"Error validating token: {str(e)}")


