from loguru import logger
import botocore.exceptions
import pymupdf
import docx
import json
import base64
from io import BytesIO
from PIL import Image
from typing import Dict, Any
import os
import numpy as np
import contextlib
import ast


class PythonASTREPL:
    def __init__(self, dataframes=None, locals=None, globals=None):
        """
        Initialize the REPL with optional local and global namespaces and dataframes.

        Args:
            dataframes (dict, optional): A dictionary of DataFrames.
            locals (dict, optional): Local namespace for code execution.
            globals (dict, optional): Global namespace for code execution.
        """
        self.locals = locals if locals is not None else {}
        self.globals = globals if globals is not None else {}
        if dataframes:
            self.locals.update(dataframes)

    def run(self, code: str) -> str:
        """Execute the provided Python code and return the result or error message.

        Args:
            code (str): The Python code to be executed.

        Returns:
            str: The result of the code execution or an error message.
        """

        buffer = io.StringIO()
        assigned_vars = []

        # Parse the code to identify assigned variables
        try:
            parsed_code = ast.parse(code)
            for node in ast.walk(parsed_code):
                if isinstance(node, ast.Assign):
                    # For targets in the assignment, get their ids (variable names)
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            assigned_vars.append(target.id)
        except Exception as e:
            return f"Error parsing code: {e}"

        try:
            with contextlib.redirect_stdout(buffer):
                try:
                    # Attempt to compile the code as an expression
                    compiled_code = compile(code, '<string>', 'eval')
                    result = eval(compiled_code, self.globals, self.locals)
                    print(repr(result))
                except SyntaxError:
                    # If it isn't an expression, compile it as a statement
                    compiled_code = compile(code, '<string>', 'exec')
                    exec(compiled_code, self.globals, self.locals)
                    result = None
                    # If no output and variables were assigned, print their values
                    if not buffer.getvalue().strip() and assigned_vars:
                        for var in assigned_vars:
                            value = self.locals.get(var, 'Undefined')
                            print(f"{var} = {repr(value)}")
                    elif not buffer.getvalue().strip():
                        # If no output and no assigned vars, print 'None'
                        print('None')
        except Exception as e:
            # Capture any exceptions raised during execution
            return f"Error: {e}"
        # Retrieve the captured output from stdout
        output = buffer.getvalue().strip()
        return output


