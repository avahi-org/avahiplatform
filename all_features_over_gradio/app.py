import gradio as gr
import os
import shutil  # For file operations
import sys

# Add the parent directory of logicsdk to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import avahiplatform

# ==========================
# Configuration and Setup
# ==========================

# Directory to store uploaded files
UPLOADS_DIR = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)


# ==========================
# Helper Functions
# ==========================

def save_uploaded_file(file_obj):
    """
    Saves the uploaded file to the uploads directory.

    Parameters:
    - file_obj (gr.File): The uploaded file object.

    Returns:
    - str: The name of the saved file, or None if saving failed.
    """
    if file_obj is not None:
        try:
            # Extract the filename
            file_name = os.path.basename(file_obj.name)
            destination_path = os.path.join(UPLOADS_DIR, file_name)

            # Copy the file from the temporary location to uploads_dir
            shutil.copy(file_obj.name, destination_path)

            return file_name
        except Exception as e:
            print(f"Error saving file {file_obj.name}: {e}")
            return None
    return None


def delete_uploaded_file(file_name):
    """
    Deletes the specified file from the uploads directory.

    Parameters:
    - file_name (str): The name of the file to delete.

    Returns:
    - str: Response message indicating success or failure.
    """
    if not file_name or file_name in ["-- Select a File --", "-- No Files Uploaded --"]:
        return "Error: No valid file selected."

    file_path = os.path.join(UPLOADS_DIR, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)
        return f"File '{file_name}' has been deleted."
    else:
        return f"File '{file_name}' does not exist."


def list_uploaded_files():
    """
    Retrieves a list of all files in the uploads directory.

    Returns:
    - list: List of file names.
    """
    try:
        files = os.listdir(UPLOADS_DIR)
        return [f for f in files if os.path.isfile(os.path.join(UPLOADS_DIR, f))]
    except Exception as e:
        print(f"Error listing files: {e}")
        return []


def list_uploaded_files_with_placeholder():
    """
    Retrieves a list of files with a placeholder for the Dropdown component.

    Returns:
    - list: List containing a placeholder followed by file names.
    """
    files = list_uploaded_files()
    if not files:
        return ["-- No Files Uploaded --"]
    return ["-- Select a File --"] + files


# ==========================
# Functionality Implementations
# ==========================

