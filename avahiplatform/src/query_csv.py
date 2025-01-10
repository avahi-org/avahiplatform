import pandas as pd
from avahiplatform.helpers.chats.bedrock_chat import BedrockChat
from avahiplatform.helpers.connectors.utils import PythonASTREPL
from avahiplatform.helpers.connectors.s3_helper import S3Helper
from avahiplatform.src.Observability import track_observability

class QueryCSV:
    def __init__(self, 
                bedrockchat: BedrockChat,
                s3_helper: S3Helper
                ):
        
        self.bedrockchat = bedrockchat
        self.s3_helper = s3_helper

    def query_data(
        self, 
        query: str, 
        dataframes: Dict[str, pd.DataFrame],
        stream: bool = False
    ) -> dict:
        """
        Executes the data query by interacting with BedrockChat in two phases.

        Args:
            query (str): The user-provided query.
            dataframes (Dict[str, pd.DataFrame]): A dictionary of pandas DataFrames.
            user_prompt (Optional[str]): An optional user prompt to guide the model.
            stream (bool): Whether to use streaming for responses.

        Returns:
            Tuple[str, float, float, float]: A tuple containing the final human-readable answer,
                                             input token cost, output token cost, and total cost.
        """
        if not query or not dataframes:
            raise ValueError("Incomplete input. Please provide a query and dataframes.")

        # Phase 1: Generate Python code to answer the query
        python_code = self._generate_python_code(query, dataframes, stream)
        assistant_message = python_code["response_text"]

        # Execute the generated Python code
        python_repl = PythonASTREPL(dataframes=dataframes)
        execution_result = python_repl.run(assistant_message)
        
        # Phase 2: Generate a human-readable answer from the execution result
        human_readable_answer = self._generate_human_readable_answer(query, execution_result, stream)
        
        return human_readable_answer

    @track_observability
    def _generate_python_code(
        self, 
        query: str, 
        dataframes: Dict[str, pd.DataFrame],
        stream: bool
    ) -> dict:
        """
        Phase 1: Generates Python code by interacting with BedrockChat.

        Args:
            query (str): The user-provided query.
            dataframes (Dict[str, pd.DataFrame]): A dictionary of pandas DataFrames.
            stream (bool): Whether to use streaming for responses.

        Returns:
            str: The generated Python code.
        """
        system_message = """
        You are a senior Python developer tasked with analyzing data in a pandas DataFrame and generating correct Python code for that.
        - Analyze the DataFrames which USER provides and then write the code.
        - Always assume DataFrame will be given, so please don't create a new DataFrame.
        - Strictly remember that the syntax should always be correct in your code.
        - Do not import data (i.e., no read_csv statements or creating any DataFrame).
        - Don't use print statements to return output in the console unless conveying a message.
        - Don't add unnecessary filters.
        - Keep it simple.
        - Make sure the input data for the Python commands has the correct data values for proper usage.
        - If unsure about something, say so and explain why.
        - Import seaborn like: import seaborn as sns; if needed, then only.
        - For comparison purposes, always use values such as int, float, or string. Never use pandas objects.
        - Unless prompted to do so, never use plots.
        - Always keep the labels for groupby operations.
        - Write Python commands only and no other instructions.
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
               Please provide Python code for the given DataFrames to generate the answer without including any explanation.
               """

        prompt = f"""SYSTEM: {system_message}\nUSER: {user_message}"""

        if stream:
            return self.bedrockchat.invoke_stream_parsed(prompt)
        else:
            return self.bedrockchat.invoke(prompt)

    @track_observability
    def _generate_human_readable_answer(
        self, 
        query: str, 
        execution_result: str,
        stream: bool
    ) -> dict:
        """
        Phase 2: Generates a human-readable answer based on the execution result.

        Args:
            query (str): The original user query.
            execution_result (str): The result of executing the Python code.
            stream (bool): Whether to use streaming for responses.

        Returns:
            Tuple[str, float, float, float]: A tuple containing the final human-readable answer,
                                             input token cost, output token cost, and total cost.
        """
        system_message = """
        - Given an <Answer> and a user <Query>, respond directly using only the information from <Answer>.
        - Format the <Answer> clearly and human-readably in your response, using bullet points if there are multiple answers.
        - Answer like an expert Data Analyst; give a brief explanation of your answers and add the values that support these claims.
        - Use natural human responses; don't use 'Based on the data...'.
        """

        user_message = f"""
        Answer: {execution_result}
        Query: {query}
        """

        prompt = f"""SYSTEM: {system_message}\nUSER: {user_message}"""

        if stream:
            return self.bedrockchat.invoke_stream_parsed(prompt)
        else:
            return self.bedrockchat.invoke(prompt)

    def query_from_file(self, query: str, csv_file_paths: dict, stream: bool = False) -> dict:
        """
        Query data from a file.
        """
        dataframes = {}
        for name, path in csv_file_paths.items():
            df = pd.read_csv(str(path))
            dataframes[name] = df

        return self.query_data(query, dataframes, stream)
    
    def query_from_s3(self, query: str, s3_file_paths: dict, stream: bool = False) -> dict:
        """
        Query data from S3.
        """
        dataframes = self.s3_helper.fetch_csv_files(s3_file_paths)

        return self.query_data(query, dataframes, stream)
