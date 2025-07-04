from typing import List

class Segmenter:
    def __init__(self, max_words: int = 150):
        self.max_words = max_words

    def segment(self, transcript: str) -> List[str]:
        words = transcript.split()
        segments = []

        for i in range(0, len(words), self.max_words):
            chunk = words[i:i + self.max_words]
            segments.append(" ".join(chunk))

        return segments
