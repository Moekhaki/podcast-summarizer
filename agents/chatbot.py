import os
from typing import List, Dict, Tuple
from dotenv import load_dotenv
import google.generativeai as genai
import numpy as np
from utils.embedding import EmbeddingStore



class ChatBot:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        model_name = os.getenv("GEMINI_MODEL_NAME")
        
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.embedding_store = EmbeddingStore()
        self.context = {}
        self.history = []
        self.chat = None
        
    def add_context(self, transcript: str, chunks_and_embeddings: List[Tuple[str, np.ndarray]] = None):
        """Initialize chat with context and history"""
        if chunks_and_embeddings:
            self.chunks_and_embeddings = chunks_and_embeddings
            self.chunks = [chunk for chunk, _ in chunks_and_embeddings]
        else:
            # Fallback to creating embeddings if not provided
            print("[ChatBot] No embeddings provided, creating new ones...")
            self.chunks_and_embeddings = self.embedding_store.create_embeddings(transcript)
            self.chunks = [chunk for chunk, _ in self.chunks_and_embeddings]
        
        
        # Initialize chat with system prompt and history
        system_prompt = """You are a helpful AI assistant that answers questions about a podcast.
        You will answer questions only based on the provided context and previous exchanges.
        Maintain conversation continuity by referencing previous exchanges when relevant.
        If the answer cannot be found in the context, say "I cannot answer that based on the podcast content."
        """
        
        self.chat = self.model.start_chat(history=[])
        self.chat.send_message(system_prompt)
        
    def ask(self, question: str) -> str:            
        try:
            # Get relevant chunks using semantic search
            relevant_chunks = self.embedding_store.get_relevant_chunks(
                query=question,
                chunks=self.chunks,
                top_k=3
            )
            
            # Create prompt with retrieved context and recent history
            context_text = "\n\n".join([
                f"Relevant Context (similarity: {score:.2f}):\n{chunk}"
                for chunk, score in relevant_chunks
            ])
            
            prompt = f"""Based on these relevant sections from the podcast:

{context_text}

Please answer this question: {question}

Remember to only use information from the provided context sections and previous exchanges."""

            response = self.chat.send_message(prompt)
            answer = response.text.strip()
            
            # Store question, answer and used context
            self.history.append({
                "question": question,
                "answer": answer,
                "context": context_text
            })
            
            return answer
            
        except Exception as e:
            return f"[Error] Failed to get response: {e}"
