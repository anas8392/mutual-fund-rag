import faiss
import pickle
import numpy as np
import os
try:
    from fastembed import TextEmbedding
    USE_FASTEMBED = True
except ImportError:
    from sentence_transformers import SentenceTransformer
    USE_FASTEMBED = False

class FundRetriever:
    def __init__(self, index_dir="../phase2_knowledge_base"):
        self.index_path = os.path.join(index_dir, "mutual_funds.index")
        self.meta_path = os.path.join(index_dir, "metadata.pkl")
        
        # Ensure files exist
        if not os.path.exists(self.index_path) or not os.path.exists(self.meta_path):
            raise FileNotFoundError(f"FAISS index or metadata not found in {index_dir}")
        
        print("Loading FAISS index & metadata...")
        self.index = faiss.read_index(self.index_path)
        with open(self.meta_path, "rb") as f:
            self.metadata = pickle.load(f)
            
        print(f"Initializing embedding model (all-MiniLM-L6-v2) | FastEmbed: {USE_FASTEMBED}...")
        if USE_FASTEMBED:
            self.model = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2", cache_dir=os.environ.get("VERCEL_TMP_CACHE", None))
        else:
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
        
    def retrieve(self, query: str, top_k: int = 2) -> list:
        """
        Embeds the query and fetches the top_k closest chunks from the FAISS index.
        Returns a list of dictionaries with content and source paths.
        """
        # Encode the query
        if USE_FASTEMBED:
            # FastEmbed yields an array sequence, so extract the first one
            query_vector = np.array(list(self.model.embed([query]))[0])
        else:
            query_vector = self.model.encode(query)
            
        # FAISS normalization expects a 2D array: (1, vector_dimension)
        query_vector = np.expand_dims(query_vector, axis=0)
        faiss.normalize_L2(query_vector)
        
        # Perform inner product (cosine) search
        distances, indices = self.index.search(query_vector, top_k)
        
        results = []
        for i in range(top_k):
            idx = indices[0][i]
            score = distances[0][i]
            
            if idx != -1 and idx < len(self.metadata):
                meta = self.metadata[idx]
                results.append({
                    "score": float(score),
                    "fund_name": meta.get("fund_name"),
                    "source_url": meta.get("source_url"),
                    "content": meta.get("chunk_text")
                })
                
        return results

# For testing independently
if __name__ == "__main__":
    import sys
    # Force UTF-8 on Windows consoles to prevent crashes when printing Rupee symbol (₹)
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
        
    retriever = FundRetriever()
    test_query = "What is the exit load for HDFC Flexi cap?"
    results = retriever.retrieve(test_query)
    
    print(f"\nQUERY: {test_query}")
    for i, res in enumerate(results):
        print(f"\nResult {i+1} (Sim Score: {res['score']:.4f}):")
        print(f"Content: {res['content']}")
        print(f"URL: {res['source_url']}")
