import gc
import tempfile
import hashlib
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple, Dict
from pathlib import Path

from faster_whisper import WhisperModel
from pydub import AudioSegment

from utils.caching import with_cache
from utils.embedding import EmbeddingStore

class Transcriber:
    def __init__(self, model_size="base", chunk_size=300):  # chunk_size in seconds
        self.model = WhisperModel(model_size, compute_type="int8")
        self.chunk_size = chunk_size
        self.temp_dir = Path(tempfile.mkdtemp(prefix="podcast_chunks_"))
        self.embedding_store = EmbeddingStore()

    def _split_audio(self, audio_path: str) -> List[Tuple[int, AudioSegment]]:
        """Split audio file into chunks and return with indices"""
        audio = AudioSegment.from_file(audio_path)
        chunk_length = self.chunk_size * 1000  # convert to milliseconds
        
        chunks = []
        for i in range(0, len(audio), chunk_length):
            chunk = audio[i:i + chunk_length]
            chunks.append((i, chunk))
        return chunks

    def _transcribe_chunk(self, chunk_data: Tuple[int, AudioSegment]) -> Tuple[int, str]:
        """Transcribe a single chunk and return index with text"""
        chunk_idx, chunk = chunk_data
        
        # Create unique temp file for this chunk
        temp_path = self.temp_dir / f"chunk_{chunk_idx}.wav"
        chunk.export(str(temp_path), format="wav")
        
        try:
            segments, _ = self.model.transcribe(
                str(temp_path),
                beam_size=5,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            return chunk_idx, " ".join([segment.text for segment in segments])
        finally:
            if temp_path.exists():
                temp_path.unlink()
            gc.collect()

    def _cleanup(self):
        """Clean up temporary directory"""
        if self.temp_dir.exists():
            for file in self.temp_dir.glob("*.wav"):
                file.unlink(missing_ok=True)
            self.temp_dir.rmdir()

    def _get_file_id(self, audio_path: str) -> str:
        """Generate unique ID for the audio file"""
        with open(audio_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    @with_cache("transcription_cache")
    def transcribe(self, audio_path: str) -> str:
        """Transcribe audio file to text with chunking and caching"""
        print(f"[Transcriber] Transcribing {audio_path} ...")
        
        try:
            # Split audio into manageable chunks
            chunks = self._split_audio(audio_path)
            print(f"[Transcriber] Split into {len(chunks)} chunks")
            
            # Transcribe each chunk
            with ThreadPoolExecutor(max_workers=3) as executor:
                results = list(executor.map(self._transcribe_chunk, chunks))
            
            # Sort by chunk index and combine
            results.sort(key=lambda x: x[0])
            return " ".join(text for _, text in results)
            
        finally:
            self._cleanup()

    def transcribe_and_embed(self, audio_path: str) -> Dict[str, str]:
        """Transcribe audio and create embeddings"""
        # Generate file ID first
        file_id = self._get_file_id(audio_path)
        
        # Get transcript (this call is cached)
        transcript = self.transcribe(audio_path)
        
        # Create embeddings
        print("[Transcriber] Generating embeddings...")
        self.embedding_store.create_embeddings(
            text=transcript,
            file_id=file_id
        )
        
        # Return dictionary with both results
        return {
            "transcript": transcript,
            "file_id": file_id
        }
