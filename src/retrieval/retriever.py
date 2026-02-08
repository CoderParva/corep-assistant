import pickle
import numpy as np
from typing import List, Dict
from sentence_transformers import SentenceTransformer

class RegulatoryRetriever:
    """Retrieves relevant regulatory passages for a given query"""
    
    def __init__(self, chunks_path: str = "data/processed/chunks.pkl"):
        
        # Load chunks
        with open(chunks_path, 'rb') as f:
            self.chunks = pickle.load(f)
        
        # Load embedder
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Generate embeddings for all chunks
        print("Loading document embeddings...")
        texts = [chunk['text'] for chunk in self.chunks]
        self.embeddings = self.embedder.encode(texts)
        
        print(f"✓ Loaded retriever with {len(self.chunks)} documents")
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search for relevant regulatory passages using cosine similarity"""
        
        # Generate query embedding
        query_embedding = self.embedder.encode([query])[0]
        
        # Calculate cosine similarities
        similarities = []
        for doc_embedding in self.embeddings:
            similarity = np.dot(query_embedding, doc_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
            )
            similarities.append(similarity)
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Retrieve chunks
        results = []
        for idx in top_indices:
            chunk = self.chunks[idx]
            results.append({
                'text': chunk['text'],
                'article_number': chunk['metadata']['article_number'],
                'source': chunk['metadata']['source'],
                'relevance_score': float(similarities[idx])
            })
        
        return results
    
    def format_context(self, results: List[Dict]) -> str:
        """Format retrieved chunks into context for LLM"""
        context_parts = []
        for result in results:
            context_parts.append(
                f"[{result['source']}]\n{result['text']}\n"
            )
        return "\n".join(context_parts)


def test_retriever():
    """Test the retriever with sample queries"""
    retriever = RegulatoryRetriever()
    
    test_queries = [
        "What is the risk weight for unrated corporate exposures?",
        "What risk weight applies to residential mortgages?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        
        results = retriever.search(query, top_k=2)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['source']} (Score: {result['relevance_score']:.3f})")
            print(f"   {result['text'][:200]}...")

if __name__ == "__main__":
    test_retriever()