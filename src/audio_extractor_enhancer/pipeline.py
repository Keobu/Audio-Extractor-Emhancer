"""Core orchestration logic for the audio extraction and enhancement pipeline."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .extraction import extract_audio
from .separation import separate_music_and_vocals


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
        """Separate audio into stems and return the selected output track."""

        separation_dir = self.config.work_dir / "separation"
        music_path, vocals_path = separate_music_and_vocals(audio_path, separation_dir)

        if self.config.isolate_vocals:
            target_vocals = self.config.work_dir / "vocals.wav"
            target_vocals.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(vocals_path, target_vocals)

        if not self.config.isolate_music:
            return vocals_path

        target_music = self.config.work_dir / "music.wav"
        shutil.copy2(music_path, target_music)
        return target_music

    def enhance_audio(self, music_path: Path) -> Path:
        """Placeholder for Phase 4: apply EQ, noise reduction, and leveling."""

        # TODO: implement enhancement with librosa or pydub.
        return self.config.output_path

    def run(self) -> Path:
        """Execute the pipeline end-to-end using the placeholder stages."""

        extracted_audio = self.extract_audio()
        selected_track = self.separate_sources(extracted_audio)
        return self.enhance_audio(selected_track)


__all__ = ["PipelineConfig", "AudioProcessingPipeline"]

