import os
import pandas as pd
import logging
from groq import Groq
from uuid import uuid4
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("chatbot")

class ChatBot():

  def __init__(self):
    logger.info("Initializing ChatBot")
    self.data_path = os.environ.get("DATA_PATH", "Data")
    self.faiss_index_path = os.environ.get("FAISS_INDEX_PATH", "faiss_index")
    self.k = 5
    self.model_name = 'sentence-transformers/all-mpnet-base-v2'
    logger.info(f"Using model: {self.model_name}")
    self.load_faiss_index()

  def load_faiss_index(self):
    """Load the FAISS index from disk"""
    logger.info(f'Loading FAISS index from: {self.faiss_index_path}')
    try:
      embeddings = HuggingFaceEmbeddings(model_name=self.model_name)
      self.faiss_index = FAISS.load_local(self.faiss_index_path, embeddings, allow_dangerous_deserialization=True)
      logger.info('FAISS index loaded successfully')
    except Exception as e:
      logger.error(f'Failed to load FAISS index from {self.faiss_index_path}. Exception: {e}')
      logger.warning('Please ensure the index has been built using build_index.py before running the application')
      self.faiss_index = None

  def busca_contexto(self, query):
    """Search for relevant context in the FAISS index"""
    if not self.faiss_index:
        logger.warning("FAISS index is not loaded. Cannot perform search.")
        return []
    
    try:
        logger.info(f"Searching for context with query length: {len(query)}")
        results = self.faiss_index.similarity_search(query, k=self.k)
        logger.info(f"Found {len(results)} context results")
        return [result.page_content for result in results]
    except Exception as e:
        logger.error(f"Error searching for context: {e}")
        return []

  def llamaResponse(self, query):
    """Generate a response using the GROQ API"""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        logger.error("GROQ_API_KEY environment variable not set")
        raise ValueError("GROQ_API_KEY environment variable not set.")
    
    try:
        logger.info("Initializing GROQ client")
        client = Groq(api_key=api_key)
        
        # Get context for the query
        logger.info("Retrieving context for query")
        context = self.busca_contexto(query)
        
        # Create system prompt with context
        system_prompt = f"""
        You are an assistant designed to answer questions related to cybersecurity.
        Please, only answer the question with the context provided, not with your knowledge.
        If the context does not provide the answer to the user question just say 'I don't know'.

        The context is: {context}
        """
        
        logger.info("Calling GROQ API for response")
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": query,
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        
        logger.info("Response received from GROQ API")
        return chat_completion.choices[0].message.content
    
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return f"I apologize, but an error occurred: {str(e)}"
