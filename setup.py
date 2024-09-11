from setuptools import find_packages, setup

with open("./README.md", "r") as f:
    long_description = f.read()

setup(
    name="avahiplatform",
    version="0.0.7",
    description="An avahiai library which makes your Gen-AI tasks effortless",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/avahi-org/avahiplatform",
    author="Avahi AWS",
    author_email="info@avahitech.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    install_requires=["boto3>=1.34.160", "loguru>=0.7.2", "python-docx>=1.1.2", "PyMuPDF>=1.24.9", "langchain>=0.2.16",
                      "langchain_community>=0.2.16", "langchain-experimental>=0.0.64", "psycopg2>=2.9.9",
                      "PyMySQL>=1.1.1", "tabulate>=0.9.0", "langchain-aws>=0.1.17","chromadb==0.5.3", "langchain-chroma>=0.1.3", "unstructured>=0.12.3", "unstructured[pdf]", "pillow>=10.4.0","pandas"],
    extras_require={
        "dev": ["twine>=4.0.2"],
        "pdf": ["unstructured[pdf]"]
    },
    python_requires=">=3.9",
)
