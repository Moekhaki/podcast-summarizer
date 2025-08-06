from typing import List, Tuple

import chromadb
from chromadb.utils import embedding_functions
from chromadb.errors import NotFoundError

class EmbeddingStore:
    def __init__(self, 
                 model_name: str = "all-MiniLM-L6-v2", 
                 persist_dir: str = "embedding_cache"):
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name)
        
    def get_or_create_collection(self, file_id: str):
        """Get existing collection or create new one"""
        try:
            # Try to get existing collection
            collection = self.client.get_collection(
                name=file_id,
                embedding_function=self.embedding_fn
            )
            print(f"[EmbeddingStore] Using existing collection for {file_id}")
        except NotFoundError:
            # Create new collection if doesn't exist
            print(f"[EmbeddingStore] Creating new collection for {file_id}")
            collection = self.client.create_collection(
                name=file_id,
                embedding_function=self.embedding_fn
            )
        return collection
        
    def create_embeddings(self, text: str, file_id: str, chunk_size: int = 200) -> List[str]:
        """Create overlapping text chunks and store in ChromaDB if not exists"""
        # Get or create collection
        collection = self.get_or_create_collection(file_id)
        
        # Check if collection already has embeddings
        if collection.count() > 0:
            print(f"[EmbeddingStore] Found existing embeddings for {file_id}")
            results = collection.get()
            return results['documents']
            
        # Create new embeddings if needed
        print(f"[EmbeddingStore] Creating new embeddings for {file_id}")
        words = text.split()
        chunks = []
        
        # Create chunks with 50% overlap
        for i in range(0, len(words), chunk_size // 2):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
            
        # Add chunks to collection with IDs
        if chunks:
            collection.add(
                documents=chunks,
                ids=[f"chunk_{i}" for i in range(len(chunks))]
            )
        
        return chunks

    def get_relevant_chunks(self, query: str, file_id: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """Get most relevant chunks using ChromaDB"""
        try:
            collection = self.client.get_collection(
                name=file_id,
                embedding_function=self.embedding_fn
            )
            
            results = collection.query(
                query_texts=[query],
                n_results=top_k,
                include=['documents', 'distances']
            )
            
            # Convert distances to similarities
            similarities = [1 / (1 + dist) for dist in results['distances'][0]]
            return list(zip(results['documents'][0], similarities))
            
        except NotFoundError:
            print(f"[EmbeddingStore] No collection found for {file_id}")
            return []