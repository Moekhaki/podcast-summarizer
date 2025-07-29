from faster_whisper import WhisperModel
from utils.caching import with_cache
import numpy as np
from pydub import AudioSegment
import os
from typing import List
from concurrent.futures import ThreadPoolExecutor
import gc

class Transcriber:
    def __init__(self, model_size="base", chunk_size=300):  # chunk_size in seconds
        self.model = WhisperModel(model_size, compute_type="int8")
        self.chunk_size = chunk_size
        
    def _split_audio(self, audio_path: str) -> List[AudioSegment]:
        """Split audio file into chunks"""
        audio = AudioSegment.from_file(audio_path)
        chunk_length = self.chunk_size * 1000  # convert to milliseconds
        
        chunks = []
        for i in range(0, len(audio), chunk_length):
            chunk = audio[i:i + chunk_length]
            chunks.append(chunk)
        return chunks

    def _transcribe_chunk(self, chunk: AudioSegment) -> str:
        """Transcribe a single audio chunk"""
        # Save chunk temporarily
        temp_path = "temp_chunk.wav"
        chunk.export(temp_path, format="wav")
        
        try:
            segments, _ = self.model.transcribe(
                temp_path,
                beam_size=5,
                vad_filter=True,  # Voice Activity Detection
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            return " ".join([segment.text for segment in segments])
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            gc.collect()  # Suggestion code change: garbage collection after processing each chunk

    @with_cache("transcription_cache")
    def transcribe(self, audio_path: str) -> str:
        """Transcribe audio file to text with chunking and caching"""
        print(f"[Transcriber] Transcribing {audio_path} ...")
        
        # Split audio into manageable chunks
        chunks = self._split_audio(audio_path)
        print(f"[Transcriber] Split into {len(chunks)} chunks")
        
        # Transcribe each chunk
        with ThreadPoolExecutor(max_workers=3) as executor:
            transcriptions = list(executor.map(self._transcribe_chunk, chunks))
        
        # Combine all transcriptions
        return " ".join(transcriptions)
