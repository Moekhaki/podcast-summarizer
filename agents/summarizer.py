import os
import requests
from typing import List

API_URL = "https://api-inference.huggingface.co/models/sshleifer/distilbart-cnn-12-6"
HF_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

headers = {"Authorization": f"Bearer {HF_TOKEN}"}

class Summarizer:
    def __init__(self):
        self.api_url = API_URL
        self.headers = headers

    def summarize_segment(self, text: str) -> str:
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"inputs": text}
            )
            response.raise_for_status()
            summary = response.json()[0]["summary_text"]
            return summary.strip()
        except Exception as e:
            return f"[Error] Failed to summarize segment: {e}"

    def summarize_all(self, segments: List[str]) -> List[str]:
        print(f"[Summarizer] Summarizing {len(segments)} segments...")
        return [self.summarize_segment(seg) for seg in segments]
