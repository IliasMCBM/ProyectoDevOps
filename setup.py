from setuptools import setup, find_packages

setup(
    name="denexus-chatbot",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    description="A chatbot built using Retrieval Augmented Generation (RAG)",
    author="DeNexus Team",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.10",
    install_requires=[
        "groq>=0.5.0",
        "langchain>=0.1.0",
        "langchain-community>=0.0.20",
        "langchain-core>=0.1.20",
        "langchain-huggingface>=0.0.1",
        "pandas>=1.0.0",
        "faiss-cpu>=1.7.0",
        "sentence-transformers>=2.2.0",
        "streamlit>=1.0.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "build-index=build_index:build_faiss_index",
        ],
    },
) 