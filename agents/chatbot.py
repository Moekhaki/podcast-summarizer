import os
import requests

MODEL = "mistralai/Mistral-7B-Instruct-v0.3"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL}"
HF_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

class ChatBot:
    def ask(self, context: str, question: str) -> str:
        prompt = f"""You are a helpful assistant. Use the following podcast summary to answer the user's question.

Podcast Summary:
{context}

Question: {question}
Answer:"""

        try:
            response = requests.post(
                API_URL,
                headers=HEADERS,
                json={"inputs": prompt}
            )
            response.raise_for_status()
            output = response.json()
            if isinstance(output, list):
                return output[0].get("generated_text", "[No answer returned]").strip()
            elif isinstance(output, dict) and "generated_text" in output:
                return output["generated_text"].strip()
            else:
                return "[Error] Unexpected model output format."
        except Exception as e:
            return f"[Error] {e}"
