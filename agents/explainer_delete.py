import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import List

class Explainer:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
        
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def explain_segment(self, segment: str) -> str:
        try:
            prompt = f"""Given this podcast segment, extract the key insight and main message:

Segment:
{segment}

Please provide a concise but meaningful insight that:
1. Identifies the core message or theme
2. Extracts the most important information
3. Explains why this matters to the listener

Key Insight:"""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"[Error] Failed to generate insight: {e}"

    def explain_all(self, segments: List[str]) -> List[str]:
        print(f"[Explainer] Generating insights for {len(segments)} segments...")
        return [self.explain_segment(s) for s in segments]
