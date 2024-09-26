from .summarizer import BedrockSummarizer
from .structredExtraction import BedrockstructredExtraction
from .data_masking import BedrockDataMasking
from .nl2sql import BedrockNL2SQL
from .rag_semantic_search import RAGSemanticSearch
from .pdfSummarizer import BedrockPdfSummarizer
from .grammarCorrection import BedrockGrammarCorrection
from .productDescriptionGeneration import productDescriptionGeneration
from .imageGeneration import BedrockImageGeneration
from .medical_scribing import MedicalScribe
from .query_csv import QueryCSV
from .icd_code_generator import ICDCodeGenerator

# from summarizer import BedrockSummarizer
# from structredExtraction import BedrockstructredExtraction
# from data_masking import BedrockDataMasking
# from nl2sql import BedrockNL2SQL
# from rag_semantic_search import RAGSemanticSearch
# from pdfSummarizer import BedrockPdfSummarizer
# from grammarCorrection import BedrockGrammarCorrection
# from productDescriptionGeneration import productDescriptionGeneration
# from imageGeneration import BedrockImageGeneration
# from medical_scribing import MedicalScribe
# from query_csv import QueryCSV
# from icd_code_generator import ICDCodeGenerator
# from .chatbot import BedrockChatbot


import os
from loguru import logger


def get_instance(aws_access_key_id=None, aws_secret_access_key=None, region_name=None):
    # global _instance
    # if _instance is None:
    _instance = BedrockSummarizer(aws_access_key_id=aws_access_key_id,
                                  aws_secret_access_key=aws_secret_access_key,
                                  region_name=region_name)
    return _instance


def get_instance_extraction(aws_access_key_id=None, aws_secret_access_key=None, region_name=None):
    # global _instance
    # if _instance is None:
    _instance = BedrockstructredExtraction(aws_access_key_id=aws_access_key_id,
                                           aws_secret_access_key=aws_secret_access_key,
                                           region_name=region_name)
    return _instance


def get_instance_Data_mask(aws_access_key_id=None, aws_secret_access_key=None, region_name=None):
    # global _instance
    # if _instance is None:
    _instance = BedrockDataMasking(aws_access_key_id=aws_access_key_id,
                                   aws_secret_access_key=aws_secret_access_key,
                                   region_name=region_name)
    return _instance


def get_instance_nl2sql(aws_access_key_id=None, aws_secret_access_key=None, region_name=None):
    # global _instance
    # if _instance is None:
    _instance = BedrockNL2SQL(aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              region_name=region_name)
    return _instance

_instance = None

def get_instance_rag_semantic_search(s3_path, aws_access_key_id=None, aws_secret_access_key=None, region_name=None):
    #global _instance
    # if _instance is None:
    _instance = RAGSemanticSearch(s3_path, aws_access_key_id=aws_access_key_id,
                                    aws_secret_access_key=aws_secret_access_key,
                                    region_name=region_name)
    return _instance


def get_instance_pdf(aws_access_key_id=None, aws_secret_access_key=None, region_name=None):
    # global _instance
    # if _instance is None:
    _instance = BedrockPdfSummarizer(aws_access_key_id=aws_access_key_id,
                                  aws_secret_access_key=aws_secret_access_key,
                                  region_name=region_name)
    return _instance

def get_instance_grammar_correction(aws_access_key_id=None, aws_secret_access_key=None, region_name=None):
    # global _instance
    # if _instance is None:
    _instance = BedrockGrammarCorrection(aws_access_key_id=aws_access_key_id,
                                  aws_secret_access_key=aws_secret_access_key,
                                  region_name=region_name)
    return _instance


def get_instance_product_description_generation(aws_access_key_id=None, aws_secret_access_key=None, region_name=None):
    # global _instance
    # if _instance is None:
    _instance = productDescriptionGeneration(aws_access_key_id=aws_access_key_id,
                                  aws_secret_access_key=aws_secret_access_key,
                                  region_name=region_name)
    return _instance


