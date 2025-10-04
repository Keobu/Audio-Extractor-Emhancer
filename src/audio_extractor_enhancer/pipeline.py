"""Core orchestration logic for the audio extraction and enhancement pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .extraction import extract_audio


@dataclass
class PipelineConfig:
    """Configuration container for pipeline paths and options."""

    input_path: Path
    work_dir: Path
    output_path: Path
    isolate_vocals: bool = False
    isolate_music: bool = True
    enhancement_profile: Optional[str] = None


class AudioProcessingPipeline:
    """End-to-end pipeline skeleton for forthcoming audio processing phases."""

    def __init__(self, config: PipelineConfig) -> None:
        self.config = config
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create working directories so later stages can write intermediate files."""

        self.config.work_dir.mkdir(parents=True, exist_ok=True)
        self.config.output_path.parent.mkdir(parents=True, exist_ok=True)

    def extract_audio(self) -> Path:
        """Extract the raw audio track from the configured input video."""

        extracted_path = self.config.work_dir / "extracted_audio.wav"
        return extract_audio(self.config.input_path, extracted_path)

    def separate_sources(self, audio_path: Path) -> Path:
        """Placeholder for Phase 3: split stems using Spleeter or Demucs."""

        # TODO: implement source separation logic.
        return self.config.work_dir / "music.wav"

    def enhance_audio(self, music_path: Path) -> Path:
        """Placeholder for Phase 4: apply EQ, noise reduction, and leveling."""

        # TODO: implement enhancement with librosa or pydub.
        return self.config.output_path

    def run(self) -> Path:
        """Execute the pipeline end-to-end using the placeholder stages."""

        extracted_audio = self.extract_audio()
        music_track = self.separate_sources(extracted_audio)
        return self.enhance_audio(music_track)


__all__ = ["PipelineConfig", "AudioProcessingPipeline"]

