# AvahiPlatform

[![GitHub stars](https://img.shields.io/github/stars/avahi-org/avahiplatform)](https://star-history.com/#avahiplatform/avahiplatform)
[![PyPI - License](https://img.shields.io/pypi/l/avahiplatform?style=flat-square)](https://opensource.org/licenses/MIT)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/avahiplatform?style=flat-square)](https://pypistats.org/packages/avahiplatform)

## Quickstart

### Installation

You can install AvahiPlatform by running:

```bash
pip install avahiplatform -U
```

## Welcome to AvahiPlatform! 🚀

Hey there, AI enthusiast! 👋 Are you ready to supercharge your Gen-AI projects? Look no further than AvahiPlatform - your new best friend in the world of Large Language Models (LLMs)!

With AvahiPlatform, you can **create and deploy GenAI applications on Bedrock in just 60 seconds**. It's that fast and easy!

### What's AvahiPlatform all about?

AvahiPlatform is not just a library; it's your ticket to effortless AI-powered applications. We've taken the complexity out of working with LLMs on AWS Bedrock, so you can focus on what really matters - bringing your brilliant ideas to life!

### Here's what makes AvahiPlatform special:

- **Simplicity at its core**: With just a few lines of Python code, you'll be up and running. No PhD in AI required! 😉
- **AWS Bedrock integration**: We've done the heavy lifting to seamlessly connect you with the power of AWS Bedrock. It's like having a direct line to AI goodness!
- **Enterprise-ready**: Whether you're a solo developer or part of a large team, AvahiPlatform scales with your needs. From proof-of-concept to production, we've got you covered.
- **Python-friendly**: If you can Python, you can AvahiPlatform. It's that simple!
- **Global Gradio URL**: Quickly generate and share a URL to allow others to experience your functionality directly from your running environment.
- **Observability with metrics tracking and optional Prometheus integration** 📊

## 🧱 What can you build with AvahiPlatform?

- **Summarization** (plain text, local files, S3 files) 📝
- **Image and Video Summarization** 📹
- **Structured Information Extraction** 🏗️
- **Data Masking** 🕵️‍♀️
- **Grammar Correction** ✍️
- **Product Description Generation** 🛍️
- **ICD-10 Code Generation** 🏥
- **Image Generation** 🎨
- **Image similarity** 📊
- **Medical Scribing** 👩‍⚕️
- **CSV Querying** 📊
- **Natural Language to SQL Conversion** 🗣️➡️💾
- **Chatbot** 🤖
- **Global Gradio URL for Any Functionality/Features** 🌐
- **Support for Custom Prompts and Different Anthropic Claude Model Versions** 🧠
- **Error Handling with User-Friendly Messages** 🛠️

## New version migration guide

[AvahiPlatform SDK changes](https://github.com/avahi-org/avahiplatform/blob/main/sdk_new_version_migration-guide.md)

## New feature integration guide

[AvahiPlatform SDK changes](https://github.com/avahi-org/avahiplatform/blob/main/sdk_feature-structure-guide.md)

### Basic Usage

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1D323xAdN0eiM070tjPIE0cofkQLR4zpF?usp=sharing)

With the provided Google Colab notebook, you can easily test and explore the features of this project. Simply click the "Open In Colab" badge above to get started!

```python
import avahiplatform
import os
import sys

# Add the parent directory of logicsdk to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure AvahiPlatform
avahiplatform.configure(default_model_name='amazon.nova-pro-v1:0')
# You can pass all this configuration:                 aws_access_key_id, aws_secret_access_key, aws_session_token, region_name, input_tokens_price, output_tokens_price, input_bucket_name_for_medical_scribing, iam_arn_for_medical_scribing, default_model_name
 

# Initialize observability
avahiplatform.initialize_observability(metrics_file='./metrics.jsonl', start_prometheus=True, prometheus_port=8007)

# Launch Chat UI
chatbot = avahiplatform.chatbot
chatbot.launch_chat_ui()

# Summarize any document Example
summary = avahiplatform.summarize_document(document_path='./Test/df1.csv')
print("Summary:", summary['response_text'])

# Summarize text Example
summary = avahiplatform.summarize_text(text="sameple text")
print("Summary:", summary['response_text'])

# Summarize s3 document Example
summary = avahiplatform.summarize_s3_document(s3_path='s3://avahi-python-package-data/Patient’s clinical history.txt')
print("Summary:", summary['response_text'])

# Summarize image Example
summary = avahiplatform.summarize_image(image_path='./Test/041_400NB_Ramp_to_Glenridge_Conn_2024-09-13T17-30-20.340+00-00.jpg')
print("Summary:", summary['response_text'])

# Summarize video Example
summary = avahiplatform.summarize_video(video_path='./Test/041_400NB_Ramp_to_Glenridge_Conn_2024-09-13T17-30-20.340+00-00.mp4')
print("Summary:", summary['response_text'])

# Data Masking Example
masked_data = avahiplatform.mask_data(input_content="s3://avahi-python-package-data/Patient’s clinical history.txt")
print("Masked Data:", masked_data['response_text'])

# Structured Extraction Example
extraction = avahiplatform.structuredExtraction(input_content="s3://avahi-python-package-data/Patient’s clinical history.txt")
print("Extraction:", extraction['response_text'])

# Grammar Correction Example
corrected_text = avahiplatform.grammar_assistant(input_content="I in am english speaker and I like write a sentence english in.")
print("Corrected Text:", corrected_text['response_text'])

# Product Description Generation Example
description = avahiplatform.product_description_assistant("SKU123", "Summer Sale", "Young Adults")
print("Product Description:", description['response_text'])

# Image Generation Example
avahiplatform.configure(default_model_name='stability.stable-diffusion-xl-v1')
result = avahiplatform.generate_image(image_prompt="A beautiful sunset over mountains")
output[0].save('./Test/output.png')
print(f"output: {output[1]}")

# ICD-10 Code Generation Example
icd_codes = avahiplatform.generate_icdcode(input_content="s3://avahi-python-package-data/Patient’s clinical history.txt")
print("ICD-10 Codes:", icd_codes)

# Medical Scribing Example
medical_summary = avahiplatform.medicalscribing(audio_filepath="./Test/Doctor-patient-conversation.mp3")
print("Medical Summary:", medical_summary)

# CSV Querying Example
csv_files = {
    "df1": "./Test/df1.csv",
    "df2": "./Test/df2.csv"
}
csv_query_answer = avahiplatform.query_csv("How many entries are there in df1?", csv_file_paths=csv_files)
print(f"CSV Query Answer: {csv_query_answer}")


# Image similarity Example
image1 = "./Test/image_1.jpg"
image2 = "./Test/image_2.jpg"
similarity = avahiplatform.get_similar_images(image1, image2)
print(f"Similarity: {similarity}")
```

## Features

| Category | Feature | Description |
|----------|---------|-------------|
| Text Processing | Text Summarization | Summarize plain text, local files, or files stored in S3 |
| | Grammar Correction | Automatically correct grammatical errors in your text |
| Multimedia | Image and Video Summarization | Generate summaries for images and videos |
| | Image Generation | Create custom images using state-of-the-art AI models |
| | Image Similarity | Find and compare similar images in your dataset |
| Data Processing | Structured Information Extraction | Extract structured data from unstructured text sources |
| | Data Masking | Protect sensitive information by masking data in your datasets |
| | CSV Querying | Perform natural language queries on your CSV files |
| Healthcare | ICD-10 Code Generation | Generate ICD-10 codes from clinical documents |
| | Medical Scribing | Transcribe and summarize medical conversations from audio files |
| E-commerce | Product Description Generation | Generate compelling product descriptions based on SKU, campaign, and target audience |
| | Chatbot | Deploy interactive chatbots with customizable prompts and behaviors |
| Platform Features | Global Gradio URL | Generate shareable URLs for any of your deployed functionalities |
| | Custom Prompts and Models | Support for custom prompts and different Anthropic Claude model versions |
| | Error Handling | Receive clear and actionable error messages for common issues |

## Usage Examples

### Summarization

```python
import avahiplatform

# Summarize plain text
summary = avahiplatform.summarize_text(text="sample text")
print("Summary:", summary['response_text'])

# Summarize a local file
summary = avahiplatform.summarize_document(document_path='path/to/local/file.txt')
print("Summary:", summary['response_text'])

# Summarize a file from S3
summary = avahiplatform.summarize_s3_document(s3_path='s3://bucket-name/file.txt')
print("Summary:", summary['response_text'])

# Summarize an image
image_summary = avahiplatform.summarize_image(image_path='./Test/image.jpg')
print("Image Summary:", image_summary['response_text'])

# Summarize a video
video_summary = avahiplatform.summarize_video(video_path='./Test/video.mp4', system_prompt="Summarize the video content.")
print("Video Summary:", video_summary['response_text'])
```

### Structured Information Extraction

```python
extraction = avahiplatform.structuredExtraction(input_content="s3://avahi-python-package-data/Patient’s clinical history.txt") # anything local path, plain text or s3 path
print("Extraction:", extraction['response_text'])
```

### Data Masking

```python
masked_data = avahiplatform.mask_data(input_content="s3://avahi-python-package-data/Patient’s clinical history.txt") # anything local path, plain text or s3 path
print("Masked Data:", masked_data['response_text'])
```

### Grammar Correction

```python
corrected_text = avahiplatform.grammar_assistant(input_content="I in am english speaker and I like write a sentence english in.") # plain text or s3 path
print("Corrected Text:", corrected_text['response_text'])
```

### Product Description Generation

```python
description = avahiplatform.product_description_assistant("SKU123", "Summer Sale", "Young Adults") # product name, season, target audience
print("Product Description:", description['response_text'])
```

### Image Generation

```python
# Remember to give us-west-2 in region name in configuration as many stability models are in us-west-2.
avahiplatform.configure(default_model_name='stability.stable-diffusion-xl-v1')
result = avahiplatform.generate_image(image_prompt="A beautiful sunset over mountains")
result[0].save('./Test/output.png')
print(f"output: {result[1]}")
```

### Image Similarity

```python
image1 = "./Test/image_1.jpg"
image2 = "./Test/image_2.jpg"
similarity = avahiplatform.get_similar_images(image1, image2)
print(f"Similarity: {similarity}")

# You can also compare multiple images contained in the folder
image1 = "./Test/image_1.jpg"
folder = "./Test/"      
similarity = avahiplatform.get_similar_images(image1, folder)
print(f"Similarity: {similarity}")

# You can also compare multiple s3 images contained in the folder
image1 = "s3://bucket-name/image_1.jpg"
folder = "s3://bucket-name/"
similarity = avahiplatform.get_similar_images(image1, folder)
print(f"Similarity: {similarity}")
```

### ICD-10 Code Generation

```python
icd_codes = avahiplatform.generate_icdcode(input_content="s3://avahi-python-package-data/Patient’s clinical history.txt") # anything local path, plain text or s3 path
print("ICD-10 Codes:", icd_codes)
```

### Medical Scribing

```python
medical_summary = avahiplatform.medicalscribing(audio_filepath="./Test/Doctor-patient-conversation.mp3") 
print("Medical Summary:", medical_summary)
```

### CSV Querying

```python
csv_files = {
    "df1": "./Test/df1.csv",
    "df2": "./Test/df2.csv"
}
csv_query_answer = avahiplatform.query_csv("How many entries are there in df1?", csv_file_paths=csv_files) # local filepath or s3 path
print(f"CSV Query Answer: {csv_query_answer}")
```

### Natural Language to SQL

```python
result = avahiplatform.nl2sql(
    "Show me all users who signed up in the last month.",
    db_type="postgresql",
    username="user",
    password="pass",
    host="localhost",
    port=5432,
    dbname="mydb"
)
print("SQL Result:", result)
```

### Retrieval-Augmented Generation (RaG) with Sources

```python
answer, sources = avahiplatform.perform_rag_with_sources(
    "What is Kafka?",
    s3_path="s3://your-bucket-path-where-doc-is-present/"
)
print(f"Generated Answer: {answer}")
print(f"Retrieved Sources: {sources}")
```

### Semantic Search

```python
similar_docs = avahiplatform.perform_semantic_search(
    "What is Kafka?",
    s3_path="s3://your-bucket-path-where-doc-is-present/"
)
print(f"Similar Documents: {similar_docs}")
```

### Chatbot

```python
chatbot = avahiplatform.chatbot
chatbot.initialize_system(system_prompt="You are a Python developer. You only answer queries related to Python. If you receive any other queries, please respond with 'I don't know.'")

# Chat with the chatbot
response = chatbot.chat(user_input="Create me a function to add 2 numbers")
print(f"Chatbot Response: {response["response_text"]}")

response = chatbot.chat(user_input="What is Avahi?")
print(f"Chatbot Response: {response["response_text"]}")

# Get chat history
history = chatbot.get_history()
print(f"Chat History: {history}")

# Clear chat history
chatbot.clear_history()
```

### Global Gradio URL for Any Functionality/Features 🌐

```python
# For Summarization
avahiplatform.summarize_document.create_url()

# For Medical Scribing
avahiplatform.medicalscribing.create_url()

# For CSV Querying
avahiplatform.query_csv.create_url()

# For RaG with Sources
avahiplatform.perform_rag_with_sources.create_url()

# For Chatbot
chatbot = avahiplatform.chatbot
chatbot.create_url()
```

This will generate a global URL which you can share with anyone, allowing them to explore and utilize any of the features running in your environment using the AvahiPlatform SDK.

## Configuration

### AWS Credentials Setup 🔐

AvahiPlatform requires AWS credentials to access AWS Bedrock and S3 services. You have two options for providing your AWS credentials:

#### Default AWS Credentials
- Configure your AWS credentials in the `~/.aws/credentials` file.
- Or use the AWS CLI to set up your credentials.

#### Explicit AWS Credentials
- Pass the AWS Access Key ID and Secret Access Key directly when calling functions.

💡 **Tip**: For detailed instructions on setting up AWS credentials, please refer to the [AWS CLI Configuration Guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html).

Ensuring your AWS credentials are correctly set up will allow you to seamlessly use all of AvahiPlatform's powerful features. If you encounter any issues with authentication, double-check your credential configuration or reach out to our support team for assistance.

### Additional Configuration for Medical Scribing

To use medical scribing features, configure the IAM role and input bucket name:

```python
avahiplatform.configure(
    iam_arn_for_medical_scribing="arn:aws:iam::<account-id>:role/<role-name>",
    input_bucket_name_for_medical_scribing="your-input-bucket-name",
    default_model_name='amazon.nova-pro-v1:0'
)
```

**IAM Policy for Medical Scribing:**

Ensure the IAM role has the following inline policy:

```json
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
```

Additionally, the role/user should have full access to both **Transcribe** and **Comprehend** services.

## Error Handling 🛠️

AvahiPlatform provides user-friendly error messages for common issues, ensuring you can quickly identify and resolve any problems. Here are some examples:

- ❌ **Invalid AWS credentials**: Ensure your AWS credentials are correctly configured.
- 🔍 **File not found**: Verify the file paths provided exist and are accessible.
- 🔌 **Database connection errors**: Check your database credentials and network connectivity.
- ⚠️ **Unexpected errors**: Review the error message and consult the documentation or support.

Our detailed error messages will guide you towards quick resolutions, keeping your development process smooth and efficient.

## Requirements 📋

To use AvahiPlatform, make sure you have the following:

- **Python 3.9 or higher**

### Required Libraries:

```bash
boto3>=1.34.160
python-docx>=1.1.2
PyMuPDF>=1.24.9
loguru>=0.7.2
setuptools>=72.1.0
sqlalchemy>=2.0.35
gradio>=4.44.0
tabulate>=0.9.0
python-magic-bin>=0.4.14
pillow>=10.4.0
pandas>=2.2.3
gradio>=4.44.0
typing_extensions>=4.0.0
prometheus-client>=0.21.0
python-magic>=0.4.27
anthropic>=0.42.0
```

You can install these dependencies using pip. We recommend using a virtual environment for your project.

```bash
pip install -r requirements.txt
```

## Contributors 🎉

We would like to thank the following individuals for their valuable contributions:

### Avahi Team Members:
- **Abel Cotoñeto Padilla**
- **Sergio Martinez**
- **Nashita Khandaker**
- **Diana Lopez**
- **Shivangi Motwani**
- **Urvish Patel**
- **Amol Walnuj**
- **Om Patel**
- **Vivek Gohel**

### AWS Team Member:
- **Jon Turdiev**

## License 📄

This project is licensed under the MIT License. See the [Open-source MIT license](https://opensource.org/licenses/MIT) file for details.

## Contributing 🤝

We welcome contributions from the community! Whether you've found a bug or have a feature in mind, we'd love to hear from you. Here's how you can contribute:

1. **Open an issue** to discuss your ideas or report bugs.
2. **Fork the repository** and create a new branch for your feature.
3. **Submit a pull request** with your changes.

Let's make AvahiPlatform even better together!

## Contact Us 📬

We're here to help! If you have any questions, suggestions, or just want to say hi, feel free to reach out:

- **Author**: Avahi Tech
- **Email**: [info@avahitech.com](mailto:info@avahitech.com)
- **GitHub**: [https://github.com/avahi-org/avahiplatform](https://github.com/avahi-org/avahiplatform)

## Authors ✍️

Lead by [Dhruv Motwani](https://github.com/DhruvAvahi)

**Contributors:**
- [Abel Cotoneto Padilla](https://github.com/AbelCotonetoPadilla)
- [Amol Dwalunj-Awahi](https://github.com/Amoldwalunj-awahi)
- [Diana Avahitech](https://github.com/diana-avahitech)
- [Jon Turdiev](https://github.com/JonTurdiev)
- [Nashita K](https://github.com/nashitak)
- [Om Avahi](https://github.com/om-avahi)
- [Sergio Martinez](https://github.com/SergioMartinezAvahitech)
- [Vivek Avahi](https://github.com/vivekavahi)

---

Thank you for choosing AvahiPlatform! We are excited to see the amazing applications you'll build.