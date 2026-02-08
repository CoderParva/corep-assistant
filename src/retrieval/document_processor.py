import json
from pathlib import Path
from typing import List, Dict
import pickle

class DocumentProcessor:
    """Handles loading and chunking of regulatory documents"""
    
    def __init__(self, corpus_path: str = "data/raw/sample_pra_corpus.json"):
        self.corpus_path = corpus_path
        self.chunks = []
        
    def load_corpus(self) -> List[Dict]:
        """Load regulatory corpus from JSON"""
        with open(self.corpus_path, 'r', encoding='utf-8') as f:
            corpus = json.load(f)
        print(f"✓ Loaded {len(corpus)} articles")
        return corpus
    
    def chunk_documents(self, corpus: List[Dict]) -> List[Dict]:
        """Split documents into chunks"""
        chunks = []
        for doc in corpus:
            chunks.append({
                'text': doc['content'],
                'metadata': {
                    'article_number': doc['article_number'],
                    'source': doc['source']
                }
            })
        
        print(f"✓ Created {len(chunks)} chunks")
        self.chunks = chunks
        return chunks
    
    def save_chunks(self, chunks: List[Dict]):
        """Save chunks to disk"""
        Path("data/processed").mkdir(parents=True, exist_ok=True)
        
        with open("data/processed/chunks.pkl", 'wb') as f:
            pickle.dump(chunks, f)
        
        print(f"✓ Saved {len(chunks)} chunks")

def build_vector_store():
    """Main function to process documents"""
    processor = DocumentProcessor()
    
    # Load and process documents
    corpus = processor.load_corpus()
    chunks = processor.chunk_documents(corpus)
    
    # Save chunks
    processor.save_chunks(chunks)
    
    print("\n✓ Document processing complete!")

if __name__ == "__main__":
    build_vector_store()