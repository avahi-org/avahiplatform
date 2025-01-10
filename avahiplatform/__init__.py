# from .main import summarize, structredExtraction, DataMasking, nl2sql, imageGeneration, pdfsummarizer, grammarAssistant, productDescriptionAssistant, perform_semantic_search, perform_rag_with_sources, query_csv, medicalscribing, icdcoding
# from . import helpers
# from .main import AvahiPlatform

# Initialize the platform instance
# avahi_platform = AvahiPlatform()

# # Expose the functionalities
# summarize = avahi_platform.
# structredExtraction = avahi_platform.structredExtraction
# DataMasking = avahi_platform.DataMasking
# nl2sql = avahi_platform.nl2sql
# imageGeneration = avahi_platform.imageGeneration
# pdfsummarizer = avahi_platform.pdfsummarizer
# grammarAssistant = avahi_platform.grammarAssistant
# productDescriptionAssistant = avahi_platform.productDescriptionAssistant
# perform_semantic_search = avahi_platform.perform_semantic_search
# perform_rag_with_sources = avahi_platform.perform_rag_with_sources
# query_csv = avahi_platform.query_csv
# medicalscribing = avahi_platform.medicalscribing
# icdcoding = avahi_platform.icdcoding
# chatbot = avahi_platform.chatbot
# initialize_observability = avahi_platform.initialize_observability
# imageSimilarity = avahi_platform.imageSimilarity

from .platform_core import AvahiPlatform

# Initialize the platform instance
avahi_platform = AvahiPlatform()

# Expose the functionalities
summarize_text = avahi_platform.summarize_text
summarize_document = avahi_platform.summarize_document
summarize_image = avahi_platform.summarize_image
summarize_s3_document = avahi_platform.summarize_s3_document

# Core functionalities
structredExtraction = avahi_platform.structredExtraction
mask_data = avahi_platform.mask_data
grammar_assistant = avahi_platform.grammar_assistant
product_description_assistant = avahi_platform.product_description_assistant

# AI Services
nl2sql = avahi_platform.nl2sql
imageGeneration = avahi_platform.imageGeneration
perform_semantic_search = avahi_platform.perform_semantic_search
perform_rag_with_sources = avahi_platform.perform_rag_with_sources
imageSimilarity = avahi_platform.imageSimilarity

# Healthcare Services
query_csv = avahi_platform.query_csv
medicalscribing = avahi_platform.medicalscribing
generate_icdcode = avahi_platform.generate_icdcode

# Chat and Observability
chatbot = avahi_platform.chatbot
initialize_observability = avahi_platform.initialize_observability