import boto3
import time
from loguru import logger
import botocore.exceptions
import pandas as pd
import io
import os
import json
import sys
import contextlib


class PythonASTREPL:
    def __init__(self, dataframes=None, locals=None, globals=None):
        """Initialize the REPL with optional local and global namespaces and dataframes.

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
        try:
            with contextlib.redirect_stdout(buffer):
                try:
                    # Attempt to compile the code as an expression
                    compiled_code = compile(code, '<string>', 'eval')
                    result = eval(compiled_code, self.globals, self.locals)
                except SyntaxError:
                    # If it isn't an expression, compile it as a statement
                    compiled_code = compile(code, '<string>', 'exec')
                    exec(compiled_code, self.globals, self.locals)
                    result = None
        except Exception as e:
            # Capture any exceptions raised during execution
            return f"Error: {e}"

        # Retrieve the captured output from stdout
        output = buffer.getvalue().strip()

        # Determine what to return based on captured output and result
        if output and result is not None:
            return f"{output}\n{repr(result)}"
        elif output:
            return output
        elif result is not None:
            return repr(result)
        else:
            return "Executed Successfully"


class QueryCSV:
    def __init__(self, default_model_name='sonnet-3', aws_access_key_id=None,
                 aws_secret_access_key=None, region_name=None):
        self.region_name = region_name
        self.default_model_name = default_model_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.bedrock = self._get_bedrock_client()

    def _get_bedrock_client(self):
        try:
            if self.aws_access_key_id and self.aws_secret_access_key:
                logger.info("Using provided AWS credentials for authentication.")
                session = boto3.Session(
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key,
                    region_name=self.region_name
                )
                return session.client(service_name="bedrock-runtime")
            else:
                logger.info("No explicit credentials provided. Attempting to use default credentials.")
                return boto3.client(service_name="bedrock-runtime", region_name=self.region_name)
        except botocore.exceptions.NoCredentialsError:
            logger.error("No AWS credentials found. Please provide credentials or configure your environment.")
            raise ValueError(
                "AWS credentials are required. Please provide aws_access_key_id and aws_secret_access_key or configure your environment with AWS credentials.")
        except Exception as e:
            logger.error(f"Error setting up Bedrock client: {str(e)}")
            raise

    def model_invoke(self, query, dataframes, model_name=None, user_prompt=None, max_retries=15, initial_delay=2):
        if model_name is None:
            model_name = self.default_model_name
        model_id, _, _ = self._get_model_details(model_name)
        retries = 0
        while retries < max_retries:
            try:
                query_result = self._execute_query(query, dataframes, model_id, user_prompt)
                logger.info(f"query output: {query_result}")
                result = self._generate_answer(query, query_result, model_id, user_prompt)
                return result
            except self.bedrock.exceptions.ThrottlingException as e:
                retries += 1
                wait_time = initial_delay * (2 ** (retries - 1))  # Exponential backoff
                logger.warning(f"Service is being throttled. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            except Exception as e:
                user_friendly_error = self._get_user_friendly_error(e)
                logger.error(user_friendly_error)
                break
        return None

    def _execute_query(self, query, dataframes, model_id, user_prompt):
        system_message = """
        You are an senior python developer tasked with analyzing data in a pandas DataFrame and generate a correct python code for that. 
        - Your goal is to generate python code to get the answer questions about the data accurately. 
        - Just give output in python code only, Make sure, you don't write anything else than python code.
        - df will be given so please dont write `df = pd.read_csv('your_data.csv')`
        - Dont use print statement to return the output in the console, unless or until you want to convey some message.
        - Don't add unnecessary filters.
        - Keep it simple.
        - Strictly always gives correct python code, syntax should be always correct, please verify and then only give answer.
        - If you're unsure about something, say so and explain why.
        """

        df_info = {name: df.info(verbose=False, show_counts=False) for name, df in dataframes.items()}
        df_head = {name: df.head().to_string() for name, df in dataframes.items()}
        df_dtypes = {name: df.dtypes.to_string() for name, df in dataframes.items()}

        user_message = f"""I have multiple pandas DataFrames with the following information:
               {df_info}
               Here are the first few rows of the DataFrames:
               {df_head}
               And here are the data types of the columns:
               {df_dtypes}
               My question is: {query}
               Please provide a python code for a given DataFrames to generate the answer for the question asked, without including any explanation.
               """

        prompt = user_prompt if user_prompt else f""" SYSTEM: {system_message} USER: {user_message} """

        messages = [
            {"role": "user", "content": [{"type": "text", "text": prompt}]}
        ]

        response = self.bedrock.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "messages": messages,
                "temperature": 0,
                "max_tokens": 4096,
                "anthropic_version": "bedrock-2023-05-31"
            })
        )

        response_body = json.loads(response['body'].read())
        assistant_message = response_body['content'][0]['text']
        logger.info(f"assistant_message: {assistant_message}")

        python_repl = PythonASTREPL(dataframes=dataframes)
        answer = python_repl.run(assistant_message)

        return answer

    def _generate_answer(self, query, query_result, model_id, user_prompt):
        system_message = """
            - You are given an <Answer> and a user <Query>. Answer the query by using the <Answer>, assuming that in the provided <Answer> are the answers to the <Query>.
            - Do not include any of the reasoning
        """

        user_message = f"""
        Answer: {query_result}
        Query: {query}
        
        So the Context is the Answer for the Query user asked, but now you have to give answer in proper sentence.
        """

        prompt = user_prompt if user_prompt else f""" SYSTEM: {system_message} USER: {user_message} """

        messages = [
            {"role": "user", "content": [{"type": "text", "text": prompt}]}
        ]

        response = self.bedrock.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "messages": messages,
                "temperature": 0,
                "max_tokens": 4096,
                "anthropic_version": "bedrock-2023-05-31"
            })
        )

        response_body = json.loads(response['body'].read())
        answer = response_body['content'][0]['text']
        # logger.info(f"Final answer: {answer}")

        return answer

    def _get_model_details(self, model_name):
        if model_name.lower() == "sonnet-3.5":
            model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
            input_cost = 0.003
            output_cost = 0.015
        elif model_name.lower() == "sonnet-3":
            model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
            input_cost = 0.003
            output_cost = 0.015
        elif model_name.lower() == "haiku-3.0":
            model_id = "anthropic.claude-3-haiku-20240307-v1:0"
            input_cost = 0.00025
            output_cost = 0.00125
        else:
            logger.error(f"Unrecognized model name: {model_name}")
            raise ValueError(f"Unrecognized model name: {model_name}")

        logger.info(f"Using model: {model_id}")
        return model_id, input_cost, output_cost

    def query_from_local_paths(self, user_query, csv_file_paths, model_name=None, user_prompt=None):
        dataframes = {}
        try:
            for name, path in csv_file_paths.items():
                df = pd.read_csv(str(path))
                dataframes[name] = df
        except Exception as e:
            user_friendly_error = self._get_user_friendly_error(e)
            logger.error(user_friendly_error)
            raise ValueError(user_friendly_error)
        return self.model_invoke(user_query, dataframes, model_name, user_prompt)

    def query_from_s3_paths(self, user_query, s3_file_paths, model_name=None, user_prompt=None):
        s3 = boto3.client('s3')
        dataframes = {}
        for name, s3_file_path in s3_file_paths.items():
            bucket_name, key_name = self._parse_s3_path(s3_file_path)
            try:
                logger.info(f"Fetching file from S3: {s3_file_path}")
                response = s3.get_object(Bucket=bucket_name, Key=key_name)
                content_type = response['ContentType']
                body = response['Body'].read()
                _, file_extension = os.path.splitext(key_name)
                if content_type == 'text/csv' or file_extension.lower() == '.csv':
                    dataframes[name] = pd.read_csv(io.StringIO(body.decode('utf-8')))
                else:
                    logger.error(f"Unsupported content type: {content_type}. Expected 'text/csv'.")
                    raise ValueError(f"Unsupported content type: {content_type}. Expected 'text/csv'.")
            except s3.exceptions.NoSuchKey:
                logger.error(f"The file {s3_file_path} does not exist in the S3 bucket. Please check the S3 file path.")
                raise ValueError(
                    f"The file {s3_file_path} does not exist in the S3 bucket. Please check the S3 file path.")
            except s3.exceptions.NoSuchBucket:
                logger.error(f"The S3 bucket does not exist. Please check the bucket name in the S3 file path.")
                raise ValueError(f"The S3 bucket does not exist. Please check the bucket name in the S3 file path.")
            except Exception as e:
                user_friendly_error = self._get_user_friendly_error(e)
                logger.error(user_friendly_error)
                raise ValueError(user_friendly_error)
        return self.model_invoke(user_query, dataframes, model_name, user_prompt)

    def _parse_s3_path(self, s3_file_path):
        if not s3_file_path.startswith('s3://'):
            logger.error("S3 path should start with 's3://'. Please check the S3 file path.")
            raise ValueError("S3 path should start with 's3://'. Please check the S3 file path.")
        parts = s3_file_path[5:].split('/', 1)
        if len(parts) != 2:
            logger.error("Invalid S3 path format. It should be 's3://bucket_name/key_name'.")
            raise ValueError("Invalid S3 path format. It should be 's3://bucket_name/key_name'.")
        return parts[0], parts[1]

    def _get_user_friendly_error(self, error):
        # Customize user-friendly error messages here
        if isinstance(error, ValueError):
            return str(error)
        elif isinstance(error, botocore.exceptions.BotoCoreError):
            return "An error occurred with the AWS service. Please check your AWS resources and permissions."
        else:
            return f"An unexpected error occurred: {str(error)}."