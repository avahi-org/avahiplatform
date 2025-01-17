import boto3
import os
import json
import uuid
from typing import Any, List, Tuple
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
import botocore.exceptions
import re
from urllib.parse import urlparse
from io import BytesIO
import pymupdf
import docx


class CustomS3Loader:
    def __init__(self, s3_path: str):
        """
        Initializes the loader with S3 path.

        :param s3_path: S3 path to the directory or prefix.
        """
        self.s3_path = s3_path
        self.bucket_name, self.prefix = self._parse_s3_path(s3_path)
        self.s3_client = boto3.client('s3')

    @staticmethod
    def _parse_s3_path(s3_path: str) -> Tuple[str, str]:
        """
        Parses the S3 path to extract bucket name and prefix.

        :param s3_path: Full S3 path (s3://bucket-name/prefix/...).
        :return: Tuple containing the bucket name and the prefix.
        """
        parsed_url = urlparse(s3_path)
        bucket_name = parsed_url.netloc
        prefix = parsed_url.path.lstrip('/')
        return bucket_name, prefix

    def list_files(self) -> List[str]:
        """
        Lists files in the specified S3 path.

        :return: List of file keys in the S3 bucket.
        """
        response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=self.prefix)
        files = [content['Key'] for content in response.get('Contents', []) if not content['Key'].endswith('/')]
        return files

    def fetch_file(self, s3_key: str) -> str:
        """
        Fetches a file from S3 and extracts its text content.

        :param s3_key: S3 key of the file to fetch.
        :return: Text content of the file.
        """
        _, file_extension = os.path.splitext(self.prefix)
        response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
        content_type = response['ContentType']
        body = response['Body'].read()
        if 'application/pdf' in content_type or file_extension == ".pdf":
            text = self._read_pdf_from_stream(BytesIO(body))
        elif 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type or file_extension == ".docx":
            text = self._read_docx(BytesIO(body))
        else:
            text = body.decode('utf-8')
        return text

    def _read_pdf_from_stream(self, file_obj: BytesIO) -> str:
        """
        Reads PDF content from an in-memory file object.

        :param file_obj: In-memory file object.
        :return: Extracted text content.
        """
        doc = pymupdf.open(stream=file_obj, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text

    def _read_docx(self, file_obj: BytesIO) -> str:
        """
        Reads DOCX content from an in-memory file object.

        :param file_obj: In-memory file object.
        :return: Extracted text content.
        """
        doc = docx.Document(file_obj)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])

    def load(self) -> List[dict]:
        """
        Loads the documents from the S3 bucket into a list of raw text.

        :return: List of raw text documents.
        """
        documents = []
        files = self.list_files()
        for s3_key in files:
            try:
                text = self.fetch_file(s3_key)
                text_splitter = RecursiveTextSplitter(chunk_size=2000, chunk_overlap=200)
                split_texts = text_splitter.split_text(text)
                for chunk_number, split_text in enumerate(split_texts):
                    doc_with_metadata = {'page_content': split_text,
                                         'metadata': {"source": s3_key, "chunk_number": chunk_number}}
                    documents.append(doc_with_metadata)
            except Exception as e:
                print(f"Failed to fetch or process file {s3_key}: {e}")
        return documents


