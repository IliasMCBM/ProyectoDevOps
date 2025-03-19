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
    self.csvs = {
    'CISSM': ['event_description'],
    'HACKMAGEDDON': ['Description'],
    'ICSSTRIVE': ['description'],
    'KONBRIEFING': ['description'],
    'TISAFE': ['attack_details', 'id'],
    'WATERFALL': ['incident_summary', 'id']
    }
    self.k = 5
    self.documents = []
    self.model_name = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-mpnet-base-v2')
    self.vector_db_path = os.getenv('VECTOR_DB_PATH', 'faiss_index')
    self.api_key = os.getenv("GROQ_API_KEY")

    if not self.api_key:
      raise ValueError('API_KEY is required')

    self.carga_documentos()
    self.search_with_langchain_faiss()

  def carga_documentos(self):
    # Paso 2: Divide los csv en Documentos
    for titulo_documento, columns in self.csvs.items():
      file_path = f'Data/{titulo_documento}_cleaned.csv'
      if not os.path.exists(file_path):
        raise ValueError(f'El archivo {file_path} no existe')
      
      df = pd.read_csv(file_path)
      df = df[columns]
      
      # Generate id only for documents that don't have it
      if 'id' not in columns:
        df['id'] = df.index

      for _, row in df.iterrows():
        metadata = {"source": titulo_documento}
        if 'id' in df.columns:
          metadata["id"] = row['id']
        
        # Get the content from the first column and convert to string
        content = str(row.iloc[0])
            
        self.documents.append(
          Document(
            page_content=content,
            metadata=metadata
          )
        )

  def search_with_langchain_faiss(self):
    # Paso 1: Configura el modelo de embeddings
    print('Iniciando configuración del modelo de embeddings...')
    try:
      embeddings = HuggingFaceEmbeddings(
        model_name=self.model_name,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
      )
      print('Modelo de embeddings configurado exitosamente')
    except Exception as e:
      print(f'Error al configurar el modelo de embeddings: {str(e)}')
      raise

    try:
      print('Cargando base de datos vectorial...')
      self.faiss_index = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
      print('Base de datos vectorial cargada exitosamente')
    except Exception as e:
      print('Base de datos no encontrada, generando nueva base de datos...')
      try:
        # Paso 4: Carga los documentos en el índice FAISS usando from_documents
        self.faiss_index = FAISS.from_documents(self.documents, embedding=embeddings)
        self.faiss_index.save_local("faiss_index")
        print('Nueva base de datos vectorial generada y guardada exitosamente')
      except Exception as e:
        print(f'Error al generar la base de datos vectorial: {str(e)}')
        raise

    print('Base de datos vectorial lista')


  def busca_contexto(self, query):
    # Paso 5: Realiza la búsqueda
    results = self.faiss_index.similarity_search(query, k= self.k)

    # Paso 6: Devuelve los resultados como texto
    return [result.page_content for result in results]


  def llamaResponse(self, query):
    client = Groq(api_key=self.api_key)
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
