import os
import pandas as pd
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

def build_faiss_index():
    """
    Loads documents from CSV files specified in the CSVS_CONFIG,
    generates FAISS index using HuggingFace embeddings, and saves it locally.
    Environment variables DATA_PATH and FAISS_INDEX_PATH specify the locations.
    """
    load_dotenv()

    data_path = os.environ.get("DATA_PATH", "data")
    faiss_index_path = os.environ.get("FAISS_INDEX_PATH", "faiss_index")
    model_name = 'sentence-transformers/all-mpnet-base-v2' # This could also be an env var

    # Configuration for CSV files and relevant columns
    # Matches the one in RAG.py, consider centralizing if it grows more complex
    csvs_config = {
        'CISSM': ['event_description'],
        'HACKMAGEDDON': ['Description'],
        'ICSSTRIVE': ['description'],
        'KONBRIEFING': ['description'],
        'TISAFE': ['attack_details', 'id'],
        'WATERFALL': ['incident_summary', 'id']
    }

    documents = []
    print(f"Loading documents from: {data_path}")
    for titulo_documento, columns in csvs_config.items():
        file_path = f'{data_path}/{titulo_documento}_cleaned.csv'
        try:
            df = pd.read_csv(file_path)
            df = df[columns]
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
            print(f"Loaded {len(df)} documents from {file_path}")
        except FileNotFoundError:
            print(f"ERROR: File not found {file_path}. Skipping.")
            continue
        except KeyError as e:
            print(f"ERROR: Column {e} not found in {file_path}. Skipping.")
            continue
    
    if not documents:
        print("No documents loaded. FAISS index will not be built.")
        return

    print(f"Generating FAISS index with model: {model_name}")
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    
    try:
        vector_store = FAISS.from_documents(documents, embedding=embeddings)
        vector_store.save_local(faiss_index_path)
        print(f"FAISS index successfully built and saved to: {faiss_index_path}")
    except Exception as e:
        print(f"Error building or saving FAISS index: {e}")

if __name__ == '__main__':
    print("Starting FAISS index build process...")
    build_faiss_index()
    print("FAISS index build process finished.") 