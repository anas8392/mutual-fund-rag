import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
import os
import sqlite3

# ChromaDB now strictly requires sqlite3 >= 3.35.0. 
# pysqlite3 provides an updated sqlite3 engine that we can hot-swap if the built-in is too old.
import sys
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

def ingest_data():
    csv_path = "../phase1_data_acquisition/mutual_fund_data.csv"
    if not os.path.exists(csv_path):
        print(f"Error: Could not find {csv_path}")
        return

    df = pd.read_csv(csv_path)
    
    # Initialize ChromaDB Local Client
    # It will create a folder 'chroma_db' in the current directory
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    
    # Define an embedding function using HuggingFace sentence-transformers
    # all-MiniLM-L6-v2 is small, fast, and highly effective for standard RAG
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    # Create or get the collection
    collection_name = "mutual_funds"
    collection = chroma_client.get_or_create_collection(
        name=collection_name, 
        embedding_function=sentence_transformer_ef,
        metadata={"description": "Mutual Fund details scraped from Indmoney"}
    )
    
    # Prepare documents, metadatas, and ids
    documents = []
    metadatas = []
    ids = []
    
    for index, row in df.iterrows():
        # Create a rich text chunk that the LLM can easily read and retrieve against
        chunk_text = (
            f"Mutual Fund Name: {row['Fund Name']}. "
            f"This fund has an Expense Ratio of {row['Expense Ratio']} and an Exit Load of {row['Exit Load']}. "
            f"The minimum SIP amount is {row['Minimum SIP']}. "
            f"Lock-in period: {row['Lock-in']}. "
            f"Riskometer: {row['Riskometer']}. "
            f"Benchmark: {row['Benchmark']}. "
            f"Instructions to download statements: {row['How to download statements']}."
        )
        documents.append(chunk_text)
        
        # Store exact values as metadata for exact filtering later if needed
        metadata = {
            "fund_name": row['Fund Name'],
            "source_url": row['Source URL'],
            "expense_ratio": row['Expense Ratio'],
            "exit_load": row['Exit Load'],
            "min_sip": row['Minimum SIP'],
            "lock_in": row['Lock-in'],
            "riskometer": row['Riskometer'],
            "benchmark": row['Benchmark']
        }
        metadatas.append(metadata)
        
        # Use a slugified version of the fund name as the ID
        id_str = row['Fund Name'].lower().replace(" ", "-").replace(",", "")
        ids.append(id_str)

    # Ingest data into ChromaDB
    print(f"Ingesting {len(documents)} mutual fund records into ChromaDB...")
    collection.upsert(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    # Verify insertion
    count = collection.count()
    print(f"Success! The 'mutual_funds' collection now contains {count} records.")

if __name__ == "__main__":
    ingest_data()
