# !pip install -U langchain-openai
# !pip install avahiplatform


import time
import statistics
from loguru import logger
import avahiplatform as ap
import os

# Import LangChain components
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.agents import load_tools, initialize_agent, AgentType

# Function to get OpenAI API key
os.environ["OPENAI_API_KEY"] = "<KEY>"


def get_openai_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        api_key = input("Please enter your OpenAI API key: ").strip()
        os.environ["OPENAI_API_KEY"] = api_key
    return api_key


# Initialize OpenAI LLM
try:
    api_key = get_openai_api_key()
    llm = OpenAI(temperature=0, openai_api_key=api_key)
except Exception as e:
    logger.error(f"Error initializing OpenAI LLM: {str(e)}")
    logger.warning("LangChain features will be skipped in the latency test.")
    llm = None

# Initialize OpenAI LLM (you'll need to set your OpenAI API key)
# llm = OpenAI(temperature=0)


# List of functions to test
functions_to_test = {
    # Avahi Platform functions
    "ap_summarize": ap.summarize,
    "ap_structredExtraction": ap.structredExtraction,
    "ap_DataMasking": ap.DataMasking,
    "ap_nl2sql": ap.nl2sql,
    "ap_pdfsummarizer": ap.pdfsummarizer,
    "ap_grammarAssistant": ap.grammarAssistant,
    "ap_productDescriptionAssistant": ap.productDescriptionAssistant,
    "ap_imageGeneration": ap.imageGeneration,
    "ap_icdcoding": ap.icdcoding,
    "ap_query_csv": ap.query_csv,
    "ap_medicalscribing": ap.medicalscribing,
    "ap_perform_semantic_search": ap.perform_semantic_search,
    "ap_perform_rag_with_sources": ap.perform_rag_with_sources,

    # LangChain functions
    "lc_llm_chain": lambda x: LLMChain(llm=llm, prompt=PromptTemplate(input_variables=["text"],
                                                                      template="Summarize the following text: {text}")),
    "lc_sequential_chain": lambda: SimpleSequentialChain(chains=[
        LLMChain(llm=llm, prompt=PromptTemplate(input_variables=["text"], template="Summarize: {text}")),
        LLMChain(llm=llm, prompt=PromptTemplate(input_variables=["text"], template="Translate to French: {text}"))
    ]),
    "lc_embeddings": lambda: OpenAIEmbeddings(),
    "lc_vectorstore": lambda: FAISS.from_texts(["Hello world", "Bye bye", "Hello nice world"], OpenAIEmbeddings()),
    "lc_text_splitter": lambda: CharacterTextSplitter(chunk_size=1000, chunk_overlap=0),
    "lc_document_loader": lambda: TextLoader("sample.txt"),
    "lc_agent": lambda: initialize_agent(load_tools(["wikipedia", "llm-math"], llm=llm), llm,
                                         agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
}

# Sample inputs for each function
sample_inputs = {
    "ap_summarize": ("This is a sample text to summarize.",),
    "ap_structredExtraction": ("Extract entities from this text.",),
    "ap_DataMasking": ("This is sensitive data to mask.",),
    "ap_nl2sql": ("Get all users", "sqlite", "user", "pass", "localhost", "5432", "test_db"),
    # "ap_pdfsummarizer": ("/path/to/sample.pdf",),
    "ap_grammarAssistant": ("This sentence has grammer mistakes.",),
    "ap_productDescriptionAssistant": ("SKU123", "Summer Sale", "Young Adults"),
    "ap_imageGeneration": ("A beautiful landscape",),
    "ap_icdcoding": ("Patient has a fever and cough.",),
    # "ap_query_csv": ("What's the total sales?", "/path/to/sales.csv"),
    # "ap_medicalscribing": ("/path/to/audio.mp3", "input-bucket", "iam-arn"),
    # "ap_perform_semantic_search": ("What is machine learning?", "s3://bucket/documents/"),
    # "ap_perform_rag_with_sources": ("Explain quantum computing", "s3://bucket/documents/"),

    "lc_llm_chain": ("This is a test sentence for the LLM chain.",),
    "lc_sequential_chain": ("This is a test sentence for the sequential chain.",),
    "lc_embeddings": ("This is a test sentence for embeddings.",),
    "lc_vectorstore": (),
    "lc_text_splitter": ("This is a very long text that needs to be split into smaller chunks for processing.",),
    "lc_document_loader": (),
    "lc_agent": ("What is the population of France raised to the power of 0.23?",)
}


def test_function_latency(func, args, num_runs=5):
    latencies = []
    for _ in range(num_runs):
        start_time = time.time()
        try:
            if callable(func):
                func(*args)
            else:
                func
        except Exception as e:
            logger.error(f"Error running {func.__name__}: {str(e)}")
        end_time = time.time()
        latencies.append(end_time - start_time)

    avg_latency = statistics.mean(latencies)
    std_dev = statistics.stdev(latencies) if len(latencies) > 1 else 0
    return avg_latency, std_dev


def run_latency_tests():
    results = []
    for func_name, func in functions_to_test.items():
        args = sample_inputs.get(func_name, ())

        logger.info(f"Testing {func_name}...")
        avg_latency, std_dev = test_function_latency(func, args)

        results.append({
            "function": func_name,
            "avg_latency": avg_latency,
            "std_dev": std_dev
        })

        logger.info(f"{func_name}: Avg Latency = {avg_latency:.4f}s, Std Dev = {std_dev:.4f}s")

    return results


if __name__ == "__main__":
    logger.info("Starting latency tests...")
    results = run_latency_tests()

    # Sort results by average latency
    sorted_results = sorted(results, key=lambda x: x["avg_latency"])

    logger.info("\nLatency Test Results (sorted by average latency):")
    for result in sorted_results:
        logger.info(
            f"{result['function']}: Avg Latency = {result['avg_latency']:.4f}s, Std Dev = {result['std_dev']:.4f}s")