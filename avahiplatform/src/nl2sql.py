from loguru import logger
import sqlalchemy
from sqlalchemy import create_engine, text
from avahiplatform.helpers.chats.bedrock_chat import BedrockChat
from typing import Optional, Dict, Any


class BedrockNL2SQL:
    def __init__(self, bedrockchat: BedrockChat):
        """
        Initialize the BedrockSQLHandler with a BedrockChat instance.
        
        Args:
            bedrockchat: BedrockChat instance for making API calls
        """
        self.bedrockchat = bedrockchat

    def _create_prompt_list(self, nl_query: str, table_info: str, user_prompt: Optional[str] = None) -> list:
        """
        Creates a list of prompts for generating SQL from natural language using BedrockChat.
        
        Args:
            nl_query: The natural language query from the user
            table_info: Database schema information
            user_prompt: Optional custom system prompt
            
        Returns:
            list: List of prompts formatted for BedrockChat
        """
        system_prompt = user_prompt if user_prompt else f"""
        You are a senior data analyst with expertise in SQL.
        Your task is to generate a valid SQL query based on the user's question and the provided database schema.
        
        Database schema:
        {table_info}
        
        Instructions:
        1. Carefully analyze the user's question.
        2. Generate a valid SQL query that can be executed on the provided database schema.
        3. Return the query without explanation.
        
        If you're ready, return the query in the format:
        [SQL]
        Your SQL query here
        [/SQL]
        """
        return [{"text": f"System prompt: {system_prompt} \n User: {nl_query}"}]

    def handle_query(self, db_uri: str, nl_query: str, user_prompt: Optional[str] = None, stream: bool = False) -> Dict[str, Any]:
        """
        Handles a user query by generating SQL, executing it, and providing a human-readable interpretation.
        
        Args:
            db_uri: Database connection URI
            nl_query: The natural language query from the user
            user_prompt: Optional custom system prompt
            stream: Whether to stream the response
            
        Returns:
            dict: Final response with human-friendly interpretation
        """
        try:
            # Reflect database schema
            engine = create_engine(db_uri)
            metadata = sqlalchemy.MetaData()
            metadata.reflect(bind=engine)
            table_info = self._get_table_info(metadata)
            
            # Phase 1: Generate SQL query
            prompts = self._create_prompt_list(nl_query, table_info, user_prompt)
            response = self.bedrockchat.invoke(prompts) if not stream else self.bedrockchat.invoke_stream_parsed(prompts)
            
            assistant_message = response["response_text"]
            if '[SQL]' in assistant_message and '[/SQL]' in assistant_message:
                sql_query = assistant_message.split('[SQL]')[1].split('[/SQL]')[0].strip()
                
                # Execute the SQL query
                query_results = self._execute_sql_query(engine, sql_query)
                
                # Phase 2: Generate human-readable interpretation
                system_prompt_phase2 = """
                You are a senior data analyst. Your task is to interpret SQL query results and provide a human-friendly summary.
                Use clear, concise language and avoid robotic phrases like 'Based on the query results'.
                """
                user_message_phase2 = f"SQL Query Results: {query_results}\nUser Query: {nl_query}"
                prompts_phase2 = [{"text": f"System prompt: {system_prompt_phase2} \n User: {user_message_phase2}"}]
                
                final_response = self.bedrockchat.invoke(prompts_phase2) if not stream else self.bedrockchat.invoke_stream_parsed(prompts_phase2)
                return final_response
            
            else:
                return {"error": "Failed to generate a valid SQL query"}

        except Exception as e:
            logger.error(f"Error in handling query: {str(e)}")
            raise

    def _get_table_info(self, metadata):
        table_info = []
        for table_name, table in metadata.tables.items():
            columns = [f"{col.name} ({col.type})" for col in table.columns]
            table_info.append(f"Table: {table_name}\nColumns: {', '.join(columns)}")
        return "\n\n".join(table_info)

    def _execute_sql_query(self, engine, query):
        with engine.connect() as connection:
            result = connection.execute(text(query))
            return [row for row in result]

    def get_answer_from_db(self, db_type, nl_query, username=None, password=None, host=None,
                           port=None, dbname=None, db_path=None, user_prompt=None, stream=False):

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

        return self.model_invoke(nl_query, db_type, db_uri, user_prompt)

