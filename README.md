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

With AvahiPlatform, you can **create and deploy GenAI applications on Bedrock in just 60 seconds**. It's that fast and easy!
### What's AvahiPlatform all about?
AvahiPlatform is not just a library; it's your ticket to effortless AI-powered applications. We've taken the complexity out of working with LLMs on AWS Bedrock, so you can focus on what really matters - bringing your brilliant ideas to life!

### Here's what makes AvahiPlatform special:

- Simplicity at its core: With just a few lines of Python code, you'll be up and running. No PhD in AI required! 😉
- AWS Bedrock integration: We've done the heavy lifting to seamlessly connect you with the power of AWS Bedrock. It's like having a direct line to AI goodness!
- Enterprise-ready: Whether you're a solo developer or part of a large team, AvahiPlatform scales with your needs. From proof-of-concept to production, we've got you covered.
- Python-friendly: If you can Python, you can AvahiPlatform. It's that simple!
- Global Gradio URL: Quickly generate and share a URL to allow others to experience your functionality directly from your running environment.
- Observability with metrics tracking and optional Prometheus integration 📊

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
- Retrieval-Augmented Generation (RaG) with Sources 🔍📚
- Semantic Search 🔎💡
- Chatbot 🤖
- Global gradio URL for Any Functionality/Features 🌐
- Support for custom prompts and different Anthropic Claude model versions 🧠
- Error handling with user-friendly messages 🛠️

### Basic Usage

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1D323xAdN0eiM070tjPIE0cofkQLR4zpF?usp=sharing)

With the provided Google Colab notebook, you can easily test and explore the features of this project. Simply click the "Open In Colab" badge above to get started!


```python
import avahiplatform

# Initialize observability - You can access these metrics on specified prometheus_port, i.e in this case: 8000
avahiplatform.initialize_observability(metrics_file='./metrics.jsonl', start_prometheus=True, prometheus_port=8000)
# If you don't want to get prometheus metrics avahiplatform.initialize_observability(metrics_file='./metrics.jsonl', start_prometheus=True, prometheus_port=8000)

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

# Icd10code Generation 🏥
codes = avahiplatform.icdcoding("Any prescription or path/to/prescription.txt")
print("Icd 10 codes:", codes)

# CSV querying 📊
csv_files = {
    "df1": "path/to/1st_csv.csv",
    "df2": "path/to/2nd_csv.csv"
}
# In the `csv_files` dictionary, you can pass any number of CSV files 1 or more than 1, but they must follow the structure where the key is the name and the value is the path(s3_path or local_path).
csv_query_answer = avahiplatform.query_csv("How many active locations are there in each region?",
                                           csv_file_paths=csv_files)
print(f"csv query answer: {csv_query_answer}")

# RaG with Sources 🔍📚
answer, sources = avahiplatform.perform_rag_with_sources("What is kafka?", s3_path="s3://your-bucket-path-where-doc-is-present/")
print(f"Generated answer: {answer}")
print(f"Retrieved sourcce: {sources}")

# Semantic Search 🔎💡
similar_docs = avahiplatform.perform_semantic_search("What is kafka?", s3_path="s3://your-bucket-path-where-doc-is-present/")
print(f"similar docs: {similar_docs}")

# Chatbot 🤖
--------------------------------
chatbot = avahiplatform.chatbot()
chatbot.initialize_instance(system_prompt="You are a python developer, you only answer queries related to python only, if you get any other queries, then please say I don't know")
chatbot_response = chatbot.chat(user_input="Create me a function to add 2 numbers")
print(f"chatbot_response: {chatbot_response}")

chatbot_response = chatbot.chat(user_input="What is avahi?")
print(f"chatbot_response: {chatbot_response}")

# Get chat history
chatbot_history = chatbot.get_history()
print(chatbot_history)

# clear_chat_history
chatbot.clear_history()
---------------------------------------

# Few examples for getting global gradio URL for Any Functionality/Features 🌐

# For summarizer
avahiplatform.summarize.create_url()

# For medical-scribing
avahiplatform.medicalscribing.create_url()

# For csv querying
avahiplatform.query_csv.create_url()

# For RAG with sources
avahiplatform.perform_rag_with_sources.create_url()

# For chatbot we first have initialize chatbot and then we can create the url
chatbot = avahiplatform.chatbot()
chatbot.create_url()

# This will generate a global URL which you can share with anyone, allowing them to explore and utilize any of the features which is running in your environment using avahiplatform sdk
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
csv_files = {
    "df1": "path/to/1st_csv.csv",
    "df2": "path/to/2nd_csv.csv"
}
# In the `csv_files` dictionary, you can pass any number of CSV files 1 or more than 1, but they must follow the structure where the key is the name and the value is the path(s3_path or local_path).
csv_query_answer = avahiplatform.query_csv("<Your query goes here>",
                                           csv_file_paths=csv_files)
print(f"csv query answer: {csv_query_answer}")
```

### Global Gradio URL for Any Functionality/Features 🌐

```python
avahiplatform.feature_name.create_url()

For example:
- avahiplatform.summarize.create_url()
- avahiplatform.medicalscribing.create_url()
- avahiplatform.query_csv.create_url()

# For interactive chatbot
chatbot = avahiplatform.chatbot()
chatbot.create_url()
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
boto3==1.34.160
python-docx==1.1.2
PyMuPDF==1.24.9
loguru==0.7.2
setuptools==72.1.0
chromadb==0.5.3
sqlalchemy>=2.0.35
gradio>=4.44.0
tabulate==0.9.0
python-magic-bin>=0.4.14
pillow>=10.4.0
pandas>=2.2.3
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
