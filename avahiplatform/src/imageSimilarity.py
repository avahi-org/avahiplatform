import base64
from loguru import logger
from io import BytesIO
from PIL import Image
import os
import numpy as np
from avahiplatform.helpers import BedrockEmbeddings, S3Helper, Utils


class BedrockImageSimilarity(BedrockEmbeddings):

    def __init__(self, boto_helper, s3_helper: S3Helper, default_model_id):
            """
            Initialize the ImageGeneration class
            
            Args:
                boto_helper: Helper object for AWS interactions
            """
            self.boto_helper = boto_helper
            self.model_id = default_model_id
            self.s3_helper = s3_helper
            self.bedrock_embeddings = BedrockEmbeddings(model_id=self.model_id,
            boto_helper=self.boto_helper)


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
            bucket_name, key_name = self.s3_helper.parse_s3_path(input_image)
            image_data = self.s3_helper.get_s3_object(bucket_name, key_name)
        else:
            raise ValueError("Unsupported image format: must be a bytes string, a file path or a PIL Image object.")

        encoded_image = base64.b64encode(image_data).decode('utf-8')

        return encoded_image

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
            embedding_result = self.bedrock_embeddings.generate_embeddings(
                image=image,
                dimension=output_embedding_length
            )
            image_embedding = np.array(embedding_result['embeddings'])

            # Preprocess the other image
            other_image = self._image_preprocessing(other_image)

            # Generate embedding for the other image
            other_image_embedding_result = self.bedrock_embeddings.generate_embeddings(
                image=other_image,
                dimension=output_embedding_length
            )
            other_image_embedding = np.array(other_image_embedding_result['embeddings'])

            # Calculate cosine similarity between the two embeddings
            similarity = Utils.cosine_similarity(image_embedding, other_image_embedding)

            logger.info(f"Pipeline invocation successfull")

            return similarity

        except Exception as e:
            user_friendly_error = Utils.get_user_friendly_error(e)
            logger.error(user_friendly_error)
            return None

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

            # Generate embedding for the first image
            embedding_result = self.bedrock_embeddings.generate_embeddings(
                image=image,
                dimension=output_embedding_length
            )
            image_embedding = np.array(embedding_result['embeddings'])

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
                # Generate embedding for the first image
                embedding_result = self.bedrock_embeddings.generate_embeddings(
                    image=other_image,
                    dimension=output_embedding_length
                )
                other_image_embedding = np.array(embedding_result['embeddings'])
                folder_image_embeddings[idx, :] = other_image_embedding
                keys.append(file_path)

            # Calculate cosine similarity between the input image and all folder images
            similarities = Utils.cosine_similarity(image_embedding, folder_image_embeddings)

            top_k_similarities_by_path = Utils.get_top_k_values(keys, similarities, k)

            logger.info(f"Pipeline invocation successfull")

            return top_k_similarities_by_path

        except Exception as e:
            user_friendly_error = Utils.get_user_friendly_error(e)
            logger.error(user_friendly_error)
            return None

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

            # Generate embedding for the first image
            embedding_result = self.bedrock_embeddings.generate_embeddings(
                image=image,
                dimension=output_embedding_length
            )
            image_embedding = np.array(embedding_result['embeddings'])

            # Prepare an array to store embeddings for all images in the PIL list
            num_images = len(pil_image_list)
            pil_image_embeddings = np.zeros((num_images, output_embedding_length))

            # Process each PIL image and compute its embedding
            keys = []
            for idx, pil_image in enumerate(pil_image_list):
                # Preprocess the PIL image (assuming similar preprocessing function works for PIL objects)
                other_image = self._image_preprocessing(pil_image)
                # Generate embedding for the first image
                embedding_result = self.bedrock_embeddings.generate_embeddings(
                    image=other_image,
                    dimension=output_embedding_length
                )
                other_image_embedding = np.array(embedding_result['embeddings'])
                pil_image_embeddings[idx, :] = other_image_embedding
                keys.append(pil_image.filename)

            # Calculate cosine similarity between the input image and all images in the list
            similarities = Utils.cosine_similarity(image_embedding, pil_image_embeddings)

            top_k_similarities_by_path = Utils.get_top_k_values(keys, similarities, k)

            logger.info(f"Pipeline invocation successful.")

            return top_k_similarities_by_path

        except Exception as e:
            # Handle any errors and log a user-friendly error message
            user_friendly_error = Utils.get_user_friendly_error(e)
            logger.error(user_friendly_error)
            return None

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

            # Generate embedding for the first image
            embedding_result = self.bedrock_embeddings.generate_embeddings(
                image=image,
                dimension=output_embedding_length
            )
            image_embedding = np.array(embedding_result['embeddings'])

            # Get a list of images/objects in the S3 folder
            bucket_name, folder_name = self.s3_helper.parse_s3_path(s3_folder_path)
            image_objects = self.s3_helper.get_s3_folder_objects(bucket_name, folder_name)

            # Prepare an array to store embeddings for all images/objects in the folder
            num_files = len(image_objects)
            folder_image_embeddings = np.zeros((num_files, output_embedding_length))

            # Process each image/object in the folder and compute its embedding
            keys = []
            for idx, (name, image) in enumerate(image_objects.items()):
                other_image = self._image_preprocessing(image)
                # Generate embedding for the first image
                embedding_result = self.bedrock_embeddings.generate_embeddings(
                    image=other_image,
                    dimension=output_embedding_length
                )
                other_image_embedding = np.array(embedding_result['embeddings'])
                folder_image_embeddings[idx, :] = other_image_embedding
                s3_path = f"s3://{bucket_name}/{name}"
                keys.append(s3_path)

            # Calculate cosine similarity between the input image and all folder images
            similarities = Utils.cosine_similarity(image_embedding, folder_image_embeddings)

            top_k_similarities_by_path = Utils.get_top_k_values(keys, similarities, k)

            logger.info(f"Pipeline invocation successful.")

            return top_k_similarities_by_path

        except Exception as e:
            # Handle any errors and log a user-friendly error message
            user_friendly_error = Utils.get_user_friendly_error(e)
            logger.error(user_friendly_error)
            return None