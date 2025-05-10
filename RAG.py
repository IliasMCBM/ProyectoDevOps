import os
import pandas as pd
from groq import Groq
from uuid import uuid4
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document



class ChatBot():

  def __init__(self):
    self.data_path = os.environ.get("DATA_PATH", "data")
    self.faiss_index_path = os.environ.get("FAISS_INDEX_PATH", "faiss_index")
    self.k = 5
    self.model_name = 'sentence-transformers/all-mpnet-base-v2'
    self.load_faiss_index()

  def load_faiss_index(self):
    embeddings = HuggingFaceEmbeddings(model_name=self.model_name)
    try:
      print(f'Loading FAISS index from: {self.faiss_index_path}')
      self.faiss_index = FAISS.load_local(self.faiss_index_path, embeddings, allow_dangerous_deserialization=True)
      print('FAISS index loaded successfully.')
    except Exception as e:
      print(f'ERROR: Failed to load FAISS index from {self.faiss_index_path}. Exception: {e}')
      print('Please ensure the index has been built using build_index.py before running the application.')
      self.faiss_index = None

  def busca_contexto(self, query):
    if not self.faiss_index:
        print("FAISS index is not loaded. Cannot perform search.")
        return []
    results = self.faiss_index.similarity_search(query, k= self.k)
    return [result.page_content for result in results]


  def llamaResponse(self, query):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set.")
    client = Groq(
        # This is the default and can be omitted
        api_key=api_key,
    )

    chat_completion = client.chat.completions.create(

        messages=[

            {
                "role": "system",

                "content": f"""

                You are an assitant designed to answer questions related to cibersecurity.
                Please, only answer the question with the context provided, not with your knowledge. If the context
                do not provide the answer to the user question just say 'I don't know'.

                The context is: {self.busca_contexto(query)}
                """
            },

            {

                "role": "user",

                "content": query,

            }

        ],

        model="llama-3.3-70b-versatile",

    )

    return chat_completion.choices[0].message.content
