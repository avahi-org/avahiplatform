import boto3
import time
import json
import base64
from loguru import logger
from io import BytesIO
from PIL import Image
import botocore.exceptions
import os
import numpy as np


class BedrockImageSimilarity:

    def __init__(self, default_model_name="amazon.titan.v1", aws_access_key_id=None,
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
            raise ValueError(
                "AWS credentials are required. Please provide aws_access_key_id and aws_secret_access_key or configure your environment with AWS credentials.")
        except Exception as e:
            logger.error(f"Error setting up Bedrock client: {str(e)}")
            raise

    def _get_model_details(self, model_name):
        if model_name.lower() == "amazon.titan.v1":
            model_id = "amazon.titan-embed-image-v1"
            output_cost = 0.00006
        else:
            logger.error(f"Unrecognized model name: {model_name}")
            raise ValueError(f"Unrecognized model name: {model_name}")

        # logger.info(f"Using model: {model_id}")
        return model_id, output_cost

    def _get_user_friendly_error(self, error):
        # Customize user-friendly error messages here
        if isinstance(error, ValueError):
            return str(error)
        elif isinstance(error, botocore.exceptions.BotoCoreError):
            return "An error occurred with the AWS service. Please check your AWS resources and permissions."
        else:
            return f"An unexpected error occurred: {str(error)}."

    def _parse_s3_path(self, s3_file_path):
        if not s3_file_path.startswith('s3://'):
            logger.error("S3 path should start with 's3://'. Please check the S3 file path.")
            raise ValueError("S3 path should start with 's3://'. Please check the S3 file path.")
        parts = s3_file_path[5:].split('/', 1)
        if len(parts) != 2:
            logger.error("Invalid S3 path format. It should be 's3://bucket_name/key_name'.")
            raise ValueError("Invalid S3 path format. It should be 's3://bucket_name/key_name'.")
        return parts[0], parts[1]

    def _get_s3_object(self, bucket_name, key_name):

        s3 = boto3.client('s3')

        try:
            response = s3.get_object(Bucket=bucket_name, Key=key_name)
            content_type = response['ContentType']
            image_data = response['Body'].read()

            if "image" not in content_type:
                logger.error("Invalid S3 object. The ContentType of the object should be an image.")
                raise ValueError("Invalid S3 object. The ContentType of the object should be an image.")

        except s3.exceptions.NoSuchKey:
            logger.error(f"The file {key_name} does not exist in the S3 bucket. Please check the S3 file path.")
            raise ValueError(f"The file {key_name} does not exist in the S3 bucket. Please check the S3 file path.")
        except s3.exceptions.NoSuchBucket:
            logger.error(f"The S3 bucket does not exist. Please check the bucket name in the S3 file path.")
            raise ValueError(f"The S3 bucket does not exist. Please check the bucket name in the S3 file path.")
        except Exception as e:
            user_friendly_error = self._get_user_friendly_error(e)
            logger.error(user_friendly_error)
            raise ValueError(user_friendly_error)

        return image_data

    def _get_s3_folder_objects(self, bucket_name, folder_name):

        s3 = boto3.client('s3')
        try:
            # List all objects in the bucket
            all_objects = s3.list_objects(Bucket=bucket_name)['Contents']
        except s3.exceptions.NoSuchBucket:
            raise ValueError(f"The S3 bucket does not exist. Please check the bucket name in the S3 file path.")
        except Exception as e:
            user_friendly_error = self._get_user_friendly_error(e)
            logger.error(user_friendly_error)
            raise ValueError(user_friendly_error)

        folder_objects = {}
        # Filter and fetch objects in the folder
        for _object in all_objects:
            key_name = _object['Key']
            if (folder_name + "/") in key_name:
                response = s3.get_object(Bucket=bucket_name, Key=key_name)
                content_type = response['ContentType']
                if "image" in content_type:
                    folder_objects[key_name] = response['Body'].read()

        # Check if the folder is empty
        if not folder_objects:
            raise ValueError(f"The folder '{folder_name}' is empty or does not exist in the bucket '{bucket_name}'.")

        return folder_objects

    def _get_top_k_values(self, keys, similarities, k):

        similarities_by_path = {key: float(value) for key, value in zip(keys, similarities)}
        similarities_by_path = sorted(similarities_by_path.items(), key=lambda x: x[1], reverse=True)
        return dict(similarities_by_path[:k])

    def model_invoke(self, input_image, output_embedding_length=256, model_name=None, max_retries=15, initial_delay=2):

        if model_name is None:
            model_name = self.default_model_name

        model_id, output_cost = self._get_model_details(model_name)

        # Create request body.
        body = json.dumps({
            "inputImage": input_image,
            "embeddingConfig": {
                "outputEmbeddingLength": output_embedding_length
            }
        })

        accept = "application/json"
        content_type = "application/json"
        retries = 0

        while retries < max_retries:
            try:
                # logger.info("Invoking model to generate the image embedding.")
                response = self.bedrock.invoke_model(
                    body=body,
                    modelId=model_id,
                    accept=accept,
                    contentType=content_type
                )

                response_body = json.loads(response.get('body').read())

                embedding = response_body.get("embedding")

                total_cost = output_cost

                # logger.info(f"Model invocation successful. Total cost: ${total_cost:.6f}")
                return embedding, total_cost

            except self.bedrock.exceptions.ThrottlingException as e:
                retries += 1
                wait_time = initial_delay * (2 ** (retries - 1))  # Exponential backoff
                logger.warning(f"Service is being throttled. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            except Exception as e:
                user_friendly_error = self._get_user_friendly_error(e)
                logger.error(user_friendly_error)
                break

        return None, 0.0

    def _image_preprocessing(self, input_image):

        if isinstance(input_image, bytes):
            image_data = input_image
        elif isinstance(input_image, Image.Image):
            buffered = BytesIO()
            input_image.save(buffered, format="PNG")
            image_data = buffered.getvalue()
        elif os.path.isfile(input_image):
            with open(input_image, 'rb') as img_file:
                image_data = img_file.read()
        elif input_image.startswith('s3://'):  # Check if input is an S3 file path
            bucket_name, key_name = self._parse_s3_path(input_image)
            image_data = self._get_s3_object(bucket_name, key_name)
        else:
            raise ValueError("Unsupported image format: must be a bytes string, a file path or a PIL Image object.")

        encoded_image = base64.b64encode(image_data).decode('utf-8')

        return encoded_image

    def cosine_similarity(self, vector, matrix_or_vector):

        if matrix_or_vector.ndim == 1:
            # Compute cosine similarity between two vectors
            dot_product = np.dot(vector, matrix_or_vector)
            magnitude_vector = np.linalg.norm(vector)
            magnitude_matrix_or_vector = np.linalg.norm(matrix_or_vector)

            # Prevent division by zero
            if magnitude_vector == 0 or magnitude_matrix_or_vector == 0:
                return 0.0

            return float(dot_product / (magnitude_vector * magnitude_matrix_or_vector))

        elif matrix_or_vector.ndim == 2:
            # Compute cosine similarity between the vector and each row of the matrix
            dot_products = np.dot(matrix_or_vector, vector)
            magnitude_vector = np.linalg.norm(vector)
            magnitudes_matrix = np.linalg.norm(matrix_or_vector, axis=1)

            # Prevent division by zero in the magnitudes
            with np.errstate(divide='ignore', invalid='ignore'):
                cosine_similarities = np.divide(dot_products, magnitudes_matrix * magnitude_vector)
                cosine_similarities[magnitudes_matrix == 0] = 0

            return cosine_similarities
        else:
            raise ValueError("Input must be either a 1D vector or a 2D matrix.")

    def image_to_image_similarity(self, image, other_image, output_embedding_length=256, model_name=None):
        """
        Calculate the similarity between two images using cosine similarity.

        Args:
            image: The first image to compare (file path or a PIL Image object).
            other_image: The second image to compare (file path or a PIL Image object).
            output_embedding_length: The length of the output embeddings (default 256).
            model_name: The name of the model to use for generating embeddings (optional).

        Returns:
            A tuple containing the cosine similarity between the images and the total cost.
        """
        try:
            # Preprocess the input image
            image = self._image_preprocessing(image)

            # Generate embedding for the first image
            image_embedding, total_cost = self.model_invoke(
                input_image=image,
                output_embedding_length=output_embedding_length,
                model_name=model_name
            )
            image_embedding = np.array(image_embedding)

            # Preprocess the other image
            other_image = self._image_preprocessing(other_image)

            # Generate embedding for the other image
            other_image_embedding, additional_cost = self.model_invoke(
                input_image=other_image,
                output_embedding_length=output_embedding_length,
                model_name=model_name
            )
            other_image_embedding = np.array(other_image_embedding)

            # Add the cost from processing the second image
            total_cost += additional_cost

            # Calculate cosine similarity between the two embeddings
            similarity = self.cosine_similarity(image_embedding, other_image_embedding)

            logger.info(f"Pipeline invocation successful. Total cost: ${total_cost:.6f}")

            return similarity, total_cost

        except Exception as e:
            user_friendly_error = self._get_user_friendly_error(e)
            logger.error(user_friendly_error)
            return None, 0

    def image_to_folder_similarity(self, image, folder_path, k=10, output_embedding_length=256, model_name=None):
        """
        Calculate the similarity between an image and all images in a folder using cosine similarity.

        Args:
            image: The first image to compare (file path or a PIL Image object).
            folder_path: Path to the folder containing the images to compare with.
            k: Top k results to return with the greatest similarity (default 10).
            output_embedding_length: The length of the output embeddings (default 256).
            model_name: The name of the model to use for generating embeddings (optional).

        Returns:
            A tuple containing the cosine similarities between the input image and each image in the folder, and the total cost.
        """
        try:
            # Preprocess the input image
            image = self._image_preprocessing(image)

            # Generate embedding for the input image
            image_embedding, total_cost = self.model_invoke(
                input_image=image,
                output_embedding_length=output_embedding_length,
                model_name=model_name
            )
            image_embedding = np.array(image_embedding)

            # Get a list of image file paths in the folder (excluding hidden files)
            files_path = [
                f'{folder_path}/{file_name}'
                for file_name in os.listdir(folder_path)
                if not file_name.startswith('.')
            ]

            # Prepare an array to store embeddings for all images in the folder
            num_files = len(files_path)
            folder_image_embeddings = np.zeros((num_files, output_embedding_length))

            # Process each image in the folder and compute its embedding
            keys = []
            for idx, file_path in enumerate(files_path):
                other_image = self._image_preprocessing(file_path)
                other_image_embedding, additional_cost = self.model_invoke(
                    input_image=other_image,
                    output_embedding_length=output_embedding_length,
                    model_name=model_name
                )
                folder_image_embeddings[idx, :] = other_image_embedding
                total_cost += additional_cost
                keys.append(file_path)

            # Calculate cosine similarity between the input image and all folder images
            similarities = self.cosine_similarity(image_embedding, folder_image_embeddings)

            top_k_similarities_by_path = self._get_top_k_values(keys, similarities, k)

            logger.info(f"Pipeline invocation successful. Total cost: ${total_cost:.6f}")

            return top_k_similarities_by_path, total_cost

        except Exception as e:
            user_friendly_error = self._get_user_friendly_error(e)
            logger.error(user_friendly_error)
            return None, 0

    def image_to_pil_list_similarity(self, image, pil_image_list, k=10, output_embedding_length=256, model_name=None):
        """
        Calculate the similarity between an image and a list of PIL image objects using cosine similarity.

        Args:
            image: The input image to compare.
            pil_image_list: A list of PIL image objects to compare against.
            k: Top k results to return with the greatest similarity (default 10).
            output_embedding_length: The length of the output embeddings (default 256).
            model_name: The name of the model to use for generating embeddings (optional).

        Returns:
            A tuple containing:
                - Cosine similarities between the input image and each PIL image in the list.
                - The total cost of computing the embeddings.
        """
        try:
            # Preprocess the input image
            image = self._image_preprocessing(image)

            # Generate embedding for the input image
            image_embedding, total_cost = self.model_invoke(
                input_image=image,
                output_embedding_length=output_embedding_length,
                model_name=model_name
            )
            image_embedding = np.array(image_embedding)

            # Prepare an array to store embeddings for all images in the PIL list
            num_images = len(pil_image_list)
            pil_image_embeddings = np.zeros((num_images, output_embedding_length))

            # Process each PIL image and compute its embedding
            keys = []
            for idx, pil_image in enumerate(pil_image_list):
                # Preprocess the PIL image (assuming similar preprocessing function works for PIL objects)
                other_image = self._image_preprocessing(pil_image)
                other_image_embedding, additional_cost = self.model_invoke(
                    input_image=other_image,
                    output_embedding_length=output_embedding_length,
                    model_name=model_name
                )
                pil_image_embeddings[idx, :] = other_image_embedding
                total_cost += additional_cost
                keys.append(pil_image.filename)

            # Calculate cosine similarity between the input image and all images in the list
            similarities = self.cosine_similarity(image_embedding, pil_image_embeddings)

            top_k_similarities_by_path = self._get_top_k_values(keys, similarities, k)

            logger.info(f"Pipeline invocation successful. Total cost: ${total_cost:.6f}")

            return top_k_similarities_by_path, total_cost

        except Exception as e:
            # Handle any errors and log a user-friendly error message
            user_friendly_error = self._get_user_friendly_error(e)
            logger.error(user_friendly_error)
            return None, 0

    def image_to_s3_folder_similarity(self, image, s3_folder_path, k=10, output_embedding_length=256, model_name=None):
        """
        Calculate the similarity between an image and all images in an S3 folder using cosine similarity.

        Args:
            image: The first image to compare (file path or a PIL Image object).
            s3_folder_path: S3 path to the folder containing the images/objects to compare with.
            k: Top k results to return with the greatest similarity (default 10).
            output_embedding_length: The length of the output embeddings (default 256).
            model_name: The name of the model to use for generating embeddings (optional).

        Returns:
            A tuple containing the cosine similarities between the input image and each image in the folder, and the total cost.
        """
        try:
            # Preprocess the input image
            image = self._image_preprocessing(image)

            # Generate embedding for the input image
            image_embedding, total_cost = self.model_invoke(
                input_image=image,
                output_embedding_length=output_embedding_length,
                model_name=model_name
            )
            image_embedding = np.array(image_embedding)

            # Get a list of images/objects in the S3 folder
            bucket_name, folder_name = self._parse_s3_path(s3_folder_path)
            image_objects = self._get_s3_folder_objects(bucket_name, folder_name)

            # Prepare an array to store embeddings for all images/objects in the folder
            num_files = len(image_objects)
            folder_image_embeddings = np.zeros((num_files, output_embedding_length))

            # Process each image/object in the folder and compute its embedding
            keys = []
            for idx, (name, image) in enumerate(image_objects.items()):
                other_image = self._image_preprocessing(image)
                other_image_embedding, additional_cost = self.model_invoke(
                    input_image=other_image,
                    output_embedding_length=output_embedding_length,
                    model_name=model_name
                )
                folder_image_embeddings[idx, :] = other_image_embedding
                total_cost += additional_cost
                s3_path = f"s3://{bucket_name}/{name}"
                keys.append(s3_path)

            # Calculate cosine similarity between the input image and all folder images
            similarities = self.cosine_similarity(image_embedding, folder_image_embeddings)

            top_k_similarities_by_path = self._get_top_k_values(keys, similarities, k)

            logger.info(f"Pipeline invocation successful. Total cost: ${total_cost:.6f}")

            return top_k_similarities_by_path, total_cost

        except Exception as e:
            # Handle any errors and log a user-friendly error message
            user_friendly_error = self._get_user_friendly_error(e)
            logger.error(user_friendly_error)
            return None, 0