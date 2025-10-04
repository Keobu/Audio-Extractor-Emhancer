"""Top-level package for the Audio Extractor & Enhancer project."""

from .enhancement import AudioEnhancementError, EnhancementSettings, enhance_music
from .extraction import AudioExtractionError, extract_audio
from .pipeline import AudioProcessingPipeline
from .separation import SourceSeparationError, separate_music_and_vocals

__all__ = [
    "AudioProcessingPipeline",
    "extract_audio",
    "AudioExtractionError",
    "separate_music_and_vocals",
    "SourceSeparationError",
    "enhance_music",
    "EnhancementSettings",
    "AudioEnhancementError",
]

