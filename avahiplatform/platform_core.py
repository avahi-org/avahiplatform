from avahiplatform.helpers import (
    BedrockChat,
    BotoHelper,
    S3Helper,
    Utils
)
from avahiplatform.src import (
    FunctionWrapper,
    track_observability,
    Observability,
    BedrockSummarizer,
    BedrockStructuredExtraction,
    ProductDescriptionGeneration, 
    GrammarCorrection,
    DataMasking,
    BedrockChatbot,
    QueryCSV,
    ICDCodeGenerator,
    MedicalScribe,
    BedrockNL2SQL,
    ImageGeneration,
    BedrockImageSimilarity
)

import os
from loguru import logger


class AvahiPlatform:
    def __init__(self, 
                 aws_access_key_id=None, 
                 aws_secret_access_key=None,
                 aws_session_token=None,
                 region_name=None,
                 input_tokens_price=None,
                 output_tokens_price=None,
                 input_bucket_name_for_medical_scribing="",
                 iam_arn_for_medical_scribing="",
                 default_model_name='anthropic.claude-3-sonnet-20240229-v1:0'):

        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_session_token = aws_session_token
        self.region_name = region_name

        self.input_tokens_price = input_tokens_price
        self.output_tokens_price = output_tokens_price

        self.default_model_name = default_model_name

        # Initialize boto helper
        self.boto_helper = BotoHelper(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_session_token=self.aws_session_token,
            region_name=self.region_name
        )

        self.s3_helper = S3Helper(
            s3_client=self.boto_helper.create_client(service_name="s3")
        )

        self.observability = Observability()

        # Initialize BedrockChat
        self.bedrockchat = BedrockChat(
            model_id=self.default_model_name,
            boto_helper=self.boto_helper,
            input_tokens_price=self.input_tokens_price,
            output_tokens_price=self.output_tokens_price
        )

        self.summarizer = BedrockSummarizer(
            bedrockchat=self.bedrockchat
        )

        self.structuredExtraction = BedrockStructuredExtraction(
            bedrockchat=self.bedrockchat
        )

        self.productDescriptionAssistant = ProductDescriptionGeneration(
            bedrockchat=self.bedrockchat
        )

        self.grammarAssistant = GrammarCorrection(
            bedrockchat=self.bedrockchat
        )

        self.dataMasking = DataMasking(
            bedrockchat=self.bedrockchat
        )

        self.chatbot = BedrockChatbot(
            bedrockchat=self.bedrockchat
        )

        self.csv_querying = QueryCSV(
            bedrockchat=self.bedrockchat,
            s3_helper=self.s3_helper
        )

        self.icd_code_generator = ICDCodeGenerator(
            bedrock_helper=self.boto_helper,
            s3_helper=self.s3_helper
        )

        self.medical_scribing = MedicalScribe(
            boto_helper=self.boto_helper,
            s3_helper=self.s3_helper,
            input_bucket_name=input_bucket_name_for_medical_scribing,
            iam_arn=iam_arn_for_medical_scribing,
            region_name=self.region_name
        )

        self.natural_language_to_sql = BedrockNL2SQL(
            bedrockchat=self.bedrockchat
        )

        self.imageGeneration = ImageGeneration(
            boto_helper=self.boto_helper,
            default_model_id=self.default_model_name
        )

        self.imageSimilarity = BedrockImageSimilarity(
            boto_helper=self.boto_helper,
            s3_helper=self.s3_helper,
            default_model_id=self.default_model_name
        )

        # Initialize observability

        # Wrapper functions with observability tracking
        @track_observability
        def summarize_text_with_tracking(*args, **kwargs):
            return self.summarizer.summarize_text(*args, **kwargs)

        @track_observability
        def summarize_document_with_tracking(*args, **kwargs):
            return self.summarizer.summarize_document(*args, **kwargs)

        @track_observability
        def summarize_image_with_tracking(*args, **kwargs):
            return self.summarizer.summarize_image(*args, **kwargs)

        @track_observability
        def summarize_video_with_tracking(*args, **kwargs):
            return self.summarizer.summarize_video(*args, **kwargs)

        @track_observability
        def summarize_s3_document_with_tracking(*args, **kwargs):
            return self.summarizer.summarize_s3_document(*args, **kwargs)

        self.summarize_text = FunctionWrapper(summarize_text_with_tracking)
        self.summarize_document = FunctionWrapper(summarize_document_with_tracking)
        self.summarize_image = FunctionWrapper(summarize_image_with_tracking)
        self.summarize_video = FunctionWrapper(summarize_video_with_tracking)
        self.summarize_s3_document = FunctionWrapper(summarize_s3_document_with_tracking)

        self.medicalscribing = FunctionWrapper(self._medicalscribing)
        self.generate_icdcode = FunctionWrapper(self.icdcoding)
        self.query_csv = FunctionWrapper(self._query_csv)
        self.extract_structures = FunctionWrapper(self.structure_extraction)
        self.mask_data = FunctionWrapper(self.data_masking)
        self.grammar_assistant = FunctionWrapper(self.grammar_correction)
        self.product_description_assistant = FunctionWrapper(self.product_description)
        self.nl2sql = FunctionWrapper(self.nlquery2sql)
        self.get_similar_images = FunctionWrapper(self._imageSimilarity)


        self.image_generation = FunctionWrapper(self._imageGeneration)
        # self.pdfsummarizer = FunctionWrapper(pdfsummarizer)
        # self.perform_semantic_search = FunctionWrapper(perform_semantic_search)
        # self.perform_rag_with_sources = FunctionWrapper(perform_rag_with_sources)
        # self.imageSimilarity = imageSimilarity

        self.initialize_observability = self._initialize_observability

    @track_observability
    def icdcoding(self, input_content):
        try:
            if os.path.exists(input_content):  # Check if input is a local file path
                return self.icd_code_generator.generate_code_from_file(input_content)
            elif input_content.startswith('s3://'):  # Check if input is an S3 file path
                return self.icd_code_generator.generate_code_from_s3_file(input_content)
            else:  # Assume input is text
                return self.icd_code_generator.generate_icdcode(input_content)
        except Exception as e:
            user_friendly_error = Utils.get_user_friendly_error(e)
            logger.error(user_friendly_error)
            return "None"

    @track_observability
    def _medicalscribing(self, audio_filepath):
        try:
            if os.path.exists(audio_filepath):  # Check if input is a local file path
                return self.medical_scribing.fetch_medical_scribing_from_filepath(audio_filepath)
            elif audio_filepath.startswith('s3://'):  # Check if input is an S3 file path
                return self.medical_scribing.fetch_medical_scribing_from_s3_path(audio_filepath)
            else:
                raise ValueError(f"Audio file path is wrong please check that and try again")
        except Exception as e:
            user_friendly_error = Utils.get_user_friendly_error(e)
            logger.error(user_friendly_error)
            return None, None
    
    def _query_csv(self, user_query, csv_file_paths):

        if isinstance(csv_file_paths, str):
            logger.info("We received csv_file_paths as a string, processing into the dict")
            try:
                # Parse the input string as a dictionary
                csv_file_paths_dict = json.loads(csv_file_paths)
                csv_file_paths = csv_file_paths_dict
            except json.JSONDecodeError:
                logger.error("Invalid dictionary format! Please enter a valid JSON string.")
        
        # Separate file paths into local and S3 paths
        local_paths = {}
        s3_paths = {}

        for name, path in csv_file_paths.items():
            if os.path.exists(path):  # Check if input is a local file path
                local_paths[name] = path
            elif path.startswith('s3://'):  # Check if input is an S3 file path
                s3_paths[name] = path
            else:
                raise ValueError(f"Invalid CSV file path '{path}'. Please check and try again.")

        # Execute the queries
        try:
            if local_paths and not s3_paths:
                # If all paths are local
                return self.csv_querying.query_from_file(user_query, local_paths)
            elif s3_paths and not local_paths:
                # If all paths are in S3
                return self.csv_querying.query_from_s3(user_query, s3_paths)
            else:
                # Handle mixed local and S3 paths if needed
                raise ValueError(
                    "Cannot handle mixed local and S3 paths in one query. Please provide either only local paths or only S3 paths.")
        except Exception as e:
            user_friendly_error = Utils.get_user_friendly_error(e)
            logger.error(user_friendly_error)
            return "None"

    @track_observability
    def structure_extraction(self, input_content, system_prompt=None, stream=False):
        try:
            if os.path.exists(input_content):  # Check if input is a local file path
                return self.structuredExtraction.extract_document(input_content, system_prompt, stream)
            elif input_content.startswith('s3://'):  # Check if input is an S3 file path
                return self.structuredExtraction.extract_s3_document(input_content, system_prompt, stream)
            else:  # Assume input is text
                return self.structuredExtraction.extract_text(input_content, system_prompt, stream)
        except Exception as e:
            user_friendly_error = Utils.get_user_friendly_error(e)
            logger.error(user_friendly_error)
            return "None"

    @track_observability
    def data_masking(self, input_content, system_prompt=None, stream=False):
        try:
            if os.path.exists(input_content):  # Check if input is a local file path
                return self.dataMasking.mask_document(input_content, system_prompt, stream)
            elif input_content.startswith('s3://'):  # Check if input is an S3 file path
                return self.dataMasking.mask_s3_file(input_content, system_prompt, stream)
            else:  # Assume input is text
                return self.dataMasking.mask_text(input_content, system_prompt, stream)
        except Exception as e:
            user_friendly_error = Utils.get_user_friendly_error(e)
            logger.error(user_friendly_error)
            return "None"

    @track_observability
    def grammar_correction(self, input_content, system_prompt=None, stream=False):
        try:
            if os.path.exists(input_content):  # Check if input is a local file path
                return self.grammarAssistant.correct_document(input_content, system_prompt, stream)
            elif input_content.startswith('s3://'):  # Check if input is an S3 file path
                return self.grammarAssistant.correct_s3_document(input_content, system_prompt, stream)
            else:  # Assume input is text
                return self.grammarAssistant.correct_text(input_content, system_prompt, stream)
        except Exception as e:
            user_friendly_error = Utils.get_user_friendly_error(e)
            logger.error(user_friendly_error)
            return "None"
    
    @track_observability
    def product_description(self, product_sku, event_name, customer_segmentation, system_prompt=None, stream=False):
        try:
            return self.productDescriptionAssistant.generate_product_description(product_sku, event_name, customer_segmentation, system_prompt, stream)
        except Exception as e:
            user_friendly_error = Utils.get_user_friendly_error(e)
            logger.error(user_friendly_error)

    @track_observability
    def nlquery2sql(self, nl_query, db_type, username, password, host,
           port, dbname, db_path=None, user_prompt=None, stream=False):
        try:
            return self.natural_language_to_sql.get_answer_from_db(db_type, nl_query, username, password, host,
                           port, dbname, db_path, user_prompt, stream)
        except Exception as e:
            user_friendly_error = Utils.get_user_friendly_error(e)
            logger.error(user_friendly_error)
            return "None"

    @track_observability
    def _imageGeneration(self, image_prompt):
        try:
            return self.imageGeneration.generate_image(image_prompt)
        except Exception as e:
            user_friendly_error = Utils.get_user_friendly_error(e)
            logger.error(user_friendly_error)
            return "None"

    @track_observability
    def _imageSimilarity(self, image, other_file, k=10, embedding_length=256):
        try:
            if isinstance(other_file, str):
                if os.path.isfile(other_file) or (other_file.startswith("s3://") and mimetypes.guess_type(other_file)[0] is not None):
                    # Case where 'other' is a file (local or S3)
                    return self.imageSimilarity.image_to_image_similarity(
                        image=image,
                        other_image=other_file,
                        output_embedding_length=embedding_length,
                    )
                elif os.path.isdir(other_file):
                    # Case where 'other' is a folder (local or S3)
                    return self.imageSimilarity.image_to_folder_similarity(
                        image=image,
                        folder_path=other_file,
                        k=k,
                        output_embedding_length=embedding_length,
                    )
                elif (other_file.startswith("s3://") and (other_file.endswith("/") or mimetypes.guess_type(other_file)[0] is None)):
                    return self.imageSimilarity.image_to_s3_folder_similarity(
                        image=image,
                        s3_folder_path=other_file,
                        k=k,
                        output_embedding_length=embedding_length
                    )
                else:
                    raise ValueError("other is of an unrecognized type.")
            elif isinstance(other_file, Image.Image):
                # Case where 'other' is a single PIL Image
                return self.imageSimilarity.image_to_image_similarity(
                    image=image,
                    other_image=other_file,
                    output_embedding_length=embedding_length
                )
            elif isinstance(other_file, list) and all(isinstance(img, Image.Image) for img in other_file):
                # Case where 'other' is a list of PIL Images
                return self.imageSimilarity.image_to_pil_list_similarity(
                    image=image,
                    pil_image_list=other_file,
                    k=k,
                    output_embedding_length=embedding_length
                )
            else:
                raise ValueError("other is of an unrecognized type.")
        except Exception as e:
            user_friendly_error = Utils.get_user_friendly_error(e)
            logger.error(user_friendly_error)
            return None

    def _initialize_observability(self, metrics_file='metrics.jsonl', start_prometheus=False, prometheus_port=8000):
        """
        Initialize the observability system.

        :param metrics_file: Path to the file where metrics will be logged
        :param start_prometheus: Whether to start the Prometheus server
        :param prometheus_port: Port on which to start the Prometheus server
        """
        self.observability.initialize(metrics_file=metrics_file,
                                start_prometheus=start_prometheus,
                                prometheus_port=prometheus_port)