def get_instance_image_generation(aws_access_key_id=None, aws_secret_access_key=None, region_name=None):
    # global _instance
    # if _instance is None:
    _instance = BedrockImageGeneration(aws_access_key_id=aws_access_key_id,
                                       aws_secret_access_key=aws_secret_access_key,
                                       region_name=region_name)
    return _instance


def get_instance_icdcode(aws_access_key_id=None, aws_secret_access_key=None, region_name=None):
    # global _instance
    # if _instance is None:
    _instance = ICDCodeGenerator(aws_access_key_id=aws_access_key_id,
                                 aws_secret_access_key=aws_secret_access_key,
                                 region_name=region_name)
    return _instance


def get_instance_query_csv(aws_access_key_id=None, aws_secret_access_key=None, region_name=None):
    # global _instance
    # if _instance is None:
    _instance = QueryCSV(aws_access_key_id=aws_access_key_id,
                         aws_secret_access_key=aws_secret_access_key,
                         region_name=region_name)
    return _instance


def get_instance_medical_scribe(input_bucket_name, iam_arn, aws_access_key_id=None, aws_secret_access_key=None, region_name=None):
    # global _instance
    # if _instance is None:
    _instance = MedicalScribe(input_bucket_name=input_bucket_name, iam_arn=iam_arn, aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              region_name=region_name)
    return _instance

def get_instance_chatbot(aws_access_key_id=None, aws_secret_access_key=None, region_name=None):
    _instance = BedrockChatbot(aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key,
                          region_name=region_name)
    return _instance

def chat_with_bot(chatbot, user_input, model_name=None, aws_access_key_id=None,
              aws_secret_access_key=None, region_name=None):
    """
    Function to interact with the chatbot and handle its response.
    """
    instance = get_instance_chatbot(aws_access_key_id, aws_secret_access_key, region_name);
    try:
        response = instance.chat(user_input)

        history = chatbot.get_conversation_history()
        return response, history
    except Exception as e:
        user_friendly_error = instance._get_user_friendly_error(e)
        logger.error(user_friendly_error)
        return f"An error occurred: {user_friendly_error}"

def medicalscribing(audio_filepath, input_bucket_name, iam_arn, aws_access_key_id=None, aws_secret_access_key=None, region_name=None):
    """ Generate medical scribing for the given audio file path. The input can be a local file path or an S3 file path.

    Parameters:
    audio_filepath (str): The path to the audio file for generating medical scribing.
                          This can be a local file path or an S3 file path.
    input_bucket_name (str): The name of the S3 bucket where the input files are stored.
    iam_arn (str): The IAM Amazon Resource Name (ARN) used for authentication.
    aws_access_key_id (str, optional): AWS Access Key ID (optional).
    aws_secret_access_key (str, optional): AWS Secret Access Key (optional).
    region_name (str, optional): AWS region name for accessing cloud-based resources (optional).

    Returns:
    (str, str): A tuple containing two strings:
                    - The first string contains summary report.
                    - The second string contain transcript.
    """
    instance = get_instance_medical_scribe(input_bucket_name, iam_arn, aws_access_key_id, aws_secret_access_key, region_name)
    try:
        if os.path.exists(audio_filepath): # Check if input is a local file path
            return instance.fetch_medical_scribing_from_filepath(audio_filepath)
        elif audio_filepath.startswith('s3://'): # Check if input is an S3 file path
            return instance.fetch_medical_scribing_from_s3_path(audio_filepath)
        else:
            raise ValueError(f"Audio file path is wrong please check that and try again")
    except Exception as e:
        user_friendly_error = instance._get_user_friendly_error(e)
        logger.error(user_friendly_error)
        return None, None

