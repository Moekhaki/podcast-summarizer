from typing import List

class Explainer:
    def __init__(self):
        pass  # No external model, just basic logic

    def explain_summary(self, summary: str) -> str:
        return f"Main takeaway: {summary[:100]}..."

    def explain_all(self, summaries: List[str]) -> List[str]:
        print(f"[Explainer] Generating insights for {len(summaries)} summaries...")
        return [self.explain_summary(s) for s in summaries]
