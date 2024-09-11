# avahiplatform
[![GitHub stars](https://img.shields.io/github/stars/avahi-org/avahiplatform)](https://star-history.com/#avahiplatform/avahiplatform)
[![PyPI - License](https://img.shields.io/pypi/l/avahiplatform?style=flat-square)](https://opensource.org/licenses/MIT)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/avahiplatform?style=flat-square)](https://pypistats.org/packages/avahiplatform)

## Quickstart

### Installation

You can install avahiplatform by running:

```bash
pip install avahiplatform
```

## Welcome to AvahiPlatform! 🚀
Hey there, AI enthusiast! 👋 Are you ready to supercharge your Gen-AI projects? Look no further than AvahiPlatform - your new best friend in the world of Large Language Models (LLMs)!

### What's AvahiPlatform all about?
AvahiPlatform is not just a library; it's your ticket to effortless AI-powered applications. We've taken the complexity out of working with LLMs on AWS Bedrock, so you can focus on what really matters - bringing your brilliant ideas to life!

### Here's what makes AvahiPlatform special:

- Simplicity at its core: With just a few lines of Python code, you'll be up and running. No PhD in AI required! 😉
- AWS Bedrock integration: We've done the heavy lifting to seamlessly connect you with the power of AWS Bedrock. It's like having a direct line to AI goodness!
- Enterprise-ready: Whether you're a solo developer or part of a large team, AvahiPlatform scales with your needs. From proof-of-concept to production, we've got you covered.
- Python-friendly: If you can Python, you can AvahiPlatform. It's that simple!

## 🧱 What can you build with avahiplatform? 

- Text summarization (plain text, local files, S3 files) 📝
- Structured information extraction 🏗️
- Data masking 🕵️‍♀️
- Natural Language to SQL conversion 🗣️➡️💾
- PDF summarization 📄
- Grammar correction ✍️
- Product description generation 🛍️
- Image generation 🎨
- Medical scribing 👩‍⚕️
- ICD-10 code generation 🏥
- CSV querying 📊
- Support for custom prompts and different Anthropic Claude model versions 🧠
- Error handling with user-friendly messages 🛠️

### Basic Usage

```python
import avahiplatform

# Summarization - Text summarization (plain text, local files, S3 files) 📝
summary, input_tokens, output_tokens, cost = avahiplatform.summarize("This is a test string to summarize.")
print("Summary:", summary)

# Structured Extraction - Structured information extraction 🏗️
extraction, input_tokens, output_tokens, cost = avahiplatform.structredExtraction("This is a test string for extraction.")
print("Extraction:", extraction)

# Data Masking - Data masking 🕵️‍♀️
masked_data, input_tokens, output_tokens, cost = avahiplatform.DataMasking("This is a test string for Data Masking.")
print("Masked Data:", masked_data)

# PDF Summarization - PDF summarization 📄
summary, _, _, _ = avahiplatform.summarize("path/to/pdf/file.pdf")
print("PDF Summary:", summary)

# Grammar Correction - Grammar correction ✍️
corrected_text, _, _, _ = avahiplatform.grammarAssistant("Text with grammatical errors")
print("Corrected Text:", corrected_text)

# Product Description Generation - Product description generation 🛍️
description, _, _, _ = avahiplatform.productDescriptionAssistant("SKU123", "Summer Sale", "Young Adults")
print("Product Description:", description)

# Image Generation - Image generation 🎨
image, seed, cost = avahiplatform.imageGeneration("A beautiful sunset over mountains")
print("Generated Image:", image)

# Medical Scribing - Medical scribing 👩‍⚕️
medical_summary, _ = avahiplatform.medicalscribing("path/to/audio.mp3", "input-bucket", "iam-arn")
print("Medical Summary:", medical_summary)
```

## Configuration

### AWS Credentials Setup 🔐
AvahiPlatform requires AWS credentials to access AWS Bedrock and S3 services. You have two options for providing your AWS credentials:

Default AWS Credentials
- Configure your AWS credentials in the ~/.aws/credentials file
- Or use the AWS CLI to set up your credentials

Explicit AWS Credentials
- Pass the AWS Access Key ID and Secret Access Key directly when calling functions

💡 Tip: For detailed instructions on setting up AWS credentials, please refer to the [AWS CLI Configuration Guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html).

Ensuring your AWS credentials are correctly set up will allow you to seamlessly use all of AvahiPlatform's powerful features. If you encounter any issues with authentication, double-check your credential configuration or reach out to our support team for assistance.
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

## Error Handling 🛠️

AvahiPlatform provides user-friendly error messages for common issues, ensuring you can quickly identify and resolve any problems. Here are some examples:

- ❌ Invalid AWS credentials
- 🔍 File not found
- 🔌 Database connection errors
- ⚠️ Unexpected errors

Our detailed error messages will guide you towards quick resolutions, keeping your development process smooth and efficient.

## Requirements 📋

To use AvahiPlatform, make sure you have the following:

- Python 3.9 or higher

### Required Libraries:
```
boto3 >= 1.34.160
loguru >= 0.7.2
python-docx >= 1.1.2
PyMuPDF >= 1.24.9
langchain >= 0.1.12
langchain_community >= 0.0.29
langchain-experimental >= 0.0.54
psycopg2 >= 2.9.9
PyMySQL >= 1.1.1
tabulate >= 0.9.0
langchain-aws >= 0.1.17
```

You can install these dependencies using pip. We recommend using a virtual environment for your project.

## Contributing 🤝

We welcome contributions from the community! Whether you've found a bug or have a feature in mind, we'd love to hear from you. Here's how you can contribute:

1. Open an issue to discuss your ideas or report bugs
2. Fork the repository and create a new branch for your feature
3. Submit a pull request with your changes

Let's make AvahiPlatform even better together!

## License 📄

This project is licensed under the MIT License. See the [Open-source MIT license](https://opensource.org/licenses/MIT) file for details.

## Contact Us 📬

We're here to help! If you have any questions, suggestions, or just want to say hi, feel free to reach out:

- Author: Avahi Tech
- Email: info@avahitech.com
- GitHub: [https://github.com/avahi-org/avahiplatform](https://github.com/avahi-org/avahiplatform)
