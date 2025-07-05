from huggingface_hub import InferenceClient
import os

class ChatBot:
    def __init__(self):
        hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
        self.client = InferenceClient(model="deepset/roberta-base-squad2", token=hf_token)

    def ask(self, context: str, question: str) -> str:
        try:
            result = self.client.question_answering(question=question, context=context)
            return result.get("answer", "[No answer found]").strip()
        except Exception as e:
            return f"[Error] {e}"
