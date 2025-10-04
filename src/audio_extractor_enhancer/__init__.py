"""Top-level package for the Audio Extractor & Enhancer project."""

from .extraction import AudioExtractionError, extract_audio
from .pipeline import AudioProcessingPipeline

__all__ = ["AudioProcessingPipeline", "extract_audio", "AudioExtractionError"]

