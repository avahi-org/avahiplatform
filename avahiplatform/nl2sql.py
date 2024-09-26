import boto3
import time
from loguru import logger
import botocore.exceptions
import json
import sqlalchemy
from sqlalchemy import create_engine, text


class BedrockNL2SQL:
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

    def model_invoke(self, nl_query, db_type, db_uri, user_prompt, model_name=None, max_retries=15, initial_delay=2):
        if model_name is None:
            model_name = self.default_model_name

        model_id, _, _ = self._get_model_details(model_name)

        engine = create_engine(db_uri)
        metadata = sqlalchemy.MetaData()
        metadata.reflect(bind=engine)

        table_info = self._get_table_info(metadata)

        system_prompt = user_prompt if user_prompt else f"""
        You are a helpful assistant. Your task is to answer User Queries precisely by generating an appropriate {db_type} query, executing it on the database, and then formatting the results.
        ***NEVER START ANSWER WITH 'Based on the query results or like that way, it should look like human answer not robotic answer'.

        Database schema:
        {table_info}

        Instructions:
        1. Analyze the user's question and the database schema.
        2. Generate a SQL query to answer the question.
        3. Execute the query and return the results.
        4. Provide a human-friendly interpretation of the results.

        If you need to execute a SQL query, use the following format:
        [SQL]
        Your SQL query here
        [/SQL]

        I will execute the query and provide you with the results.
        """

        prompt = f"""
        SYSTEM: {system_prompt}
        USER: {nl_query}
        """
        messages = [
            {"role": "user", "content": [{"type": "text", "text": prompt}]}
        ]

        retries = 0
        while retries < max_retries:
            try:
                response = self._invoke_bedrock(model_id, messages)
                assistant_message = response['content'][0]['text']

                # Check if the assistant's message contains a SQL query
                if '[SQL]' in assistant_message and '[/SQL]' in assistant_message:
                    sql_query = assistant_message.split('[SQL]')[1].split('[/SQL]')[0].strip()
                    # logger.info(f"")
                    query_results = self._execute_sql_query(engine, sql_query)

                    # Add the query results to the conversation
                    messages.append({"role": "assistant", "content": [{"type": "text", "text": assistant_message}]})
                    messages.append(
                        {"role": "user", "content": [{"type": "text", "text": f"Query results: {query_results}"}]})

                    # Get the final interpretation from the model
                    final_response = self._invoke_bedrock(model_id, messages)
                    return final_response['content'][0]['text']
                else:
                    return assistant_message

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

    def _get_table_info(self, metadata):
        table_info = []
        for table_name, table in metadata.tables.items():
            columns = [f"{col.name} ({col.type})" for col in table.columns]
            table_info.append(f"Table: {table_name}\nColumns: {', '.join(columns)}")
        return "\n\n".join(table_info)

    def _invoke_bedrock(self, model_id, messages):
        body = json.dumps({
            "messages": messages,
            "temperature": 0,
            "max_tokens": 4096,
            "anthropic_version": "bedrock-2023-05-31"
        })
        accept = "application/json"
        content_type = "application/json"
        response = self.bedrock.invoke_model(body=body, modelId=model_id, accept=accept,
                                             contentType=content_type)
        return json.loads(response['body'].read())

    def _execute_sql_query(self, engine, query):
        with engine.connect() as connection:
            result = connection.execute(text(query))
            return [row for row in result]

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

    def get_answer_from_db(self, db_type, nl_query, username=None, password=None, host=None,
                           port=None, dbname=None, db_path=None, model_name=None, user_prompt=None):

        if db_type == "sqlite":
            if not db_path:
                raise ValueError("For SQLite, db_path must be provided")
            db_uri = f"sqlite:///{db_path}"
        elif db_type in ["postgresql", "mysql"]:
            if not (username and password and host and port and dbname):
                logger.error(f"Missing required parameters for {db_type} database connection")
                raise ValueError(f"Missing required parameters for {db_type} database connection")

            if db_type == "postgresql":
                db_uri = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{dbname}"
            else:  # mysql
                db_uri = f"mysql+pymysql://{username}:{password}@{host}:{port}/{dbname}"
        else:
            logger.error(f"{db_type} cannot be connected")
            raise ValueError(f"{db_type} cannot be connected")

        return self.model_invoke(nl_query, db_type, db_uri, user_prompt, model_name)

    def _get_user_friendly_error(self, error):
        # Customize user-friendly error messages here
        if isinstance(error, ValueError):
            return str(error)
        elif isinstance(error, botocore.exceptions.BotoCoreError):
            return "An error occurred with the AWS service. Please check your AWS resources and permissions."
        else:
            return f"An unexpected error occurred: {str(error)}."