def icdcoding(input_content, aws_access_key_id=None,
              aws_secret_access_key=None, region_name=None):
    """
    Generate the icd10 code for the given input content. The input can be text, a local file path, or an S3 file path.

    Parameters:
    input_content (str): The content to be used for generating the icd10 code. This can be a text string, a local file path, or an S3 file path.
    aws_access_key_id (str, optional): AWS Access Key ID.
    aws_secret_access_key (str, optional): AWS Secret Access Key.
    region_name (str, optional): AWS region name for accessing cloud-based resources (optional).

    Returns:
    json_string: A json_string containing the icd10 entity.
    """
    instance = get_instance_icdcode(aws_access_key_id, aws_secret_access_key, region_name)
    try:
        if os.path.exists(input_content):  # Check if input is a local file path
            return instance.generate_code_from_file(input_content)
        elif input_content.startswith('s3://'):  # Check if input is an S3 file path
            return instance.generate_code_from_s3_file(input_content)
        else:  # Assume input is text
            return instance.generate_icdcode(input_content)
    except Exception as e:
        user_friendly_error = instance._get_user_friendly_error(e)
        logger.error(user_friendly_error)
        return None


def query_csv(user_query, csv_file_path, model_name=None, aws_access_key_id=None,
              aws_secret_access_key=None, region_name=None):
    """
    Process a user query on a CSV file located either locally or on S3 and invoke a model.

    Parameters:
    user_query (str): The query string provided by the user.
    csv_file_path (str): The path to the CSV file; can be a local file path or an S3 URI.
    model_name (str, optional): The name of the model to use for processing the query.
    aws_access_key_id (str, optional): AWS Access Key ID.
    aws_secret_access_key (str, optional): AWS Secret Access Key.
    region_name (str, optional): AWS region name for accessing cloud-based resources.

    Returns:
    Any: The result of the model invocation based on the user's query.

    Raises:
    ValueError: If the CSV file path is invalid or the file cannot be processed.
    """

    instance = get_instance_query_csv(aws_access_key_id, aws_secret_access_key, region_name)
    try:
        if os.path.exists(csv_file_path):  # Check if input is a local file path
            return instance.query_from_local_path(user_query, csv_file_path, model_name)
        elif csv_file_path.startswith('s3://'):  # Check if input is an S3 file path
            return instance.query_from_s3(user_query, csv_file_path, model_name)
        else:
            raise ValueError(f"CSV file path is wrong please check that and try again")
    except Exception as e:
        user_friendly_error = instance._get_user_friendly_error(e)
        logger.error(user_friendly_error)
        return None


def imageGeneration(prompt, seed=None, model_name=None, aws_access_key_id=None,
                    aws_secret_access_key=None, region_name=None):
    """
    Generates an image based on the provided prompt using a specified or default model. 

    Parameters:
    prompt (str): The text description used to generate the image.
    seed (int, optional): A seed for random number generation, which allows reproducibility of results. If not provided, the result will vary each time the function is run.
    model_name (str, optional): The name of the model to be used for image generation. If not provided, a default model will be used.
    aws_access_key_id (str, optional): AWS Access Key ID, used to authenticate requests to AWS services.
    aws_secret_access_key (str, optional): AWS Secret Access Key, used in conjunction with the access key ID to authenticate requests to AWS services.
    region_name (str, optional): The AWS region name to specify where to access cloud-based resources. This is optional if default region settings are configured.

    Returns:
    tuple: A tuple containing the generated image, the seed value used, and the associated costs. Or in case of an error, a tuple with Nones, and zeroes.
    """
    instance = get_instance_image_generation(aws_access_key_id, aws_secret_access_key, region_name)
    try:
        return instance.generate_image(prompt, seed, model_name)
    except Exception as e:
        user_friendly_error = instance._get_user_friendly_error(e)
        logger.error(user_friendly_error)
        return None, None, 0.0
    


