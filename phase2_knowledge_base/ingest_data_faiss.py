import pandas as pd
import numpy as np
import faiss
import pickle
import os
try:
    from fastembed import TextEmbedding
    USE_FASTEMBED = True
except ImportError:
    from sentence_transformers import SentenceTransformer
    USE_FASTEMBED = False

def ingest_data():
    csv_path = "../phase1_data_acquisition/mutual_fund_data.csv"
    if not os.path.exists(csv_path):
        print(f"Error: Could not find {csv_path}")
        return

    df = pd.read_csv(csv_path)
    
    # Initialize Embedding Model 
    print(f"Loading embedding model 'sentence-transformers/all-MiniLM-L6-v2' (FastEmbed={USE_FASTEMBED})...")
    if USE_FASTEMBED:
        model = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2", cache_dir=os.environ.get("VERCEL_TMP_CACHE", None))
    else:
        model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Prepare documents and metadata
    documents = []
    metadatas = []
    
    for index, row in df.iterrows():
        # Create a rich text chunk targeting ideal retrieval
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
        
        # Store metadata to retrieve alongside the vector payload
        metadata = {
            "id": index,
            "fund_name": row['Fund Name'],
            "source_url": row['Source URL'],
            "expense_ratio": row['Expense Ratio'],
            "exit_load": row['Exit Load'],
            "min_sip": row['Minimum SIP'],
            "lock_in": row['Lock-in'],
            "riskometer": row['Riskometer'],
            "benchmark": row['Benchmark'],
            "chunk_text": chunk_text
        }
        metadatas.append(metadata)

    # Generate Embeddings
    print(f"Generating embeddings for {len(documents)} records...")
    if USE_FASTEMBED:
        embeddings = np.vstack(list(model.embed(documents)))
    else:
        embeddings = model.encode(documents)
        
    embeddings = np.array(embeddings).astype(np.float32)
    
    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(embeddings)

    # Initialize FAISS Index (IndexFlatIP for inner product/cosine similarity since vectors are normalized)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    
    print("Adding vectors to FAISS index...")
    index.add(embeddings)
    
    # Save the index and the metadata mapping to disk
    faiss.write_index(index, "mutual_funds.index")
    with open("metadata.pkl", "wb") as f:
        pickle.dump(metadatas, f)
        
    print(f"Successfully ingested {index.ntotal} records.")
    print("Saved 'mutual_funds.index' and 'metadata.pkl' to phase2_knowledge_base.")

if __name__ == "__main__":
    ingest_data()
