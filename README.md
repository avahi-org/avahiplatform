# AvahiAI

Logicsdk is an open source AI framework to build with LLMs on AWS Bedrock. Turn your enterprise use cases into production application in few lines of python code

## Quickstart
## Installation

You can install logic just by running:
```python
! pip install logicsdk

import logicsdk
summarization_output, input_token_cost, output_token_cost, total_cost = logicsdk.summarize("This is a test string to summarize.")
print("Summary:", summarization_output)
extraction_output, input_token_cost, output_token_cost, total_cost = logicsdk.structredExtraction("This is a test string for the extraction.")
print("Extraction:", extraction_output)
masking_output, input_token_cost, output_token_cost, total_cost = logicsdk.DataMasking("This is a test string to for the Data Masking.")
print("DataMasking:", masking_output)
nl2sql_result = logicsdk.nl2sql("What are the names and ages of employees who joined after January 1, 2020?",
                                db_type = "postgresql", username = "dbuser", password = "dbpassword",
                                host = "localhost", port = 5432, dbname = "employees"
                                )
print("nl2sql generated answer:", nl2sql_result)

```

## current Features
- Summarize plain text.
- Summarize text from local files (`.txt`, `.pdf`, `.docx`).
- Summarize text from S3 files (`.txt`, `.pdf`, `.docx`).
- Extract the entities from plain text.
- Extract the entities from from local files (`.txt`, `.pdf`, `.docx`).
- Extract the entities from from S3 files (`.txt`, `.pdf`, `.docx`).
- Mask the entities from the plain text.
- Mask the entities from text from local files (`.txt`, `.pdf`, `.docx`).
- Mask the entities from the text from S3 files (`.txt`, `.pdf`, `.docx`).
- Converts a natural language query into an SQL/PostgreSQL/SQLite query, executes it against the specified database, and returns the results in a user-friendly manner. 
- Support for custom prompts and different anthropic claude model versions.
- Error handling with user-friendly messages.
- And many more to come...

### AWS CLI Installation (Optional but Recommended)
To configure your AWS credentials easily, you can use the AWS CLI. Install it by following instructions on the [AWS CLI Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html).

## Configuration

### AWS Credentials

AvahiAI requires AWS credentials to access AWS Bedrock and S3 services. You can provide your AWS credentials in two ways:

1. **Default AWS Credentials**: Ensure your AWS credentials are configured in the `~/.aws/credentials` file or by using the AWS CLI.
2. **Explicit AWS Credentials**: Pass the AWS Access Key and Secret Key when calling the `summarize` function.

### Configuring AWS Credentials Using AWS CLI

After installing the AWS CLI, run the following command to configure your credentials:

```sh
aws configure
```

You will be prompted to enter your AWS Access Key ID, Secret Access Key, region, and output format. This will create or update the `~/.aws/credentials` file with your credentials.

### Sample `~/.aws/credentials` File:

```ini
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```

## Usage

### Importing logicsdk

```python
import logicsdk
```

### Summarizing Text Strings

```python
summarization_output, input_token_cost, output_token_cost, total_cost = logicsdk.summarize("This is a test string to summarize.")
print("Summary:", summarization_output)
print("Input Cost:", input_token_cost)
print("Output Cost:", output_token_cost)
print("Cost:", total_cost)
```

## Summarization

### Summarizing Local Files

#### Text File (`.txt`)

```python
summarization_output, input_token_cost, output_token_cost, total_cost = logicsdk.summarize("path/to/your/file.txt")
print("Summary:", summarization_output)
```

#### PDF File (`.pdf`)

```python
summarization_output, input_token_cost, output_token_cost, total_cost = logicsdk.summarize("path/to/your/file.pdf")
print("Summary:", summarization_output)
```

#### DOCX File (`.docx`)

```python
summarization_output, input_token_cost, output_token_cost, total_cost = logicsdk.summarize("path/to/your/file.docx")
print("Summary:", summarization_output)
```

### Summarizing Files from S3

```python
summarization_output, input_token_cost, output_token_cost, total_cost = logicsdk.summarize("s3://your-bucket-name/your-file.pdf", aws_access_key_id="your_access_key", aws_secret_access_key="your_secret_key")
print("Summary:", summarization_output)
```