def nl2sql(nl_query, db_type, username, password, host,
           port, dbname, db_path=None, user_prompt=None,
           model_name=None, aws_access_key_id=None, aws_secret_access_key=None, region_name=None):
    """
       Converts a natural language query into an SQL query, executes it against the specified database,
       and returns the results in a user-friendly manner.

       Parameters:
       - nl_query (str): The natural language query provided by the user.
       - db_type (str): The type of the database (e.g., 'postgresql', 'mysql', 'sqlite').
       - username (str): The username used to authenticate with the database.
       - password (str): The password used to authenticate with the database.
       - host (str): The host address of the database.
       - port (int or str): The port number of the database.
       - dbname (str): The name of the database.
       - db_path (str, optional): The file path for SQLite database (optional, required if db_type is 'sqlite').
       - user_prompt (str, optional): The custom prompt to guide the NL2SQL conversion (optional).
       - model_name (str, optional): The name of the model to be used for NL2SQL conversion (optional).
       - aws_access_key_id (str, optional): AWS access key ID for accessing cloud-based resources (optional).
       - aws_secret_access_key (str, optional): AWS secret access key for accessing cloud-based resources (optional).
       - region_name (str, optional): AWS region name for accessing cloud-based resources (optional).

       Returns:
       - str or None: The answer to the user's natural language query as a string. If an error occurs, returns None.

    """
    instance = get_instance_nl2sql(aws_access_key_id, aws_secret_access_key, region_name)
    try:
        return instance.get_answer_from_db(db_type, nl_query, username, password, host,
                                           port, dbname, db_path, model_name, user_prompt)
    except Exception as e:
        user_friendly_error = instance._get_user_friendly_error(e)
        logger.error(user_friendly_error)
        return None


def summarize(input_content, user_prompt=None, model_name=None, aws_access_key_id=None,
              aws_secret_access_key=None, region_name=None):
    """
    Summarizes the given input content. The input can be text, a local file path, or an S3 file path.

    Parameters:
    input_content (str): The content to be summarized. This can be a text string, a local file path, or an S3 file path.
    user_prompt (str, optional): A custom prompt to be used for the summarization. If not provided, a default prompt will be used.
    model_name (str, optional): The name of the model to be used. If not provided, the default model will be used.
    aws_access_key_id (str, optional): AWS Access Key ID.
    aws_secret_access_key (str, optional): AWS Secret Access Key.
    region_name (str, optional): AWS region name for accessing cloud-based resources (optional).

    Returns:
    tuple: A tuple containing the summary text, input token count, output token count, and the cost of the operation.
    """
    instance = get_instance(aws_access_key_id, aws_secret_access_key, region_name)
    try:
        if os.path.exists(input_content):  # Check if input is a local file path
            return instance.summarize_file(input_content, user_prompt, model_name)
        elif input_content.startswith('s3://'):  # Check if input is an S3 file path
            return instance.summarize_s3_file(input_content, user_prompt, model_name)
        else:  # Assume input is text
            return instance.summarize_text(input_content, user_prompt, model_name)
    except Exception as e:
        user_friendly_error = instance._get_user_friendly_error(e)
        logger.error(user_friendly_error)
        return None, 0, 0, 0.0


def structredExtraction(input_content, user_prompt=None, model_name=None, aws_access_key_id=None,
                        aws_secret_access_key=None, region_name=None):
    """
    Extract the given input content. The input can be text, a local file path, or an S3 file path.

    Parameters:
    input_content (str): The content to be used for extraction. This can be a text string, a local file path, or an S3 file path.
    user_prompt (str, optional): A custom prompt to be used for the Extraction. If not provided, a default prompt will be used.
    model_name (str, optional): The name of the model to be used. If not provided, the default model will be used.
    aws_access_key_id (str, optional): AWS Access Key ID.
    aws_secret_access_key (str, optional): AWS Secret Access Key.
    region_name (str, optional): AWS region name for accessing cloud-based resources (optional).

    Returns:
    tuple: A tuple containing the Extracted entity, input token count, output token count, and the cost of the operation.
    """
    instance = get_instance_extraction(aws_access_key_id, aws_secret_access_key, region_name)
    try:
        if os.path.exists(input_content):  # Check if input is a local file path
            return instance.extract_file(input_content, user_prompt, model_name)
        elif input_content.startswith('s3://'):  # Check if input is an S3 file path
            return instance.extract_s3_file(input_content, user_prompt, model_name)
        else:  # Assume input is text
            return instance.extract_text(input_content, user_prompt, model_name)
    except Exception as e:
        user_friendly_error = instance._get_user_friendly_error(e)
        logger.error(user_friendly_error)
        return None, 0, 0, 0.0


