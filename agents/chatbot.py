import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import List, Dict

class ChatBot:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        model_name = os.getenv("GEMINI_MODEL_NAME")
        
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.context = {}
        self.history = []
        
    def add_context(self, transcript: str, summaries: List[str]):
        """Store podcast context for reference"""
        self.context = {
            "transcript": transcript,
            "summaries": summaries
        }
        
        # Initialize chat with context
        system_prompt = f"""You are a helpful AI assistant that answers questions about a podcast.
        Use only the following content to answer questions:
        
        TRANSCRIPT:
        {transcript[:1000]}... (truncated)
        
        SUMMARY:
        {' '.join(summaries)}
        
        Only answer questions based on this content. If the answer cannot be found in the content, say "I cannot answer that based on the podcast content."
        """
        
        self.chat = self.model.start_chat(history=[])
        self.chat.send_message(system_prompt)
        
    def ask(self, question: str) -> str:
        """Answer questions based on podcast context"""
        if not self.context:
            return "Please add podcast context first using add_context()"
            
        try:
            response = self.chat.send_message(
                f"Based only on the podcast content provided, {question}"
            )
            answer = response.text.strip()
            self.history.append({"question": question, "answer": answer})
            return answer
            
        except Exception as e:
            return f"[Error] Failed to get response: {e}"
            
    def get_history(self) -> List[Dict[str, str]]:
        """Return chat history"""
        return self.history