def text_summarization(input_text, file_obj, access_key, secret_key, region):
    """
    Performs text summarization on input text or uploaded file.

    Parameters:
    - input_text (str): Text to summarize.
    - file_obj (gr.File): Uploaded file to summarize.
    - access_key (str): AWS Access Key.
    - secret_key (str): AWS Secret Key.
    - region (str): AWS Region.

    Returns:
    - tuple: (Summary, Input Tokens, Output Tokens, Cost) or error messages.
    """
    uploaded_file = save_uploaded_file(file_obj)
    if input_text:
        try:
            summary, input_tokens, output_tokens, cost = avahiplatform.summarize(
                input_text,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            return summary, input_tokens, output_tokens, cost
        except Exception as e:
            return f"Error: {str(e)}", None, None, None
    elif uploaded_file:
        try:
            summary, input_tokens, output_tokens, cost = avahiplatform.summarize(
                os.path.join(UPLOADS_DIR, uploaded_file),
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            return summary, input_tokens, output_tokens, cost
        except Exception as e:
            return f"Error: {str(e)}", None, None, None
    return "Error: Please provide text or upload a file.", None, None, None


def structured_extraction(input_text, file_obj, access_key, secret_key, region):
    """
    Extracts structured data from input text or uploaded file.

    Parameters:
    - input_text (str): Text for structured extraction.
    - file_obj (gr.File): Uploaded file for structured extraction.
    - access_key (str): AWS Access Key.
    - secret_key (str): AWS Secret Key.
    - region (str): AWS Region.

    Returns:
    - tuple: (Extraction, Input Tokens, Output Tokens, Cost) or error messages.
    """
    uploaded_file = save_uploaded_file(file_obj)
    if input_text:
        try:
            extraction, input_tokens, output_tokens, cost = avahiplatform.structredExtraction(
                input_text,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            return extraction, input_tokens, output_tokens, cost
        except Exception as e:
            return f"Error: {str(e)}", None, None, None
    elif uploaded_file:
        try:
            extraction, input_tokens, output_tokens, cost = avahiplatform.structredExtraction(
                os.path.join(UPLOADS_DIR, uploaded_file),
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            return extraction, input_tokens, output_tokens, cost
        except Exception as e:
            return f"Error: {str(e)}", None, None, None
    return "Error: Please provide text or upload a file.", None, None, None


def data_masking(input_text, file_obj, access_key, secret_key, region):
    """
    Performs data masking on input text or uploaded file.

    Parameters:
    - input_text (str): Text to mask.
    - file_obj (gr.File): Uploaded file to mask.
    - access_key (str): AWS Access Key.
    - secret_key (str): AWS Secret Key.
    - region (str): AWS Region.

    Returns:
    - tuple: (Masked Data, Input Tokens, Output Tokens, Cost) or error messages.
    """
    uploaded_file = save_uploaded_file(file_obj)
    if input_text:
        try:
            masked_data, input_tokens, output_tokens, cost = avahiplatform.DataMasking(
                input_text,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            return masked_data, input_tokens, output_tokens, cost
        except Exception as e:
            return f"Error: {str(e)}", None, None, None
    elif uploaded_file:
        try:
            masked_data, input_tokens, output_tokens, cost = avahiplatform.DataMasking(
                os.path.join(UPLOADS_DIR, uploaded_file),
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            return masked_data, input_tokens, output_tokens, cost
        except Exception as e:
            return f"Error: {str(e)}", None, None, None
    return "Error: Please provide text or upload a file.", None, None, None


def natural_language_to_sql(nl_query, db_type, username, password, host, port, dbname, access_key, secret_key, region):
    """
    Converts natural language queries to SQL and executes them.

    Parameters:
    - nl_query (str): Natural language query.
    - db_type (str): Database type.
    - username (str): Database username.
    - password (str): Database password.
    - host (str): Database host.
    - port (int): Database port.
    - dbname (str): Database name.
    - access_key (str): AWS Access Key.
    - secret_key (str): AWS Secret Key.
    - region (str): AWS Region.

    Returns:
    - str: SQL Query Result or error message.
    """
    if not all([nl_query, db_type, username, password, host, port, dbname]):
        return "Error: Please provide all SQL query details."

    try:
        result = avahiplatform.nl2sql(
            nl_query,
            db_type=db_type,
            username=username,
            password=password,
            host=host,
            port=port,
            dbname=dbname,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        return result
    except Exception as e:
        return f"Error: {str(e)}"


def pdf_summarization(file_obj, access_key, secret_key, region):
    """
    Summarizes the content of a PDF/Text/Docx file.

    Parameters:
    - file_obj (gr.File): Uploaded PDF/Text/Docx file.
    - access_key (str): AWS Access Key.
    - secret_key (str): AWS Secret Key.
    - region (str): AWS Region.

    Returns:
    - tuple: (Summary, Input Tokens, Output Tokens, Cost) or error messages.
    """
    uploaded_file = save_uploaded_file(file_obj)
    if uploaded_file:
        try:
            summary, input_tokens, output_tokens, cost = avahiplatform.summarize(
                os.path.join(UPLOADS_DIR, uploaded_file),
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            return summary, input_tokens, output_tokens, cost
        except Exception as e:
            return f"Error: {str(e)}", None, None, None
    return "Error: Please upload a file.", None, None, None


def grammar_correction(input_text, file_obj, access_key, secret_key, region):
    """
    Corrects grammatical errors in input text or uploaded file.

    Parameters:
    - input_text (str): Text with grammatical errors.
    - file_obj (gr.File): Uploaded file with grammatical errors.
    - access_key (str): AWS Access Key.
    - secret_key (str): AWS Secret Key.
    - region (str): AWS Region.

    Returns:
    - tuple: (Corrected Text, Input Tokens, Output Tokens, Cost) or error messages.
    """
    uploaded_file = save_uploaded_file(file_obj)
    if input_text:
        try:
            corrected_text, input_tokens, output_tokens, cost = avahiplatform.grammarAssistant(
                input_text,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            return corrected_text, input_tokens, output_tokens, cost
        except Exception as e:
            return f"Error: {str(e)}", None, None, None
    elif uploaded_file:
        try:
            corrected_text, input_tokens, output_tokens, cost = avahiplatform.grammarAssistant(
                os.path.join(UPLOADS_DIR, uploaded_file),
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            return corrected_text, input_tokens, output_tokens, cost
        except Exception as e:
            return f"Error: {str(e)}", None, None, None
    return "Error: Please provide text or upload a file.", None, None, None


def product_description_generation(sku, sale_details, audience, access_key, secret_key, region):
    """
    Generates a product description based on SKU, sale details, and target audience.

    Parameters:
    - sku (str): Stock Keeping Unit identifier.
    - sale_details (str): Details about the sale.
    - audience (str): Target audience for the product.
    - access_key (str): AWS Access Key.
    - secret_key (str): AWS Secret Key.
    - region (str): AWS Region.

    Returns:
    - tuple: (Product Description, Input Tokens, Output Tokens, Cost) or error messages.
    """
    if not all([sku, sale_details, audience]):
        return "Error: Please provide SKU, sale details, and target audience.", None, None, None

    try:
        description, input_tokens, output_tokens, cost = avahiplatform.productDescriptionAssistant(
            sku,
            sale_details,
            audience,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        return description, input_tokens, output_tokens, cost
    except Exception as e:
        return f"Error: {str(e)}", None, None, None


def image_generation(description, model_name, access_key, secret_key, region):
    """
    Generates an image based on the provided description and model.

    Parameters:
    - description (str): Description of the desired image.
    - model_name (str): Name of the image generation model.
    - access_key (str): AWS Access Key.
    - secret_key (str): AWS Secret Key.
    - region (str): AWS Region.

    Returns:
    - tuple: (Generated Image, Seed, Cost) or error messages.
    """
    if not description or not model_name:
        return "Error: Please provide a description and select a model.", None, None

    try:
        image, seed, cost = avahiplatform.imageGeneration(
            description,
            model_name=model_name,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        return image, seed, cost
    except Exception as e:
        return f"Error: {str(e)}", None, None, None


def medical_scribing(audio_file, input_bucket, iam_arn, access_key, secret_key, region):
    """
    Performs medical scribing on an uploaded audio file.

    Parameters:
    - audio_file (gr.File): Uploaded audio file.
    - input_bucket (str): S3 Input Bucket.
    - iam_arn (str): IAM ARN role.
    - access_key (str): AWS Access Key.
    - secret_key (str): AWS Secret Key.
    - region (str): AWS Region.

    Returns:
    - str: Medical summary or error message.
    """
    uploaded_file = save_uploaded_file(audio_file)
    if uploaded_file and input_bucket and iam_arn:
        try:
            medical_summary, _ = avahiplatform.medicalscribing(
                os.path.join(UPLOADS_DIR, uploaded_file),
                input_bucket,
                iam_arn,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            return medical_summary
        except Exception as e:
            return f"Error: {str(e)}"
    return "Error: Please upload an audio file and provide S3 Input Bucket and IAM ARN."


def icd_10_code_generation(input_text, file_obj, access_key, secret_key, region):
    """
    Generates ICD-10 codes based on input text or uploaded file.

    Parameters:
    - input_text (str): Medical prescription text.
    - file_obj (gr.File): Uploaded file containing medical prescriptions.
    - access_key (str): AWS Access Key.
    - secret_key (str): AWS Secret Key.
    - region (str): AWS Region.

    Returns:
    - str: ICD-10 code or error message.
    """
    uploaded_file = save_uploaded_file(file_obj)
    if input_text:
        try:
            icd_code = avahiplatform.icdcoding(
                input_text,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            return icd_code
        except Exception as e:
            return f"Error: {str(e)}"
    elif uploaded_file:
        try:
            icd_code = avahiplatform.icdcoding(
                os.path.join(UPLOADS_DIR, uploaded_file),
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            return icd_code
        except Exception as e:
            return f"Error: {str(e)}"
    return "Error: Please provide text or upload a file."


def csv_querying(input_query, file_objs, access_key, secret_key, region):
    """
    Executes a query on multiple uploaded CSV or Excel files.

    Parameters:
    - input_query (str): Query to execute.
    - file_objs (list): List of uploaded file objects.
    - access_key (str): AWS Access Key.
    - secret_key (str): AWS Secret Key.
    - region (str): AWS Region.

    Returns:
    - str: Query result or error message.
    """
    if not input_query:
        return "Error: Please provide a query and upload at least one CSV or Excel file."

    # Initialize the dictionary to hold file names and their paths
    csv_files = {}

    # Iterate over the uploaded files and save them
    if file_objs:
        for idx, file_obj in enumerate(file_objs, start=1):
            saved_file_name = save_uploaded_file(file_obj)
            if saved_file_name:
                # Assign a custom key name, e.g., "df1", "df2", etc.
                key_name = f"df{idx}"
                file_path = os.path.join(UPLOADS_DIR, saved_file_name)
                csv_files[key_name] = file_path
            else:
                return f"Error: Failed to save the file '{file_obj.name}'."
    else:
        return "Error: No files were uploaded."

    try:
        # Perform the CSV query using the constructed dictionary
        csv_query_answer = avahiplatform.query_csv(
            input_query,
            csv_file_paths=csv_files,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        return csv_query_answer
    except Exception as e:
        return f"Error: {str(e)}"


def semantic_search(question, dataset_name, access_key, secret_key, region):
    """
    Performs semantic search on a specified dataset.

    Parameters:
    - question (str): The question to search for.
    - dataset_name (str): Name or path of the dataset.
    - access_key (str): AWS Access Key.
    - secret_key (str): AWS Secret Key.
    - region (str): AWS Region.

    Returns:
    - str: Similar documents or error message.
    """
    if question and dataset_name:
        try:
            similar_docs = avahiplatform.perform_semantic_search(
                question,
                dataset_name,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            return similar_docs
        except Exception as e:
            return f"Error: {str(e)}"
    return "Error: Please provide a question and dataset name."


def rag_with_sources(question, dataset_name, access_key, secret_key, region):
    """
    Performs Retrieval-Augmented Generation (RAG) with sources.

    Parameters:
    - question (str): The question for which to fetch answers.
    - dataset_name (str): Name or path of the dataset.
    - access_key (str): AWS Access Key.
    - secret_key (str): AWS Secret Key.
    - region (str): AWS Region.

    Returns:
    - tuple: (Answer, Similar Documents) or error messages.
    """
    if question and dataset_name:
        try:
            answer, similar_docs = avahiplatform.perform_rag_with_sources(
                question,
                dataset_name,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            return answer, similar_docs
        except Exception as e:
            return f"Error: {str(e)}", None
    return "Error: Please provide a question and dataset name.", None


def chatbot_function(system_prompt, user_input, access_key, secret_key, region):
    """
    Interacts with a chatbot based on user input.

    Parameters:
    - system_prompt (str): The system prompt to initialize the chatbot.
    - user_input (str): The user's input message.
    - access_key (str): AWS Access Key.
    - secret_key (str): AWS Secret Key.
    - region (str): AWS Region.

    Returns:
    - str: Chatbot's response or error message.
    """
    if not system_prompt or not user_input:
        return "Error: Please provide both system prompt and user input."

    try:
        chatbot = avahiplatform.chatbot()
        chatbot.initialize_instance(system_prompt=system_prompt)
        response = chatbot.chat(user_input=user_input)
        return response
    except Exception as e:
        return f"Error: {str(e)}"


# ==========================
# Panel Visibility Management
# ==========================

def update_panel(selected_functionality):
    """
    Updates the visibility of functionality panels based on user selection.

    Parameters:
    - selected_functionality (str): The functionality selected by the user.

    Returns:
    - list: List of visibility updates for each panel.
    """
    updates = []
    for name, panel in panels.items():
        if name == selected_functionality:
            updates.append(gr.update(visible=True))
        else:
            updates.append(gr.update(visible=False))
    return updates


def refresh_file_list():
    """
    Refreshes the list of uploaded files in the dropdown.

    Returns:
    - gr.Dropdown.update: Updated Dropdown component with new choices and value.
    """
    files = list_uploaded_files()
    if files:
        return gr.update(choices=files, value=files[0])
    else:
        return gr.update(choices=["-- No Files Uploaded --"], value="-- No Files Uploaded --")


def delete_and_refresh(file_name):
    """
    Deletes the selected file and refreshes the dropdown.

    Parameters:
    - file_name (str): The name of the file to delete.

    Returns:
    - tuple: (delete_response, updated_dropdown)
    """
    delete_msg = delete_uploaded_file(file_name)
    # Refresh the file list after deletion
    files = list_uploaded_files()
    if files:
        dropdown_update = gr.update(choices=files, value=files[0])
    else:
        dropdown_update = gr.update(choices=["-- No Files Uploaded --"], value="-- No Files Uploaded --")
    return delete_msg, dropdown_update


# ==========================
# Initialize Gradio Interface
# ==========================

with gr.Blocks() as app:
    with gr.Row():
        # Sidebar Column
        with gr.Column(scale=1, min_width=250):
            # Avahi SDK Configuration
            with gr.Accordion(label="Avahi Python Package SDK UI", open=True):
                functionality = gr.Dropdown(
                    label="Choose Functionality",
                    choices=[
                        "Text Summarization",
                        "Structured Extraction",
                        "Data Masking",
                        "Natural Language to SQL",
                        "PDF Summarization",
                        "Grammar Correction",
                        "Product Description Generation",
                        "Image Generation",
                        "Medical Scribing",
                        "ICD-10 Code Generation",
                        "CSV Querying",
                        "Semantic Search",
                        "RAG with Sources",
                        "Chatbot"
                    ],
                    value="Text Summarization"  # Default selected functionality
                )
                access_key = gr.Textbox(label="AWS Access Key", type="password")
                secret_key = gr.Textbox(label="AWS Secret Key", type="password")
                region = gr.Textbox(label="AWS Region", value="us-east-1")

            # Uploaded Files Management
            with gr.Accordion(label="Manage Uploaded Files", open=False):
                file_name = gr.Dropdown(
                    label="Select a File to Delete",
                    choices=list_uploaded_files_with_placeholder(),
                    value="-- Select a File --"
                )
                delete_response = gr.Textbox(label="Response", interactive=False)
                delete_button = gr.Button("Delete File")
                delete_button.click(
                    fn=delete_and_refresh,
                    inputs=file_name,
                    outputs=[delete_response, file_name]
                )
                refresh_button = gr.Button("Refresh File List")
                refresh_button.click(
                    fn=refresh_file_list,
                    inputs=None,
                    outputs=file_name
                )

        # Main Content Column
        with gr.Column(scale=3):
            # Dictionary to hold panel components
            panels = {}

            # ------------------------
            # Text Summarization Panel
            # ------------------------
            panels['Text Summarization'] = gr.Group(visible=True)
            with panels['Text Summarization']:
                gr.Markdown("## Text Summarization")
                ts_input_text = gr.Textbox(lines=5, label="Enter text to summarize")
                ts_file_obj = gr.File(label="Or Upload File")
                ts_outputs = [
                    gr.Textbox(label="Summary", interactive=False),
                    gr.Textbox(label="Input Tokens", interactive=False),
                    gr.Textbox(label="Output Tokens", interactive=False),
                    gr.Textbox(label="Cost", interactive=False)
                ]
                ts_button = gr.Button("Summarize")
                ts_button.click(
                    fn=text_summarization,
                    inputs=[ts_input_text, ts_file_obj, access_key, secret_key, region],
                    outputs=ts_outputs
                )

            # ------------------------
            # Structured Extraction Panel
            # ------------------------
            panels['Structured Extraction'] = gr.Group(visible=False)
            with panels['Structured Extraction']:
                gr.Markdown("## Structured Extraction")
                se_input_text = gr.Textbox(lines=5, label="Enter text for extraction")
                se_file_obj = gr.File(label="Or Upload File")
                se_outputs = [
                    gr.Textbox(label="Extraction", interactive=False),
                    gr.Textbox(label="Input Tokens", interactive=False),
                    gr.Textbox(label="Output Tokens", interactive=False),
                    gr.Textbox(label="Cost", interactive=False)
                ]
                se_button = gr.Button("Extract")
                se_button.click(
                    fn=structured_extraction,
                    inputs=[se_input_text, se_file_obj, access_key, secret_key, region],
                    outputs=se_outputs
                )

            # ------------------------
            # Data Masking Panel
            # ------------------------
            panels['Data Masking'] = gr.Group(visible=False)
            with panels['Data Masking']:
                gr.Markdown("## Data Masking")
                dm_input_text = gr.Textbox(lines=5, label="Enter text for masking")
                dm_file_obj = gr.File(label="Or Upload File")
                dm_outputs = [
                    gr.Textbox(label="Masked Data", interactive=False),
                    gr.Textbox(label="Input Tokens", interactive=False),
                    gr.Textbox(label="Output Tokens", interactive=False),
                    gr.Textbox(label="Cost", interactive=False)
                ]
                dm_button = gr.Button("Mask Data")
                dm_button.click(
                    fn=data_masking,
                    inputs=[dm_input_text, dm_file_obj, access_key, secret_key, region],
                    outputs=dm_outputs
                )

            # ------------------------
            # Natural Language to SQL Panel
            # ------------------------
            panels['Natural Language to SQL'] = gr.Group(visible=False)
            with panels['Natural Language to SQL']:
                gr.Markdown("## Natural Language to SQL")
                nl2sql_nl_query = gr.Textbox(label="Natural Language Query")
                nl2sql_db_type = gr.Textbox(label="DB Type")
                nl2sql_username = gr.Textbox(label="DB Username")
                nl2sql_password = gr.Textbox(label="DB Password", type="password")
                nl2sql_host = gr.Textbox(label="DB Host")
                nl2sql_port = gr.Number(label="DB Port")
                nl2sql_dbname = gr.Textbox(label="Database Name")
                nl2sql_output = gr.Textbox(label="SQL Query Result", interactive=False)
                nl2sql_button = gr.Button("Execute Query")
                nl2sql_button.click(
                    fn=natural_language_to_sql,
                    inputs=[nl2sql_nl_query, nl2sql_db_type, nl2sql_username, nl2sql_password, nl2sql_host, nl2sql_port,
                            nl2sql_dbname, access_key, secret_key, region],
                    outputs=nl2sql_output
                )

            # ------------------------
            # PDF Summarization Panel
            # ------------------------
            panels['PDF Summarization'] = gr.Group(visible=False)
            with panels['PDF Summarization']:
                gr.Markdown("## PDF Summarization")
                pdf_file_obj = gr.File(label="Upload PDF/Text/Docx File")
                pdf_outputs = [
                    gr.Textbox(label="PDF Summary", interactive=False),
                    gr.Textbox(label="Input Tokens", interactive=False),
                    gr.Textbox(label="Output Tokens", interactive=False),
                    gr.Textbox(label="Cost", interactive=False)
                ]
                pdf_button = gr.Button("Summarize PDF")
                pdf_button.click(
                    fn=pdf_summarization,
                    inputs=[pdf_file_obj, access_key, secret_key, region],
                    outputs=pdf_outputs
                )

            # ------------------------
            # Grammar Correction Panel
            # ------------------------
            panels['Grammar Correction'] = gr.Group(visible=False)
            with panels['Grammar Correction']:
                gr.Markdown("## Grammar Correction")
                gc_input_text = gr.Textbox(lines=5, label="Enter text with grammatical errors")
                gc_file_obj = gr.File(label="Or Upload File")
                gc_outputs = [
                    gr.Textbox(label="Corrected Text", interactive=False),
                    gr.Textbox(label="Input Tokens", interactive=False),
                    gr.Textbox(label="Output Tokens", interactive=False),
                    gr.Textbox(label="Cost", interactive=False)
                ]
                gc_button = gr.Button("Correct Grammar")
                gc_button.click(
                    fn=grammar_correction,
                    inputs=[gc_input_text, gc_file_obj, access_key, secret_key, region],
                    outputs=gc_outputs
                )

            # ------------------------
            # Product Description Generation Panel
            # ------------------------
            panels['Product Description Generation'] = gr.Group(visible=False)
            with panels['Product Description Generation']:
                gr.Markdown("## Product Description Generation")
                pdg_sku = gr.Textbox(label="SKU")
                pdg_sale_details = gr.Textbox(label="Sale Details")
                pdg_audience = gr.Textbox(label="Target Audience")
                pdg_outputs = [
                    gr.Textbox(label="Product Description", interactive=False),
                    gr.Textbox(label="Input Tokens", interactive=False),
                    gr.Textbox(label="Output Tokens", interactive=False),
                    gr.Textbox(label="Cost", interactive=False)
                ]
                pdg_button = gr.Button("Generate Description")
                pdg_button.click(
                    fn=product_description_generation,
                    inputs=[pdg_sku, pdg_sale_details, pdg_audience, access_key, secret_key, region],
                    outputs=pdg_outputs
                )

            # ------------------------
            # Image Generation Panel
            # ------------------------
            panels['Image Generation'] = gr.Group(visible=False)
            with panels['Image Generation']:
                gr.Markdown("## Image Generation")
                img_description = gr.Textbox(label="Description")
                img_model_name = gr.Dropdown(
                    choices=["amazon.titan.v1", "amazon.titan.v2", "sdxl", "sd3-large", "stable-image-ultra",
                             "stable-image-core"],
                    label="Model Name"
                )
                img_outputs = [
                    gr.Image(label="Generated Image"),
                    gr.Textbox(label="Seed", interactive=False),
                    gr.Textbox(label="Cost", interactive=False)
                ]
                img_button = gr.Button("Generate Image")
                img_button.click(
                    fn=image_generation,
                    inputs=[img_description, img_model_name, access_key, secret_key, region],
                    outputs=img_outputs
                )

            # ------------------------
            # Medical Scribing Panel
            # ------------------------
            panels['Medical Scribing'] = gr.Group(visible=False)
            with panels['Medical Scribing']:
                gr.Markdown("## Medical Scribing")
                ms_audio_file = gr.File(label="Upload Audio File")
                ms_input_bucket = gr.Textbox(label="S3 Input Bucket")
                ms_iam_arn = gr.Textbox(label="IAM ARN")
                med_output = gr.Textbox(label="Medical Summary", interactive=False)
                med_button = gr.Button("Generate Medical Summary")
                med_button.click(
                    fn=medical_scribing,
                    inputs=[ms_audio_file, ms_input_bucket, ms_iam_arn, access_key, secret_key, region],
                    outputs=med_output
                )

            # ------------------------
            # ICD-10 Code Generation Panel
            # ------------------------
            panels['ICD-10 Code Generation'] = gr.Group(visible=False)
            with panels['ICD-10 Code Generation']:
                gr.Markdown("## ICD-10 Code Generation")
                icd_input_text = gr.Textbox(lines=5, label="Enter Medical Prescription")
                icd_file_obj = gr.File(label="Or Upload File")
                icd_output = gr.Textbox(label="ICD-10 Code", interactive=False)
                icd_button = gr.Button("Generate ICD-10 Code")
                icd_button.click(
                    fn=icd_10_code_generation,
                    inputs=[icd_input_text, icd_file_obj, access_key, secret_key, region],
                    outputs=icd_output
                )

            # ------------------------
            # CSV Querying Panel
            # ------------------------
            panels['CSV Querying'] = gr.Group(visible=False)
            with panels['CSV Querying']:
                gr.Markdown("## CSV Querying")
                csv_input_query = gr.Textbox(label="Enter Your Query")
                csv_file_objs = gr.File(label="Upload CSV or Excel Files", file_count="multiple")
                csv_output = gr.Textbox(label="Query Result", interactive=False)
                csv_button = gr.Button("Execute CSV Query")
                csv_button.click(
                    fn=csv_querying,
                    inputs=[csv_input_query, csv_file_objs, access_key, secret_key, region],
                    outputs=csv_output
                )

            # ------------------------
            # Semantic Search Panel
            # ------------------------
            panels['Semantic Search'] = gr.Group(visible=False)
            with panels['Semantic Search']:
                gr.Markdown("## Semantic Search")
                ss_question = gr.Textbox(label="Enter Your Question")
                ss_dataset_name = gr.Textbox(label="Enter Dataset Name (S3 Path)")
                ss_output = gr.Textbox(label="Similar Documents", interactive=False)
                ss_button = gr.Button("Search")
                ss_button.click(
                    fn=semantic_search,
                    inputs=[ss_question, ss_dataset_name, access_key, secret_key, region],
                    outputs=ss_output
                )

            # ------------------------
            # RAG with Sources Panel
            # ------------------------
            panels['RAG with Sources'] = gr.Group(visible=False)
            with panels['RAG with Sources']:
                gr.Markdown("## RAG with Sources")
                rag_question = gr.Textbox(label="Enter Your Question")
                rag_dataset_name = gr.Textbox(label="Enter Dataset Name (S3 Path)")
                rag_outputs = [
                    gr.Textbox(label="Answer", interactive=False),
                    gr.Textbox(label="Similar Documents", interactive=False)
                ]
                rag_button = gr.Button("Fetch Answer with Sources")
                rag_button.click(
                    fn=rag_with_sources,
                    inputs=[rag_question, rag_dataset_name, access_key, secret_key, region],
                    outputs=rag_outputs
                )

            # ------------------------
            # Chatbot Panel
            # ------------------------
            panels['Chatbot'] = gr.Group(visible=False)
            with panels['Chatbot']:
                gr.Markdown("## Chatbot")
                cb_system_prompt = gr.Textbox(label="System Prompt")
                cb_user_input = gr.Textbox(label="User Input")
                cb_output = gr.Textbox(label="Chatbot Response", interactive=False)
                cb_button = gr.Button("Send")
                cb_button.click(
                    fn=chatbot_function,
                    inputs=[cb_system_prompt, cb_user_input, access_key, secret_key, region],
                    outputs=cb_output
                )

            # Mapping of panel names to their groups
            panels = {
                'Text Summarization': panels['Text Summarization'],
                'Structured Extraction': panels['Structured Extraction'],
                'Data Masking': panels['Data Masking'],
                'Natural Language to SQL': panels['Natural Language to SQL'],
                'PDF Summarization': panels['PDF Summarization'],
                'Grammar Correction': panels['Grammar Correction'],
                'Product Description Generation': panels['Product Description Generation'],
                'Image Generation': panels['Image Generation'],
                'Medical Scribing': panels['Medical Scribing'],
                'ICD-10 Code Generation': panels['ICD-10 Code Generation'],
                'CSV Querying': panels['CSV Querying'],
                'Semantic Search': panels['Semantic Search'],
                'RAG with Sources': panels['RAG with Sources'],
                'Chatbot': panels['Chatbot']
            }

            # Dropdown change event to update panel visibility
            functionality.change(
                fn=update_panel,
                inputs=functionality,
                outputs=list(panels.values())
            )

# ==========================
# Launch the Application
# ==========================

if __name__ == "__main__":
    app.launch(share=True)