def DataMasking(input_content, user_prompt=None, model_name=None, aws_access_key_id=None,
                aws_secret_access_key=None, region_name=None):
    """
    Extract the given input content. The input can be text, a local file path, or an S3 file path.

    Parameters:
    input_content (str): The content to be used for extraction. This can be a text string, a local file path, or an S3 file path.
    user_prompt (str, optional): A custom prompt to be used for the Extraction. If not provided, a default prompt will be used.
    model_name (str, optional): The name of the model to be used. If not provided, the default model will be used.
    aws_access_key_id (str, optional): AWS Access Key ID.
    aws_secret_access_key (str, optional): AWS Secret Access Key.
    region_name (str, optional): AWS region name for accessing cloud-based resources (optional).

    Returns:
    tuple: A tuple containing the Extracted entity, input token count, output token count, and the cost of the operation.
    """
    instance = get_instance_Data_mask(aws_access_key_id, aws_secret_access_key, region_name)
    try:
        if os.path.exists(input_content):  # Check if input is a local file path
            return instance.mask_file(input_content, user_prompt, model_name)
        elif input_content.startswith('s3://'):  # Check if input is an S3 file path
            return instance.mask_s3_file(input_content, user_prompt, model_name)
        else:  # Assume input is text
            return instance.mask_text(input_content, user_prompt, model_name)
    except Exception as e:
        user_friendly_error = instance._get_user_friendly_error(e)
        logger.error(user_friendly_error)
        return None, 0, 0, 0.0
    

def pdfsummarizer(input_content, user_prompt=None, model_name=None, aws_access_key_id=None,
              aws_secret_access_key=None, region_name=None):
    """
    Summarizes the given pdf file. The input should be pdf file.

    Parameters:
    input_content (str): The file to be summarized. This should be a pdf file path.
    user_prompt (str, optional): A custom prompt to be used for the summarization. If not provided, a default prompt will be used.
    model_name (str, optional): The name of the model to be used. If not provided, the default model will be used.
    aws_access_key_id (str, optional): AWS Access Key ID.
    aws_secret_access_key (str, optional): AWS Secret Access Key.
    region_name (str, optional): AWS region name for accessing cloud-based resources (optional).

    Returns:
    tuple: A tuple containing the summary text, input token count, output token count, and the cost of the operation.
    """
    instance = get_instance_pdf(aws_access_key_id, aws_secret_access_key, region_name)
    try:
        if os.path.exists(input_content):  # Check if input is a local file path
            return instance.summarize_pdf_file(input_content, user_prompt, model_name)
        else:  # Assume input is text
            raise ValueError("Input file should be PDF.")
    except Exception as e:
        user_friendly_error = instance._get_user_friendly_error(e)
        logger.error(user_friendly_error)
        return None, 0, 0, 0.0

def grammarAssistant(input_content, user_prompt=None, model_name=None, aws_access_key_id=None,
              aws_secret_access_key=None, region_name=None):
    """
    Corrects the grammar of the given input content. The input can be text, a local file path, or an S3 file path.

    Parameters:
    input_content (str): The content to be processed for grammar correction. This can be a text string, a local file path, or an S3 file path.
    user_prompt (str, optional): A custom prompt to be used for grammar correction. If not provided, a default prompt will be used.
    model_name (str, optional): The name of the model to be used for grammar correction. If not provided, the default model will be used.
    aws_access_key_id (str, optional): AWS Access Key ID for accessing S3 files.
    aws_secret_access_key (str, optional): AWS Secret Access Key for accessing S3 files.
    region_name (str, optional): AWS region name for accessing cloud-based resources (optional).

    Returns:
    tuple: A tuple containing the corrected text, input token count, output token count, and the cost of the operation.

    Raises:
    Exception: If an error occurs during grammar correction, it logs the error and returns default values (None, 0, 0, 0.0).
    """
    instance = get_instance_grammar_correction(aws_access_key_id, aws_secret_access_key, region_name)
    try:
        if os.path.exists(input_content):  # Check if input is a local file path
            return instance.grammar_correction_file(input_content, user_prompt, model_name)
        elif input_content.startswith('s3://'):  # Check if input is an S3 file path
            return instance.grammar_correction_s3_file(input_content, user_prompt, model_name)
        else:  # Assume input is text
            return instance.grammar_correction_text(input_content, user_prompt, model_name)
    except Exception as e:
        user_friendly_error = instance._get_user_friendly_error(e)
        logger.error(user_friendly_error)
        return None, 0, 0, 0.0

