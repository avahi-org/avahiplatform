# Avahi Platform: Guide to Structuring New Features

## Table of Contents
1. [Introduction](#introduction)
2. [Directory Structure Overview](#directory-structure-overview)
3. [Step-by-Step Feature Integration Guide](#step-by-step-feature-integration-guide)
4. [Best Practices](#best-practices)
5. [Code Examples](#code-examples)

## Introduction
This document outlines the process of integrating new features into the Avahi Platform while maintaining its architectural integrity and code organization. The platform follows a modular approach where common functionalities are abstracted into helper classes while feature-specific logic resides in the src directory.

## Directory Structure Overview
```
avahiplatform/
├── helpers/
│   ├── chats/
│   │   ├── bedrock_chat.py
│   │   └── base_chat.py
│   └── connectors/
│       ├── boto_helper.py
│       ├── s3_helper.py
│       └── utils.py
├── src/
│   ├── feature_name.py
│   └── platform_core.py
└── __init__.py
```

## Step-by-Step Feature Integration Guide

### 1. Identify Helper Components
Before implementing a new feature, analyze which components can leverage existing helper classes:

- **BotoHelper**: AWS service client creation and management
- **S3Helper**: S3 operations
- **BedrockChat**: LLM interactions
- **Utils**: Common utility functions

### 2. Create Feature Implementation File
Place your main feature implementation in the `src` directory:

1. Create a new file: `src/your_feature_name.py`
2. Structure the class to use helper components
3. Implement feature-specific logic

### 3. Update Platform Core
Modify `platform_core.py` to integrate your feature:

1. Import your feature class
2. Initialize it in `AvahiPlatform.__init__()`
3. Create wrapper methods with observability tracking
4. Add function exports

### 4. Update __init__.py
Update the package's `__init__.py` to expose your feature:

1. Add feature export in `_init_platform_exports()`
2. Update global variable declarations

## Best Practices

### Helper Class Usage
- **DO**: Use helper classes for:
  - AWS service interactions (BotoHelper)
  - S3 operations (S3Helper)
  - LLM interactions (BedrockChat)
  - Common utilities (Utils)
- **DON'T**: Reimplement functionality that exists in helper classes

### Feature Implementation
- **DO**:
  - Keep feature-specific logic in src/
  - Use dependency injection for helper classes
  - Implement error handling with Utils.get_user_friendly_error
  - Add observability tracking
- **DON'T**:
  - Mix helper functionality with feature logic
  - Create direct AWS client instances

## Code Examples

### 1. Feature Implementation Template
```python
# src/new_feature.py
from loguru import logger
from avahiplatform.helpers.connectors.utils import Utils

class NewFeature:
    def __init__(self, bedrockchat, s3_helper):
        self.bedrockchat = bedrockchat
        self.s3_helper = s3_helper
    
    def process_input(self, input_content, system_prompt=None, stream=False):
        try:
            if os.path.exists(input_content):
                return self.process_local_file(input_content, system_prompt, stream)
            elif input_content.startswith('s3://'):
                return self.process_s3_file(input_content, system_prompt, stream)
            else:
                return self.process_text(input_content, system_prompt, stream)
        except Exception as e:
            user_friendly_error = Utils.get_user_friendly_error(e)
            logger.error(user_friendly_error)
            return "None"
```

### 2. Platform Core Integration
```python
# platform_core.py
from avahiplatform.src.new_feature import NewFeature

class AvahiPlatform:
    def __init__(self, ...):
        # Existing initialization code...
        
        self.new_feature = NewFeature(
            bedrockchat=self.bedrockchat,
            s3_helper=self.s3_helper
        )
        
        # Add wrapper with observability
        self.new_feature_function = FunctionWrapper(self._new_feature_function)
    
    @track_observability
    def _new_feature_function(self, input_content, system_prompt=None, stream=False):
        try:
            return self.new_feature.process_input(input_content, system_prompt, stream)
        except Exception as e:
            user_friendly_error = Utils.get_user_friendly_error(e)
            logger.error(user_friendly_error)
            return "None"
```

### 3. __init__.py Update
```python
# __init__.py
def _init_platform_exports():
    global new_feature_function  # Add global declaration
    
    # Existing initialization code...
    
    new_feature_function = _platform_instance.new_feature_function  # Add export
```

## Common Pitfalls to Avoid

1. **Direct AWS Client Creation**
   ```python
   # DON'T
   s3_client = boto3.client('s3')
   
   # DO
   s3_client = self.boto_helper.create_client('s3')
   ```

2. **Missing Error Handling**
   ```python
   # DON'T
   def process_data(self, data):
       return self.some_operation(data)
   
   # DO
   def process_data(self, data):
       try:
           return self.some_operation(data)
       except Exception as e:
           user_friendly_error = Utils.get_user_friendly_error(e)
           logger.error(user_friendly_error)
           return "None"
   ```

3. **Duplicate Helper Functions**
   ```python
   # DON'T: Create new S3 upload function
   def upload_to_s3(self, file_path, bucket, key):
       s3_client.upload_file(file_path, bucket, key)
   
   # DO: Use S3Helper
   result = self.s3_helper.upload_file(file_path, bucket, key)
   ```

Remember to always follow these guidelines when implementing new features to maintain code consistency and prevent duplication of functionality across the platform.