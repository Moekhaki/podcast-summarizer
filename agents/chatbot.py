import os

from dotenv import load_dotenv
import google.generativeai as genai

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
        self.file_id = None
        self.context = None
        
    def add_context(self, transcript: str, file_id: str):
        """Store podcast context and file_id for embeddings"""
        self.file_id = file_id
        self.context = transcript
        
        # Initialize chat
        system_prompt = """You are a helpful AI assistant that answers questions about a podcast.
        Only answer questions based on the provided context and previous exchanges."""
        self.chat = self.model.start_chat(history=[])
        self.chat.send_message(system_prompt)
        
    def ask(self, question: str) -> str:
        if not self.file_id:
            return "Please add podcast context first"
            
        try:
            relevant_chunks = self.embedding_store.get_relevant_chunks(
                query=question,
                file_id=self.file_id,
                top_k=3
            )
            
            context_text = "\n\n".join([
                f"Relevant Context (similarity: {score:.2f}):\n{chunk}"
                for chunk, score in relevant_chunks
            ])
            
            prompt = f"""Based on these podcast sections:

{context_text}

Question: {question}"""

            response = self.chat.send_message(prompt)
            return response.text.strip()
            
        except Exception as e:
            return f"Error: {str(e)}"
