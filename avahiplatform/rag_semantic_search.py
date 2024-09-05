import boto3
from langchain_community.document_loaders import S3DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import json
import uuid
from typing import Any, List, Tuple
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from langchain_community.embeddings import BedrockEmbeddings
from langchain_chroma import Chroma
import botocore.exceptions
import re

from loguru import logger

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
            input_body = {"texts": [text], "input_type":"search_document"}
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
    def __init__(self, s3_path: str, aws_access_key_id: str = None, aws_secret_access_key: str = None, region_name: str = 'us-east-1'):
        self.s3_path = s3_path
        self.session = self._create_session(aws_access_key_id, aws_secret_access_key, region_name)
        self.bedrock_client = self.session.client(service_name="bedrock-runtime")
        self.docs = self._load_and_process_documents()
        self.collection_name = self._get_collection_name()
        self.persistent_client = self._create_and_populate_collection()
        self.db = self._create_chroma_db()

    def _get_collection_name(self) -> str:
        # Extract bucket name from S3 path
        bucket_name = self.s3_path.split('/')[0]
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

    def _create_session(self, aws_access_key_id: str = None, aws_secret_access_key: str = None, region_name: str = 'us-east-1') -> boto3.Session:
        if aws_access_key_id and aws_secret_access_key:
            return boto3.Session(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region_name
            )
        else:
            return boto3.Session(region_name=region_name)

    def _load_and_process_documents(self) -> List:
        loader = S3DirectoryLoader(self.s3_path)
        chunk_size = 2000
        chunk_overlap = 60
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        documents = loader.load()
        return text_splitter.split_documents(documents)

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
                ids=[str(uuid.uuid1())], metadatas=doc.metadata, documents=doc.page_content
            )
        
        return persistent_client

    def _create_chroma_db(self) -> Chroma:
        bedrock_embeddings = BedrockEmbeddings(model_id="cohere.embed-english-v3", client=self.bedrock_client)
        return Chroma(
            client=self.persistent_client,
            collection_name=self.collection_name,
            embedding_function=bedrock_embeddings,
        )

    def get_similar_docs(self, query: str, k: int = 5) -> List[Tuple]:
        return self.db.similarity_search_with_relevance_scores(query, k=k)

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

    def semantic_search(self, question: str) -> List[Tuple]:
        return self.get_similar_docs(question, k=5)

    def rag_with_sources(self, question: str) -> Tuple[str, List[str]]:
        similar_docs = self.semantic_search(question)
        context = "\n\n".join([doc[0].page_content for doc in similar_docs])
        
        answer = self.get_answer(question, context)
        sources = [doc[0].metadata['source'] for doc in similar_docs]

        return answer, sources
    
    def _get_user_friendly_error(self, error):
        if isinstance(error, ValueError):
            return str(error)
        elif isinstance(error, botocore.exceptions.BotoCoreError):
            return "An error occurred with the AWS service. Please check your AWS resources and permissions."
        else:
            return f"An unexpected error occurred: {str(error)}."