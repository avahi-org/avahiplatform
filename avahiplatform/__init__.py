from .main import AvahiPlatform

# Initialize the platform instance
avahi_platform = AvahiPlatform()

# Expose the functionalities
summarize = avahi_platform.summarize
structredExtraction = avahi_platform.structredExtraction
DataMasking = avahi_platform.DataMasking
nl2sql = avahi_platform.nl2sql
imageGeneration = avahi_platform.imageGeneration
pdfsummarizer = avahi_platform.pdfsummarizer
grammarAssistant = avahi_platform.grammarAssistant
productDescriptionAssistant = avahi_platform.productDescriptionAssistant
perform_semantic_search = avahi_platform.perform_semantic_search
perform_rag_with_sources = avahi_platform.perform_rag_with_sources
query_csv = avahi_platform.query_csv
medicalscribing = avahi_platform.medicalscribing
icdcoding = avahi_platform.icdcoding