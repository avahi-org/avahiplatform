from .platform_core import AvahiPlatform

# Initialize with default settings
_platform_instance = None

def configure(
    aws_access_key_id=None,
    aws_secret_access_key=None,
    aws_session_token=None,
    region_name=None,
    input_tokens_price=None,
    output_tokens_price=None,
    max_tokens=512,
    temperature=0.6,
    p=0.5,
    input_bucket_name_for_medical_scribing="",
    iam_arn_for_medical_scribing="",
    default_model_name='anthropic.claude-3-sonnet-20240229-v1:0'
):
    """
    Configure the AvahiPlatform with custom settings.
    Must be called before using any platform functionalities.
    """
    global _platform_instance
    _platform_instance = AvahiPlatform(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
        region_name=region_name,
        input_tokens_price=input_tokens_price,
        output_tokens_price=output_tokens_price,
        max_tokens=max_tokens,
        temperature=temperature,
        p=p,
        input_bucket_name_for_medical_scribing=input_bucket_name_for_medical_scribing,
        iam_arn_for_medical_scribing=iam_arn_for_medical_scribing,
        default_model_name=default_model_name
    )
    _init_platform_exports()

def _init_platform_exports():
    """Initialize all platform exports with the configured instance."""
    global summarize_text, summarize_document, summarize_image, summarize_s3_document, summarize_video
    global structuredExtraction, mask_data, grammar_assistant, product_description_assistant, generate_image, get_similar_images
    global nl2sql, query_csv, medicalscribing, generate_icdcode, chatbot, initialize_observability
    global _platform_instance  

    if _platform_instance is None:
        _platform_instance = AvahiPlatform()  # Initialize with defaults if not configured

    # Expose the functionalities
    summarize_text = _platform_instance.summarize_text
    summarize_document = _platform_instance.summarize_document
    summarize_image = _platform_instance.summarize_image
    summarize_s3_document = _platform_instance.summarize_s3_document
    summarize_video = _platform_instance.summarize_video

    # Core functionalities
    structuredExtraction = _platform_instance.extract_structures
    mask_data = _platform_instance.mask_data
    grammar_assistant = _platform_instance.grammar_assistant
    product_description_assistant = _platform_instance.product_description_assistant

    # AI Services
    nl2sql = _platform_instance.nl2sql
    generate_image = _platform_instance.image_generation
    get_similar_images = _platform_instance.get_similar_images

    # imageGeneration = _platform_instance.imageGeneration
    # perform_semantic_search = _platform_instance.perform_semantic_search
    # perform_rag_with_sources = _platform_instance.perform_rag_with_sources
    # imageSimilarity = _platform_instance.imageSimilarity

    # Healthcare Services
    query_csv = _platform_instance.query_csv
    medicalscribing = _platform_instance.medicalscribing
    generate_icdcode = _platform_instance.generate_icdcode

    # Chat and Observability
    chatbot = _platform_instance.chatbot
    initialize_observability = _platform_instance.initialize_observability

# Initialize with default settings
_init_platform_exports()