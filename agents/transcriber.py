from faster_whisper import WhisperModel

class Transcriber:
    def __init__(self, model_size="base"):
        self.model = WhisperModel(model_size, compute_type="int8")  # fast on CPU

    def transcribe(self, audio_path: str) -> str:
        print(f"[Transcriber] Transcribing {audio_path} ...")
        segments, _ = self.model.transcribe(audio_path, beam_size=5)

        # Combine all segments into a single text string
        transcript = " ".join([segment.text for segment in segments])
        return transcript
