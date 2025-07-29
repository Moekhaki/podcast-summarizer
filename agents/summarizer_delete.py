import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import List
from utils.caching import with_cache

class Summarizer:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
        
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    @with_cache("summary_cache")
    def summarize_segment(self, text: str) -> str:
        try:
            prompt = f"""Summarize this text concisely while preserving key information:
            {text}
            """
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"[Error] Failed to summarize segment: {e}"

    def summarize_all(self, segments: List[str]) -> List[str]:
        print(f"[Summarizer] Summarizing {len(segments)} segments...")
        return [self.summarize_segment(seg) for seg in segments]
