import boto3
import time
from loguru import logger
import botocore.exceptions
import langchain
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.chat_models import BedrockChat
from langchain.agents.agent_types import AgentType
from langchain.prompts.chat import ChatPromptTemplate


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
        llm = BedrockChat(model_id=model_id, client=self.bedrock, model_kwargs={"temperature": 0})
        db = SQLDatabase.from_uri(db_uri)

        agent_executor = create_sql_agent(llm, db=db, agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                                          verbose=False,
                                          max_execution_time=420, max_iterations=100)
        langchain.debug = False

        if user_prompt:
            final_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", user_prompt
                     ),
                    ("user", f"{nl_query}\n ai: "),
                ]
            )
        else:
            final_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system",
                     f"""
                      You are a helpful assistant. Your task is to answer User Queries precisely by generating an appropriate {db_type} query, executing it on the database, and then formatting the results.
                        ***NEVER START ANSWER WITH 'Based on the query results or like that way, it should look like human answer not robotic answer'.
                     """
                     ),
                    ("user", f"{nl_query}\n ai: "),
                ]
            )
        retries = 0
        while retries < max_retries:
            try:
                result = agent_executor.invoke(final_prompt)["output"]
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
                           port=None, dbname=None, db_path=None, model_name=None, user_prompt=None,
                           ):

        if db_type == "sqlite":
            if not db_path:
                raise ValueError("For SQLite, db_path must be provided")
            db_uri = f"sqlite:///{db_path}"
        if not (username and password and host and port and dbname):
            logger.error(f"Missing required parameters for {db_type} database connection")
            raise ValueError(f"Missing required parameters for {db_type} database connection")

        if db_type == "postgresql":
            db_uri = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{dbname}"
        elif db_type == "mysql":
            db_uri = f"mysql+pymysql://{username}:{password}@{host}:{port}/{dbname}"
        else:
            logger.error(f"{db_type} cannot be connect")
            raise ValueError(f"{db_type} cannot be connect")

        return self.model_invoke(nl_query, db_type, db_uri, user_prompt, model_name)

    def _get_user_friendly_error(self, error):
        # Customize user-friendly error messages here
        if isinstance(error, ValueError):
            return str(error)
        elif isinstance(error, botocore.exceptions.BotoCoreError):
            return "An error occurred with the AWS service. Please check your AWS resources and permissions."
        else:
            return f"An unexpected error occurred: {str(error)}."
