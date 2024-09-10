![GitHub stars](https://img.shields.io/github/stars/avahi-org/avahiplatform)


# avahiplatform

avahiplatform is a library that makes your Gen-AI tasks effortless. It provides an easy-to-use interface for working with Large Language Models (LLMs) on AWS Bedrock, allowing you to turn enterprise use cases into production applications with just a few lines of Python code.

## Quickstart

### Installation

You can install avahiplatform by running:

```bash
pip install avahiplatform
```

### Basic Usage

```python
import avahiplatform

# Summarization
summary, input_tokens, output_tokens, cost = avahiplatform.summarize("This is a test string to summarize.")
print("Summary:", summary)

# Structured Extraction
extraction, input_tokens, output_tokens, cost = avahiplatform.structredExtraction("This is a test string for extraction.")
print("Extraction:", extraction)

# Data Masking
masked_data, input_tokens, output_tokens, cost = avahiplatform.DataMasking("This is a test string for Data Masking.")
print("Masked Data:", masked_data)

# PDF Summarization
summary, _, _, _ = avahiplatform.summarize("path/to/pdf/file.pdf")
print("PDF Summary:", summary)

# Grammar Correction
corrected_text, _, _, _ = avahiplatform.grammarAssistant("Text with grammatical errors")
print("Corrected Text:", corrected_text)

# Product Description Generation
description, _, _, _ = avahiplatform.productDescriptionAssistant("SKU123", "Summer Sale", "Young Adults")
print("Product Description:", description)

# Image Generation
image, seed, cost = avahiplatform.imageGeneration("A beautiful sunset over mountains")
print("Generated Image:", image)

# Medical Scribing
medical_summary, _ = avahiplatform.medicalscribing("path/to/audio.mp3", "input-bucket", "iam-arn")
print("Medical Summary:", medical_summary)
```

## Features

- Text summarization (plain text, local files, S3 files)
- Structured information extraction
- Data masking
- Natural Language to SQL conversion
- PDF summarization
- Grammar correction
- Product description generation
- Image generation
- Medical scribing
- ICD-10 code generation
- CSV querying
- Semantic search and Retrieval-Augmented Generation (RAG)
- Support for custom prompts and different Anthropic Claude model versions
- Error handling with user-friendly messages

## Configuration

### AWS Credentials

avahiplatform requires AWS credentials to access AWS Bedrock and S3 services. You can provide your AWS credentials in two ways:

1. **Default AWS Credentials**: Configure your AWS credentials in the `~/.aws/credentials` file or by using the AWS CLI.
2. **Explicit AWS Credentials**: Pass the AWS Access Key ID and Secret Access Key when calling functions.

For detailed instructions on setting up AWS credentials, please refer to the [AWS CLI Configuration Guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html).

## Usage Examples

### Summarization

```python
# Summarize text
summary, _, _, _ = avahiplatform.summarize("Text to summarize")

# Summarize a local file
summary, _, _, _ = avahiplatform.summarize("path/to/local/file.txt")

# Summarize a file from S3
summary, _, _, _ = avahiplatform.summarize("s3://bucket-name/file.txt", 
                                            aws_access_key_id="your_access_key", 
                                            aws_secret_access_key="your_secret_key")
```

### Structured Extraction

```python
extraction, _, _, _ = avahiplatform.structredExtraction("Text for extraction")
```

### Data Masking

```python
masked_data, _, _, _ = avahiplatform.DataMasking("Text containing sensitive information")
```

### Natural Language to SQL

```python
result = avahiplatform.nl2sql("Your natural language query", 
                               db_type="postgresql", username="user", password="pass",
                               host="localhost", port=5432, dbname="mydb")
```

### PDF Summarization

```python
summary, _, _, _ = avahiplatform.pdfsummarizer("path/to/file.pdf")
```

### Grammar Correction

```python
corrected_text, _, _, _ = avahiplatform.grammarAssistant("Text with grammatical errors")
```

### Product Description Generation

```python
description, _, _, _ = avahiplatform.productDescriptionAssistant("SKU123", "Summer Sale", "Young Adults")
```

### Image Generation

```python
image, seed, cost = avahiplatform.imageGeneration("A beautiful sunset over mountains")
```

### Medical Scribing

```python
summary, transcript = avahiplatform.medicalscribing("path/to/audio.mp3", "input-bucket", "iam-arn")

# Note in medical scribe in iam_arn: It should have iam pass role inline policy which should look like this:
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Effect": "Allow",
			"Action": [
				"iam:GetRole",
				"iam:PassRole"
			],
			"Resource": [
				"arn:aws:iam::<account-id>:role/<role-name>"
			]
		}
	]
}

Along with this, the role/user should have full access to both Transcribe and Comprehend.
```

### ICD-10 Code Generation

```python
icd_code = avahiplatform.icdcoding("local_file.txt")
```

### CSV Querying

```python
result = avahiplatform.query_csv("What is the average age?", "path/to/data.csv")
```

### Semantic Search and RAG

```python
similar_docs = avahiplatform.perform_semantic_search("Your question", "s3://bucket/documents/")
answer, sources = avahiplatform.perform_rag_with_sources("Your question", "s3://bucket/documents/")
```

## Error Handling

avahiplatform provides user-friendly error messages for common issues. Examples include:

- Invalid AWS credentials
- File not found
- Database connection errors
- Unexpected errors

## Requirements

- Python 3.9 or higher
- boto3 (>= 1.34.160)
- loguru (>= 0.7.2)
- python-docx (>= 1.1.2)
- PyMuPDF (>= 1.24.9)
- langchain (>= 0.1.12)
- langchain_community (>= 0.0.29)
- langchain-experimental (>= 0.0.54)
- psycopg2 (>= 2.9.9)
- PyMySQL (>= 1.1.1)
- tabulate (>= 0.9.0)
- langchain-aws (>= 0.1.17)



## Contributing

We welcome contributions! Feel free to open issues or submit pull requests if you find bugs or have features to add.

## License

This project is licensed under the MIT License.

## Contact

- Author: Avahi Tech
- Email: info@avahitech.com
- GitHub: [https://github.com/avahi-org/avahiplatform](https://github.com/avahi-org/avahiplatform)