class Utils:
    """Utility class containing helper methods used across the application."""
    
    @staticmethod
    def get_user_friendly_error(error: Exception) -> str:
        """
        Convert technical errors into user-friendly messages.
        
        Args:
            error (Exception): The original error
            
        Returns:
            str: A user-friendly error message
        """
        if isinstance(error, ValueError):
            return str(error)
        elif isinstance(error, botocore.exceptions.BotoCoreError):
            return "An error occurred with the AWS service. Please check your AWS resources and permissions."
        else:
            return f"An unexpected error occurred: {str(error)}."

    @staticmethod
    def transform_response_to_pillow(response: Dict[str, Any], model_name: str) -> Image.Image:
        """
        Transform a base64 image response from various AI models into a Pillow Image.
        
        Args:
            response (Dict[str, Any]): The response from the AI model containing the base64 image
            model_name (str): Name of the AI model that generated the image
            
        Returns:
            Image.Image: A Pillow Image object
            
        Raises:
            ValueError: If the model_name is not supported or if response format is invalid
        """
        try:
            model_response = json.loads(response.get('body').read())
            
            # Dictionary mapping model names to their response structures
            model_mappings = {
                'amazon.titan.v1': lambda x: x["images"][0],
                'amazon.titan.v2': lambda x: x["images"][0],
                'sdxl': lambda x: x["artifacts"][0]["base64"],
                'sd3-large': lambda x: x["images"][0],
                'stable-image-ultra': lambda x: x["images"][0],
                'stable-image-core': lambda x: x["images"][0]
            }
            
            if model_name not in model_mappings:
                raise ValueError(f"Unsupported model: {model_name}")
                
            # Get base64 image string using the appropriate mapping
            base64_image = model_mappings[model_name](model_response)
            
            # Decode and convert to Pillow Image
            image_decoded = base64.b64decode(base64_image)
            image_decoded = BytesIO(image_decoded)
            image = Image.open(image_decoded).convert("RGB")
            
            return image
            
        except (KeyError, json.JSONDecodeError) as e:
            logger.error(f"Error processing response from {model_name}: {str(e)}")
            raise ValueError(f"Invalid response format from {model_name}")
        except Exception as e:
            logger.error(f"Unexpected error processing {model_name} response: {str(e)}")
            raise

    @staticmethod
    def read_pdf(file_obj):
        logger.info(f"Reading PDF content from in-memory file object")
        doc = pymupdf.open(file_obj)
        text = ""
        for page in doc:
            text += page.get_text()
        return text

    @staticmethod
    def read_pdf_from_stream(file_obj):
        logger.info(f"Reading PDF content from in-memory file object")
        doc = pymupdf.open(stream=file_obj, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text

    @staticmethod
    def read_docx(file_obj):
        logger.info(f"Reading DOCX content from in-memory file object")
        doc = docx.Document(file_obj)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])

    @staticmethod
    def _get_user_friendly_error(error):
        # Customize user-friendly error messages here
        if isinstance(error, ValueError):
            return str(error)
        elif isinstance(error, botocore.exceptions.BotoCoreError):
            return "An error occurred with the AWS service. Please check your AWS resources and permissions."
        else:
            return f"An unexpected error occurred: {str(error)}."

    @staticmethod
    def get_top_k_values(keys, similarities, k):
        """
        Get the top k items based on similarity scores.
        
        Args:
            keys (list): List of keys/identifiers
            similarities (list): List of similarity scores corresponding to the keys
            k (int): Number of top items to return
            
        Returns:
            dict: Dictionary of top k items with their similarity scores
        """
        similarities_by_path = {key: float(value) for key, value in zip(keys, similarities)}
        similarities_by_path = sorted(similarities_by_path.items(), key=lambda x: x[1], reverse=True)
        return dict(similarities_by_path[:k])

    @staticmethod
    def preprocess_image(input_image):
        """
        Preprocess an image from various input formats into bytes.
        
        Args:
            input_image: The input image in one of these formats:
                        - bytes: Raw image bytes
                        - PIL.Image: PIL Image object
                        - str: File path or S3 path (starting with 's3://')
            
        Returns:
            bytes: The image data as bytes
            
        Raises:
            ValueError: If the input format is not supported or if S3 operations fail
        """
        if isinstance(input_image, bytes):
            return input_image
        elif isinstance(input_image, Image.Image):
            buffered = BytesIO()
            input_image.save(buffered, format="PNG")
            return buffered.getvalue()
        elif isinstance(input_image, str):
            if os.path.isfile(input_image):
                with open(input_image, 'rb') as img_file:
                    return img_file.read()
            elif input_image.startswith('s3://'):
                if s3_helper is None:
                    raise ValueError("S3Helper instance required for S3 operations")
                bucket_name, key_name = s3_helper.parse_s3_path(input_image)
                return s3_helper.get_s3_object(bucket_name, key_name)
            else:
                raise ValueError("File path does not exist or is not a valid S3 path")
        else:
            raise ValueError("Unsupported image format: must be bytes, file path, S3 path, or PIL Image object")

    @staticmethod
    def cosine_similarity(vector, matrix_or_vector):
        """
        Calculate cosine similarity between a vector and a matrix or another vector.
        
        Args:
            vector (numpy.ndarray): Input vector
            matrix_or_vector (numpy.ndarray): Matrix of vectors or single vector to compare against
            
        Returns:
            numpy.ndarray: Array of similarity scores
        """
        if len(matrix_or_vector.shape) == 1:
            # If comparing with a single vector
            dot_product = np.dot(vector, matrix_or_vector)
            vector_norm = np.linalg.norm(vector)
            matrix_norm = np.linalg.norm(matrix_or_vector)
            return dot_product / (vector_norm * matrix_norm)
        else:
            # If comparing with a matrix
            dot_product = np.dot(matrix_or_vector, vector)
            vector_norm = np.linalg.norm(vector)
            matrix_norm = np.linalg.norm(matrix_or_vector, axis=1)
            return dot_product / (vector_norm * matrix_norm)

    @staticmethod
    def extract_clinical_report(data):
        """
        Extract and format clinical report sections from medical documentation.
        
        Args:
            data (dict): Dictionary containing ClinicalDocumentation with Sections
            
        Returns:
            str: Formatted string containing section names and their summaries
        """
        output = []
        sections = data.get('ClinicalDocumentation', {}).get('Sections', [])
        for section in sections:
            output.append(f"Section: {section.get('SectionName')}")
            summaries = section.get('Summary', [])
            for summary in summaries:
                output.append(f"  {summary.get('SummarizedSegment')}")
            output.append("\n")
        return "\n".join(output)

    @staticmethod
    def format_conversation(data):
        """
        Format conversation transcripts into a readable dialogue format.
        
        Args:
            data (dict): Dictionary containing Conversation with TranscriptItems
            
        Returns:
            str: Formatted string containing the conversation dialogue
        """
        transcripts = data.get('Conversation', {}).get('TranscriptItems', [])
        dialogue = []
        current_speaker = "Speaker 1"
        last_speaker = "Speaker 1"
        speech_accumulator = ""
        
        for item in transcripts:
            content = " ".join(alt['Content'] for alt in item.get('Alternatives', []) if alt['Content'].strip())
            # Determine speaker change by questions and answers
            if content.endswith('?'):
                if last_speaker == "Speaker 1":
                    current_speaker = "Speaker 2"
                else:
                    current_speaker = "Speaker 1"
                    
            if last_speaker != current_speaker:
                if speech_accumulator:
                    dialogue.append(f"{last_speaker}: {speech_accumulator.strip()}")
                    speech_accumulator = content + " "
                last_speaker = current_speaker
            else:
                speech_accumulator += content + " "
                
        # Add the last accumulated speech
        if speech_accumulator:
            dialogue.append(f"{current_speaker}: {speech_accumulator.strip()}")
            
        return "\n".join(dialogue)