### Changing the Default Model

```python
summarization_output, input_token_cost, output_token_cost, total_cost = logicsdk.summarize("path/to/your/file.docx", model_name="haiku-3.0")
print("Summary:", summarization_output)
```


## Extraction

### Extracting from Strings

```python
extraction_output, input_token_cost, output_token_cost, total_cost = logicsdk.structredExtraction("This is a test string to for the extraction.")
print("Extraction:", extraction_output)
print("Input Cost:", input_token_cost)
print("Output Cost:", output_token_cost)
print("Cost:", total_cost)
```


### Extracting from Local Files

#### Text File (`.txt`)

```python
extraction_output, input_token_cost, output_token_cost, total_cost = logicsdk.structredExtraction("path/to/your/file.txt")
print("Extraction:", extraction_output)
```

#### PDF File (`.pdf`)

```python
extraction_output, input_token_cost, output_token_cost, total_cost = logicsdk.structredExtraction("path/to/your/file.pdf")
print("Extraction:", extraction_output)
```

#### DOCX File (`.docx`)

```python
extraction_output, input_token_cost, output_token_cost, total_cost = logicsdk.structredExtraction("path/to/your/file.docx")
print("Extraction:", extraction_output)
```

### Extracting from Files in S3

```python
extraction_output, input_token_cost, output_token_cost, total_cost = logicsdk.structredExtraction("s3://your-bucket-name/your-file.pdf", aws_access_key_id="your_access_key", aws_secret_access_key="your_secret_key")
print("Extraction:", extraction_output)
```


### Changing the Default Model

```python
extraction_output, input_token_cost, output_token_cost, total_cost = logicsdk.structredExtraction("path/to/your/file.docx", model_name="haiku-3.0")
print("Extraction:", extraction_output)
```


## Data Masking

### Extracting from Strings

```python
masking_output, input_token_cost, output_token_cost, total_cost = logicsdk.DataMasking("This is a test string to for the Data Masking.")
print("DataMasking:", masking_output)
print("Input Cost:", input_token_cost)
print("Output Cost:", output_token_cost)
print("Cost:", total_cost)
```


### DataMasking from Local Files

#### Text File (`.txt`)

```python
masking_output, input_token_cost, output_token_cost, total_cost = logicsdk.DataMasking("path/to/your/file.txt")
print("DataMasking:", masking_output)
```

#### PDF File (`.pdf`)

```python
masking_output, input_token_cost, output_token_cost, total_cost = logicsdk.DataMasking("path/to/your/file.pdf")
print("DataMasking:", masking_output)
```

#### DOCX File (`.docx`)

```python
masking_output, input_token_cost, output_token_cost, total_cost = logicsdk.DataMasking("path/to/your/file.docx")
print("DataMasking:", masking_output)
```

### DataMasking from Files in S3

```python
masking_output, input_token_cost, output_token_cost, total_cost = logicsdk.DataMasking("s3://your-bucket-name/your-file.pdf", aws_access_key_id="your_access_key", aws_secret_access_key="your_secret_key")
print("DataMasking:", masking_output)
```

### Changing the Default Model

```python
masking_output, input_token_cost, output_token_cost, total_cost = logicsdk.DataMasking("path/to/your/file.docx", model_name="haiku-3.0")
print("DataMasking:", masking_output)
```

## Nl2SQL

### Generate user-friendly answer from the natural language query

```python
nl2sql_result = logicsdk.nl2sql("What are the names and ages of employees who joined after January 1, 2020?",
                                db_type = "mysql", username = "dbuser", password = "dbpassword",
                                host = "localhost", port = 3306, dbname = "employees"
                                )
print("nl2sql_result:", nl2sql_result)
```


## Other more Gen-ai task to come

## Error Handling

AvahiAI provides user-friendly error messages for common issues. Here are some common errors you might encounter:

1. **Invalid AWS Credentials**
```sh
AWS credentials are not set or invalid. Please configure your AWS credentials.
```

2. **File Not Found**
```sh
The file at path/to/your/file.pdf does not exist. Please check the file path.
```

4. **Unexpected Errors**
```sh
An unexpected error occurred: <error message>.
```

## Contributing

Feel free to open issues or submit pull requests if you find bugs or have features to add.

## License
