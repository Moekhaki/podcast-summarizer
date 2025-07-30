import os
from typing import List

import google.generativeai as genai
from dotenv import load_dotenv

from utils.caching import with_cache

class ContentAnalyzer:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
        
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    @with_cache("analysis_cache")
    def analyze_segment(self, segment: str) -> str:
        """Analyze a segment to produce analysis"""
        try:
            prompt = f"""Analyze this podcast segment and provide both a summary and key insights:

Segment:
{segment}

Please provide:
1. A concise summary of the main points
2. 3-5 key insights as bullet points that:
   - Identify core themes
   - Extract important information
   - Explain why it matters

Format your response as:
**Summary**:
[your summary here]

**Key Insights**:
• [insight 1]
• [insight 2]
• [insight 3]"""

            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            return f"[Error] Failed to analyze segment: {e}"

    def analyze_all(self, segments: List[str]) -> List[str]:
        """Analyze all segments"""
        print(f"[ContentAnalyzer] Analyzing {len(segments)} segments...")
        return [self.analyze_segment(s) for s in segments]