class RecursiveTextSplitter:
    def __init__(self, chunk_size: int, chunk_overlap: int):
        """
        Initializes the text splitter with chunk size and overlap.

        :param chunk_size: The size of each chunk.
        :param chunk_overlap: The number of overlapping characters between chunks.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        """
        Splits the given text into chunks of specified size with overlap.

        :param text: The text to split.
        :return: List of text chunks.
        """
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            chunks.append(text[start:end])
            start += (self.chunk_size - self.chunk_overlap)

            # Prevent infinite loops in case chunk_size <= chunk_overlap
            if start >= end:
                break

        return chunks

    def split_documents(self, documents: List[str]) -> List[str]:
        """
        Splits a list of documents into chunks of specified size with overlap.

        :param documents: List of documents to split.
        :return: List of text chunks.
        """
        split_documents = []
        for document in documents:
            split_documents.extend(self.split_text(document))
        return split_documents


class AmazonBedrockEmbeddingFunction(EmbeddingFunction[Documents]):
    def __init__(
            self,
            session: "boto3.Session",
            model_name: str = "amazon.titan-embed-text-v1",
            **kwargs: Any,
    ):
        self._model_name = model_name
        self._client = session.client(
            service_name="bedrock-runtime",
            **kwargs,
        )

    def __call__(self, input: Documents) -> Embeddings:
        accept = 'application/json'
        content_type = 'application/json'
        embeddings = []
        for text in input:
            input_body = {"texts": [text], "input_type": "search_document"}
            body = json.dumps(input_body)
            response = self._client.invoke_model(
                body=body,
                modelId=self._model_name,
                accept=accept,
                contentType=content_type,
            )
            embedding = json.loads(response.get("body").read()).get("embeddings")
            embeddings.append(embedding[0])
        return embeddings


class RAGSemanticSearch:
    def __init__(self, s3_path: str, aws_access_key_id: str = None, aws_secret_access_key: str = None,
                 region_name: str = 'us-east-1'):
        self.s3_path = s3_path
        self.session = self._create_session(aws_access_key_id, aws_secret_access_key, region_name)
        self.bedrock_client = self.session.client(service_name="bedrock-runtime")
        self.docs = self._load_and_process_documents()
        self.collection_name = self._get_collection_name()
        self.persistent_client = self._create_and_populate_collection()
        self.db = self._create_chroma_db()

    def _parse_s3_path(self, s3_path: str) -> Tuple[str, str]:
        """
        Parses the S3 path to extract bucket name and prefix.

        :param s3_path: Full S3 path (s3://bucket-name/prefix/...).
        :return: Tuple containing the bucket name and the prefix.
        """
        parsed_url = urlparse(s3_path)
        bucket_name = parsed_url.netloc
        prefix = parsed_url.path.lstrip('/')
        return bucket_name, prefix

    def _get_collection_name(self) -> str:
        # Extract bucket name from S3 path
        bucket_name = self._parse_s3_path(self.s3_path)[0]
        # Clean the bucket name
        cleaned_name = self._clean_bucket_name(bucket_name)
        return f"collection_{cleaned_name}"

    def _clean_bucket_name(self, bucket_name: str) -> str:
        # Remove any non-alphanumeric characters and replace with underscores
        cleaned = re.sub(r'[^a-zA-Z0-9]', '_', bucket_name)
        # Ensure the name starts with a letter
        if not cleaned[0].isalpha():
            cleaned = 'b_' + cleaned
        # Truncate if longer than 63 characters (Chroma's limit)
        return cleaned[:63]

    def _create_session(self, aws_access_key_id: str = None, aws_secret_access_key: str = None,
                        region_name: str = 'us-east-1') -> boto3.Session:
        if aws_access_key_id and aws_secret_access_key:
            return boto3.Session(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region_name
            )
        else:
            return boto3.Session(region_name=region_name)

    def _load_and_process_documents(self) -> List:
        loader = CustomS3Loader(self.s3_path)
        documents = loader.load()
        return documents

    def _create_and_populate_collection(self) -> chromadb.PersistentClient:
        ef = AmazonBedrockEmbeddingFunction(session=self.session, model_name="cohere.embed-english-v3")
        persistent_client = chromadb.PersistentClient()
        collection = persistent_client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
            embedding_function=ef
        )

        for doc in self.docs:
            collection.add(
                ids=[str(uuid.uuid1())], metadatas=doc["metadata"], documents=doc["page_content"]
            )

        return persistent_client

    def _create_chroma_db(self):
        bedrock_embeddings = AmazonBedrockEmbeddingFunction(session=self.session, model_name="cohere.embed-english-v3")
        collection = self.persistent_client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
            embedding_function=bedrock_embeddings
        )
        return collection

    def get_similar_docs(self, query: str, k: int = 5) -> list[dict[str, Any]]:
        results = self.db.query(
            query_texts=[query],
            n_results=k
        )
        # Extract the first list of documents and distances
        documents = results['documents']
        metadatas = results['metadatas']
        distances = results['distances']

        # Combine document information with distances
        combined_results = [
            {'metadata': md, 'page_content': doc, "distance": distance}
            for doc, md, distance in zip(documents[0], metadatas[0], distances[0])
        ]

        return combined_results

    def model_invoke(self, prompt: str) -> str:
        body = json.dumps({
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}],
                }
            ],
            "max_tokens": 2000,
            "top_p": 0.2,
            "temperature": 0,
            "anthropic_version": "bedrock-2023-05-31"
        })

        modelId = "anthropic.claude-3-sonnet-20240229-v1:0"
        accept = "application/json"
        contentType = "application/json"

        response = self.bedrock_client.invoke_model(
            body=body,
            modelId=modelId,
            accept=accept,
            contentType=contentType
        )
        return json.loads(response.get('body').read())['content'][0]['text']

    def get_answer(self, question: str, context: str) -> str:
        prompt_template = f"""You are a helpful assistant that answers questions directly and only using the information provided in the context below.
        Guidance for answers:
            - Always use English as the language in your responses.
            - In your answers, always use a professional tone.
            - If the context does not contain the answer, say "answer not found."

        Now read this context below and answer the question at the bottom.

        ***Context: 
        {context}

        ***Question: 
        {question}

        ***INSTRUCTIONS***
        Answer the users QUESTION ONLY using the DOCUMENT Context text above.
        Keep your answer ground in the facts of the DOCUMENT Context.
        If the DOCUMENT Context doesn't contain the facts to answer the QUESTION return in 3 words- 'answer not found'

        Assistant:"""

        return self.model_invoke(prompt_template)

    def semantic_search(self, question: str) -> list[dict[str, Any]]:
        return self.get_similar_docs(question, k=5)

    def rag_with_sources(self, question: str) -> Tuple[str, List[str]]:
        similar_docs = self.semantic_search(question)
        context = "\n\n".join([doc["page_content"] for doc in similar_docs])

        answer = self.get_answer(question, context)
        sources = [doc["metadata"]['source'] for doc in similar_docs]
        sources = list(set(sources))

        return answer, sources

    def _get_user_friendly_error(self, error):
        if isinstance(error, ValueError):
            return str(error)
        elif isinstance(error, botocore.exceptions.BotoCoreError):
            return "An error occurred with the AWS service. Please check your AWS resources and permissions."
        else:
            return f"An unexpected error occurred: {str(error)}."