# AvahiPlatform Python SDK Changes

## Table of Contents
1. [Introduction](#introduction)
2. [Major SDK Changes](#major-sdk-changes)
3. [Package Initialization Changes](#package-initialization-changes)
4. [Function-by-Function Changes](#function-by-function-changes)
5. [Return Value Changes](#return-value-changes)

## Introduction

This document outlines the changes in the AvahiPlatform Python SDK to help developers transition from the previous version to the new version. It provides a comprehensive comparison of function calls and usage patterns.

## Major SDK Changes

### Package Import and Setup
```python
# Previous Version
import avahiplatform

# New Version
import avahiplatform
avahiplatform.configure(
    default_model_name='amazon.nova-pro-v1:0',
    # Other optional parameters...
)
```

## Function-by-Function Changes

### Summarization Changes

| Feature | Old API | New API | Notes |
|---------|---------|---------|--------|
| Text Summarization | `avahiplatform.summarize("text")` | `avahiplatform.summarize_text(text="text")` | Split into specific function |
| Document Summarization | `avahiplatform.summarize("path/to/file.txt")` | `avahiplatform.summarize_document(document_path='path/to/file.txt')` | More explicit parameter naming |
| S3 Document Summarization | `avahiplatform.summarize("s3://bucket/file.txt")` | `avahiplatform.summarize_s3_document(s3_path='s3://bucket/file.txt')` | Dedicated S3 function |
| Image Summarization | Not available | `avahiplatform.summarize_image(image_path='path/to/image.jpg')` | New feature |
| Video Summarization | Not available | `avahiplatform.summarize_video(video_path='path/to/video.mp4')` | New feature |

### Other Function Changes

| Feature | Previous Version | New Version | Notes |
|---------|-----------------|-------------|--------|
| Data Masking | `avahiplatform.DataMasking("text")` | `avahiplatform.mask_data(input_content="text")` | Renamed for consistency |
| Structure Extraction | `avahiplatform.structredExtraction("text")` | `avahiplatform.structuredExtraction(input_content="text")` | Fixed typo in function name |
| Grammar Correction | `avahiplatform.grammarAssistant("text")` | `avahiplatform.grammar_assistant(input_content="text")` | Standardized naming |
| ICD Code Generation | `avahiplatform.icdcoding("text")` | `avahiplatform.generate_icdcode(input_content="text")` | More descriptive name |
| Product Description | `avahiplatform.productDescriptionAssistant("sku", "event", "segment")` | `avahiplatform.product_description_assistant("sku", "event", "segment")` | Snake case naming |
| Image Generation | `avahiplatform.imageGeneration(prompt="text")` | `avahiplatform.generate_image(image_prompt="text")` | Renamed for consistency |
| Image Similarity | `avahiplatform.imageSimilarity(image1, image2)` | `avahiplatform.get_similar_images(image1, image2)` | Renamed for consistency |

## Return Value Changes

### Previous Version Return Format
```python
# Previous Version - Multiple return values
summary, input_tokens, output_tokens, cost = avahiplatform.summarize("text")
print("Summary:", summary)
```

### New Version Return Format
```python
# New Version - Dictionary return value
result = avahiplatform.summarize_text(text="text")
print("Summary:", result['response_text'])
```

## Migration Examples

### Summarization Example

```python
# Previous Version
summary, _, _, _ = avahiplatform.summarize("This is a test string")
print("Summary:", summary)

# New Version
# For text:
summary = avahiplatform.summarize_text(text="This is a test string")
print("Summary:", summary['response_text'])

# For documents:
summary = avahiplatform.summarize_document(document_path='./document.pdf')
print("Summary:", summary['response_text'])

# For S3:
summary = avahiplatform.summarize_s3_document(s3_path='s3://bucket/file.txt')
print("Summary:", summary['response_text'])
```

### Data Masking Example

```python
# Previous Version
masked_data, _, _, _ = avahiplatform.DataMasking("sensitive text")
print("Masked:", masked_data)

# New Version
result = avahiplatform.mask_data(input_content="sensitive text")
print("Masked:", result['response_text'])
```

### Image Summarization Example

```python
# Previous Version
image, seed, cost = avahiplatform.imageGeneration("A beautiful sunset over mountains")
print("Generated Image:", image)


# New Version
avahiplatform.configure(default_model_name='stability.stable-diffusion-xl-v1')
result = avahiplatform.generate_image(image_prompt="A beautiful sunset over mountains")
output[0].save('./Test/output.png')
print(f"output: {output[1]}")
```

### Image Similarity Example

```python    
# Previous Version
similarity, _, _, _ = avahiplatform.imageSimilarity(image1, image2)
print("Similarity:", similarity)

# New Version   
Similarity = avahiplatform.get_similar_images(image1, image2)
print("Similarity:", Similarity)
```

## Key Improvements in New SDK

1. **Specialized Functions**: Each task has its own dedicated function instead of overloaded methods
2. **Consistent Naming**: Uses Python's standard snake_case naming convention
3. **Better Parameter Names**: More descriptive parameter names
4. **Structured Returns**: Consistent dictionary-based return values
5. **New Features**: Added support for image and video summarization
6. **Explicit Configuration**: More control over SDK configuration
7. **Improved Input Handling**: Clear separation between different types of inputs (text, file, S3)

## Best Practices for Updating Your Code

1. **Initialize SDK**: Start with the `configure()` method in the new version
2. **Use Specific Functions**: Replace generic function calls with specific ones
3. **Update Return Value Handling**: Modify code to work with dictionary responses
4. **Use Named Parameters**: Update to use explicit parameter names
5. **Review Error Handling**: Update error handling for new return format

## Need Help?

If you encounter any issues while updating your code:
1. Check the complete documentation
2. Review the examples in our GitHub repository
4. Open an issue on our GitHub repository