def productDescriptionAssistant(product_sku, event_name, customer_segmentation, user_prompt=None, model_name=None, aws_access_key_id=None,
              aws_secret_access_key=None, region_name=None):
    """
    Generates a product description based on the given inputs: product SKU, event name, and customer segmentation.
    Parameters:
    product_sku (str): The SKU of the product for which the description will be generated.
    event_name (str): The name of the event associated with the product.
    customer_segmentation (str): The customer segment to target for the product description.
    user_prompt (str, optional): A custom prompt to be used for the description generation. If not provided, a default prompt will be used.
    model_name (str, optional): The name of the model to be used for product description generation. If not provided, the default model will be used.
    aws_access_key_id (str, optional): AWS Access Key ID for accessing cloud-based services (if needed).
    aws_secret_access_key (str, optional): AWS Secret Access Key for accessing cloud-based services (if needed).
    region_name (str, optional): AWS region name for accessing cloud-based services (if needed).

    Returns:
    tuple: A tuple containing the generated product description, input token count, output token count, and the cost of the operation.

    Raises:
    ValueError: If any of the required inputs (product SKU, event name, or customer segmentation) are missing.

    Logs:
    Logs any exceptions and provides a user-friendly error message in case of failure.

    Example:
    If the required inputs (product SKU, event name, and customer segmentation) are provided, the function will generate a product description using a specified model or a default one.
    """
    instance = get_instance_product_description_generation(aws_access_key_id, aws_secret_access_key, region_name)
    try:
        if event_name and customer_segmentation:  # Check if input having event name and customer segmentation
            return instance.generate_product_description(product_sku, event_name, customer_segmentation, user_prompt, model_name)
        else:  # Assume input is text
            raise ValueError("Incomplete input provided. Please ensure you provide the product SKU, event name, and customer segmentation to generate the product description.")
    except Exception as e:
        user_friendly_error = instance._get_user_friendly_error(e)
        logger.error(user_friendly_error)
        return None, 0, 0, 0.0
    

def perform_semantic_search(question, s3_path, aws_access_key_id=None, aws_secret_access_key=None, region_name=None):
    """
    Perform semantic search on the given question.

    Parameters:
    question (str): The question to be used for semantic search.
    s3_path (str): The S3 path where the documents are stored.
    aws_access_key_id (str, optional): AWS Access Key ID.
    aws_secret_access_key (str, optional): AWS Secret Access Key.
    region_name (str, optional): AWS region name for accessing cloud-based resources.

    Returns:
    list: A list of tuples containing similar documents and their scores.
    """
    instance = get_instance_rag_semantic_search(s3_path, aws_access_key_id, aws_secret_access_key, region_name)
    try:
        similar_docs = instance.semantic_search(question)
        return similar_docs
    except Exception as e:
        user_friendly_error = instance._get_user_friendly_error(e)
        logger.error(user_friendly_error)
        return None

def perform_rag_with_sources(question, s3_path, aws_access_key_id=None, aws_secret_access_key=None, region_name=None):
    """
    Perform RAG with sources on the given question.

    Parameters:
    question (str): The question to be used for RAG.
    s3_path (str): The S3 path where the documents are stored.
    aws_access_key_id (str, optional): AWS Access Key ID.
    aws_secret_access_key (str, optional): AWS Secret Access Key.
    region_name (str, optional): AWS region name for accessing cloud-based resources.

    Returns:
    tuple: A tuple containing the answer and sources.
    """
    instance = get_instance_rag_semantic_search(s3_path, aws_access_key_id, aws_secret_access_key, region_name)
    try:
        answer, sources = instance.rag_with_sources(question)
        return answer, sources
    except Exception as e:
        user_friendly_error = instance._get_user_friendly_error(e)
        logger.error(user_friendly_error)
        return None, None
