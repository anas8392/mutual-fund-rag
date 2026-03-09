import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

def test_retrieval(query, top_k=2):
    print(f"Loading FAISS index...")
    index = faiss.read_index("mutual_funds.index")
    
    print(f"Loading metadata...")
    with open("metadata.pkl", "rb") as f:
        metadatas = pickle.load(f)
        
    print("Loading SentenceTransformer model 'all-MiniLM-L6-v2'...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print(f"\nQuery: '{query}'")
    
    # Generate embedding for the query
    query_vector = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_vector)
    
    # Perform similarity search
    distances, indices = index.search(query_vector, top_k)
    
    print("\n--- RETRIEVAL RESULTS ---")
    for i in range(top_k):
        idx = indices[0][i]
        score = distances[0][i]
        
        if idx != -1 and idx < len(metadatas):
            meta = metadatas[idx]
            print(f"\nRank {i+1} (Score: {score:.4f}):")
            print(f"Fund: {meta['fund_name']}")
            print(f"URL: {meta['source_url']}")
            print(f"Content Chunk: {meta['chunk_text']}")
        else:
            print(f"Rank {i+1}: Valid document not found.")

if __name__ == "__main__":
    test_queries = [
        "Which mutual fund has the lowest exit load?",
        "I'm looking for a gold mutual fund to invest in.",
        "Give me a fund with a 3 year lock-in period."
    ]
    
    for q in test_queries:
        test_retrieval(q, top_k=2)
        print("-" * 50)
