from setuptools import find_packages, setup

with open("./README.md", "r") as f:
    long_description = f.read()

setup(
    name="avahiplatform",
    version="0.0.12",
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
    install_requires=["boto3>=1.34.160", "loguru>=0.7.2", "python-docx>=1.1.2", "PyMuPDF>=1.24.9",
                      "psycopg2>=2.9.9", "PyMySQL>=1.1.1", "tabulate>=0.9.0", "chromadb==0.5.3",
                      "pillow>=10.4.0", "sqlalchemy>=2.0.35", "pandas>=2.2.3", "gradio>=4.44.0",
                      "typing_extensions>=4.0.0", "prometheus-client>=0.21.0"],
    extras_require={
        "dev": ["twine>=4.0.2"]
    },
    python_requires=">=3.9",
)
