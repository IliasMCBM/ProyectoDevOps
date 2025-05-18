import os
import pandas as pd
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import time

def build_faiss_index(max_docs_per_source=500):
    """
    Loads documents from CSV files specified in the CSVS_CONFIG,
    generates FAISS index using HuggingFace embeddings, and saves it locally.
    
    Args:
        max_docs_per_source: Maximum number of documents to load per source file
    """
    print("Loading environment variables...")
    load_dotenv()

    data_path = os.environ.get("DATA_PATH", "Data")
    faiss_index_path = os.environ.get("FAISS_INDEX_PATH", "faiss_index")
    model_name = 'sentence-transformers/all-mpnet-base-v2'

    # Configuration for CSV files and relevant columns
    csvs_config = {
        'CISSM': ['event_description'],
        'HACKMAGEDDON': ['Description'],
        'ICSSTRIVE': ['description'],
        'KONBRIEFING': ['description'],
        'TISAFE': ['attack_details', 'id'],
        'WATERFALL': ['incident_summary', 'id']
    }

    documents = []
    print(f"Loading documents from: {data_path} (limited to {max_docs_per_source} per source)")
    total_start_time = time.time()
    
    for titulo_documento, columns in csvs_config.items():
        file_path = f'{data_path}/{titulo_documento}_cleaned.csv'
        try:
            start_time = time.time()
            print(f"Reading {file_path}...")
            df = pd.read_csv(file_path)
            df = df[columns]
            
            # Limit the number of documents per source
            if len(df) > max_docs_per_source:
                print(f"Limiting {titulo_documento} to {max_docs_per_source} documents (from {len(df)})")
                df = df.sample(max_docs_per_source, random_state=42)
            
            if 'id' not in columns:
                df['id'] = df.index

            for i, r in df.iterrows():
                documents.append(
                    Document(
                        page_content=r.iloc[0],
                        metadata={
                            "source": titulo_documento,
                            "id": r['id']
                        }
                    )
                )
            elapsed = time.time() - start_time
            print(f"Loaded {len(df)} documents from {file_path} in {elapsed:.2f} seconds")
        except FileNotFoundError:
            print(f"ERROR: File not found {file_path}. Skipping.")
            continue
        except KeyError as e:
            print(f"ERROR: Column {e} not found in {file_path}. Skipping.")
            continue
    
    if not documents:
        print("No documents loaded. FAISS index will not be built.")
        return

    print(f"\nTotal documents loaded: {len(documents)}")
    print(f"Loading time: {time.time() - total_start_time:.2f} seconds")
    print(f"\nGenerating FAISS index with model: {model_name}")
    print("This may take several minutes depending on the number of documents...")
    
    embedding_start_time = time.time()
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    print(f"Model loaded in {time.time() - embedding_start_time:.2f} seconds")
    
    try:
        print("Creating vector store from documents...")
        vector_start_time = time.time()
        vector_store = FAISS.from_documents(documents, embedding=embeddings)
        print(f"Vector store created in {time.time() - vector_start_time:.2f} seconds")
        
        print(f"Saving FAISS index to: {faiss_index_path}")
        save_start_time = time.time()
        vector_store.save_local(faiss_index_path)
        print(f"Index saved in {time.time() - save_start_time:.2f} seconds")
        
        total_time = time.time() - total_start_time
        print(f"\nFAISS index successfully built and saved to: {faiss_index_path}")
        print(f"Total processing time: {total_time:.2f} seconds")
    except Exception as e:
        print(f"Error building or saving FAISS index: {e}")

if __name__ == '__main__':
    print("Starting FAISS index build process...")
    build_faiss_index(max_docs_per_source=500)  # Limit to 500 docs per source
    print("FAISS index build process finished.") 